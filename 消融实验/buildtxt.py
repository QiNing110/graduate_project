'''
ollama pull nomic-embed-text

pip install llama-index-llms-ollama
pip install llama-index-embeddings-ollama
pip install -U llama-index-readers-file

'''
import json

from tqdm import tqdm


def load_testset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        test_set = json.loads(content)
    return test_set

if __name__ == '__main__':


    test_set_path = "/home/chenningfei/PycharmProjects/graduate_project/消融实验/dataset/fictions_utf8/fictions_testset.json"
    test_set = load_testset(test_set_path)
    results = ''
    prompt = '''我是一个{role}，我的任务是{task}，我的问题是{question}'''
    for item in tqdm(test_set, desc="Processing items", unit="item"):
        role = item['role']
        task = item['task']
        question = item['question']
        id = item['id']
        format_prompt = prompt.format(role=role, task=task, question=question)
        results +=format_prompt+'\n'


        # 保存结果
    with open("dataset/fictions_utf8/queries.txt", "w") as f:
        f.write(results)



