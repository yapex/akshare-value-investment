"""
直接测试diskcache
"""

from diskcache import Cache

def test_direct_diskcache():
    """直接测试diskcache"""
    print("=== 直接测试diskcache ===")

    # 使用相同的配置
    cache = Cache("./cache_data", eviction_policy="least-recently-used", size_limit=1000)

    test_key = "direct_test_key"
    test_value = {"message": "hello", "data": [1, 2, 3]}

    print(f"1. 设置缓存: {test_key} -> {test_value}")
    set_result = cache.set(test_key, test_value)
    print(f"   设置结果: {set_result}")

    print(f"2. 检查缓存大小: {len(cache)}")
    print(f"   缓存卷大小: {cache.volume()}")

    print(f"3. 获取缓存: {test_key}")
    get_result = cache.get(test_key)
    print(f"   获取结果: {get_result}")
    print(f"   数据一致: {test_value == get_result}")

    # 检查所有键
    print(f"4. 缓存中的键:")
    with cache.transact():
        for key in cache.iterkeys():
            print(f"   {key}")

    # 尝试不同的获取方式
    print(f"5. 测试不同的获取方式:")
    print(f"   cache.get('{test_key}'): {cache.get(test_key)}")
    if test_key in cache:
        print(f"   '{test_key}' in cache: True")
        print(f"   cache['{test_key}']: {cache[test_key]}")
    else:
        print(f"   '{test_key}' in cache: False")

    cache.close()


if __name__ == "__main__":
    test_direct_diskcache()