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
    results_path = "./dataset/fictions_utf8/results/merged_results.json"
    result_set = load_testset(results_path)


    # 数据保存到本地准备
    # result_path = "./dataset/fictions_utf8/pure_LLM_fictions_result.csv"
    # output = open(result_path, 'w', encoding='utf-8')
    # output.write("\t".join(["id", "question", "answer"]) + "\n")

    # 定义openai sdk
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-6a784eb168794dcd873c445e3890d9db",
        base_url="https://api.deepseek.com",
    )

    json_format = '''
       {
            "全面性": {
                    "Score": {
                            "答案 1": int,
                            "答案 2": int,
                            "答案 3": int,
                            "答案 4": int,
                            
                    },
                    "Reason": ""
            },
            "多样性": {
                    "Score": {
                            "答案 1": int,
                            "答案 2": int,
                            "答案 3": int,
                            "答案 4": int,
                            
                    },
                    "Reason": ""
            },
            "赋能性": {
                    "Score": {
                            "答案 1": int,
                            "答案 2": int,
                            "答案 3": int,
                            "答案 4": int,
                            
                    },
                    "Reason": ""
            },
            "直接性": {
                    "Score": {
                            "答案 1": int,
                            "答案 2": int,
                            "答案 3": int,
                            "答案 4": int,
                            
                    },
                    "Reason": ""
            }
            "无重复性": {
                    "Score": {
                            "答案 1": int,
                            "答案 2": int,
                            "答案 3": int,
                            "答案 4": int,
                            
                    },
                    "Reason": ""
            }
    }'''

    prompt = '''
现将《三体》三部曲输入给了四个模型，使之根据其内容回答用户问题，生成了四个答案：
问题：{question}
评价指标：
1,全面性：答案提供了多少细节，以涵盖问题的所有方面和细节？
2,多样性：答案在针对问题提供不同的观点和见解方面，丰富程度和多样程度如何？
3,赋能性：答案在帮助读者理解主题并做出明智判断方面表现得有多好？
4,直接性：答案在具体且清晰地回答问题方面做得如何？
5,无重复性：答案在简洁高效没有多余重复内容地回答问题方面做得如何？
答案 1：{ans1}
答案 2：{ans2}
答案 3：{ans3}
答案 4：{ans4}
请依据上述问题、对这四个答案在每一个指标维度上进行打分（score 范围为0~10，类型为整数）并分别对这四个答案的得分作出解释。
你可能会在答案里看到类似"[Data: Reports (874)]"这样的内容，这是在引用原文。
输出格式应该为下面的JSON格式，输出纯json格式内容，不需要添加markdown代码块：
{json_format}
    '''

    complete_prompt = '''
    请根据以下内容进行操作：
    问题：{question}
    评价指标：
    1,全面性：答案提供了多少细节，以涵盖问题的所有方面和细节？
    2,多样性：答案在针对问题提供不同的观点和见解方面，丰富程度和多样程度如何？
    3,赋能性：答案在帮助读者理解主题并做出明智判断方面表现得有多好？
    4,直接性：答案在具体且清晰地回答问题方面做得如何？
    5,无重复性：答案在简洁高效没有多余重复内容地回答问题方面做得如何？
    答案 1：{ans1}
    答案 2：{ans2}
    答案 3：{ans3}
    答案 4：{ans4}
    答案 5：{ans5}
    请依据上述问题、对这五个答案在每一个指标维度上进行打分（score 范围为0~10，类型为整数）并详细说明原因。
    输出格式应该为下面的JSON格式：
    {json_format}
        '''
    judger_responses = []
    for item in tqdm(result_set, desc="Processing items", unit="item"):
        id = item['id']
        question = item['question']
        pure_LLM_eval_results = item['pure_LLM_eval_results']
        RAG_model_eval_results = item['RAG_model_eval_results']
        RAG_SFTmodel_eval_results = item['RAG_SFTmodel_eval_results']
        GraphRAG_SFT_LLM_eval_results = item['GraphRAG_SFT_LLM_eval_results']
        # GraphRAG_model_eval_results = item['GraphRAG_model_eval_results']


        format_prompt = prompt.format(question=question,
                                      ans1 = pure_LLM_eval_results,ans2=RAG_model_eval_results,
                                      ans3=RAG_SFTmodel_eval_results, ans4=GraphRAG_SFT_LLM_eval_results,
                                      json_format=json_format)

        max_retries = 3  # Maximum number of retries if response is not JSON
        retry_count = 0
        response_json = None

        while retry_count < max_retries:
            completion = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的语言类评委"},
                    {"role": "user", "content": format_prompt},
                ],
            )

            response = completion.choices[0].message.content

            try:
                # Try to parse the response as JSON
                response_json = json.loads(response)
                break  # If successful, exit the retry loop
            except json.JSONDecodeError:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Response is not valid JSON, retrying ({retry_count}/{max_retries})...")
                else:
                    print(f"Max retries reached for item {id}, response is not valid JSON")
                    response_json = {"error": "Invalid JSON response", "original_response": response}

        judger_responses.append({
            "id": id,
            "question": question,
            "judgement": response_json
        })

    with open('judger_responses.json', 'w', encoding='utf-8') as f:
        json.dump(judger_responses, f, ensure_ascii=False, indent=2)

