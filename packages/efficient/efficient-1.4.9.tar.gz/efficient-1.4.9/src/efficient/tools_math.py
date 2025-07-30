import math


# 获取一个整数的某位的值
def digit_pos(num, pos):
    _max = math.floor(math.log(num, 10))  # 最大是几位数
    if pos > _max:
        raise Exception('{} 的最大位数是 {} 但是传入的是 {}'.format(num, _max, pos))
    # 移位操作: num // 10**pos 相当于将数字向右移动pos位，丢弃右边的数字
    # 提取操作: % 10 提取结果的个位数字
    return num // 10 ** pos % 10


# 将整数转换为中文数字
def num_to_zh(num: int, simple=True) -> str:
    if simple:
        chinese_num = {
            0: '零', 1: '一', 2: '二', 3: '三', 4: '四',
            5: '五', 6: '六', 7: '七', 8: '八', 9: '九'
        }
        chinese_unit = ['', '十', '百', '千', '万', '十', '百', '千', '亿']
    else:
        chinese_num = {
            0: '零', 1: '壹', 2: '贰', 3: '叁', 4: '肆',
            5: '伍', 6: '陆', 7: '柒', 8: '捌', 9: '玖'
        }
        chinese_unit = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    if num < 0:
        return f"负{num_to_zh(abs(num))}"
    if num == 0:
        return "零"

    # 转换为字符串
    num_str = str(num)
    num_len = len(num_str)
    result = ""

    for i, digit in enumerate(num_str):
        # 当前数字的中文
        current_num = chinese_num[int(digit)]
        # 当前位置的单位
        unit_index = num_len - 1 - i
        current_unit = chinese_unit[unit_index]

        # 处理零的特殊情况
        if current_num == '零':
            # 如果是最后一位数字，不加单位
            if i == num_len - 1:
                result += current_num
            # 如果后面还有数字，且不是万或亿的位置，只加数字不加单位
            elif unit_index not in [4, 8]:
                if result[-1] != '零':  # 避免重复的零
                    result += current_num
        else:
            result += current_num + current_unit

    # 清理末尾的零
    while result.endswith('零'):
        result = result[:-1]

    return result


# 中文数字转整数
def zh_to_num(zh_num):
    _map = {
        '零': 0,
        '一': 1,
        '二': 2, '两': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10 ** 1,
        '百': 10 ** 2,
        '千': 10 ** 3,
        '万': 10 ** 4,
    }
    arr = []
    for i in zh_num:
        if i in ['十', '百', '千', '万']:
            if len(arr) <= 0:  # 处理以单位开头的数字，如：十一
                arr = [1]
            arr[-1] = _map[i] * arr[-1]
        else:
            arr.append(_map[i])

    return sum(arr)


if '__main__' == __name__:
    # print(digit_pos(199, 1))
    cases = [
        10000,
        10001,
        10011,
        10111,
        11111,
        10001,
        11001,
        11101,
        111,
    ]
    for n in cases:
        # print(num_to_zh(n))
        # print()
        a = num_to_zh(n)
        b = zh_to_num(a)
        print(a, b)

    print(zh_to_num('一万零一百'))
    print(zh_to_num('二千'))
    print(zh_to_num('两千零一'))
    print(zh_to_num('十一'))
    print(zh_to_num('十'))
    print(zh_to_num('九十一'))
    print(zh_to_num('一'))
