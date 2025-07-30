# 按配置从 json 中提取数据
class JsonExtr:
    @classmethod
    def _get_value(cls, container, key):
        try:
            return container[key]
        except Exception as e:
            return None

    @classmethod
    def _get_value_by_list(cls, lst, data):
        tmp = None
        for idx, field in enumerate(lst):
            if idx == 0:
                tmp = cls._get_value(data, field)
            else:
                tmp = cls._get_value(tmp, field)
        return tmp

    @classmethod
    def extr(cls, config, raw_data):
        """
        :param config:
        {
            'uid': 'uid',
            'name': ['user_info', 'nickname'],
            'name': (['user_info', 'nickname'],lambda a:a),
        }
        :param raw_data:
        :return:
        """
        data = {}
        for k, v in config.items():
            if type(v) is not tuple:
                v = (v, None)
            field, formatting = v

            if type(field) is list:
                data[k] = cls._get_value_by_list(field, raw_data)
            else:
                data[k] = cls._get_value(raw_data, field)
            # 格式化
            if callable(formatting):
                data[k] = formatting(data[k])

        return data


# 搜索元素在数组中的路径
class JsonTree:
    __key = None  # 数组的键名，如果是数字就转成字符串
    __val = None  # 数组的键值

    def __init__(self, data, key=None):
        # 把数组转成树状结构，查找的时候每个分枝对比自己的__val就好了
        self.__key = key
        if type(data) is dict:
            for k, v in data.items():
                setattr(self, k, JsonTree(v, k))
        elif type(data) is list:
            for idx, i in enumerate(data):
                setattr(self, str(idx), JsonTree(i, str(idx)))
        else:
            self.__val = data

    def search(self, val, path=''):
        for i in self.__dict__:
            # print(type(i), i)
            if '_Tree' not in i:
                _t = getattr(self, i)
                _t.search(val, "{}/{}".format(path, _t.__key))
                if _t.__val == val:
                    print('搜索结果', val, path + '/' + _t.__key)
