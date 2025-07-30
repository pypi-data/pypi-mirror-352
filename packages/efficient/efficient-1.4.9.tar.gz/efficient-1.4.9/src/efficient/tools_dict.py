def dic_get(dic: dict, key, default=None):
    value = dic.get(key)
    if value is None:
        return default
    return value


# 创建指定层级的字典
def set_nested_value(dictionary, path, value):
    keys = path.split('.')
    current = dictionary

    # 遍历除最后一个键以外的所有键
    for key in keys[:-1]:
        # 如果键不存在或者对应的值不是字典，则创建一个新字典
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    # 设置最后一个键的值
    current[keys[-1]] = value

    return dictionary


if '__main__' == __name__:
    d = dict(x=1, a=dict(y=1))
    t = set_nested_value(d, 'a.b.c', 1)
    print(t)
    print(d)
    print(id(t), id(d))
