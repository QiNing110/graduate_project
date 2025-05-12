import json
import string
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
import os
from tqdm import tqdm
import tiktoken

os.environ['MODELSCOPE_CACHE'] = './models'


def truncate_text_to_tokens(text: str, max_tokens: int) -> str:
    """
    将文本截断到指定的token数

    参数:
        text: 要截断的文本
        max_tokens: 最大保留的token数
        model: 使用的模型名称，影响tokenizer的选择

    返回:
        截断后的文本
    """
    encoder = tiktoken.get_encoding("cl100k_base")

    # 编码文本为tokens
    tokens = encoder.encode(text)

    # 截断tokens
    if len(tokens) <= max_tokens:
        return text  # 无需截断

    truncated_tokens = tokens[:max_tokens]
    # 解码回文本
    try:
        # 尝试解码，如果截断导致不完整的多字节字符，可能会失败
        truncated_text = encoder.decode(truncated_tokens)
    except Exception:
        # 如果解码失败，退回到安全解码，替换无法解码的字符
        truncated_text = encoder.decode_bytes(truncated_tokens).decode('utf-8', errors='replace')

    return truncated_text


def load_testset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        test_set = json.loads(content)
    return test_set


def load_documents(file_path):
    documents = ''
    max_tokens = 32000
    with open(file_path, 'r', encoding='UTF-8-sig') as f:
        lines = f.readlines()
        for line in lines:
            documents += line
    truncated_text = truncate_text_to_tokens(documents, max_tokens)
    return truncated_text


def evaluate_parallel(model_path):
    # 初始化模型
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.float16,
        # attn_implementation="flash_attention_2"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model.eval()

    print("model and tokenizer loaded...")

    # 加载数据集与文档
    test_set_path = "./dataset/fictions_utf8/fictions_testset.json"
    documents_path = "./dataset/fictions_utf8/三体_合集.txt"
    test_set = load_testset(test_set_path)
    documents = load_documents(documents_path)

    results = []
    prompt = '''
参考文档（三体三部曲）：{documents}

请根据参考文档回答用户提出的问题。

我是一个{role}，我的任务是{task}，我的问题是{question}
    '''

    for item in tqdm(test_set, desc="Processing items", unit="item"):
        role = item['role']
        task = item['task']
        question = item['question']
        id = item['id']
        format_prompt = prompt.format(documents=documents, role=role, task=task, question=question)

        messages = [
            {"role": "user", "content": format_prompt}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False  # Switches between thinking and non-thinking modes. Default is True.
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # conduct text completion
        generated_ids = model.generate(
            **model_inputs,
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            min_p=0,
            max_new_tokens=32768
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        response = tokenizer.decode(output_ids, skip_special_tokens=True)
        response = response.replace("\n", '\\n')

        print(question + '\n' + response)

        print('batch processed ... ')

        # 记录结果
        results.append({
            "id": id,
            "question": question,
            "response": response
        })

    # 保存结果
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    model_path = "unsloth/Qwen3-14B"
    evaluate_parallel(model_path)