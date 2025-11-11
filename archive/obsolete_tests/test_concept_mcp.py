#!/usr/bin/env python3
"""
测试MCP概念搜索功能
"""

import asyncio
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from akshare_value_investment.mcp_server import AkshareMCPServer


async def test_concept_search():
    """测试概念搜索功能"""
    print("🔧 测试MCP概念搜索功能")
    print("=" * 50)

    # 初始化MCP服务器
    mcp_server = AkshareMCPServer()

    # 测试概念搜索
    test_queries = [
        {"query": "每股收益", "market": None},
        {"query": "ROE", "market": "a_stock"},
        {"query": "毛利率", "market": None},
        {"query": "资产负债率", "market": "hk_stock"},
    ]

    for test_args in test_queries:
        print(f"\n🔍 测试查询: {test_args}")
        result = await mcp_server._search_financial_concepts(test_args)
        print("📋 结果:", result.content[0].text[:200] + "...")

    # 测试配置重载
    print(f"\n🔄 测试配置重载")
    reload_result = await mcp_server._reload_concepts_config({})
    print("📋 结果:", reload_result.content[0].text)


if __name__ == "__main__":
    try:
        asyncio.run(test_concept_search())
        print("\n✅ 概念搜索MCP功能测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()