import xml.etree.ElementTree as ET
import os

def strip_ns(tag: str) -> str:
    """Remove namespace from XML tag."""
    return tag[tag.find("}")+1:] if "}" in tag else tag

def extract_dumbledore_elements(input_path: str, output_path: str):
    # 1. 解析 GraphML
    tree = ET.parse(input_path)
    root = tree.getroot()

    # 2. 提取默认命名空间映射
    ns_uri = root.tag[root.tag.find("{")+1:root.tag.find("}")]
    ns_map = {'g': ns_uri}

    extracted = []

    # 3. 筛选 <node>，id 为 DUMBLEDORE
    for node in root.findall('.//g:node', ns_map):
        raw_id = node.get('id', '').strip('"').strip()
        if raw_id.lower() == 'dumbledore':
            extracted.append(node)

    # 4. 筛选 <edge>，source 或 target 为 DUMBLEDORE
    for edge in root.findall('.//g:edge', ns_map):
        src = edge.get('source', '').strip('"').strip().lower()
        tgt = edge.get('target', '').strip('"').strip().lower()
        if src == 'dumbledore' or tgt == 'dumbledore':
            extracted.append(edge)

    # 5. 手动拼装纯净 XML，去掉 namespace 前缀和声明
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<graphml_extract>\n')

        for elem in extracted:
            tag = strip_ns(elem.tag)
            # 拼接属性，例如 id="..." 或 source="..." target="..."
            attrs = " ".join(f'{strip_ns(k)}="{v}"' for k, v in elem.items())
            f.write(f'  <{tag} {attrs}>\n')

            # 拼接子元素 <data key="...">...</data>
            for child in elem:
                child_tag = strip_ns(child.tag)
                key = child.get('key')
                text = child.text or ""
                f.write(f'    <{child_tag} key="{key}">{text}</{child_tag}>\n')

            f.write(f'  </{tag}>\n')

        f.write('</graphml_extract>\n')

if __name__ == '__main__':
    input_file = os.path.join('cache2', 'graph_chunk_entity_relation.graphml')
    output_file = 'graphml_extract.graphml'
    extract_dumbledore_elements(input_file, output_file)
    print(f"Extraction complete. Output saved to {output_file}")
