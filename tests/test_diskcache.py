"""
测试DiskCache适配器的序列化问题
"""

from diskcache import Cache
import pickle

def test_diskcache_serialization():
    """测试diskcache的序列化功能"""
    print("=== 测试DiskCache序列化 ===")

    # 创建一个临时缓存
    cache = Cache("./test_cache_temp")

    # 测试简单数据
    simple_data = {"data": "test_value"}
    print(f"\n1. 测试简单数据: {simple_data}")
    cache.set("simple_key", simple_data)
    retrieved = cache.get("simple_key")
    print(f"   原始数据: {simple_data}")
    print(f"   获取数据: {retrieved}")
    print(f"   数据一致: {simple_data == retrieved}")

    # 测试复杂数据
    complex_data = {
        "指标": "营业收入",
        "选项": "",
        "20231231": "1000000000",
        "20221231": "900000000"
    }
    print(f"\n2. 测试复杂数据: {complex_data}")
    cache.set("complex_key", complex_data)
    retrieved_complex = cache.get("complex_key")
    print(f"   原始数据: {complex_data}")
    print(f"   获取数据: {retrieved_complex}")
    print(f"   数据一致: {complex_data == retrieved_complex}")

    # 测试列表数据
    list_data = [
        {"指标": "营业收入", "20231231": "1000000000"},
        {"指标": "净利润", "20231231": "200000000"}
    ]
    print(f"\n3. 测试列表数据: {list_data}")
    cache.set("list_key", list_data)
    retrieved_list = cache.get("list_key")
    print(f"   原始数据: {list_data}")
    print(f"   获取数据: {retrieved_list}")
    print(f"   数据一致: {list_data == retrieved_list}")

    # 测试pickle序列化
    print(f"\n4. 测试pickle序列化:")
    pickled_data = pickle.dumps(simple_data)
    print(f"   pickle成功: {len(pickled_data)} bytes")
    unpickled_data = pickle.loads(pickled_data)
    print(f"   unpickle一致: {simple_data == unpickled_data}")

    # 清理测试缓存
    cache.clear()

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_diskcache_serialization()