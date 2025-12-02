"""
MCP服务器启动入口

提供命令行启动MCP服务器的功能。
"""

import asyncio
import argparse
import sys
import json
from typing import Dict, Any

from .server import create_server
from .config import MCPServerConfig


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AKShare价值投资分析系统 MCP服务器")

    parser.add_argument(
        "--host",
        default="localhost",
        help="服务器主机地址 (默认: localhost)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="服务器端口 (默认: 8080)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="显示服务器信息和可用工具"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="运行测试模式"
    )

    parser.add_argument(
        "--stdio",
        action="store_true",
        help="启用stdio模式（用于MCP协议通信）"
    )

    args = parser.parse_args()

    # 创建服务器配置
    config = MCPServerConfig(
        host=args.host,
        port=args.port,
        debug=args.debug,
        log_level="DEBUG" if args.debug else "INFO"
    )

    # 创建服务器实例
    server = create_server(config)

    # 如果只是显示信息
    if args.info:
        tools_info = server.get_tools_info()
        print(json.dumps(tools_info, indent=2, ensure_ascii=False))
        return

    # 如果是测试模式
    if args.test:
        await run_test_mode(server)
        return

    # 如果是stdio模式
    if args.stdio:
        await run_stdio_mode(server)
        return

    # 启动服务器
    print(f"🚀 启动MCP服务器: {config.server_name} v{config.server_version}")
    print(f"📍 监听地址: {config.host}:{config.port}")
    print(f"🛠️  可用工具数量: {len(tool_registry.get_all_tools())}")

    if config.debug:
        print("🐛 调试模式已启用")

    print("\n按 Ctrl+C 停止服务器")

    try:
        # 这里可以添加具体的服务器启动逻辑
        # 例如使用FastAPI、Flask等Web框架
        print("✅ MCP服务器已启动，等待连接...")

        # 简单的命令行交互测试
        await run_interactive_mode(server)

    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)


async def run_interactive_mode(server):
    """运行交互模式用于测试"""
    print("\n=== MCP服务器交互模式 ===")
    print("输入JSON格式的请求，输入'quit'退出")
    print("示例: {\"tool\": \"get_tools_info\", \"parameters\": {}}")

    while True:
        try:
            line = input("\n> ").strip()

            if line.lower() in ('quit', 'exit', 'q'):
                break

            if not line:
                continue

            try:
                request = json.loads(line)

                # 特殊命令：获取工具信息
                if request.get("tool") == "get_tools_info":
                    response = server.get_tools_info()
                else:
                    response = await server.handle_request(request)

                print("\n响应:")
                print(json.dumps(response, indent=2, ensure_ascii=False))

            except json.JSONDecodeError:
                print("❌ JSON格式错误")
            except Exception as e:
                print(f"❌ 处理请求失败: {e}")

        except EOFError:
            break
        except KeyboardInterrupt:
            break

    print("\n👋 退出交互模式")


async def run_stdio_mode(server):
    """运行stdio模式用于MCP协议通信"""
    import sys

    # 启用调试模式时输出到stderr，避免干扰stdio通信
    if server.config.debug:
        print("🚀 启动MCP服务器stdio模式", file=sys.stderr)

    try:
        while True:
            try:
                # 从stdin读取一行JSON-RPC请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break  # EOF

                line = line.strip()
                if not line:
                    continue

                # 解析JSON-RPC请求
                try:
                    request = json.loads(line)

                    # 处理标准MCP协议请求
                    response = await handle_mcp_request(server, request)

                    # 输出JSON-RPC响应到stdout
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False))
                    sys.stdout.flush()

                except Exception as e:
                    request_id = request.get("id") if 'request' in locals() else None
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False))
                    sys.stdout.flush()

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    except Exception as e:
        if server.config.debug:
            print(f"❌ stdio模式错误: {e}", file=sys.stderr)
        sys.exit(1)


async def handle_mcp_request(server, request):
    """处理标准MCP协议请求"""
    jsonrpc_version = request.get("jsonrpc", "2.0")
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    # 构建基本响应结构
    response = {
        "jsonrpc": jsonrpc_version,
        "id": request_id
    }

    try:
        # 处理initialize请求
        if method == "initialize":
            response["result"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "akshare-value-investment-mcp",
                    "version": "1.0.0"
                }
            }

        # 处理tools/list请求
        elif method == "tools/list":
            tools_info = server.get_tools_info()
            mcp_tools = []

            for tool_name, tool_info in tools_info["tools"].items():
                mcp_tool = {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "inputSchema": tool_info["schema"]
                }
                mcp_tools.append(mcp_tool)

            response["result"] = {
                "tools": mcp_tools
            }

        # 处理tools/call请求
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # 转换为我们的内部请求格式
            internal_request = {
                "tool": tool_name,
                "parameters": arguments,
                "id": str(request_id)
            }

            # 调用内部处理逻辑
            internal_response = await server.handle_request(internal_request)

            if internal_response.get("success"):
                # 现在DataFrame已经在MCPResponse中使用pandas.to_json()处理过了
                # 直接序列化整个响应即可
                response_text = json.dumps(internal_response["result"], ensure_ascii=False, indent=2)

                response["result"] = {
                    "content": [
                        {
                            "type": "text",
                            "text": response_text
                        }
                    ]
                }
            else:
                response["error"] = {
                    "code": -32603,
                    "message": internal_response.get("error", {}).get("message", "Tool execution failed")
                }

        # 处理其他请求
        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}"
            }

    except Exception as e:
        response["error"] = {
            "code": -32603,
            "message": f"Internal error: {str(e)}"
        }

    return response


async def run_test_mode(server):
    """运行测试模式"""
    print("\n=== MCP服务器测试模式 ===")

    # 测试用例
    test_cases = [
        {
            "name": "获取工具信息",
            "request": {
                "tool": "get_tools_info",
                "parameters": {}
            }
        },
        {
            "name": "获取A股财务指标可用字段",
            "request": {
                "tool": "get_available_fields",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators"
                }
            }
        },
        {
            "name": "查询A股财务指标（示例）",
            "request": {
                "tool": "query_financial_data",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators",
                    "symbol": "600519",
                    "fields": ["报告期", "净利润"],
                    "frequency": "annual"
                }
            }
        }
    ]

    passed = 0
    failed = 0

    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['name']}")

        try:
            if test_case["request"]["tool"] == "get_tools_info":
                response = server.get_tools_info()
            else:
                response = await server.handle_request(test_case["request"])

            success = response.get("success", True)

            if success:
                print(f"✅ 通过")
                passed += 1
            else:
                print(f"❌ 失败: {response.get('error', {}).get('message', '未知错误')}")
                failed += 1

        except Exception as e:
            print(f"❌ 异常: {e}")
            failed += 1

    print(f"\n📊 测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败")


if __name__ == "__main__":
    # 需要导入tool_registry用于测试
    from .config import tool_registry

    asyncio.run(main())