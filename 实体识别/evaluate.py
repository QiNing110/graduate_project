import ast
import csv

import pandas as pd
# from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer
from tqdm import tqdm

import os
os.environ['MODELSCOPE_CACHE'] =  'root/autodl-tmp/models'

def load_data(file_path):
    df = pd.read_csv(file_path)
    texts = df['text'].tolist()
    labels = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # 遍历每一行数据
        for row in reader:
            # 获取 info_list 列的值
            info_list_str = row['info_list']
            # 如果 info_list 不为空字符串
            if info_list_str:
                try:
                    # 将字符串解析为 Python 对象
                    info_list = ast.literal_eval(info_list_str)
                    # 初始化一个空列表，用于存储解析后的字典
                    parsed_info = []
                    # 遍历 info_list 中的每个子列表
                    for sub_list in info_list:
                        for item in sub_list:
                            # 提取 type 和 span 信息
                            parsed_info.append({
                                'type': item['type'],
                                'span': item['span']
                            })
                    # 将解析后的信息添加到结果列表中
                    row['info_list'] = parsed_info
                except (SyntaxError, ValueError):
                    print(f"无法解析行 {row['id']} 的 info_list 列")
            else:
                # 如果 info_list 为空字符串，将其设置为空列表
                row['info_list'] = []
            # 将处理后的行添加到解析结果列表中
            labels.append(row['info_list'])
    return texts, labels


# def load_model(model_name):
#     cache_dir = 'root/autodl-tmp/models'
#     tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir = cache_dir,trust_remote_code=True)
#     model = AutoModelForCausalLM.from_pretrained(model_name,
#                                                  device_map='auto',
#                                                  torch_dtype="auto",
#                                                  cache_dir=cache_dir,
#                                                  trust_remote_code=True)
#     return tokenizer, model


# def inference(tokenizer, model, text):
#     content = f'''
# 请对以下文本进行实体识别，并按照特定格式输出结果。
# 示例：
# 文本: "相比之下，青岛海牛队和广州松日队的雨中之战虽然也是0∶0，但乏善可陈。"
# 输出: [{{"span": "广州松日队", "type": "组织机构"}}, {{"span": "青岛海牛队", "type": "组织机构"}}]。
#
# 请使用如下格式输出识别结果：
# [
#     {{"span": "实体在文本中的具体内容", "type": "预定义的实体类型，如人物、组织机构、地理位置等"}}
# ]
#
# 如果文本中没有识别出任何实体，请输出 []。只能输出最终的格式化结果，不能输出其他任何额外解释。
# 实体类型包括：人物、地理位置、组织机构。
# 文本: {text}
# 输出:
# '''
#     messages = [
#         # {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
#         {"role": "user", "content": content}
#     ]
#     context = tokenizer.apply_chat_template(
#         messages,
#         tokenize=False,
#         add_generation_prompt=True
#     )
#     model_inputs = tokenizer([context], return_tensors="pt").to(model.device)
#
#     generated_ids = model.generate(
#         **model_inputs,
#         max_new_tokens=512
#     )
#     generated_ids = [
#         output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
#     ]
#
#     response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     try:
#         import ast
#         entities = ast.literal_eval(response)
#     except:
#         print("解析为列表失败")
#         entities = response
#     return entities

def evaluate(labels, predictions):
    all_true_labels = []
    all_pred_labels = []
    for true_entities, pred_entities in zip(labels, predictions):
        true_span_types = [span_type["span"] for span_type in true_entities]
        pred_span_types = [span_type["span"] for span_type in pred_entities]
        all_true_labels.append(true_span_types)
        all_pred_labels.append(pred_span_types)
    # 初始化 MultiLabelBinarizer
    mlb = MultiLabelBinarizer()

    # 对真实标签进行拟合和转换
    y_true = mlb.fit_transform(all_true_labels)

    # 对预测标签进行转换（使用在真实标签上拟合的编码器）
    y_pred = mlb.transform(all_pred_labels)
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')
    return precision, recall, f1


