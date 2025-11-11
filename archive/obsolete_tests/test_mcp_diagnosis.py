#!/usr/bin/env python3
"""
MCP服务器诊断脚本
"""

import sys
import asyncio
import json
from pathlib import Path

def test_imports():
    """测试所有必要的导入"""
    print("=== 测试导入 ===")
    try:
        from akshare_value_investment.mcp_server import create_mcp_server, main
        print("✓ MCP服务器导入成功")

        from akshare_value_investment.services import (
            FinancialQueryService,
            ResponseFormatter,
            FieldMapper,
            TimeRangeProcessor,
            DataStructureProcessor,
            FieldDiscoveryService
        )
        print("✓ 所有服务导入成功")

        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_creation():
    """测试服务器创建"""
    print("\n=== 测试服务器创建 ===")
    try:
        from akshare_value_investment.mcp_server import create_mcp_server
        server = create_mcp_server()
        print(f"✓ 服务器创建成功: {server.server.name}")

        # 测试工具列表
        async def get_tools():
            return await server.server.list_tools()

        tools = asyncio.run(get_tools())
        print(f"✓ 工具列表获取成功: {len(tools)} 个工具")

        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")

        return True
    except Exception as e:
        print(f"✗ 服务器创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tool_call():
    """测试工具调用"""
    print("\n=== 测试工具调用 ===")
    try:
        from akshare_value_investment.mcp_server import create_mcp_server
        server = create_mcp_server()

        # 测试字段发现工具
        test_args = {"symbol": "600036", "max_results": 5}
        result = await server._handle_discover_fields(test_args)
        print("✓ 字段发现工具调用成功")
        print(f"  返回内容长度: {len(result.content[0].text)} 字符")

        return True
    except Exception as e:
        print(f"✗ 工具调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stdio_protocol():
    """测试stdio协议"""
    print("\n=== 测试stdio协议 ===")
    try:
        import subprocess
        import time

        # 启动服务器进程
        proc = subprocess.Popen([
            "uv", "run", "python", "-m", "akshare_value_investment.mcp_server"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        print("✓ 服务器进程启动成功")

        # 等待一小段时间
        time.sleep(1)

        # 检查进程是否还在运行
        if proc.poll() is None:
            print("✓ 服务器进程正在运行")
            proc.terminate()
            proc.wait()
            print("✓ 服务器进程已终止")
        else:
            stderr = proc.stderr.read()
            print(f"✗ 服务器进程意外退出: {stderr}")
            return False

        return True
    except Exception as e:
        print(f"✗ stdio协议测试失败: {e}")
        return False

async def main():
    """主诊断函数"""
    print("MCP服务器诊断开始...\n")

    tests = [
        test_imports,
        test_server_creation,
        test_tool_call,
        test_stdio_protocol
    ]

    passed = 0
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()

            if result:
                passed += 1
        except Exception as e:
            print(f"✗ 测试执行异常: {e}")

    print(f"\n=== 诊断结果 ===")
    print(f"通过测试: {passed}/{len(tests)}")

    if passed == len(tests):
        print("✓ 所有测试通过，MCP服务器应该可以正常工作")
        return 0
    else:
        print("✗ 存在问题，需要进一步调试")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))