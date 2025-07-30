import hashlib
from zlib import crc32


def calc_crc32(txt: str):
    crc = crc32(txt.encode('utf-8'))
    return format(crc & 0xFFFFFFFF, '08x')


def md5(txt: str):
    return hashlib.md5(txt.encode()).hexdigest()
