import json

from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from tqdm import tqdm


def load_testset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        test_set = json.loads(content)
    return test_set

if __name__ == '__main__':

    documents = SimpleDirectoryReader("dataset/fictions_utf8").load_data()

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

    Settings.llm = Ollama(model="QiNing/Qwen3-14B-RAG-Instruct", request_timeout=360.0)

    index = VectorStoreIndex.from_documents(
        documents,
    )

    # 存储向量索引
    # persist_dir = 'data/'
    # index.storage_context.persist(persist_dir=persist_dir)


    test_set_path = "./dataset/fictions_utf8/fictions_testset.json"
    test_set = load_testset(test_set_path)
    results = []
    prompt = '''
我是一个{role}，我的任务是{task}，我的问题是{question}
    '''
    for item in tqdm(test_set, desc="Processing items", unit="item"):
        role = item['role']
        task = item['task']
        question = item['question']
        id = item['id']
        format_prompt = prompt.format(role=role, task=task, question=question)
        query_engine = index.as_query_engine()
        response = query_engine.query(format_prompt)
        print(response)

        # 记录结果
        results.append({
            "id": id,
            "question": question,
            "response": response
        })

        # 保存结果
    with open("RAG_SFTmodel_eval_results.json", "w") as f:
        json.dump(results, f, indent=2)


# 检索上下文进行对话
# from llama_index.core.memory import ChatMemoryBuffer
# memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

# chat_engine = index.as_chat_engine(
#     chat_mode="context",
#     memory=memory,
#     system_prompt=(
#         "You are a chatbot, able to have normal interactions."
#     ),
# )

# # 存储向量索引
# persist_dir = 'data/'
# index.storage_context.persist(persist_dir=persist_dir)

# # 加载向量索引
# from llama_index.core import StorageContext, load_index_from_storage
# storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
# index= load_index_from_storage(storage_context)