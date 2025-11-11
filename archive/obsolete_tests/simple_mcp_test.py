#!/usr/bin/env python3
"""
简单的MCP测试
"""

import asyncio
import subprocess
import time

async def test_mcp_server():
    """直接测试MCP服务器是否能正常运行"""
    print("测试MCP服务器启动...")

    try:
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

        # 等待进程初始化
        time.sleep(2)

        # 检查进程状态
        if proc.poll() is None:
            print("✓ 服务器进程仍在运行")

            # 尝试发送简单的JSON-RPC消息
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            message = json.dumps(init_message) + "\n"
            proc.stdin.write(message)
            proc.stdin.flush()

            # 等待响应
            time.sleep(1)

            if proc.poll() is None:
                print("✓ 服务器在接收消息后仍在运行")
                proc.terminate()
                proc.wait()
                print("✓ 服务器正常终止")
                return True
            else:
                stderr = proc.stderr.read()
                print(f"✗ 服务器在处理消息后退出: {stderr}")
                return False
        else:
            stderr = proc.stderr.read()
            print(f"✗ 服务器启动后立即退出: {stderr}")
            return False

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    import json
    result = asyncio.run(test_mcp_server())
    if result:
        print("\n✓ MCP服务器基本功能正常")
    else:
        print("\n✗ MCP服务器存在问题")