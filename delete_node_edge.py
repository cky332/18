
import os
import sys
import xml.etree.ElementTree as ET
ET.register_namespace('', 'http://graphml.graphdrawing.org/xmlns')
# 文件路径和节点ID常量
CACHE_GRAPHML = os.path.join("cache", "graph_chunk_entity_relation.graphml")
RAW_NODE_ID = "Dumbledore"
OUTPUT_PATH = None  # None 表示覆盖原文件


def clean_node_id(raw: str) -> str:
    """去除外层双引号并去掉 HTML 实体引用（如 &quot;）。"""
    # 先去除 HTML 实体
    unesc = raw.replace("&quot;", '"')
    # 再去除外层双引号
    if unesc.startswith('"') and unesc.endswith('"'):
        return unesc[1:-1]
    return unesc


def remove_node_and_edges(graphml_path: str, raw_node_id: str, output_path: str = None):
    """
    从 GraphML 文件中删除与 raw_node_id 精确匹配的 <node> 及所有 incident edges。
    使用 case-insensitive 匹配：clean_node_id(node/@id).lower() == raw_node_id.lower().
    同理，删除 <edge> 时，对 source/target 都应用 clean_node_id 比较。
    """
    if output_path is None:
        output_path = graphml_path

    tree = ET.parse(graphml_path)
    root = tree.getroot()
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

    graph_elem = root.find('.//g:graph', ns)
    if graph_elem is None:
        print("Error: <graph> element not found.")
        return

    # 1. 收集要删除的节点原始 id
    to_delete = set()
    for node in graph_elem.findall('g:node', ns):
        nid = node.get('id')
        if nid and clean_node_id(nid).lower() == raw_node_id.lower():
            to_delete.add(nid)

    if not to_delete:
        print(f"No matching node id found for '{raw_node_id}'. Nothing to remove.")
        return

    print(f"Found node IDs to delete: {to_delete}")

    # 2. 删除节点
    for node in list(graph_elem.findall('g:node', ns)):
        if node.get('id') in to_delete:
            graph_elem.remove(node)

    # 3. 删除相关边
    removed_edges = 0
    for edge in list(graph_elem.findall('g:edge', ns)):
        src = edge.get('source')
        tgt = edge.get('target')
        if (src and clean_node_id(src).lower() == raw_node_id.lower()) or \
           (tgt and clean_node_id(tgt).lower() == raw_node_id.lower()):
            graph_elem.remove(edge)
            removed_edges += 1

    # 4. 写回文件
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Removed {len(to_delete)} node(s) and {removed_edges} edge(s).")
    print(f"Updated GraphML written to: {output_path}")


if __name__ == '__main__':
    if not os.path.isfile(CACHE_GRAPHML):
        print(f"Error: file not found: {CACHE_GRAPHML}", file=sys.stderr)
        sys.exit(1)
    remove_node_and_edges(CACHE_GRAPHML, RAW_NODE_ID, OUTPUT_PATH)

