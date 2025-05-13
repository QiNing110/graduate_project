import json
import os
from openai import OpenAI
from tqdm import tqdm
import tiktoken


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
    max_tokens = 98000
    with open(file_path, 'r', encoding='UTF-8-sig') as f:
        lines = f.readlines()
        for line in lines:
            documents += line
    truncated_text = truncate_text_to_tokens(documents, max_tokens)
    return truncated_text


if __name__ == '__main__':
    # 加载数据集与文档
    test_set_path = "./dataset/fictions_utf8/fictions_testset.json"
    documents_path = "./dataset/fictions_utf8/三体_合集.txt"
    test_set = load_testset(test_set_path)
    documents = load_documents(documents_path)

    # 数据保存到本地准备
    result_path = "./dataset/fictions_utf8/pure_LLM_fictions_result.csv"
    output = open(result_path, 'w', encoding='utf-8')
    output.write("\t".join(["id", "question", "answer"]) + "\n")

    # 定义openai sdk
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-274ac4951c314181a6e06cf16dca7318",
        base_url="https://api.deepseek.com",
    )

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

        completion = client.chat.completions.create(
            # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen3-14b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": format_prompt},
            ],
            stream=True,
            extra_body={"enable_thinking": False},
        )

        full_content = ""
        print("输出内容为：")
        for chunk in completion:
            # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过（可以通过chunk.usage获取 Token 使用量）
            if chunk.choices:
                full_content += chunk.choices[0].delta.content

        response = full_content.replace("\n", '\\n')
        print(question + '\n' + response)
        output.write("\t".join([str(id), question, response]) + "\n")

    output.close()
