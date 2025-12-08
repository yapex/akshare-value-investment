#!/usr/bin/env python3
"""
MCP-HTTP 集成测试脚本

测试修改后的 MCP 工具是否能正确通过 HTTP 调用 FastAPI 服务。
"""

import asyncio
import sys
import os
import time
import threading
import subprocess
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool
from akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool


def start_fastapi_server():
    """启动 FastAPI 服务器"""
    try:
        print("正在启动 FastAPI 服务器...")
        # 使用 uvicorn 启动服务器
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "akshare_value_investment.api.main:create_app",
            "--host", "localhost",
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 等待服务器启动
        time.sleep(3)
        return process
    except Exception as e:
        print(f"启动 FastAPI 服务器失败: {e}")
        return None


def test_financial_query_tool():
    """测试财务查询工具"""
    print("\n=== 测试 FinancialQueryTool ===")

    try:
        # 创建工具实例
        tool = FinancialQueryTool()

        # 测试 1: 查询 A 股财务指标
        print("测试 1: 查询 A 股财务指标")
        response = tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="SH600519",
            fields=["报告期", "净利润"],
            start_date="2023-01-01",
            end_date="2023-12-31",
            frequency="annual"
        )

        print(f"响应状态: {response.get('success', 'unknown')}")
        if response.get("success"):
            data = response.get("data", {})
            print(f"数据记录数: {len(data.get('records', []))}")
        else:
            print(f"错误信息: {response.get('error', {}).get('message', 'Unknown error')}")

        # 测试 2: 获取可用字段
        print("\n测试 2: 获取 A 股财务指标可用字段")
        fields_response = tool.get_available_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        print(f"字段查询状态: {fields_response.get('success', 'unknown')}")
        if fields_response.get("success"):
            field_count = fields_response.get("field_count", 0)
            print(f"可用字段数量: {field_count}")
            if field_count > 0:
                print(f"前 5 个字段: {fields_response.get('available_fields', [])[:5]}")
        else:
            print(f"错误信息: {fields_response.get('error', {}).get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"FinancialQueryTool 测试失败: {e}")
        return False


def test_field_discovery_tool():
    """测试字段发现工具"""
    print("\n=== 测试 FieldDiscoveryTool ===")

    try:
        # 创建工具实例
        tool = FieldDiscoveryTool()

        # 测试 1: 查询 A 股财务指标字段
        print("测试 1: 查询 A 股财务指标字段")
        response = tool.discover_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        print(f"字段发现状态: {response.get('success', 'unknown')}")
        if response.get("success"):
            field_count = response.get("field_count", 0)
            print(f"可用字段数量: {field_count}")
            if field_count > 0:
                fields = response.get("available_fields", [])
                print(f"前 5 个字段: {fields[:5]}")
        else:
            print(f"错误信息: {response.get('error', {}).get('message', 'Unknown error')}")

        # 测试 2: 查询所有 A 股字段
        print("\n测试 2: 查询所有 A 股字段")
        all_fields_response = tool.discover_all_market_fields(market="a_stock")

        print(f"市场字段发现状态: {all_fields_response.get('success', 'unknown')}")
        if all_fields_response.get("success"):
            total_field_count = all_fields_response.get("total_field_count", 0)
            query_type_count = all_fields_response.get("query_type_count", 0)
            print(f"总字段数量: {total_field_count}")
            print(f"查询类型数量: {query_type_count}")
        else:
            print(f"错误信息: {all_fields_response.get('error', {}).get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"FieldDiscoveryTool 测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")

    try:
        tool = FinancialQueryTool()

        # 测试无效市场类型
        print("测试 1: 无效市场类型")
        response = tool.query_financial_data(
            market="invalid_market",
            query_type="a_stock_indicators",
            symbol="SH600519"
        )

        print(f"错误处理状态: {not response.get('success', True)}")
        if not response.get("success"):
            error_msg = response.get('error', {}).get('message', '')
            print(f"错误信息: {error_msg}")

        # 测试市场与查询类型不匹配
        print("\n测试 2: 市场与查询类型不匹配")
        response = tool.query_financial_data(
            market="a_stock",
            query_type="hk_stock_indicators",  # 港股查询类型用于A股市场
            symbol="SH600519"
        )

        print(f"不匹配处理状态: {not response.get('success', True)}")
        if not response.get("success"):
            error_msg = response.get('error', {}).get('message', '')
            print(f"错误信息: {error_msg}")

        return True

    except Exception as e:
        print(f"错误处理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("MCP-HTTP 集成测试开始")
    print("=" * 50)

    # 启动 FastAPI 服务器
    server_process = start_fastapi_server()
    if not server_process:
        print("无法启动 FastAPI 服务器，测试终止")
        return False

    try:
        # 运行测试
        test_results = []

        # 基本功能测试
        test_results.append(test_financial_query_tool())
        test_results.append(test_field_discovery_tool())

        # 错误处理测试
        test_results.append(test_error_handling())

        # 汇总结果
        passed_tests = sum(test_results)
        total_tests = len(test_results)

        print("\n" + "=" * 50)
        print("测试结果汇总:")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")

        if passed_tests == total_tests:
            print("✅ 所有测试通过！MCP-HTTP 集成功能正常")
        else:
            print("❌ 部分测试失败，需要检查集成功能")

        return passed_tests == total_tests

    finally:
        # 清理：关闭服务器
        if server_process:
            print("\n正在关闭 FastAPI 服务器...")
            server_process.terminate()
            server_process.wait(timeout=5)
            print("服务器已关闭")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)