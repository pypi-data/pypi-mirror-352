import json

import json_repair


def safety_json_loader(json_str, index=None):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 处理错误的JSON字符串
        # 可以选择忽略错误的行或进行其他处理
        print(
            f"{'' if index is None else f'Line {index} '}Error decoding JSON: {json_str}"
        )
        return None
    # print("yes"


def load_json(json_path, process_func=lambda x: x):
    # print("yes")
    with open(json_path, "r") as f:
        result = []
        for index, line in enumerate(f):
            stripped = line.strip()
            if stripped:  # 检查是否非空
                loaded = safety_json_loader(stripped, index)
                if loaded is not None:  # 检查是否非None
                    loaded = process_func(loaded)
                    result.append(loaded)
    return result


def save_normal_json(json_info, json_path):
    with open(json_path, "w") as f:
        for info in json_info:
            print(json.dumps(info, ensure_ascii=False), file=f)


def flatten_dict(my_dict):
    for k, v in my_dict.items():
        if isinstance(v, dict):
            yield from flatten_dict(v)
        else:
            yield k, v


def load_json_line(info):
    try:
        data = json.loads(info)
    except json.JSONDecodeError:
        # 可以在这里添加安装逻辑

        data = json_repair.loads(info)
    return data


def load_json_file(file_path):
    with open(file_path, "r") as file:
        data = load_json_line(file.read())
    return data
