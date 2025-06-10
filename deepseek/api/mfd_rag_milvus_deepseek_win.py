from pymilvus import MilvusClient
from pymilvus import model as milvus_model
import os
from openai import OpenAI
from tqdm import tqdm
import json

# 从环境变量获取 DeepSeek API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 获取资料文档信息
text_lines = []
with open("mfd.md", "r", encoding="utf-8") as file:
    file_text = file.read()
text_lines += file_text.split("#### ")
print(len(text_lines))

# LLM配置
deepseek_client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",  # DeepSeek API 的基地址
)

# 设置Embedding模型并获取维度信息
embedding_model = milvus_model.DefaultEmbeddingFunction()
test_embedding = embedding_model.encode_queries(["This is a test"])[0]
embedding_dim = len(test_embedding)

# 向量数据库milvus
# 创建客户端
milvus_client = MilvusClient(uri="http://localhost:19530", token="root:Milvus")
collection_name = "mfd_rag_collection"
# 检查 collection 是否已存在，如果存在则删除它。
if milvus_client.has_collection(collection_name):
    milvus_client.drop_collection(collection_name)
# 建立客户端连接
milvus_client.create_collection(
    collection_name=collection_name,
    dimension=embedding_dim,
    metric_type="IP",  # 内积距离
    consistency_level="Strong",  # 支持的值为 (`"Strong"`, `"Session"`, `"Bounded"`, `"Eventually"`)。更多详情请参见 https://milvus.io/docs/consistency.md#Consistency-Level。
)
print("链接创建成功")
# 资料向量化并插入向量数据库
data = []
doc_embeddings = embedding_model.encode_documents(text_lines)
for i, line in enumerate(tqdm(text_lines, desc="Creating embeddings")):
    data.append({"id": i, "vector": doc_embeddings[i], "text": line})
milvus_client.insert(collection_name=collection_name, data=data)

# 搜寻问题
question = "债权人有哪些权利?"
search_res = milvus_client.search(
    collection_name=collection_name,
    data=embedding_model.encode_queries(
        [question]
    ),  # 将问题转换为嵌入向量
    limit=3,  # 返回前3个结果
    search_params={"metric_type": "IP", "params": {}},  # 内积距离
    output_fields=["text"],  # 返回 text 字段
)
# 返回搜寻结果
retrieved_lines_with_distances = [
    (res["entity"]["text"], res["distance"]) for res in search_res[0]
]
# 格式缩进4个字符
print(json.dumps(retrieved_lines_with_distances, indent=4))

# 将检索到的文档转换为字符串格式
context = "\n".join(
    [line_with_distance[0] for line_with_distance in retrieved_lines_with_distances]
)
print(context)

# 利用LLM进行汇总输出
SYSTEM_PROMPT = """
Human: 你是一个 AI 助手。你能够从提供的上下文段落片段中找到问题的答案。
"""
USER_PROMPT = f"""
请使用以下用 <context> 标签括起来的信息片段来回答用 <question> 标签括起来的问题。最后追加原始回答的中文翻译，并用 <translated>和</translated> 标签标注。
<context>
{context}
</context>
<question>
{question}
</question>
<translated>
</translated>
"""
response = deepseek_client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ],
)
print(response.choices[0].message.content)

