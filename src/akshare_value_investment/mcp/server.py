"""
重构后的MCP服务器 - 轻量级架构

采用SOLID原则设计，职责单一：
- 只负责MCP协议交互
- 工具处理委托给专门的处理器
- 响应格式化委托给专门的格式化器
"""

from typing import Dict, Any, List
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import CallToolResult, Tool

from .handlers import QueryHandler, SearchHandler, DetailsHandler, FinancialStatementsHandler


class AkshareMCPServer:
    """重构后的akshare财务数据MCP服务器"""

    def __init__(self, financial_service, field_discovery_service):
        """
        初始化MCP服务器

        Args:
            financial_service: 财务指标查询服务
            field_discovery_service: 字段发现服务
        """
        self.server = Server("akshare-value-investment")

        # 初始化工具处理器
        self.query_handler = QueryHandler(financial_service, field_discovery_service)
        self.search_handler = SearchHandler(financial_service, field_discovery_service)
        self.details_handler = DetailsHandler(financial_service, field_discovery_service)
        self.statements_handler = FinancialStatementsHandler(financial_service, field_discovery_service)

        # 处理器映射
        self.handlers = {
            self.query_handler.get_tool_name(): self.query_handler,
            self.search_handler.get_tool_name(): self.search_handler,
            self.details_handler.get_tool_name(): self.details_handler,
            self.statements_handler.get_tool_name(): self.statements_handler,
        }

        self._setup_handlers()

    def _setup_handlers(self):
        """设置MCP处理器 - 只做路由，不包含业务逻辑"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name=self.query_handler.get_tool_name(),
                    description=self.query_handler.get_tool_description(),
                    inputSchema=self.query_handler.get_tool_schema()
                ),
                Tool(
                    name=self.search_handler.get_tool_name(),
                    description=self.search_handler.get_tool_description(),
                    inputSchema=self.search_handler.get_tool_schema()
                ),
                Tool(
                    name=self.details_handler.get_tool_name(),
                    description=self.details_handler.get_tool_description(),
                    inputSchema=self.details_handler.get_tool_schema()
                ),
                Tool(
                    name=self.statements_handler.get_tool_name(),
                    description=self.statements_handler.get_tool_description(),
                    inputSchema=self.statements_handler.get_tool_schema()
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """处理工具调用 - 委托给相应处理器"""
            try:
                handler = self.handlers.get(name)
                if not handler:
                    return self.query_handler.format_error_response(f"未知工具: {name}")

                return await handler.handle(arguments)

            except Exception as e:
                return self.query_handler.format_error_response(f"处理请求时发生错误: {str(e)}")


def create_mcp_server(financial_service, field_discovery_service) -> AkshareMCPServer:
    """
    创建MCP服务器实例

    Args:
        financial_service: 财务指标查询服务
        field_discovery_service: 字段发现服务

    Returns:
        配置好的MCP服务器实例
    """
    return AkshareMCPServer(
        financial_service=financial_service,
        field_discovery_service=field_discovery_service
    )


# 主入口函数
async def main():
    """启动重构后的MCP服务器"""
    # 创建服务实例
    from ..container import create_container
    container = create_container()

    financial_service = container.financial_data_service()  # 修复：使用FinancialDataService
    field_discovery_service = container.field_discovery_service()

    # 创建MCP服务器实例
    mcp_server = create_mcp_server(financial_service, field_discovery_service)

    # 使用stdio传输协议
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="akshare-value-investment",
                server_version="0.3.0",  # 重构版本
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    import sys
    import os

    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 调试信息
    sys.stderr.write(f"🔧 MCP重构版服务器启动中...\n")
    sys.stderr.write(f"📁 当前目录: {current_dir}\n")
    sys.stderr.write(f"📁 项目根目录: {project_root}\n")
    sys.stderr.write(f"🐍 Python路径已添加\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.stderr.write("🛑 MCP服务器已停止\n")
    except Exception as e:
        sys.stderr.write(f"❌ MCP服务器启动失败: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)