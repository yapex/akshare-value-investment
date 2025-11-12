"""
财务字段搜索工具处理器

专门处理 search_financial_fields 工具的请求。
负责关键字搜索和结果展示。
"""

from typing import Dict, Any
from mcp.types import CallToolResult

from .base_handler import BaseHandler


class SearchHandler(BaseHandler):
    """财务字段搜索工具处理器"""

    def get_tool_name(self) -> str:
        """获取工具名称"""
        return "search_financial_fields"

    def get_tool_description(self) -> str:
        """获取工具描述"""
        return "🔎 搜索财务指标字段，了解可查询的财务指标"

    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具输入模式"""
        return {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键字，例如：'利润'、'ROE'、'Revenue'、'每股'、'增长'"
                },
                "market": {
                    "type": "string",
                    "description": "市场类型：'a_stock'(A股)、'hk_stock'(港股)、'us_stock'(美股)、'all'(全部，默认)",
                    "default": "all"
                }
            },
            "required": ["keyword"]
        }

    async def handle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        处理财务字段搜索请求

        Args:
            arguments: 工具参数

        Returns:
            搜索结果
        """
        try:
            keyword = arguments.get("keyword", "")
            market = arguments.get("market", "all")

            if not keyword:
                return self.format_error_response("搜索关键字不能为空")

            # 委托给财务查询服务的字段搜索方法
            fields = self.financial_service.search_fields(keyword, market)

            # 格式化响应
            response_text = self.formatter.format_search_response(
                keyword=keyword,
                market=market,
                fields=fields
            )

            return self.format_success_response(response_text)

        except Exception as e:
            return self.format_error_response(f"字段搜索失败: {str(e)}")