import threading
from typing import Any

import cachetools


class CacheManager:
    """
    wanglib 的缓存管理模块，对cachetools进行了简单的封装，提供了缓存管理的功能。
    """

    def __init__(self, tag: str = "cache", max_size=1024) -> None:
        self.tag = tag
        self.lock = threading.Lock()
        self.cache = cachetools.LRUCache(maxsize=max_size)

    def set(self, key: str, value: Any):
        with self.lock:
            self.cache[key] = value

    def get(self, key: str):
        with self.lock:
            return self.cache.get(key)

    def delete(self, key: str):
        with self.lock:
            del self.cache[key]

    def clear(self):
        with self.lock:
            self.cache.clear()

    def __len__(self):
        with self.lock:
            return len(self.cache)

    def __contains__(self, key: str):
        with self.lock:
            return key in self.cache

    def __getitem__(self, key: str):
        with self.lock:
            return self.cache[key]

    def __setitem__(self, key: str, value: Any):
        with self.lock:
            self.cache[key] = value

    def __delitem__(self, key: str):
        with self.lock:
            del self.cache[key]

    def __iter__(self):
        with self.lock:
            return iter(self.cache)
