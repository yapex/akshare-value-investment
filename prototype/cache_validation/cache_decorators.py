"""
智能缓存装饰器 - 极简验证版本
使用diskcache实现持久化缓存
"""

from diskcache import Cache
from functools import wraps
import hashlib
import json
import time
from typing import Any

# 全局缓存实例
_cache = Cache('cache_data')

def smart_cache(cache_prefix: str = "default"):
    """智能缓存装饰器

    Args:
        cache_prefix: 缓存键前缀，用于区分不同类型的数据
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(cache_prefix, func.__name__, args, kwargs)

            # 尝试从缓存获取
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                print(f"🎯 Cache HIT: {cache_key}")
                return cached_result

            # 缓存未命中，执行原函数
            print(f"📡 Cache MISS: {cache_key}")
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            # 存入缓存（无TTL，永久存储）
            _cache.set(cache_key, result)
            print(f"✅ Cached in {end_time - start_time:.3f}s")

            return result

        return wrapper
    return decorator

def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """生成标准化缓存键"""
    # 过滤掉self参数，只保留业务参数
    filtered_args = args[1:] if args and hasattr(args[0], '__class__') else args

    # 创建参数签名
    param_data = {
        'args': filtered_args,
        'kwargs': sorted(kwargs.items())  # 排序确保一致性
    }

    # 生成参数哈希
    param_hash = hashlib.md5(
        json.dumps(param_data, sort_keys=True, default=str).encode('utf-8')
    ).hexdigest()[:8]

    return f"{prefix}_{func_name}_{param_hash}"

def get_cache_stats():
    """获取缓存统计信息"""
    return {
        'size': len(_cache),
        'volume': _cache.volume()
    }

def clear_cache():
    """清理所有缓存"""
    _cache.clear()
    print("🗑️ Cache cleared")