"""
wanglib 更新日志:

2025/05/18: 初始化仓库

"""

import hashlib
import random
import uuid


def rd_int(a: int, b: int):
    """
    返回一个随机整数
    """
    return random.randint(a, b)


def rd_float(a: float, b: float):
    """
    返回一个随机浮点数
    """
    return random.uniform(a, b)


def rd_text(text: str):
    """
    随机打乱字符串
    """
    return "".join(random.sample(text, len(text)))


def new_uuid():
    """
    返回一个随机的UUID
    """
    return str(uuid.uuid4())


def sha256(input: int | str | bytes):
    """
    计算SHA256哈希值
    """
    if isinstance(input, str):
        input = input.encode("utf-8")
    elif isinstance(input, int):
        input = str(input).encode("utf-8")

    return hashlib.sha256(input).hexdigest()


def md5(input: int | str | bytes):
    """
    计算MD5哈希值
    """
    if isinstance(input, str):
        input = input.encode("utf-8")
    elif isinstance(input, int):
        input = str(input).encode("utf-8")

    return hashlib.md5(input).hexdigest()