def main():
    file_path = 'dev.csv'
    texts, labels = load_data(file_path)
    model_names = [
        'Qwen/Qwen2.5-14B-Instruct',
        'Qwen/Qwen3-14B',
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B',
        'modelscope/Llama2-Chinese-13b-Chat-ms',
        'baichuan-inc/Baichuan2-13B-Chat'
    ]
    model_name = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B'

    prediction_str = '''
[]
[{'span': '青岛海牛队', 'type': '组织机构'}, {'span': '广州松日队', 'type': '组织机构'}]
[]
[]
[{'span': '胡老', 'type': '人物'}]
[{'span': '国有大中型企业', 'type': '组织机构'}]
[]
[{'span': '张敬涛', 'type': '人物'}]
[{'span': '贫困母亲', 'type': '人物'}]
[]
[{'span': '胡锦涛', 'type': '人物'}, {'span': '中国共产党', 'type': '组织机构'}, {'span': '罗社会民主主义党', 'type': '组织机构'}]
[{'span': '古巴代表团团长', 'type': '组织机构'}, {'span': '司法部长卡洛斯·阿马特', 'type': '人物'}, {'span': '古巴', 'type': '地理位置'}]
[]
[]
[{'span': '北京', 'type': '地理位置'}, {'span': '李岚清', 'type': '人物'}, {'span': '中南海', 'type': '地理位置'}, {'span': '美国', 'type': '地理位置'}, {'span': '芭芭拉·弗兰克林', 'type': '人物'}]
[{'span': '不来梅', 'type': '地理位置'}]
[{'span': '海卫1', 'type': '地理位置'}, {'span': '旅行者号探测器', 'type': '组织机构'}]
[]
[{'span': '北京', 'type': '地理位置'}, {'span': '袁日希', 'type': '人物'}, {'span': '国家新闻出版署', 'type': '组织机构'}]
[{'span': '中国检察日报社影视部', 'type': '组织机构'}]
[{'span': '前卫寰岛队', 'type': '组织机构'}, {'span': '高峰', 'type': '人物'}]
[]
[{'span': '毛泽东', 'type': '人物'}, {'span': '邓小平', 'type': '人物'}, {'span': '江泽民', 'type': '人物'}, {'span': '总社新闻研究所', 'type': '组织机构'}, {'span': '中国新闻学院', 'type': '组织机构'}]
[]
[]
[{'span': '辽宁队', 'type': '组织机构'}, {'span': '五牛队', 'type': '组织机构'}, {'span': '李', 'type': '人物'}]
[{'span': '克林顿', 'type': '人物'}, {'span': '美国', 'type': '地理位置'}, {'span': '台湾', 'type': '地理位置'}]
[{'span': '何泰权', 'type': '人物'}, {'span': '姜京珍', 'type': '人物'}]
[{'span': '陈伊玲', 'type': '人物'}]
[{'span': '青海省曲麻莱县', 'type': '地理位置'}, {'span': '青海省玛多县', 'type': '地理位置'}, {'span': '青海省称多县', 'type': '地理位置'}]
[{'span': '金大中', 'type': '人物'}, {'span': '新政府', 'type': '组织机构'}]
[]
[{'span': '国家大剧院', 'type': '组织机构'}, {'span': '广场西侧', 'type': '地理位置'}]
[{'span': '印度政府', 'type': '组织机构'}]
[{'span': '幸福工程', 'type': '组织机构'}]
[{'span': '贺龙', 'type': '人物'}, {'span': '薛明', 'type': '人物'}, {'span': '彭真', 'type': '人物'}, {'span': '张洁', 'type': '人物'}, {'span': '杨尚昆', 'type': '人物'}, {'span': '李伯钊', 'type': '人物'}, {'span': '王若飞', 'type': '人物'}, {'span': '李培之', 'type': '人物'}]
[{'span': '罗政府', 'type': '组织机构'}, {'span': '国际货币基金组织', 'type': '组织机构'}, {'span': '世界银行', 'type': '组织机构'}]
[]
[{"span": "王霞光", "type": "人物"}, {"span": "李长云", "type": "人物"}, {"span": "第十六届英联邦运动会", "type": "组织机构"},{"span": "北京", "type": "地理位置"},{"span": "马来西亚", "type": "地理位置"},{"span": "吉隆坡", "type": "地理位置"}]
[]
[{'span': '叶笃正院士', 'type': '人物'}, {'span': '雅鲁藏布江大峡谷', 'type': '地理位置'}, {'span': '青藏高原', 'type': '地理位置'}]
[{'span': '桥本', 'type': '人物'}, {'span': '日本', 'type': '地理位置'}]
[{'span': '周恩来', 'type': '人物'}]
[{'span': '五四运动', 'type': '组织机构'}, {'span': '北京大学', 'type': '组织机构'}]
[{'span': '白乐桑', 'type': '人物'}]
[{'span': '阿维兰热', 'type': '人物'}, {'span': '国际足联', 'type': '组织机构'}]
[]
[]
[{'span': '微软', 'type': '组织机构'}]
[{'span': '外国金融机构', 'type': '组织机构'}, {'span': '日本', 'type': '地理位置'}]
[{'span': '塔科马市', 'type': '地理位置'}, {'span': '莱克伍德县', 'type': '地理位置'}, {'span': '莱克伍德县法官', 'type': '人物'}]
[{'span': '市再就业基金', 'type': '组织机构'}]
[]
[{'span': '我', 'type': '人物'}]
[{'span': '北京九十中学', 'type': '组织机构'}, {'span': '李铁辰', 'type': '人物'}]
[{'span': '袁步兵', 'type': '人物'}, {'span': '如东', 'type': '地理位置'}, {'span': '如东农业系统', 'type': '组织机构'}, {'span': '县政府', 'type': '组织机构'}, {'span': '县委', 'type': '组织机构'}, {'span': '团县委', 'type': '组织机构'}, {'span': '如东县', 'type': '地理位置'}]
[]
[{'span': '中国农科院', 'type': '组织机构'}, {'span': '梅方权', 'type': '人物'}, {'span': '日本', 'type': '地理位置'}, {'span': '美国', 'type': '地理位置'}]
[{'span': '挪威政府', 'type': '组织机构'}]
[]
[]
[{'span': '法航', 'type': '组织机构'}, {'span': '《费加罗报》', 'type': '组织机构'}]
[{'span': '香港', 'type': '地理位置'}, {'span': '香港展览中心', 'type': '地理位置'}, {'span': '周恩来', 'type': '人物'}]
[{'span': '俄总统', 'type': '人物'}, {'span': '国家杜马', 'type': '组织机构'}, {'span': '日本', 'type': '地理位置'}, {'span': '俄', 'type': '地理位置'}]
[]
[{'span': '旅游景点', 'type': '地理位置'}]
[{'span': '杜比宁', 'type': '人物'}, {'span': '俄罗斯中央银行', 'type': '组织机构'}, {'span': '俄罗斯', 'type': '地理位置'}]
[{'span': '新单位', 'type': '组织机构'}]
[{'span': '国际社会', 'type': '组织机构'}]
[{'span': '科研单位', 'type': '组织机构'}]
[{'span': '山东公安机关', 'type': '组织机构'}]
[]
[]
[]
[{'span': '金大中', 'type': '人物'}, {'span': '产业资源部长官', 'type': '人物'}, {'span': '招商引资团', 'type': '组织机构'}]
[{'span': '巴西', 'type': '地理位置'}, {'span': '圣保罗州保险公司', 'type': '组织机构'}]
[{'span': '库克', 'type': '人物'}, {'span': '巴基斯坦', 'type': '地理位置'}, {'span': '印度', 'type': '地理位置'}]
[]
[]
[{'span': '曹火星', 'type': '人物'}, {'span': '香港', 'type': '地理位置'}, {'span': '邵一夫', 'type': '人物'}]
[]
[{'span': '中国美术馆', 'type': '组织机构'}]
[{'span': '国务院残疾人工作协调委员会', 'type': '组织机构'}, {'span': '卫生部', 'type': '组织机构'}, {'span': '中国残联', 'type': '组织机构'}, {'span': '国际狮子会', 'type': '组织机构'}]
[{'span': '联合国安理会常任理事国', 'type': '组织机构'}, {'span': '南亚地区', 'type': '地理位置'}]
[]
[{'span': '高新区', 'type': '地理位置'}]
[]
[{'span': '苗立杰', 'type': '人物'}, {'span': '保拉', 'type': '人物'}, {'span': '中国队', 'type': '组织机构'}]
[{'span': '月山车站汽车运贸公司', 'type': '组织机构'}]
[]
[{'span': '海口市', 'type': '地理位置'}, {'span': '海口市中级人民法院', 'type': '组织机构'}, {'span': '辛业江', 'type': '人物'}]
[{'span': '澳门日报社长李成俊', 'type': '人物'}, {'span': '澳门日报', 'type': '组织机构'}, {'span': '李成俊', 'type': '人物'}, {'span': '周恩来总理', 'type': '人物'}, {'span': '澳门', 'type': '地理位置'}, {'span': '香港', 'type': '地理位置'}]
[]
[{'span': '彭真同志', 'type': '人物'}, {'span': '毛泽东同志', 'type': '人物'}]
[]
[{'span': '东京', 'type': '地理位置'}, {'span': '东京国际法学会', 'type': '组织机构'}]
[{'span': '加拿大海军舰艇编队', 'type': '组织机构'}, {'span': '巴克海军少将', 'type': '人物'}, {'span': '加拿大海军太平洋舰队', 'type': '组织机构'}, {'span': '上海', 'type': '地理位置'}]
[{'span': '乡镇企业', 'type': '组织机构'}]
[{'span': '纳税人', 'type': '人物'}]
[{'span': '中国电视台', 'type': '组织机构'}, {'span': '江泽民', 'type': '人物'}]
    '''


    # 按行分割字符串
    lines = prediction_str.splitlines()

    predictions = []
    for line in lines:
        # 去除每行的前后空格
        line = line.strip()
        if line:
            try:
                # 使用 eval 函数将字符串转换为 Python 对象
                parsed_line = eval(line)
                predictions.append(parsed_line)
            except SyntaxError:
                print(f"无法解析行: {line}")
    # tokenizer, model = load_model(model_name)
    # predictions = []
    # for text in tqdm(texts):
    #     entities = inference(tokenizer, model, text)
    #     print(entities)
    #     predictions.append(entities)
    precision, recall, f1 = evaluate(labels, predictions)
    print(f"Model: {model_name}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-score: {f1}")


if __name__ == "__main__":
    main()

