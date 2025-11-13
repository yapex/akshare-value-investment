"""
财务三表查询工具处理器

专门处理财务三表（资产负债表、利润表、现金流量表）的查询请求。
"""

from typing import Dict, Any
from mcp.types import CallToolResult

from .base_handler import BaseHandler


class FinancialStatementsHandler(BaseHandler):
    """财务三表查询工具处理器"""

    def get_tool_name(self) -> str:
        """获取工具名称"""
        return "query_financial_statements"

    def get_tool_description(self) -> str:
        """获取工具描述"""
        return "📊 查询财务三表数据（资产负债表、利润表、现金流量表），支持三地市场（A股、港股、美股）"

    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具输入模式"""
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                },
                "statement_type": {
                    "type": "string",
                    "description": "财务报表类型",
                    "enum": ["balance_sheet", "income_statement", "cash_flow", "indicators"],
                    "default": "indicators"
                },
                "start_date": {
                    "type": "string",
                    "description": "查询开始日期，格式：YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "查询结束日期，格式：YYYY-MM-DD"
                },
                "prefer_annual": {
                    "type": "boolean",
                    "description": "是否优先返回年度数据",
                    "default": True
                }
            },
            "required": ["symbol", "statement_type"]
        }

    async def handle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """
        处理财务三表查询请求

        Args:
            arguments: 工具参数

        Returns:
            查询结果
        """
        try:
            # 验证必要参数
            symbol = arguments.get("symbol", "")
            statement_type = arguments.get("statement_type", "indicators")

            if not symbol:
                return self.format_error_response("股票代码不能为空")

            # 提取参数
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            prefer_annual = arguments.get("prefer_annual", True)

            # 调用财务数据服务
            result = await self._query_financial_statements(
                symbol=symbol,
                statement_type=statement_type,
                start_date=start_date,
                end_date=end_date,
                prefer_annual=prefer_annual
            )

            # 格式化响应
            if result["success"]:
                response_text = self._format_financial_statements_response(
                    result["data"],
                    symbol,
                    statement_type,
                    result.get("metadata", {})
                )
                return self.format_success_response(response_text)
            else:
                return self.format_error_response(f"查询失败: {result.get('message', '未知错误')}")

        except Exception as e:
            import traceback
            error_details = f"财务三表查询处理失败: {type(e).__name__}: {str(e)}\n调用栈:\n{traceback.format_exc()}"
            return self.format_error_response(error_details)

    async def _query_financial_statements(self, symbol: str, statement_type: str,
                                           **kwargs) -> Dict[str, Any]:
        """
        查询财务三表数据

        Args:
            symbol: 股票代码
            statement_type: 报表类型
            **kwargs: 其他查询参数

        Returns:
            查询结果字典
        """
        try:
            # 识别股票市场
            from ...core.stock_identifier import StockIdentifier
            from ...core.models import MarketType

            stock_identifier = StockIdentifier()
            market, normalized_symbol = stock_identifier.identify(symbol)

            # 现在应该直接接收FinancialDataService
            # 如果仍有问题，说明容器配置有问题

            # 根据报表类型调用相应的查询方法
            if statement_type == "balance_sheet":
                data = self.financial_service.query_balance_sheet(
                    normalized_symbol, market,
                    kwargs.get("start_date"), kwargs.get("end_date")
                )
            elif statement_type == "income_statement":
                data = self.financial_service.query_income_statement(
                    normalized_symbol, market,
                    kwargs.get("start_date"), kwargs.get("end_date")
                )
            elif statement_type == "cash_flow":
                data = self.financial_service.query_cash_flow(
                    normalized_symbol, market,
                    kwargs.get("start_date"), kwargs.get("end_date")
                )
            else:  # indicators
                data = self.financial_service.query_indicators(
                    normalized_symbol, market,
                    kwargs.get("start_date"), kwargs.get("end_date")
                )

            # 处理数据
            processed_data = self._process_financial_data(data, statement_type)

            return {
                "success": True,
                "data": processed_data,
                "metadata": {
                    "symbol": normalized_symbol,
                    "market": market.value,
                    "statement_type": statement_type,
                    "total_records": len(processed_data),
                    "query_params": kwargs
                }
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "data": [],
                "message": f"查询内部错误: {str(e)}\n调用栈:\n{traceback.format_exc()}",
                "metadata": {}
            }

    def _process_financial_data(self, data, statement_type: str) -> list:
        """
        处理财务数据

        Args:
            data: 原始DataFrame数据
            statement_type: 报表类型

        Returns:
            处理后的数据列表
        """
        if data is None or data.empty:
            return []

        processed_records = []

        # 根据数据结构进行处理
        if statement_type in ["balance_sheet", "income_statement", "cash_flow"]:
            # 港股和美股：长表格式，每行一个财务项目
            for _, row in data.iterrows():
                record = {
                    "report_date": self._extract_date(row),
                    "item_name": self._extract_item_name(row),
                    "amount": self._extract_amount(row),
                    "raw_data": row.to_dict()
                }
                processed_records.append(record)
        else:
            # A股：可能需要特殊处理
            for _, row in data.iterrows():
                record = {
                    "report_date": self._extract_date(row),
                    "item_name": self._extract_item_name(row),
                    "amount": self._extract_amount(row),
                    "raw_data": row.to_dict()
                }
                processed_records.append(record)

        return processed_records

    def _extract_date(self, row) -> str:
        """提取报告日期"""
        date_fields = ['REPORT_DATE', 'report_date', '日期', 'DATE', 'date']
        for field in date_fields:
            if field in row and row[field] is not None:
                date_value = row[field]
                if hasattr(date_value, 'strftime'):
                    return date_value.strftime('%Y-%m-%d')
                else:
                    return str(date_value)[:10]  # 取前10位作为日期
        return "未知日期"

    def _extract_item_name(self, row) -> str:
        """提取项目名称"""
        name_fields = ['STD_ITEM_NAME', '指标', 'ITEM_NAME', '项目名称']
        for field in name_fields:
            if field in row and row[field] is not None:
                return str(row[field])
        return "未知项目"

    def _extract_amount(self, row) -> Any:
        """提取金额"""
        amount_fields = ['AMOUNT', 'amount', '金额', '数值', '值']
        for field in amount_fields:
            if field in row and row[field] is not None:
                return row[field]
        return None

    def _format_financial_statements_response(self, data: list, symbol: str,
                                              statement_type: str, metadata: Dict) -> str:
        """
        格式化财务三表查询响应

        Args:
            data: 处理后的数据
            symbol: 股票代码
            statement_type: 报表类型
            metadata: 元数据

        Returns:
            格式化的响应文本
        """
        # 报表类型中文名映射
        type_names = {
            "balance_sheet": "资产负债表",
            "income_statement": "利润表",
            "cash_flow": "现金流量表",
            "indicators": "财务指标"
        }

        type_name = type_names.get(statement_type, "财务报表")

        response_lines = [
            f"## {symbol} - {type_name}",
            f"",
            f"**市场**: {metadata.get('market', '未知')}",
            f"**记录数**: {len(data)}",
            f"**查询时间**: {self._get_current_time()}",
            f""
        ]

        if data:
            response_lines.append("### 📊 主要数据项")
            response_lines.append("")

            # 显示前10条记录
            for i, record in enumerate(data[:10]):
                amount = record["amount"]
                if isinstance(amount, (int, float)):
                    amount_str = f"{amount:,.0f}" if amount > 1000000 else f"{amount:,.2f}"
                else:
                    amount_str = str(amount) if amount is not None else "N/A"

                response_lines.append(f"{i+1:2d}. **{record['item_name']}**: {amount_str}")

            if len(data) > 10:
                response_lines.append(f"... 还有 {len(data) - 10} 条记录")
        else:
            response_lines.append("❌ 未找到数据")

        response_lines.append("")
        response_lines.append("💡 提示：使用原始数据访问可查看完整字段信息")

        return "\n".join(response_lines)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")