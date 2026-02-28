
import os
import html
import json
import asyncio
import re
import sys
from delete_vdb_entities import delete_vdb_entities
from before_search import extract_entities
from delete_update_description import update_graphml_descriptions
from delete_node_edge import remove_node_and_edges
from delete_community import delete_community_pipeline
# Updated import: anonymize_all_chunks replaces process_text_chunks_for_node
from delete_text_chunk import anonymize_all_chunks
import xml.etree.ElementTree as ET
from delete_community_update_reports_last import update_reports_for_entity
def clean_node_id(raw: str) -> str:
    """Restore HTML entities and strip outer quotes."""
    unesc = html.unescape(raw)
    return unesc[1:-1] if unesc.startswith('"') and unesc.endswith('"') else unesc


def anonymize_text(chunk_text: str, raw_node_id: str) -> str:
    """
    Replace all occurrences of raw_node_id (case-insensitive),
    including possessive forms, with [mask].
    Ensure HTML entities are unescaped before masking.
    """
    text = html.unescape(chunk_text)
    pattern = re.compile(rf"\b{re.escape(raw_node_id)}(?:['’]s)?\b", re.IGNORECASE)
    return pattern.sub('[mask]', text)

async def main():
    raw_node_id_default = 'Benjamin'
    cache_dir = 'cache'

    vdb_path = os.path.join(cache_dir, 'vdb_entities.json')
    graphml_path = os.path.join(cache_dir, 'graph_chunk_entity_relation.graphml')
    kv_store_path = os.path.join(cache_dir, 'kv_store_text_chunks.json')

    # Step 0: Extract related entities
    entities = await extract_entities(raw_node_id_default, graphml_path)
    print(f"[Extracted Entities] 共 {len(entities)} 个：{entities}")

    for entity in entities:
        print(f"\n>>> Processing entity: {entity}")
        # Step 1: Update GraphML descriptions
        print(f"--- Step2: updating descriptions to remove '{entity}' from graphml ---")
        await update_graphml_descriptions(graphml_path, entity, raw_node_id_default)

        # Step 2: Anonymize text chunks for all entries
        try:
            results = await anonymize_all_chunks(kv_store_path, entity, raw_node_id_default)
        except FileNotFoundError as e:
            print("Error:", e)
            continue

        for cid, data in results.items():
            print(f"--- Chunk {cid} ---")
            print("Original:", data['original'])
            print("Anonymized:", data['anonymized'])



        # step3: 仅当指定节点存在 clusters 数据（<data key='d3'>）时运行 delete_community_pipeline
        run_step3 = False
        try:
            tree = ET.parse(graphml_path)
            root = tree.getroot()
            # 查找所有节点，处理 GraphML 转义的引号
            for node in root.findall('.//{*}node'):
                node_id = node.get('id', '')
                # 去除两端的双引号再比较
                if node_id.strip('"') == entity:
                    for data in node.findall('{*}data'):
                        if data.get('key') == 'd3':
                            run_step3 = True
                            break
                    break
        except Exception as e:
            print(f"Error reading GraphML for step3 check: {e}")

        if run_step3:
            print(f"--- Step3: running full delete_community pipeline for '{entity}' ---")
            await delete_community_pipeline(entity)
        else:
            print(f"--- Skipping Step3 for '{entity}': no clusters data for this node ---")

        # Step 4: Anonymize community reports for the original raw node
        print(f"--- Step4: anonymizing community reports for '{raw_node_id_default}' ---")
        update_reports_for_entity(raw_node_id_default)

        # Step 5: Remove node and edges
        remove_node_and_edges(graphml_path, entity)
        print(f"[Done] Removed node & edges for '{entity}'.")

        # Step 6: Delete entity from VDB
        delete_vdb_entities(entity, vdb_path)
        print(f"[Done] Deleted '{entity}' from VDB.")

if __name__ == '__main__':
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())