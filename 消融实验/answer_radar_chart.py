import json
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
# ---------------------- 读取数据并计算平均分 ----------------------
import json

# 读取JSON文件
# with open('judger_responses.json', 'r', encoding='utf-8') as f:
#     data_list = json.load(f)
#
# # 初始化评分存储字典
# answer_scores = {f"答案{i}": {"全面性": [], "多样性": [], "赋能性": [], "直接性": [], "无重复性": []} for i in range(1, 5)}
#
# # 解析每个问题的评分数据
# for item in data_list:
#     judgment = item['judgement']
#     for dimension, scores in judgment.items():
#         for answer, score in scores['Score'].items():
#             clean_answer = answer.replace(" ", "")  # 替换中间空格，例如"答案 1"→"答案1"
#             answer_scores[clean_answer][dimension].append(score)
#
# # 计算每个答案在不同维度上的平均分
# average_scores = {}
# for answer, dim_scores in answer_scores.items():
#     average = {dim: sum(scores) / len(scores) for dim, scores in dim_scores.items()}
#     average_scores[answer] = average
'''
{
	'Qwen3-14B-no_think': {
		'全面性': 6.356
		'多样性': 5.6784
		'无重复性': 5.5552
		'直接性': 5.7008
		'赋能性': 6.1712
	},
	'NativeRAG+Qwen3-14B-no_think': {
		'全面性': 6.36,
		'多样性': 6.216,
		'无重复性': 8.072,
		'直接性': 7.008,
		'赋能性': 6.56
	},
	'NativeRAG+Qwen3-14B-RAG-Instruct': {
		'全面性': 6.592,
		'多样性': 6.664,
		'无重复性': 8.336,
		'直接性': 7.448,
		'赋能性': 7.976
	},
	'GraphRAG+Qwen3-14B-RAG-Instruct': {
		'全面性': 8.76,
		'多样性': 8.288,
		'无重复性': 8.336,
		'直接性': 8.816,
		'赋能性': 8.656
	}
}
'''

average_scores = {
	'Qwen3-14B(Non-thinking)': {
		'全面性': 6.356,
		'多样性': 5.6784,
		'无重复性': 5.5552,
		'直接性': 5.7008,
		'赋能性': 6.1712
	},
	'NativeRAG+Qwen3-14B(Non-thinking)': {
		'全面性': 6.36,
		'多样性': 6.216,
		'无重复性': 8.072,
		'直接性': 7.008,
		'赋能性': 6.56
	},
	'NativeRAG+Qwen3-14B-RAG-Instruct': {
		'全面性': 6.592,
		'多样性': 6.664,
		'无重复性': 8.336,
		'直接性': 7.448,
		'赋能性': 7.976
	},
	'GraphRAG+Qwen3-14B-RAG-Instruct': {
		'全面性': 8.76,
		'多样性': 8.288,
		'无重复性': 8.336,
		'直接性': 8.816,
		'赋能性': 8.656
	}
}

# 输出结果（保留两位小数）
print("各答案在不同维度上的平均分：")
for answer, scores in average_scores.items():
    print(f"\n{answer}:")
    for dim, avg in scores.items():
        print(f"  {dim}: {avg:.2f}")

# ---------------------- 绘制雷达图（代码同上）----------------------
# 设置中文字体（解决乱码）
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

dimensions = ["全面性", "多样性", "无重复性", "直接性", "赋能性"]
answers_name = ["Qwen3-14B(Non-thinking)", "NativeRAG+Qwen3-14B(Non-thinking)", "NativeRAG+Qwen3-14B-RAG-Instruct", "GraphRAG+Qwen3-14B-RAG-Instruct"]
answers = ["答案1", "答案2", "答案3", "答案4"]
data = [list(average_scores[ans].values()) for ans in answers_name]

n_dims = len(dimensions)
angles = np.linspace(0, 2*np.pi, n_dims, endpoint=False).tolist()
angles += angles[:1]

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, polar=True)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
linestyles = ['-', '--', '-.', ':']

for i, ans in enumerate(answers_name):
    values = data[i] + [data[i][0]]
    ax.plot(angles, values, linestyle=linestyles[i], linewidth=2,
            label=f"{ans} ({np.mean(values):.2f})", color=colors[i])
    ax.fill(angles, values, alpha=0.1, color=colors[i])


ax.tick_params(
    axis='both',  # 'x'对应角度刻度，'y'对应径向刻度，'both'同时调整
    which='major',  # 调整主刻度标签（默认）
    labelsize=14
)
ax.set_thetagrids(np.degrees(angles[:-1]), dimensions)
ax.set_ylim(0, 10)
ax.grid(True, alpha=0.3)
# plt.title("四个答案在五个维度的平均分对比雷达图", fontsize=16, y=1.1)
plt.legend(loc="lower right", bbox_to_anchor=(1.5, 1), fontsize=14)
plt.tight_layout()
plt.show()