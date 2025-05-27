import json
import string

from openai import OpenAI
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch


import os
os.environ['MODELSCOPE_CACHE'] =  './models'

client = OpenAI(api_key="sk-0db8e78a021e463293d03e057c14e9b5", base_url="https://api.deepseek.com")


def format_documents(paragraphs):
    """将paragraphs格式化为要求的参考文档样式"""
    doc_str = []
    i = 1
    for p in paragraphs:
        # 索引从1开始显示
        doc_str.append(f"[{i}]{p['Title']}\n{p['Description']}")
        i += 1
    return "\n".join(doc_str)


def evaluate_parallel(test_file, model_path):

    # 初始化模型
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    dataset = []
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data.get('Data', []):
            answer = item.get('Answer', {})
            search_results = item.get('SearchResults', [])
            question = item.get('Question', '')

            filtered_item = {

                'Ans_aliases': answer.get('Aliases', []),
                'Question': question,
                'SearchResults': search_results
            }
            dataset.append(filtered_item)


    correct = 0
    results = []
    print("model and tokenizer loaded...")

    for idx, item in enumerate(dataset):

        doc = format_documents(item['SearchResults'])

        prompt = f"""
### Instruction:
Reference Document:
{doc}
Please refer to the abbreviated documents above and answer the following question:
{item["Question"]}
just give the answer,don't explain.
### Response:"""

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
            max_new_tokens=100
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        response = tokenizer.decode(output_ids, skip_special_tokens=True)

        print('batch processed ...   start calculate')

        # 验证答案
        judge_prompt = f"""
           问题: {item["Question"]}
           模型预测答案: {response}
           正确答案组（列表中相当于正确答案的不同表述）: {item["Ans_aliases"]}

           请判断模型预测的答案与真实答案是否一致。
           请仅回答"一致"或"不一致"。
           """

        judge_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": judge_prompt},
            ],
            stream=False
        )

        deepseek_answer = judge_response.choices[0].message.content
        if deepseek_answer:
            if "一致" == deepseek_answer:
                correct += 1
                is_correct = True
            elif "不一致" in deepseek_answer:
                print(f'{response}与正确答案 {item["Ans_aliases"]}不一致')
                is_correct = False



        results.append({
            "question": item["Question"],
            "prediction": response,
            "ground_truth": item["Ans_aliases"],
            "is_correct": is_correct
        })

        # 打印进度
        print(f"Processed {idx + 1}/{len(dataset)} | Current Accuracy: {correct / (idx + 1):.2%}")


    # 保存结果
    with open("eval_results_tqa.json", "w") as f:
        json.dump(results, f, indent=2)

    accuracy = correct / len(dataset)
    print(f"\nFinal Accuracy: {accuracy:.2%}")
    return accuracy


if __name__ == "__main__":
    test_file = "filtered-web-dev.json"
    model_path = "Qining12321/qwen3-14B-RAG-Instruct"
    evaluate_parallel(test_file, model_path)