#!/usr/bin/env python3
"""
财务指标字段映射系统测试脚本
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_field_mapping():
    """测试字段映射功能"""
    print("🔍 测试财务指标字段映射系统")
    print("=" * 50)

    try:
        from akshare_value_investment.business.mapping.query_engine import FinancialQueryEngine

        # 创建查询引擎
        engine = FinancialQueryEngine()
        print("✅ 查询引擎创建成功")

        # 获取统计信息
        stats = engine.get_statistics()
        print(f"✅ 配置已加载: {stats['config_loaded']}")
        print(f"✅ 可用市场: {stats['config_info']['available_markets']}")
        print(f"✅ 总字段数: {stats['config_info']['total_fields']}")
        print(f"✅ 总关键字数: {stats['total_keywords']}")
        print()

        # 测试多市场查询功能
        test_queries = [
            "公司赚了多少钱",
            "ROE",
            "毛利率",
            "每股收益",
            "资金链",
            "卖货速度",
            "公司家底"
        ]

        print("🎯 测试智能查询 (A股):")
        for query in test_queries:
            result = engine.query_financial_field(query, 'a_stock')
            if result['success']:
                print(f"✅ '{query}' → '{result['field_name']}' (相似度: {result['similarity']:.2f})")
            else:
                print(f"❌ '{query}' → 未找到，建议: {result['suggestions'][:2]}")

        print()
        print("🎯 测试智能查询 (港股):")
        for query in test_queries[:4]:  # 测试前4个
            result = engine.query_financial_field(query, 'hk_stock')
            if result['success']:
                print(f"✅ '{query}' → '{result['field_name']}' (相似度: {result['similarity']:.2f})")
            else:
                print(f"❌ '{query}' → 未找到")

        print()
        print("🎯 测试智能查询 (美股):")
        for query in test_queries[:4]:  # 测试前4个
            result = engine.query_financial_field(query, 'us_stock')
            if result['success']:
                print(f"✅ '{query}' → '{result['field_name']}' (相似度: {result['similarity']:.2f})")
            else:
                print(f"❌ '{query}' → 未找到")

        print()

        # 测试跨市场搜索
        print("🔍 测试跨市场字段搜索:")
        search_result = engine.search_fields("净利润", limit=10)
        for field in search_result:
            print(f"  - {field['field_name']}: {field['similarity']:.2f} ({field.get('field_id', 'N/A')})")

        print()

        # 测试市场特定查询
        print("🌍 测试市场特定查询:")
        hk_result = engine.query_financial_field("公司赚了多少钱", 'hk_stock')
        if hk_result['success']:
            print(f"✅ 港股: '{hk_result['field_name']}' (字段ID: {hk_result.get('field_id', 'N/A')})")

        us_result = engine.query_financial_field("公司赚了多少钱", 'us_stock')
        if us_result['success']:
            print(f"✅ 美股: '{us_result['field_name']}' (字段ID: {us_result.get('field_id', 'N/A')})")

        print()

        # 显示市场统计
        markets = engine.get_available_markets()
        print(f"📊 可用市场: {markets}")
        for market in markets:
            market_fields = engine.get_available_fields(market)
            print(f"  - {market.upper()}: {len(market_fields)} 个字段")

        print()
        print("🎉 字段映射系统测试成功！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise  # 使用raise而不是return False，让pytest正确处理错误

if __name__ == "__main__":
    try:
        test_field_mapping()
        sys.exit(0)  # 成功时退出
    except Exception as e:
        print(f"程序执行异常: {e}")
        sys.exit(1)  # 失败时退出