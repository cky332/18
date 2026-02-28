import os
import asyncio
import traceback
import json
from dataclasses import asdict

from nano_graphrag.graphrag import GraphRAG            # :contentReference[oaicite:0]{index=0}
from nano_graphrag._storage import NetworkXStorage     # :contentReference[oaicite:1]{index=1}
from nano_graphrag._op import generate_community_report  # :contentReference[oaicite:2]{index=2}
import sys

# 配置环境变量
os.environ["OPENAI_API_KEY"]   = "sk-zk20d46549ec2e0e53b3d943323d2f87fd0681ca5c69cd6a"
os.environ["OPENAI_BASE_URL"]  = "https://api.zhizengzeng.com/v1/"
os.environ["HTTP_PROXY"]       = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"]      = "http://127.0.0.1:7890"

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def generate_communities():
    # 1. 初始化 GraphRAG（会加载默认的工作目录和配置）
    rag = GraphRAG(working_dir=".")
    # 2. 用 NetworkXStorage 加载你自己的 graph_chunk_entity_relation3.graphml
    rag.chunk_entity_relation_graph = NetworkXStorage(
        namespace="chunk_entity_relation3",
        global_config=asdict(rag),
    )
    print(f"[DEBUG] 使用图文件: graph_chunk_entity_relation3.graphml 边数 {rag.chunk_entity_relation_graph._graph.number_of_edges()}")

    # 3. 执行 Leiden 聚类
    try:
        print("[DEBUG] 开始聚类……")
        await rag.chunk_entity_relation_graph.clustering(rag.graph_cluster_algorithm)
        print("[DEBUG] 聚类完成")
    except Exception as e:
        if type(e).__name__ == "EmptyNetworkError":
            print("⚠️ 空网络，跳过聚类")
        else:
            print("❌ 聚类失败：", e)
            traceback.print_exc()
            return

    # 4. 为每个社区生成 report_string 和 report_json
    print("[DEBUG] 开始生成社区报告……")
    await generate_community_report(
        rag.community_reports,
        rag.chunk_entity_relation_graph,
        asdict(rag),
    )
    print("[DEBUG] 社区报告生成完成")

    # 5. 将结果写入 JSON 文件
    out_file = "kv_store_community_reports3.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(rag.community_reports._data, f, indent=2, ensure_ascii=False)
    print(f"✅ 已生成 {out_file}")

# 1) 把 main 改成 async，直接 await generate_communities()
async def main():
    try:
        await generate_communities()
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    # 2) 保留脚本入口，调用 asyncio.run
    asyncio.run(main())