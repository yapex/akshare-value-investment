#!/usr/bin/env python3
"""
财务指标查询系统 - 简化版演示

展示原始数据访问功能，不进行字段映射，直接返回akshare原始字段。
"""

import sys
import os
import time
from datetime import datetime

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入简化版本组件
from akshare_value_investment.container import create_production_service
from akshare_value_investment.core.models import MarketType


def analyze_raw_data_result(result, stock_name, symbol):
    """分析原始数据查询结果并生成统计摘要"""
    print(f"\n{stock_name} ({symbol}) 原始数据查询结果分析:")
    print("-" * 60)

    if not result.success:
        print(f"❌ 查询失败: {result.message}")
        return None

    if not result.data:
        print("❌ 没有获取到数据")
        return None

    print(f"✅ 查询成功，共获取 {len(result.data)} 条记录")

    # 获取最新一期数据
    latest_indicator = result.data[0]  # 假设数据按时间降序排列

    print(f"📊 数据统计:")
    print(f"   股票代码: {latest_indicator.symbol}")
    print(f"   市场类型: {latest_indicator.market.value}")
    print(f"   公司名称: {latest_indicator.company_name}")
    print(f"   货币单位: {latest_indicator.currency}")
    print(f"   最新报告期: {latest_indicator.report_date.strftime('%Y-%m-%d')}")
    print(f"   报告期类型: {latest_indicator.period_type.value}")

    # 分析原始数据字段
    if latest_indicator.raw_data:
        raw_fields = list(latest_indicator.raw_data.keys())
        print(f"📈 原始数据字段统计:")
        print(f"   总字段数: {len(raw_fields)} 个")
        print(f"   字段列表: {raw_fields}")

        # 显示前10个字段的值
        print(f"\n🔍 前10个字段示例:")
        for i, field in enumerate(raw_fields[:10], 1):
            value = latest_indicator.raw_data.get(field)
            print(f"   {i:2d}. {field:<30}: {value}")

        if len(raw_fields) > 10:
            print(f"   ... 还有 {len(raw_fields) - 10} 个字段")

    # 统计所有记录的字段
    all_fields = set()
    for indicator in result.data:
        if indicator.raw_data:
            all_fields.update(indicator.raw_data.keys())

    print(f"\n📋 所有记录的字段统计:")
    print(f"   唯一字段数: {len(all_fields)} 个")
    print(f"   完整字段列表: {sorted(list(all_fields))}")

    return {
        'stock_name': stock_name,
        'symbol': symbol,
        'total_records': len(result.data),
        'raw_fields_count': len(raw_fields) if latest_indicator.raw_data else 0,
        'unique_fields_count': len(all_fields),
        'currency': latest_indicator.currency,
        'latest_raw_data': latest_indicator.raw_data,
        'all_fields': sorted(list(all_fields))
    }


