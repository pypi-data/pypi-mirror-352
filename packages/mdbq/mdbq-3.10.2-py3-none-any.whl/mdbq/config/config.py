import os.path
import re


def read_config(file_path):
    """读取配置文件，返回字典"""
    if not os.path.isfile(file_path):
        print(f'配置文件不存在: {file_path}')
        return
    config = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()
            # 跳过空行和注释行（以 # 或 // 开头）
            if not stripped_line or stripped_line.startswith(('#', '//')):
                continue
            # 处理行内注释（# 或 // 前有空格）
            comment_match = re.search(r'\s+[#//]', line)
            if comment_match:
                line = line[:comment_match.start()].strip()
            else:
                line = line.strip()
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def write_config(file_path, rewrite):
    """
    更新配置文件中的键值对，保留注释和其他内容，修复等号空格问题
    示例：
    write_config('spd.txt', {'is_spider': True})
    """
    # 读取所有行到内存
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        with open(file_path, 'w', encoding='utf-8') as file:
            lines = []

    new_lines = []
    found_keys = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '//')):
            new_lines.append(line)
            continue

        # 使用 partition 保留等号格式
        key_part, sep, value_part = line.partition('=')
        if not sep:  # 没有等号的行直接保留
            new_lines.append(line)
            continue

        key = key_part.strip()
        if key in rewrite:
            # 处理值部分和注释
            comment_match = re.search(r'\s+([#//].*)$', value_part)
            if comment_match:
                comment = comment_match.group(0)
                raw_value = value_part[:comment_match.start()].rstrip()
            else:
                comment = ''
                raw_value = value_part.strip()

            # 保留原值前导空格
            leading_space = re.match(r'^(\s*)', value_part).group(1)
            new_value = f"{leading_space}{rewrite[key]}{comment}"

            # 构建新行（保留原等号格式）
            new_line = f"{key_part}{sep}{new_value}\n"
            new_lines.append(new_line)
            found_keys.add(key)
        else:
            new_lines.append(line)

    # 添加新键值对
    for key in rewrite:
        if key not in found_keys:
            new_lines.append(f"{key} = {rewrite[key]}\n")

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


if __name__ == '__main__':
    res = read_config('/Users/xigua/数据中心2/spider/spd.txt')
    print(res)
    # write_config('spd.txt', {'is_spider': False})

