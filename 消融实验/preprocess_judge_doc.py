import json

# 定义文件路径和对应的模型键名
files = [
    ('dataset/fictions_utf8/results/pure_LLM_eval_results.json', 'pure_LLM_eval_results'),
    ('dataset/fictions_utf8/results/RAG_model_eval_results.json', 'RAG_model_eval_results'),
    ('dataset/fictions_utf8/results/RAG_SFTmodel_eval_results.json', 'RAG_SFTmodel_eval_results'),
    # ('results/GraphRAG_SFTmodel_eval_results.json', 'GraphRAG_SFTmodel_eval_results'),
    # ('results/GraphRAG_model_eval_results.json', 'GraphRAG_model_eval_results'),
]

# 创建空字典存储合并后的数据
merged = {}

# 读取每个文件并按 id 合并
for file_path, model_key in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for entry in data:
        q_id = entry['id']
        if q_id not in merged:
            # 初始化新条目
            merged[q_id] = {
                'id': q_id,
                'question': entry['question']
            }
        # 添加当前模型的响应
        merged[q_id][model_key] = entry['response']

# 按 id 排序并保存结果
sorted_results = sorted(merged.values(), key=lambda x: x['id'])

# 写入合并后的文件
with open('dataset/fictions_utf8/results/merged_results.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_results, f, indent=2, ensure_ascii=False)

print("合并完成，结果已保存为 merged_results.json")