import json


def add_ids_to_json(input_file):
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 为每个项目添加id
        for i, item in enumerate(data, 1):
            item['id'] = i

        # 将修改后的数据写回文件
        with open(input_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        print(f"已成功为{input_file}中的项目添加id。")
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误：文件 {input_file} 不是有效的JSON格式")
    except Exception as e:
        print(f"发生未知错误：{e}")


# 指定要处理的JSON文件路径
input_file = './dataset/news/news_testset.json'
add_ids_to_json(input_file)