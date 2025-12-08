#!/usr/bin/env python3
"""
AKShare Value Investment MCP 服务器

提供基于 MCP (Model Context Protocol) 的财务数据查询服务。
该服务器通过 HTTP 调用 FastAPI 服务来获取财务数据。

## 🚀 启动方式

1. 命令行启动:
   ```bash
   akshare-mcp-server
   ```

2. 环境变量配置:
   ```bash
   export AKSHARE_MCP_HOST=0.0.0.0
   export AKSHARE_MCP_PORT=8080
   export AKSHARE_FASTAPI_URL=http://localhost:8000
   akshare-mcp-server
   ```

3. 使用 poe 任务:
   ```bash
   poe mcp
   ```
"""

import asyncio
import logging
import os
import sys
import argparse
from pathlib import Path

from .mcp.config import MCPServerConfig, setup_logging
from .mcp.server import MCPServer


def create_mcp_server_from_env() -> MCPServer:
    """
    从环境变量创建 MCP 服务器配置

    Returns:
        MCPServer: 配置好的 MCP 服务器实例
    """
    # 从环境变量获取配置
    fastapi_url = os.getenv("AKSHARE_FASTAPI_URL", "http://localhost:8000")
    mcp_host = os.getenv("AKSHARE_MCP_HOST", "localhost")
    mcp_port = int(os.getenv("AKSHARE_MCP_PORT", "8080"))
    debug = os.getenv("AKSHARE_MCP_DEBUG", "false").lower() == "true"

    # 创建配置
    config = MCPServerConfig(
        host=mcp_host,
        port=mcp_port,
        fastapi_base_url=fastapi_url,
        debug=debug,
        log_level="DEBUG" if debug else "INFO"
    )

    # 创建服务器
    return MCPServer(config)


def main():
    """MCP 服务器主入口"""
    parser = argparse.ArgumentParser(
        description="AKShare Value Investment MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量配置:
  AKSHARE_FASTAPI_URL     FastAPI 服务地址 (默认: http://localhost:8000)
  AKSHARE_MCP_HOST        MCP 服务器监听地址 (默认: localhost)
  AKSHARE_MCP_PORT        MCP 服务器监听端口 (默认: 8080)
  AKSHARE_MCP_DEBUG       启用调试模式 (默认: false)

示例:
  akshare-mcp-server                                    # 使用默认配置
  AKSHARE_MCP_PORT=9000 akshare-mcp-server             # 自定义端口
  akshare-mcp-server --host 0.0.0.0 --port 8080       # 命令行参数
  akshare-mcp-server --debug                           # 调试模式
        """
    )

    parser.add_argument(
        "--host",
        default=None,
        help="MCP 服务器监听地址 (覆盖环境变量 AKSHARE_MCP_HOST)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="MCP 服务器监听端口 (覆盖环境变量 AKSHARE_MCP_PORT)"
    )

    parser.add_argument(
        "--fastapi-url",
        default=None,
        help="FastAPI 服务地址 (覆盖环境变量 AKSHARE_FASTAPI_URL)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    try:
        # 创建服务器配置
        config = MCPServerConfig(
            host=args.host or os.getenv("AKSHARE_MCP_HOST", "localhost"),
            port=args.port or int(os.getenv("AKSHARE_MCP_PORT", "8080")),
            fastapi_base_url=args.fastapi_url or os.getenv("AKSHARE_FASTAPI_URL", "http://localhost:8000"),
            debug=args.debug or os.getenv("AKSHARE_MCP_DEBUG", "false").lower() == "true",
            log_level="DEBUG" if (args.debug or os.getenv("AKSHARE_MCP_DEBUG", "false").lower() == "true") else "INFO"
        )

        # 设置日志
        setup_logging(config)

        # 创建并启动服务器
        server = MCPServer(config)

        print(f"🚀 启动 AKShare Value Investment MCP 服务器")
        print(f"📡 监听地址: {config.host}:{config.port}")
        print(f"🔗 FastAPI 服务: {config.fastapi_base_url}")
        print(f"🐛 调试模式: {'开启' if config.debug else '关闭'}")
        print(f"📋 服务器名称: {config.server_name}")
        print(f"📖 版本: {config.server_version}")
        print("=" * 50)

        # 启动服务器
        asyncio.run(server.start())

    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        if args.debug or os.getenv("AKSHARE_MCP_DEBUG", "false").lower() == "true":
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()