"""
缓存调试测试
找出缓存不工作的原因
"""

from akshare_value_investment.smart_cache import smart_cache, CacheConfig, KeyGenerator
from akshare_value_investment.smart_cache.adapters.diskcache_adapter import DiskCacheAdapter


def debug_cache():
    """调试缓存机制"""
    print("=== 调试缓存机制 ===")

    # 1. 测试KeyGenerator
    print("\n1. 测试KeyGenerator:")
    key_gen = KeyGenerator("test")

    key1 = key_gen.generate("test_func", ("abc",), {})
    key2 = key_gen.generate("test_func", ("abc",), {})
    key3 = key_gen.generate("test_func", ("xyz",), {})

    print(f"   相同参数的键: {key1} == {key2} -> {key1 == key2}")
    print(f"   不同参数的键: {key1} != {key3} -> {key1 != key3}")

    # 2. 测试DiskCacheAdapter
    print("\n2. 测试DiskCacheAdapter:")
    config = CacheConfig()
    adapter = DiskCacheAdapter(config)

    test_key = "debug_test_key"
    test_value = {"data": "test_value"}

    print(f"   设置缓存: {test_key} -> {test_value}")
    set_result = adapter.set(test_key, test_value)
    print(f"   设置结果: {set_result}")

    retrieved_value = adapter.get(test_key)
    print(f"   获取结果: {retrieved_value}")
    print(f"   数据一致: {test_value == retrieved_value}")

    # 3. 测试装饰器
    print("\n3. 测试装饰器:")
    call_count = 0

    @smart_cache("debug_test", ttl=3600)
    def debug_func(x):
        nonlocal call_count
        call_count += 1
        print(f"   函数被调用: call_count={call_count}, x={x}")
        return f"result_{x}"

    print("   第一次调用:")
    result1 = debug_func("abc")
    print(f"   返回: {result1}, cache_hit={result1.cache_hit}")

    print("   第二次调用:")
    result2 = debug_func("abc")
    print(f"   返回: {result2}, cache_hit={result2.cache_hit}")

    print(f"   总调用次数: {call_count}")

    # 4. 检查缓存统计
    stats = adapter.stats()
    print(f"\n4. 缓存统计: {stats}")


if __name__ == "__main__":
    debug_cache()