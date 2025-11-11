#!/usr/bin/env python3
"""
查询东鹏饮料存货周转情况的简单脚本
"""

import asyncio
from src.akshare_value_investment import create_production_service

async def query_dongpeng_inventory():
    """查询东鹏饮料的存货周转情况"""

    # 创建查询服务
    service = create_production_service()

    # 东鹏饮料股票代码
    symbol = "600932"

    print(f"🔍 正在查询东鹏饮料({symbol})的财务数据...")

    try:
        # 执行查询
        result = service.query(
            symbol,
            start_date="2023-01-01",
            end_date="2024-12-31"
        )

        if result.success:
            print(f"✅ 查询成功！获取到 {result.total_records} 条记录")
            print("\n📊 财务数据概览：")

            # 遍历所有财务指标数据
            for i, indicator in enumerate(result.data, 1):
                print(f"\n--- 记录 {i} ---")
                print(f"报告日期: {indicator.report_date.strftime('%Y-%m-%d')}")
                print(f"报告期类型: {indicator.period_type.value}")
                print(f"股票代码: {indicator.symbol}")
                print(f"市场类型: {indicator.market_type.value}")

                # 显示原始数据中与存货相关的字段
                raw_data = indicator.raw_data
                inventory_related = {}

                if raw_data and isinstance(raw_data, dict):
                    for key, value in raw_data.items():
                        # 查找与存货周转相关的字段
                        if any(keyword in str(key).lower() for keyword in
                               ['存货', 'inventory', '周转', 'turnover', '营业成本', '成本']):
                            inventory_related[key] = value

                if inventory_related:
                    print("📦 存货相关数据:")
                    for key, value in inventory_related.items():
                        print(f"  {key}: {value}")
                else:
                    print("ℹ️  未找到存货相关字段")

                # 显示所有可用字段（前10个）
                if raw_data and isinstance(raw_data, dict):
                    all_fields = list(raw_data.keys())
                    print(f"📋 可用字段示例 (共{len(all_fields)}个): {all_fields[:10]}")

                print("-" * 50)
        else:
            print(f"❌ 查询失败: {result.message}")

    except Exception as e:
        print(f"❌ 查询过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(query_dongpeng_inventory())