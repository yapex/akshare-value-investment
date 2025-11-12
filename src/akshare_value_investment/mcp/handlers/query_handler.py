"""
财务指标查询工具处理器

专门处理 query_financial_indicators 工具的请求。
负责参数验证、查询执行和结果格式化。
"""

from typing import Dict, Any
from mcp.types import CallToolResult

from .base_handler import BaseHandler


class QueryHandler(BaseHandler):
    """财务指标查询工具处理器"""

    def get_tool_name(self) -> str:
        """获取工具名称"""
        return "query_financial_indicators"

    def get_tool_description(self) -> str:
        """获取工具描述"""
        return "🔍 智能查询股票财务指标，支持自然语言查询跨市场数据（A股、港股、美股）"

    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具输入模式"""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                },
                "query": {
                    "type": "string",
                    "description": "财务指标查询，支持中英文自然语言，例如：'每股收益'、'ROE'、'公司赚了多少钱'、'EPS'、'毛利率'、'Revenue'"
                },
                "prefer_annual": {
                    "type": "boolean",
                    "description": "是否优先返回年度数据",
                    "default": True
                },
                "start_date": {
                    "type": "string",
                    "description": "查询开始日期，格式：YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "查询结束日期，格式：YYYY-MM-DD"
                }
            },
            "required": ["symbol", "query"]
        }

    async def handle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        处理财务指标查询请求

        Args:
            arguments: 工具参数

        Returns:
            查询结果
        """
        try:
            # 验证必要参数
            symbol = arguments.get("symbol", "")
            query = arguments.get("query", "")

            if not symbol:
                return self.format_error_response("股票代码不能为空")
            if not query:
                return self.format_error_response("查询内容不能为空")

            # 提取参数
            prefer_annual = arguments.get("prefer_annual", True)
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")

            # 使用同步查询方法避免异步问题
            result = self._query_financial_indicators_sync(
                symbol=symbol,
                field_query=query,
                prefer_annual=prefer_annual,
                start_date=start_date,
                end_date=end_date
            )

            # 格式化响应
            if result.get("success"):
                data = result.get("data", [])
                response_text = self.formatter.format_query_response(
                    symbol=symbol,
                    query=query,
                    data=data,
                    message=result.get("message")
                )
            else:
                response_text = f"❌ 查询失败: {result.get('message', '未知错误')}"

            return self.format_success_response(response_text)

        except Exception as e:
            return self.format_error_response(f"查询处理失败: {str(e)}")

    def _query_financial_indicators_sync(self, symbol: str, field_query: str, **kwargs) -> Dict[str, Any]:
        """
        同步财务数据查询方法，避免异步调用问题

        Args:
            symbol: 股票代码
            field_query: 字段查询
            **kwargs: 其他查询参数

        Returns:
            查询结果字典
        """
        try:
            # 使用同步的查询服务
            base_result = self.financial_service.query(symbol, **kwargs)

            if not hasattr(base_result, 'success') or not base_result.success:
                return {
                    "success": False,
                    "data": [],
                    "message": "无法获取基础财务数据",
                    "total_records": 0
                }

            # 简单的字段匹配逻辑
            matched_data = []
            query_keywords = field_query.lower().split()

            for indicator in base_result.data:
                if hasattr(indicator, 'raw_data') and indicator.raw_data:
                    # 查找包含关键字的字段
                    matched_fields = {}
                    for field_name, field_value in indicator.raw_data.items():
                        field_name_lower = field_name.lower()

                        # 简单的关键字匹配
                        if (field_query.lower() in field_name_lower or
                            any(keyword in field_name_lower for keyword in query_keywords)):
                            matched_fields[field_name] = field_value

                    if matched_fields:
                        matched_data.append({
                            "symbol": indicator.symbol,
                            "market": indicator.market,
                            "report_date": indicator.report_date,
                            "period_type": indicator.period_type,
                            "raw_data": matched_fields,
                            "metadata": {
                                "field_query": field_query,
                                "matched_field": list(matched_fields.keys()),
                                "resolution_method": "关键字匹配"
                            }
                        })

            return {
                "success": True,
                "data": matched_data,
                "message": f"成功匹配 {len(matched_data)} 条记录",
                "total_records": len(matched_data)
            }

        except Exception as e:
            import traceback
            error_details = f"同步查询内部错误: {type(e).__name__}: {str(e)}\n"
            error_details += f"调用栈:\n{traceback.format_exc()}"
            return {
                "success": False,
                "data": [],
                "message": error_details,
                "total_records": 0
            }