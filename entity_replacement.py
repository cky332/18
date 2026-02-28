import re


def replace_dumbledore_with_benjamin(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 使用正则表达式替换Dumbledore为Benjamin，不区分大小写
    content = re.sub(r'\balbus\b', 'Gandalf', content, flags=re.IGNORECASE)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# 调用函数，传入文件路径
replace_dumbledore_with_benjamin('harry.txt')
