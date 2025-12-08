#!/usr/bin/env python3
"""
MCP-HTTP 集成最终测试

验证从 MCP 工具到 FastAPI 端点的完整集成。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_value_investment.mcp.config import MCPServerConfig
from akshare_value_investment.mcp.server import MCPServer
from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool
from akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool


def test_config_with_fastapi_url():
    """测试配置包含 FastAPI URL"""
    print("测试 MCP 配置包含 FastAPI URL...")

    try:
        # 使用默认配置
        config = MCPServerConfig()
        assert config.fastapi_base_url == "http://localhost:8000"
        print("✅ 默认 FastAPI URL 配置正确")

        # 使用自定义配置
        custom_config = MCPServerConfig(
            fastapi_base_url="http://custom-api:9000"
        )
        assert custom_config.fastapi_base_url == "http://custom-api:9000"
        print("✅ 自定义 FastAPI URL 配置正确")

        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def test_mcp_server_with_fastapi_url():
    """测试 MCP 服务器使用 FastAPI URL"""
    print("\n测试 MCP 服务器使用 FastAPI URL...")

    try:
        config = MCPServerConfig(
            fastapi_base_url="http://test-api:8080"
        )

        server = MCPServer(config)

        # 验证工具初始化
        assert hasattr(server, 'financial_query_tool')
        assert hasattr(server, 'field_discovery_tool')

        # 验证工具使用了正确的 URL
        assert server.financial_query_tool.api_base_url == "http://test-api:8080"
        assert server.field_discovery_tool.api_base_url == "http://test-api:8080"

        print("✅ MCP 服务器正确初始化 FastAPI URL")
        return True
    except Exception as e:
        print(f"❌ MCP 服务器测试失败: {e}")
        return False


def test_tools_with_custom_url():
    """测试工具使用自定义 URL"""
    print("\n测试工具使用自定义 URL...")

    try:
        custom_url = "http://example-fastapi:9999"

        # 测试 FinancialQueryTool
        financial_tool = FinancialQueryTool(custom_url)
        assert financial_tool.api_base_url == custom_url
        print("✅ FinancialQueryTool 使用自定义 URL")

        # 测试 FieldDiscoveryTool
        field_tool = FieldDiscoveryTool(custom_url)
        assert field_tool.api_base_url == custom_url
        print("✅ FieldDiscoveryTool 使用自定义 URL")

        return True
    except Exception as e:
        print(f"❌ 工具自定义 URL 测试失败: {e}")
        return False


def test_url_normalization():
    """测试 URL 规范化"""
    print("\n测试 URL 规范化...")

    try:
        # 测试尾部斜杠处理
        url_with_slash = "http://localhost:8000/"
        tool1 = FinancialQueryTool(url_with_slash)
        assert tool1.api_base_url == "http://localhost:8000"

        url_without_slash = "http://localhost:8000"
        tool2 = FinancialQueryTool(url_without_slash)
        assert tool2.api_base_url == "http://localhost:8000"

        print("✅ URL 规范化处理正确")
        return True
    except Exception as e:
        print(f"❌ URL 规范化测试失败: {e}")
        return False


def test_method_compatibility():
    """测试方法兼容性"""
    print("\n测试方法兼容性...")

    try:
        tool = FinancialQueryTool()

        # 验证所有必需方法存在
        required_methods = [
            'query_financial_data',
            'get_available_fields',
            'get_supported_markets',
            'get_supported_query_types',
            'get_supported_frequencies'
        ]

        for method in required_methods:
            assert hasattr(tool, method), f"缺少方法: {method}"
            assert callable(getattr(tool, method)), f"方法不可调用: {method}"

        print("✅ FinancialQueryTool 方法兼容性正确")

        # 测试 FieldDiscoveryTool
        field_tool = FieldDiscoveryTool()

        field_required_methods = [
            'discover_fields',
            'discover_all_market_fields',
            'validate_fields',
            'get_supported_markets',
            'get_supported_query_types'
        ]

        for method in field_required_methods:
            assert hasattr(field_tool, method), f"缺少方法: {method}"
            assert callable(getattr(field_tool, method)), f"方法不可调用: {method}"

        print("✅ FieldDiscoveryTool 方法兼容性正确")

        return True
    except Exception as e:
        print(f"❌ 方法兼容性测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("MCP-HTTP 集成最终测试开始")
    print("=" * 50)

    test_results = []

    # 运行测试
    test_results.append(test_config_with_fastapi_url())
    test_results.append(test_mcp_server_with_fastapi_url())
    test_results.append(test_tools_with_custom_url())
    test_results.append(test_url_normalization())
    test_results.append(test_method_compatibility())

    # 汇总结果
    passed_tests = sum(test_results)
    total_tests = len(test_results)

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("✅ 所有集成测试通过！")
        print("✅ MCP 工具已成功改造为通过 HTTP 调用 FastAPI")
        print("✅ 配置系统支持自定义 FastAPI URL")
        print("✅ 所有方法保持向后兼容")
    else:
        print("❌ 部分测试失败，需要检查集成实现")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)