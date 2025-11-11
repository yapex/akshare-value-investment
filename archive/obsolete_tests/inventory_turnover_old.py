#!/usr/bin/env python3
"""
查询东鹏饮料存货周转情况的脚本
使用正确的异步API接口
"""

import asyncio
from src.akshare_value_investment import create_production_service

async def query_dongpeng_inventory_turnover():
    """查询东鹏饮料的存货周转情况"""

    # 创建财务查询服务
    financial_service = create_production_service()

    # 东鹏饮料股票代码
    symbol = "600932"

    print(f"🔍 正在查询东鹏饮料({symbol})的存货周转情况...")
    print(f"📅 查询时间范围: 2023-01-01 至 2024-12-31")

    try:
        # 使用正确的异步方法查询存货相关指标
        result = await financial_service.query_indicators(
            symbol=symbol,
            fields=["存货周转率", "存货周转天数", "存货", "营业成本", "周转率", "inventory turnover", "存货周转"],
            prefer_annual=True,
            start_date="2023-01-01",
            end_date="2024-12-31",
            include_metadata=True
        )

        print("📊 查询结果：")
        print(result)

    except Exception as e:
        print(f"❌ 查询过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(query_dongpeng_inventory_turnover())