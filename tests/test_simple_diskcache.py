"""
测试简化的diskcache配置
"""

from diskcache import Cache
import os
import shutil

def test_simple_diskcache():
    """测试简化的diskcache配置"""
    print("=== 测试简化的diskcache配置 ===")

    # 清理旧的缓存目录
    cache_dir = "./test_cache_simple"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    # 使用最简单的配置
    print("1. 创建最简单的缓存:")
    cache = Cache(cache_dir)  # 不使用任何额外参数
    print(f"   缓存目录: {cache_dir}")

    test_key = "simple_test"
    test_value = {"data": "test", "count": 1}

    print(f"2. 设置缓存: {test_key} -> {test_value}")
    set_result = cache.set(test_key, test_value)
    print(f"   设置结果: {set_result}")

    print(f"3. 获取缓存:")
    get_result = cache.get(test_key)
    print(f"   获取结果: {get_result}")
    print(f"   数据一致: {test_value == get_result}")

    print(f"4. 缓存统计:")
    print(f"   缓存大小: {len(cache)}")
    print(f"   缓存卷大小: {cache.volume()}")

    # 测试带参数的配置
    print("\n5. 测试带参数的配置:")
    cache_dir2 = "./test_cache_params"
    if os.path.exists(cache_dir2):
        shutil.rmtree(cache_dir2)

    cache2 = Cache(cache_dir2, size_limit=100)
    print(f"   缓存目录: {cache_dir2}")

    set_result2 = cache2.set(test_key, test_value)
    get_result2 = cache2.get(test_key)

    print(f"   设置结果: {set_result2}")
    print(f"   获取结果: {get_result2}")
    print(f"   数据一致: {test_value == get_result2}")

    cache.close()
    cache2.close()

    # 清理测试目录
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    if os.path.exists(cache_dir2):
        shutil.rmtree(cache_dir2)


if __name__ == "__main__":
    test_simple_diskcache()