"""
MCP工具处理器基类

定义所有工具处理器的通用接口和行为。
提供统一的错误处理和响应格式化。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from mcp.types import CallToolResult, TextContent

from ..formatters import ResponseFormatter


class BaseHandler(ABC):
    """MCP工具处理器基类"""

    def __init__(self, financial_service, field_discovery_service):
        """
        初始化处理器

        Args:
            financial_service: 财务指标查询服务
            field_discovery_service: 字段发现服务
        """
        self.financial_service = financial_service
        self.field_discovery_service = field_discovery_service
        self.formatter = ResponseFormatter()

    @abstractmethod
    def get_tool_name(self) -> str:
        """获取工具名称"""
        ...

    @abstractmethod
    def get_tool_description(self) -> str:
        """获取工具描述"""
        ...

    @abstractmethod
    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具输入模式"""
        ...

    @abstractmethod
    async def handle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理工具调用"""
        ...

    def format_error_response(self, error_message: str) -> CallToolResult:
        """
        格式化错误响应

        Args:
            error_message: 错误消息

        Returns:
            格式化的错误响应
        """
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ 错误: {error_message}"
            )],
            isError=False
        )

    def format_success_response(self, content: str) -> CallToolResult:
        """
        格式化成功响应

        Args:
            content: 响应内容

        Returns:
            格式化的成功响应
        """
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=content
            )],
            isError=False
        )