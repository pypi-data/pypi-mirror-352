import os
import pathlib
import ssl

import httpx


def ensure_dir(dir_path: os.PathLike) -> bool:
    """
    确保目录存在，如果不存在则创建目录
    """
    if not os.path.exists(dir_path):  # 检查目录是否存在，如果不存在则创建目录
        os.makedirs(dir_path)
        return True
    else:
        return False

def ensure_file(file_path: os.PathLike) -> bool:
    """
    确保文件存在，如果不存在则创建空文件
    """
    if not os.path.exists(file_path):  # 检查文件是否存在，如果不存在则创建空文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        return True
    else:
        return False


async def download(url: str, target_path: os.PathLike, filename: str) -> bool:
    """
    下载文件到指定的目录，返回是否成功
    """
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url)
            if response.status_code == 200:
                # ensure_dir(os.path.dirname(target_path))
                with open(pathlib.Path(target_path).joinpath(filename), "wb") as f:
                    f.write(response.content)
                return True
    except Exception as e:
        raise e
    return False


async def unsafe_download(url: str, target_path: os.PathLike, filename: str) -> bool:
    """
    下载文件到指定的目录，返回是否成功

    使用不安全的 SSL 上下文，允许更多的加密算法，主要为 Nonebot 中的文件下载场景准备
    """
    try:
        # 创建自定义 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # 降低安全级别，允许更多的加密算法

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0), verify=ssl_context) as client:
            response = await client.get(url)
            if response.status_code == 200:
                # ensure_dir(os.path.dirname(target_path))
                with open(pathlib.Path(target_path).joinpath(filename), "wb") as f:
                    f.write(response.content)
                return True
    except Exception as e:
        raise e
    return False
