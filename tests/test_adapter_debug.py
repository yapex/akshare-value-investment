"""
调试DiskCacheAdapter的问题
"""

from akshare_value_investment.smart_cache import CacheConfig
from akshare_value_investment.smart_cache.adapters.diskcache_adapter import DiskCacheAdapter


def debug_adapter():
    """调试DiskCacheAdapter"""
    print("=== 调试DiskCacheAdapter ===")

    config = CacheConfig()
    print(f"缓存目录: {config.cache_dir}")
    print(f"最大大小: {config.max_size}")
    print(f"淘汰策略: {config.eviction_policy}")

    adapter = DiskCacheAdapter(config)
    print(f"适配器创建成功: {adapter}")

    # 测试基本功能
    test_key = "test_key_123"
    test_value = {"data": "hello world", "number": 42}

    print(f"\n1. 设置缓存:")
    print(f"   键: {test_key}")
    print(f"   值: {test_value}")

    set_result = adapter.set(test_key, test_value)
    print(f"   设置结果: {set_result}")

    # 检查缓存统计
    stats_after_set = adapter.stats()
    print(f"   设置后统计: {stats_after_set}")

    print(f"\n2. 获取缓存:")
    get_result = adapter.get(test_key)
    print(f"   获取结果: {get_result}")
    print(f"   结果类型: {type(get_result)}")
    print(f"   是否为None: {get_result is None}")

    if get_result is not None:
        print(f"   数据相等: {test_value == get_result}")

    # 再次检查统计
    stats_after_get = adapter.stats()
    print(f"   获取后统计: {stats_after_get}")

    # 检查缓存目录
    print(f"\n3. 检查缓存目录内容:")
    import os
    if os.path.exists(config.cache_dir):
        files = os.listdir(config.cache_dir)
        print(f"   缓存文件: {files}")
        for file in files[:3]:  # 只显示前3个文件
            file_path = os.path.join(config.cache_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   {file}: {file_size} bytes")
    else:
        print(f"   缓存目录不存在: {config.cache_dir}")


if __name__ == "__main__":
    debug_adapter()