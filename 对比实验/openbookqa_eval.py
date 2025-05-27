import json
import string
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
import os
os.environ['MODELSCOPE_CACHE'] =  './models'


def normalize_answer(s):
    """增强版答案标准化"""
    # 移除所有标点、空格并转小写（支持Unicode）
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s.strip().lower().replace(" ", "")


def evaluate_parallel(test_file, model_path):

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

    # 读取parquet文件
    df = pd.read_parquet('openbookqa_test.parquet')
    print("数据集长度：")
    print(len(df))
    length = len(df)
    correct = 0
    results = []
    for idx, row in df.iterrows():
        item = row.to_dict()
        
        # 构建选项文本
        choices = [
            f"{label}. {text}"
            for label, text in zip(item['choices']['label'], item['choices']['text'])
        ]
        
        # 构建完整问题文本
        question = f"Question: {item['question_stem']}\n" + "\n".join(choices)
        
        # 构建完整prompt
        prompt = f"""
### Instruction:
Reference Document:
{item['fact1']}
Given four answer candidates, A, B, C and D, choose the best answer choice for the question.
You can only output the four letters A,B,C and D. Do not make any other explanations.
Please refer to the documents above and answer the following question:
{question}
### Response:
"""

        messages = [
            {"role": "user", "content": prompt}
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
            temperature=0.6,             # 降低随机性
            top_p=0.95,                   # 控制生成多样性
            top_k=20,
            min_p = 0,
            repetition_penalty=1.0,      # 防止重复
            max_new_tokens=1000
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        response = tokenizer.decode(output_ids, skip_special_tokens=True)
        print(f"response:  {response}")

        print(f'answer:  {item["answerKey"]}')

        print('batch processed ...   start calculate')

        # 验证答案
        # pred = normalize_answer(response)
        # gt = normalize_answer(item["answer"])
        # aliases = [normalize_answer(a) for a in item["aliases"]]

        ans = response.split('.')[0]

        is_correct = ans == item["answerKey"] 
        if is_correct:
            correct += 1

        # 记录详细结果
        results.append({
            "id": item["id"],
            "question": question,
            "prediction": response,
            "ground_truth": item["answerKey"],
            "is_correct": is_correct
        })

        # 打印进度
        print(f"Processed {idx + 1}/{length} | Current Accuracy: {correct / (idx + 1):.2%}")


    # 保存结果
    with open("eval_results_oqa.json", "w") as f:
        json.dump(results, f, indent=2)

    accuracy = correct / length
    print(f"\nFinal Accuracy: {accuracy:.2%}")
    return accuracy


if __name__ == "__main__":
    test_file = "openbookqa_test.parquet"
    model_path = "Qining12321/qwen3-14B-RAG-Instruct"
    '''Final Accuracy: 91.60%'''
    evaluate_parallel(test_file, model_path)  