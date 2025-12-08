#!/usr/bin/env python3
"""
MCP 查询功能测试

测试当前环境中 MCP 工具是否可以正常进行财务数据查询。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mcp_financial_query():
    """测试 MCP 财务查询功能"""
    print("🧪 测试 MCP 财务查询功能")
    print("=" * 40)

    try:
        from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool

        # 创建工具实例
        tool = FinancialQueryTool()
        print(f"✅ MCP 工具创建成功，FastAPI URL: {tool.api_base_url}")

        # 测试 1: 查询 A 股财务指标字段
        print("\n📋 测试 1: 查询 A 股财务指标可用字段")
        response = tool.get_available_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        if response.get("success"):
            field_count = response.get("field_count", 0)
            print(f"✅ 字段查询成功，共 {field_count} 个字段")
            if field_count > 0:
                fields = response.get("available_fields", [])
                print(f"   示例字段: {fields[:5]}")
        else:
            print(f"❌ 字段查询失败: {response.get('error', {}).get('message', '未知错误')}")
            return False

        # 测试 2: 查询财务数据
        print("\n📊 测试 2: 查询财务数据")
        response = tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="SH600519",
            fields=["报告期", "净利润"],
            start_date="2023-01-01",
            end_date="2023-12-31",
            frequency="annual"
        )

        if response.get("success"):
            data = response.get("data", {})
            records = data.get("records", [])
            print(f"✅ 财务数据查询成功，共 {len(records)} 条记录")
            if records:
                print(f"   示例数据: {records[0]}")
        else:
            print(f"❌ 财务数据查询失败: {response.get('error', {}).get('message', '未知错误')}")
            return False

        return True

    except Exception as e:
        print(f"❌ MCP 查询测试失败: {e}")
        return False


def test_field_discovery_tool():
    """测试字段发现工具"""
    print("\n🧪 测试字段发现工具")
    print("=" * 40)

    try:
        from akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool

        # 创建工具实例
        tool = FieldDiscoveryTool()
        print(f"✅ 字段发现工具创建成功，FastAPI URL: {tool.api_base_url}")

        # 测试字段发现
        response = tool.discover_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        if response.get("success"):
            field_count = response.get("field_count", 0)
            print(f"✅ 字段发现成功，共 {field_count} 个字段")
        else:
            print(f"❌ 字段发现失败: {response.get('error', {}).get('message', '未知错误')}")
            return False

        return True

    except Exception as e:
        print(f"❌ 字段发现测试失败: {e}")
        return False


def test_mcp_server_integration():
    """测试 MCP 服务器集成"""
    print("\n🧪 测试 MCP 服务器集成")
    print("=" * 40)

    try:
        from akshare_value_investment.mcp.server import MCPServer
        from akshare_value_investment.mcp.config import MCPServerConfig

        # 创建配置
        config = MCPServerConfig(
            fastapi_base_url="http://localhost:8000"
        )

        # 创建服务器
        server = MCPServer(config)
        print(f"✅ MCP 服务器创建成功")
        print(f"   FastAPI URL: {server.financial_query_tool.api_base_url}")

        # 测试工具初始化
        tools_ok = hasattr(server, 'financial_query_tool') and hasattr(server, 'field_discovery_tool')
        print(f"✅ 工具初始化: {'成功' if tools_ok else '失败'}")

        return tools_ok

    except Exception as e:
        print(f"❌ MCP 服务器集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 MCP 查询功能测试开始")
    print("=" * 50)

    # 测试结果
    test_results = []

    # 执行测试
    test_results.append(test_mcp_financial_query())
    test_results.append(test_field_discovery_tool())
    test_results.append(test_mcp_server_integration())

    # 汇总结果
    passed_tests = sum(test_results)
    total_tests = len(test_results)

    print("\n" + "=" * 50)
    print("🎯 测试结果汇总:")
    print(f"   总测试数: {total_tests}")
    print(f"   通过测试: {passed_tests}")
    print(f"   失败测试: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！MCP 查询功能可用")
        print("💡 你可以启动 MCP 服务器进行交互式查询:")
        print("   - 使用命令: poe mcp")
        print("   - 或直接在代码中使用 FinancialQueryTool")
    else:
        print("\n❌ 部分测试失败，MCP 查询功能不可用")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)