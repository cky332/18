# evaluate_find_neighbor_nx.py

import asyncio
import os
import sys
from nano_graphrag._storage.gdb_networkx import NetworkXStorage
import os
import sys
# 配置环境变量
os.environ["OPENAI_API_KEY"]   = "sk-zk20d46549ec2e0e53b3d943323d2f87fd0681ca5c69cd6a"
os.environ["OPENAI_BASE_URL"]  = "https://api.zhizengzeng.com/v1/"
os.environ["HTTP_PROXY"]       = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"]      = "http://127.0.0.1:7890"

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    # --------- 配置部分，请根据实际情况修改 ---------
    global_config = {
        "working_dir": "./cache2",   # 与你的 GraphRAG 工程保持一致
    }
    # 注意：GraphML 中节点 id 是带双引号的，比如 &quot;DUMBLEDORE&quot;，
    # networkx.read_graphml 会将其解析为 '"DUMBLEDORE"' 字符串
    node_id   = '"DUMBLEDORE"'             # 包含双引号且通常为大写
    namespace = "chunk_entity_relation"    # 与你创建 storage 时用的 namespace 保持一致

    # 初始化本地 NetworkX 存储
    storage = NetworkXStorage(namespace=namespace, global_config=global_config)

    # 查询指定节点的所有出边（返回 (source_id, target_id) 列表）
    edges = await storage.get_node_edges(node_id)
    connected_nodes = [tgt for _, tgt in (edges or [])]

    print(f"Nodes connected to {node_id}:")
    for tgt in connected_nodes:
        print(f"  - {tgt}")

    # （可选）如果对图做了修改，保存回 .graphml 文件
    await storage.index_done_callback()

if __name__ == "__main__":
    asyncio.run(main())
