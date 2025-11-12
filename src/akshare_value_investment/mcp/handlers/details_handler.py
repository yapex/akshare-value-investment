"""
字段详情工具处理器

专门处理 get_field_details 工具的请求。
负责字段信息查询和详细展示。
"""

from typing import Dict, Any
from mcp.types import CallToolResult

from .base_handler import BaseHandler


class DetailsHandler(BaseHandler):
    """字段详情工具处理器"""

    def get_tool_name(self) -> str:
        """获取工具名称"""
        return "get_field_details"

    def get_tool_description(self) -> str:
        """获取工具描述"""
        return "📋 获取财务指标详细信息"

    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具输入模式"""
        return {
            "type": "object",
            "properties": {
                "field_name": {
                    "type": "string",
                    "description": "字段名，例如：'净利润'、'BASIC_EPS'、'ROE'、'毛利率'"
                }
            },
            "required": ["field_name"]
        }

    async def handle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        处理字段详细信息请求

        Args:
            arguments: 工具参数

        Returns:
            字段详情结果
        """
        try:
            field_name = arguments.get("field_name", "")
            if not field_name:
                return self.format_error_response("字段名不能为空")

            # 委托给财务查询服务的字段信息方法
            field_info = self.financial_service.get_field_info(field_name)

            # 格式化响应
            response_text = self.formatter.format_field_details_response(
                field_name=field_name,
                field_info=field_info
            )

            return self.format_success_response(response_text)

        except Exception as e:
            return self.format_error_response(f"获取字段详情失败: {str(e)}")