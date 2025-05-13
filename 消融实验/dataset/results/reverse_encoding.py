import json

# 读取JSON文件
with open('pure_LLM_eval_results.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


# 将处理后的数据写回原文件
with open('pure_LLM_eval_results.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)