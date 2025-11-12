"""
Smart Cache 集成演示
展示财务数据查询系统的缓存效果
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from akshare_value_investment.datasource.adapters import AStockAdapter
from akshare_value_investment.smart_cache import get_cache_stats


def demo_cache_integration():
    """演示缓存集成效果"""
    adapter = AStockAdapter()

    print("🚀 Smart Cache 集成演示")
    print("=" * 50)

    # 测试股票代码
    test_symbol = "600519"  # 贵州茅台

    # 第一次查询（缓存未命中）
    print("📡 第一次查询：获取财务数据")
    start_time = time.time()
    try:
        # 直接调用内部方法来测试缓存效果
        result1 = adapter._get_a_stock_financial_data(test_symbol)
        end_time = time.time()

        print(f"   查询时间: {end_time - start_time:.3f}秒")
        print(f"   数据条数: {len(result1) if result1 else 0}")
        print(f"   缓存状态: 未命中（首次查询）")

        # 显示部分原始数据结构
        if result1:
            sample_data = result1[0] if isinstance(result1, list) else result1
            if hasattr(sample_data, 'data'):
                print(f"   数据样例: {type(sample_data.data).__name__}")
                print(f"   缓存键: {sample_data.cache_key}")
                print(f"   缓存命中: {sample_data.cache_hit}")
            else:
                print(f"   数据样例: 原始数据列表（{len(result1)}条记录）")
    except Exception as e:
        print(f"   ❌ 查询失败: {str(e)}")
        return

    # 第二次查询（缓存命中）
    print("\n🎯 第二次查询：相同数据（应该命中缓存）")
    start_time = time.time()
    try:
        result2 = adapter._get_a_stock_financial_data(test_symbol)
        end_time = time.time()

        print(f"   查询时间: {end_time - start_time:.3f}秒")
        print(f"   数据条数: {len(result2) if result2 else 0}")

        # 检查缓存结果
        if hasattr(result2, 'cache_hit'):
            print(f"   缓存状态: {'✅ 命中' if result2.cache_hit else '❌ 未命中'}")
            print(f"   缓存键: {result2.cache_key}")
        else:
            print("   注意: 返回的是原始数据格式（缓存装饰器内部处理）")
    except Exception as e:
        print(f"   ❌ 查询失败: {str(e)}")

    # 第三次查询（不同股票代码）
    print("\n🔄 第三次查询：不同股票代码（新的缓存项）")
    different_symbol = "000858"  # 五粮液
    start_time = time.time()
    try:
        result3 = adapter._get_a_stock_financial_data(different_symbol)
        end_time = time.time()

        print(f"   查询时间: {end_time - start_time:.3f}秒")
        print(f"   数据条数: {len(result3) if result3 else 0}")

        if hasattr(result3, 'cache_hit'):
            print(f"   缓存状态: {'✅ 命中' if result3.cache_hit else '❌ 未命中'}")
            print(f"   缓存键: {result3.cache_key}")
    except Exception as e:
        print(f"   ❌ 查询失败: {str(e)}")

    # 缓存统计
    print(f"\n📊 缓存统计信息:")
    try:
        stats = get_cache_stats()
        print(f"   缓存项数: {stats.get('size', 0)}")
        print(f"   缓存大小: {stats.get('volume', 0)} bytes")
    except Exception as e:
        print(f"   ❌ 获取缓存统计失败: {str(e)}")


def demo_public_interface():
    """演示公共接口的缓存效果（通过适配器管理器）"""
    print("\n\n🔗 公共接口演示")
    print("=" * 50)

    from akshare_value_investment.container import create_production_service
    from akshare_value_investment.core.models import MarketType

    try:
        query_service = create_production_service()

        # 查询财务数据
        print("📡 查询财务指标:")
        result = query_service.query_financial_indicators(
            symbol="600519",
            market=MarketType.A_STOCK
        )

        print(f"   查询成功: {result.success}")
        print(f"   数据条数: {result.total_records}")
        print(f"   消息: {result.message}")

        if result.success and result.data:
            sample = result.data[0]
            print(f"   样例数据: {sample.symbol} - {sample.company_name}")
            print(f"   报告期: {sample.report_date}")
            print(f"   原始字段数: {len(sample.raw_data)}")

    except Exception as e:
        print(f"   ❌ 查询失败: {str(e)}")


if __name__ == "__main__":
    demo_cache_integration()
    demo_public_interface()

    print("\n\n✨ Smart Cache 集成演示完成！")
    print("💡 提示: 缓存数据持久化存储在 ./cache_data 目录")