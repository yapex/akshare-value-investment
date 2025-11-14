"""
测试单边缺失按需补充的增量更新逻辑

验证场景：
1. 完全无缓存 → 完整获取
2. 左单边缺失 → 按需补充左侧
3. 右单边缺失 → 按需补充右侧
4. 多边缺失 → 完整重新获取
5. 中间间隙 → 完整重新获取
"""

import logging
from sqlite_cache import SQLiteCache
from smart_decorator import smart_sqlite_cache

logging.basicConfig(level=logging.INFO)

def mock_api_call(symbol: str, start_date: str, end_date: str):
    """模拟API调用，返回测试数据"""
    import pandas as pd
    import random

    print(f"   📡 API调用: {symbol} {start_date} ~ {end_date}")

    # 生成测试数据
    start = int(start_date.split('-')[0])
    end = int(end_date.split('-')[0])

    data = []
    for year in range(start, end + 1):
        for quarter in [3, 6, 9, 12]:
            date = f"{year}-{quarter:02d}-31"
            if date < start_date or date > end_date:
                continue

            data.append({
                'symbol': symbol,
                'date': date,
                'basic_eps': round(30.0 + year * 0.5 + quarter * 0.1 + random.uniform(-2, 2), 2),
                'roe': round(25.0 + year * 0.2 + random.uniform(-1, 1), 2)
            })

    return pd.DataFrame(data)

def test_incremental_logic():
    """测试增量更新逻辑"""
    print("🧪 测试单边缺失按需补充的增量更新逻辑")
    print("=" * 60)

    # 初始化测试
    adapter = SQLiteCache("./test_incremental_single.db")
    symbol = "SH600519"
    date_field = "date"
    query_type = "indicators"

    # 清理测试数据
    adapter.clear_cache_by_symbol(symbol)

    # 创建装饰器函数
    @smart_sqlite_cache(date_field=date_field, query_type=query_type, cache_adapter=adapter)
    def get_financial_data(symbol: str, start_date: str, end_date: str):
        return mock_api_call(symbol, start_date, end_date)

    print("\n📋 场景1：完全无缓存")
    print("-" * 30)
    result1 = get_financial_data(symbol, "2023-01-01", "2023-12-31")
    print(f"返回: {len(result1)} 条记录")

    print("\n📋 场景2：左单边缺失 - 已有2023数据，请求2022-2023")
    print("-" * 30)
    # 先添加2023年数据
    data_2023 = mock_api_call(symbol, "2023-01-01", "2023-12-31")
    adapter.save_records(symbol, data_2023.to_dict('records'), date_field, query_type)

    result2 = get_financial_data(symbol, "2022-01-01", "2023-12-31")
    print(f"返回: {len(result2)} 条记录")
    print(f"日期范围: {result2['date'].min()} ~ {result2['date'].max()}")

    print("\n📋 场景3：右单边缺失 - 已有2022-2023，请求2022-2024")
    print("-" * 30)
    result3 = get_financial_data(symbol, "2022-01-01", "2024-12-31")
    print(f"返回: {len(result3)} 条记录")
    print(f"日期范围: {result3['date'].min()} ~ {result3['date'].max()}")

    print("\n📋 场景4：多边缺失 - 已有2023，请求2021-2025")
    print("-" * 30)
    result4 = get_financial_data(symbol, "2021-01-01", "2025-12-31")
    print(f"返回: {len(result4)} 条记录")
    print(f"日期范围: {result4['date'].min()} ~ {result4['date'].max()}")

    print("\n📋 场景5：验证缓存命中 - 再次请求2022-2024")
    print("-" * 30)
    result5 = get_financial_data(symbol, "2022-01-01", "2024-12-31")
    print(f"返回: {len(result5)} 条记录")

    print("\n📋 场景6：中间间隙模拟 - 清理部分数据测试")
    print("-" * 30)
    # 手动删除2023-Q2数据模拟中间缺失
    conn = adapter._get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM financial_data
        WHERE symbol = ? AND date_field = ? AND query_type = ? AND date_value = ?
    """, (symbol, date_field, query_type, "2023-06-30"))
    conn.commit()

    result6 = get_financial_data(symbol, "2022-01-01", "2024-12-31")
    print(f"返回: {len(result6)} 条记录")

    # 清理
    adapter.clear_cache_by_symbol(symbol)
    print(f"\n✅ 测试完成，清理测试数据")

    print(f"\n💡 增量更新逻辑总结:")
    print(f"   1. 完全无缓存: 一次API获取完整数据")
    print(f"   2. 左单边缺失: 只获取缺失的左侧数据")
    print(f"   3. 右单边缺失: 只获取缺失的右侧数据")
    print(f"   4. 多边缺失: 一次API获取完整数据")
    print(f"   5. 中间间隙: 一次API获取完整数据")
    print(f"   6. 缓存命中: 直接返回，无需API调用")

if __name__ == "__main__":
    test_incremental_logic()