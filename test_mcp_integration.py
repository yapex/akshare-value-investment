#!/usr/bin/env python3
"""
MCP集成测试脚本

简单测试MCP服务器的核心功能。
"""

import sys
import asyncio
import json

# 确保能找到模块
sys.path.insert(0, 'src')

from akshare_value_investment.mcp.server import MCPServer


async def test_mcp_server():
    """测试MCP服务器功能"""
    print("🧪 开始MCP集成测试...")

    # 创建服务器实例
    server = MCPServer()

    # 测试1: 获取工具信息
    print("\n1️⃣ 测试获取工具信息...")
    request1 = {
        "tool": "get_tools_info",
        "parameters": {}
    }

    response1 = await server.handle_request(request1)

    if response1.get("success"):
        print("✅ 获取工具信息成功")
        tools = response1["result"]["tools"]
        print(f"   已注册工具数量: {len(tools)}")
        for tool_name, tool_info in tools.items():
            print(f"   - {tool_name}: {tool_info['description']}")
    else:
        print(f"❌ 获取工具信息失败: {response1}")
        return

    # 测试2: 获取可用字段
    print("\n2️⃣ 测试获取A股财务指标可用字段...")
    request2 = {
        "tool": "get_available_fields",
        "parameters": {
            "market": "a_stock",
            "query_type": "a_stock_indicators"
        }
    }

    response2 = await server.handle_request(request2)

    if response2.get("success"):
        result = response2["result"]
        if result.get("success"):
            print("✅ 获取可用字段成功")
            fields = result.get("available_fields", [])
            print(f"   可用字段数量: {len(fields)}")
            if fields:
                print(f"   示例字段: {fields[:5]}")
        else:
            print(f"⚠️  字段获取返回错误: {result.get('error', {}).get('message')}")
    else:
        print(f"❌ 获取可用字段失败: {response2}")

    # 测试3: 字段验证
    print("\n3️⃣ 测试字段验证...")
    request3 = {
        "tool": "validate_fields",
        "parameters": {
            "market": "a_stock",
            "query_type": "a_stock_indicators",
            "fields": ["报告期", "净利润", "不存在的字段"]
        }
    }

    response3 = await server.handle_request(request3)

    if response3.get("success"):
        result = response3["result"]
        if result.get("success"):
            print("✅ 字段验证成功")
            validation = result.get("validation_result", {})
            print(f"   有效字段: {validation.get('valid_fields', [])}")
            print(f"   无效字段: {validation.get('invalid_fields', [])}")
        else:
            print(f"⚠️  字段验证返回错误: {result.get('error', {}).get('message')}")
    else:
        print(f"❌ 字段验证失败: {response3}")

    # 测试4: 发现所有市场字段
    print("\n4️⃣ 测试发现所有A股字段...")
    request4 = {
        "tool": "discover_all_market_fields",
        "parameters": {
            "market": "a_stock"
        }
    }

    response4 = await server.handle_request(request4)

    if response4.get("success"):
        result = response4["result"]
        if result.get("success"):
            print("✅ 发现所有字段成功")
            print(f"   查询类型数量: {result.get('query_type_count', 0)}")
            print(f"   总字段数量: {result.get('total_field_count', 0)}")
            all_fields = result.get("all_fields", {})
            for query_type, info in all_fields.items():
                print(f"   {query_type}: {info.get('field_count', 0)}个字段")
        else:
            print(f"⚠️  发现字段返回错误: {result.get('error', {}).get('message')}")
    else:
        print(f"❌ 发现字段失败: {response4}")

    print("\n🎉 MCP集成测试完成！")


def main():
    """主函数"""
    print("AKShare价值投资系统 - MCP服务器集成测试")
    print("=" * 50)

    # 运行异步测试
    asyncio.run(test_mcp_server())


if __name__ == "__main__":
    main()