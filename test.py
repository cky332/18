import os
from nano_graphrag.graphrag import GraphRAG
from nano_graphrag.base import QueryParam
# 以下假设 gdb_neo4j.py 和 vdb_nanovectordb.py 与此脚本在同一目录
from nano_graphrag._storage.gdb_neo4j import Neo4jStorage
from nano_graphrag._storage.vdb_nanovectordb import NanoVectorDBStorage
import os
import sys
import asyncio
# 配置环境变量
os.environ["OPENAI_API_KEY"]   = "sk-zk20d46549ec2e0e53b3d943323d2f87fd0681ca5c69cd6a"
os.environ["OPENAI_BASE_URL"]  = "https://api.zhizengzeng.com/v1/"
os.environ["HTTP_PROXY"]       = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"]      = "http://127.0.0.1:7890"

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
def main():
    # 1. 配置 GraphRAG（Neo4j + NanoVectorDB）
    rag = GraphRAG(
        working_dir="./cache",
    )

    # 2. 读取 harry.txt
    file_path = os.path.abspath("harry.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        harry_text = f.read()

    # 3. 插入 harry.txt 的全文作为文档
    rag.insert([harry_text])

    # 4. 测试查询：检索 “Harry” 相关上下文
    res = rag.query(
        "Harry",
        QueryParam(mode="local", only_need_context=True, top_k=5)
    )
    print(res)

if __name__ == "__main__":
    main()
