# 列表分割
def list_chunk(lst, n):
    arr = []
    for i in range(0, len(lst), n):
        arr.append(lst[i:i + n])
    return arr


def array_column(array, column_key=None, index_key=None):
    """
    模拟PHP的array_column函数
    """
    if column_key is not None:
        return [row[column_key] for row in array]
    if index_key is not None:
        return {row[index_key]: row for row in array}
    return None