#!/usr/bin/env python3
"""
MCP 工具基础测试

测试修改后的 MCP 工具的基本功能，不依赖 FastAPI 服务器运行。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool
from akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool


def test_financial_query_tool_init():
    """测试财务查询工具初始化"""
    print("测试 FinancialQueryTool 初始化...")

    try:
        # 使用默认 URL
        tool = FinancialQueryTool()
        assert tool.api_base_url == "http://localhost:8000"
        assert tool.client is not None
        print("✅ 默认初始化成功")

        # 使用自定义 URL
        tool2 = FinancialQueryTool("http://example.com:8080")
        assert tool2.api_base_url == "http://example.com:8080"
        print("✅ 自定义 URL 初始化成功")

        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def test_field_discovery_tool_init():
    """测试字段发现工具初始化"""
    print("\n测试 FieldDiscoveryTool 初始化...")

    try:
        # 使用默认 URL
        tool = FieldDiscoveryTool()
        assert tool.api_base_url == "http://localhost:8000"
        assert tool.client is not None
        print("✅ 默认初始化成功")

        # 使用自定义 URL
        tool2 = FieldDiscoveryTool("http://custom-api:9000")
        assert tool2.api_base_url == "http://custom-api:9000"
        print("✅ 自定义 URL 初始化成功")

        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def test_method_signatures():
    """测试方法签名完整性"""
    print("\n测试方法签名完整性...")

    try:
        # 测试 FinancialQueryTool 方法
        financial_tool = FinancialQueryTool()

        # 检查必需方法存在
        assert hasattr(financial_tool, 'query_financial_data')
        assert hasattr(financial_tool, 'get_available_fields')
        assert hasattr(financial_tool, '_create_mcp_error')
        print("✅ FinancialQueryTool 方法签名完整")

        # 测试 FieldDiscoveryTool 方法
        field_tool = FieldDiscoveryTool()

        # 检查必需方法存在
        assert hasattr(field_tool, 'discover_fields')
        assert hasattr(field_tool, 'discover_all_market_fields')
        assert hasattr(field_tool, 'validate_fields')
        assert hasattr(field_tool, '_create_mcp_error')
        print("✅ FieldDiscoveryTool 方法签名完整")

        return True
    except Exception as e:
        print(f"❌ 方法签名检查失败: {e}")
        return False


def test_url_construction():
    """测试 URL 构建逻辑"""
    print("\n测试 URL 构建逻辑...")

    try:
        tool = FinancialQueryTool("http://localhost:8000/")

        # 测试 URL 清理
        assert tool.api_base_url == "http://localhost:8000"

        tool2 = FinancialQueryTool("http://localhost:8000/api")
        assert tool2.api_base_url == "http://localhost:8000/api"

        print("✅ URL 构建逻辑正确")
        return True
    except Exception as e:
        print(f"❌ URL 构建测试失败: {e}")
        return False


def test_http_client_setup():
    """测试 HTTP 客户端设置"""
    print("\n测试 HTTP 客户端设置...")

    try:
        tool = FinancialQueryTool()

        # 检查客户端属性
        assert hasattr(tool, 'client')
        # httpx 客户端的 timeout 属性是一个 Timeout 对象或 None
        timeout_obj = tool.client.timeout
        print(f"HTTP 客户端 timeout 类型: {type(timeout_obj)}")
        print("✅ HTTP 客户端设置正确")

        # 测试析构函数
        del tool
        print("✅ 析构函数可调用")

        return True
    except Exception as e:
        print(f"❌ HTTP 客户端设置测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("MCP 工具基础测试开始")
    print("=" * 40)

    test_results = []

    # 运行测试
    test_results.append(test_financial_query_tool_init())
    test_results.append(test_field_discovery_tool_init())
    test_results.append(test_method_signatures())
    test_results.append(test_url_construction())
    test_results.append(test_http_client_setup())

    # 汇总结果
    passed_tests = sum(test_results)
    total_tests = len(test_results)

    print("\n" + "=" * 40)
    print("测试结果汇总:")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("✅ 所有基础测试通过！MCP 工具 HTTP 集成结构正确")
    else:
        print("❌ 部分测试失败，需要检查工具实现")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)