def demo_raw_data_access():
    """演示原始数据访问功能"""
    print("=" * 80)
    print("🚀 财务指标查询系统 - 简化版原始数据访问演示")
    print("=" * 80)
    print("特点:")
    print("✓ 直接返回akshare原始数据，不进行字段映射")
    print("✓ 通过FinancialIndicator.raw_data访问所有原始字段")
    print("✓ 简化的架构，易于理解和维护")
    print("✓ 保持依赖注入和Protocol接口的优雅设计")
    print("=" * 80)

    # 创建简化版查询服务
    service = create_production_service()

    # 测试股票列表
    test_stocks = [
        ("招商银行", "600036"),
        ("腾讯控股", "00700"),
        ("苹果", "AAPL")
    ]

    results_summary = []

    for i, (stock_name, symbol) in enumerate(test_stocks, 1):
        print(f"\n{'='*20} 第{i}个查询: {stock_name} {'='*20}")
        print(f"开始查询 {stock_name} ({symbol}) 的原始数据...")

        start_time = time.time()
        try:
            # 计算三年前的日期
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3*365)  # 大约3年前

            print(f"📅 查询时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

            result = service.query(symbol, start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
            query_time = time.time() - start_time

            print(f"⏱️ 查询耗时: {query_time:.2f} 秒")

            summary = analyze_raw_data_result(result, stock_name, symbol)
            if summary:
                summary['query_time'] = query_time
                results_summary.append(summary)

        except Exception as e:
            print(f"❌ 查询过程中发生异常: {str(e)}")
            print(f"⏱️ 异常耗时: {time.time() - start_time:.2f} 秒")

    return results_summary


def print_simplified_summary_report(results_summary):
    """打印简化版汇总报告"""
    print("\n" + "=" * 80)
    print("📊 简化版原始数据访问汇总报告")
    print("=" * 80)

    if not results_summary:
        print("❌ 没有成功的查询结果")
        return

    total_stocks = len(results_summary)
    total_records = sum(r['total_records'] for r in results_summary)
    total_time = sum(r['query_time'] for r in results_summary)
    all_fields = set()
    for r in results_summary:
        all_fields.update(r['all_fields'])

    print(f"🔍 查询统计:")
    print(f"   查询时间范围: 最近3年财务数据")
    print(f"   成功查询股票数: {total_stocks}")
    print(f"   总记录数: {total_records}")
    print(f"   总查询时间: {total_time:.2f} 秒")
    print(f"   平均查询时间: {total_time/total_stocks:.2f} 秒/股")
    print(f"   总原始字段数: {len(all_fields)} 个")

    print(f"\n📈 各股票详情:")
    for result in results_summary:
        print(f"   {result['stock_name']} ({result['symbol']}):")
        print(f"     记录数: {result['total_records']}, 原始字段数: {result['raw_fields_count']}")
        print(f"     货币: {result['currency']}, 耗时: {result['query_time']:.2f}秒")

    print(f"\n💡 简化版优势:")
    print(f"   ✓ 用户可以访问所有akshare原始字段（{len(all_fields)}个字段）")
    print(f"   ✓ 没有字段映射限制，100%字段覆盖率")
    print(f"   ✓ 简化的架构，更易理解和维护")
    print(f"   ✓ 保留了依赖注入和Protocol接口的优秀设计")
    print(f"   ✓ 未来可以根据需要选择性添加字段映射功能")


def demo_field_access_examples():
    """演示字段访问示例"""
    print("\n\n" + "=" * 80)
    print("🔧 原始数据访问示例")
    print("=" * 80)

    service = create_production_service()

    # 获取一个股票的详细数据
    print("获取招商银行原始数据示例...")
    result = service.query("600036")

    if result.success and result.data:
        latest = result.data[0]

        print(f"\n📋 通过 raw_data 访问原始字段:")
        if latest.raw_data:
            # 显示一些常见的财务指标字段
            common_fields = [
                "摊薄每股收益(元)", "净资产收益率(%)", "销售毛利率(%)",
                "资产负债率(%)", "流动比率", "净利润"
            ]

            print("常见财务指标字段:")
            for field in common_fields:
                if field in latest.raw_data:
                    value = latest.raw_data[field]
                    print(f"  {field:<25}: {value}")
                else:
                    print(f"  {field:<25}: (字段不存在)")

            print(f"\n🔍 所有可用字段 ({len(latest.raw_data)}个):")
            for i, field in enumerate(latest.raw_data.keys(), 1):
                print(f"  {i:2d}. {field}")

        print(f"\n💡 使用建议:")
        print(f"   1. 通过 latest.raw_data[field_name] 访问任意原始字段")
        print(f"   2. 使用 list(latest.raw_data.keys()) 查看所有可用字段")
        print(f"   3. 根据实际需要选择性地使用字段")
        print(f"   4. 不同市场的字段名不同，需要分别处理")


def main():
    """主演示函数"""
    try:
        print("🚀 开始简化版原始数据访问演示...")

        # 执行原始数据访问演示
        results_summary = demo_raw_data_access()

        # 打印汇总报告
        print_simplified_summary_report(results_summary)

        # 字段访问示例
        demo_field_access_examples()

        print("\n" + "=" * 80)
        print("✅ 简化版原始数据访问演示完成！")
        print("\n🏆 简化版特性:")
        print("✓ 直接原始数据访问 - 100%字段覆盖率")
        print("✓ 简化架构设计 - 易于理解和维护")
        print("✓ 保留优秀设计模式 - 依赖注入 + Protocol接口")
        print("✓ 灵活的数据访问 - 用户自主选择需要的字段")
        print("✓ 为未来扩展留有空间 - 可选择性添加字段映射")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())