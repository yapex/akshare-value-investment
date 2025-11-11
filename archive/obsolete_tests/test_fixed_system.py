#!/usr/bin/env python3
"""
测试修复后的系统功能
"""

import asyncio
from src.akshare_value_investment import create_production_service

async def test_dongpeng_inventory_turnover():
    """测试东鹏饮料存货周转查询"""

    # 创建财务查询服务
    financial_service = create_production_service()

    # 东鹏饮料正确股票代码
    symbol = "605499"

    print(f"🔍 测试修复后的系统 - 东鹏饮料({symbol})存货周转查询...")

    try:
        # 测试1: 基础query方法
        print("\n--- 测试1: 基础query方法 ---")
        basic_result = financial_service.query(symbol)
        print(f"✅ 基础查询成功: {type(basic_result)}")
        if hasattr(basic_result, 'success'):
            print(f"   查询状态: {'成功' if basic_result.success else '失败'}")
            print(f"   数据记录数: {len(basic_result.data) if basic_result.data else 0}")

        # 测试2: query_indicators方法
        print("\n--- 测试2: query_indicators方法 ---")
        async_result = await financial_service.query_indicators(
            symbol=symbol,
            fields=["存货周转率", "存货周转天数"],
            prefer_annual=True,
            start_date="2023-01-01",
            end_date="2024-12-31",
            include_metadata=True
        )
        print(f"✅ 异步查询成功")
        print(f"   结果长度: {len(async_result)} 字符")
        print(f"   前200字符: {async_result[:200]}...")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dongpeng_inventory_turnover())