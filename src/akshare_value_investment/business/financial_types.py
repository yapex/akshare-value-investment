"""
财务查询相关类型定义

定义财务查询服务使用的枚举类型，为MCP提供标准化的类型系统。
"""

from enum import Enum
from typing import Dict, Type
from ..core.models import MarketType


class FinancialQueryType(Enum):
    """
    财务查询类型枚举

    定义所有支持的财务数据查询类型，覆盖A股、港股、美股三个市场的
    不同财务数据接口。
    """

    # A股查询类型 (4个接口)
    A_STOCK_INDICATORS = "a_stock_indicators"          # A股财务指标
    A_STOCK_BALANCE_SHEET = "a_stock_balance_sheet"    # A股资产负债表
    A_STOCK_INCOME_STATEMENT = "a_stock_income_statement"  # A股利润表
    A_STOCK_CASH_FLOW = "a_stock_cash_flow"            # A股现金流量表

    # 港股查询类型 (4个接口)
    HK_STOCK_INDICATORS = "hk_stock_indicators"        # 港股财务指标
    HK_STOCK_BALANCE_SHEET = "hk_stock_balance_sheet"  # 港股资产负债表
    HK_STOCK_INCOME_STATEMENT = "hk_stock_income_statement"  # 港股利润表
    HK_STOCK_CASH_FLOW = "hk_stock_cash_flow"          # 港股现金流量表

    # 美股查询类型 (4个接口)
    US_STOCK_INDICATORS = "us_stock_indicators"        # 美股财务指标
    US_STOCK_BALANCE_SHEET = "us_stock_balance_sheet"  # 美股资产负债表
    US_STOCK_INCOME_STATEMENT = "us_stock_income_statement"  # 美股利润表
    US_STOCK_CASH_FLOW = "us_stock_cash_flow"          # 美股现金流量表

    # 财务三表聚合查询类型 (3个接口)
    A_FINANCIAL_STATEMENTS = "a_financial_statements"      # A股财务三表聚合
    HK_FINANCIAL_STATEMENTS = "hk_financial_statements"    # 港股财务三表聚合
    US_FINANCIAL_STATEMENTS = "us_financial_statements"    # 美股财务三表聚合

    @classmethod
    def get_query_types_by_market(cls, market: MarketType) -> list['FinancialQueryType']:
        """
        获取指定市场支持的所有查询类型

        Args:
            market: 市场类型

        Returns:
            该市场支持的查询类型列表
        """
        market_mapping = {
            MarketType.A_STOCK: [
                cls.A_STOCK_INDICATORS,
                cls.A_STOCK_BALANCE_SHEET,
                cls.A_STOCK_INCOME_STATEMENT,
                cls.A_STOCK_CASH_FLOW,
            ],
            MarketType.HK_STOCK: [
                cls.HK_STOCK_INDICATORS,
                cls.HK_STOCK_BALANCE_SHEET,
                cls.HK_STOCK_INCOME_STATEMENT,
                cls.HK_STOCK_CASH_FLOW,
            ],
            MarketType.US_STOCK: [
                cls.US_STOCK_INDICATORS,
                cls.US_STOCK_BALANCE_SHEET,
                cls.US_STOCK_INCOME_STATEMENT,
                cls.US_STOCK_CASH_FLOW,
            ]
        }

        return market_mapping.get(market, [])

    @classmethod
    def get_all_query_types(cls) -> list['FinancialQueryType']:
        """
        获取所有查询类型

        Returns:
            所有查询类型的列表
        """
        return list(cls)

    def get_market(self) -> MarketType:
        """
        获取查询类型对应的市场

        Returns:
            市场类型
        """
        if self.value.startswith("a_stock_") or self.value.startswith("a_financial_"):
            return MarketType.A_STOCK
        elif self.value.startswith("hk_stock_") or self.value.startswith("hk_financial_"):
            return MarketType.HK_STOCK
        elif self.value.startswith("us_stock_") or self.value.startswith("us_financial_"):
            return MarketType.US_STOCK
        else:
            raise ValueError(f"未知的查询类型: {self}")

    def get_display_name(self) -> str:
        """
        获取查询类型的显示名称

        Returns:
            用户友好的显示名称
        """
        display_names = {
            # A股
            FinancialQueryType.A_STOCK_INDICATORS: "A股财务指标",
            FinancialQueryType.A_STOCK_BALANCE_SHEET: "A股资产负债表",
            FinancialQueryType.A_STOCK_INCOME_STATEMENT: "A股利润表",
            FinancialQueryType.A_STOCK_CASH_FLOW: "A股现金流量表",

            # 港股
            FinancialQueryType.HK_STOCK_INDICATORS: "港股财务指标",
            FinancialQueryType.HK_STOCK_BALANCE_SHEET: "港股资产负债表",
            FinancialQueryType.HK_STOCK_INCOME_STATEMENT: "港股利润表",
            FinancialQueryType.HK_STOCK_CASH_FLOW: "港股现金流量表",

            # 美股
            FinancialQueryType.US_STOCK_INDICATORS: "美股财务指标",
            FinancialQueryType.US_STOCK_BALANCE_SHEET: "美股资产负债表",
            FinancialQueryType.US_STOCK_INCOME_STATEMENT: "美股利润表",
            FinancialQueryType.US_STOCK_CASH_FLOW: "美股现金流量表",

            # 财务三表聚合
            FinancialQueryType.A_FINANCIAL_STATEMENTS: "A股财务三表",
            FinancialQueryType.HK_FINANCIAL_STATEMENTS: "港股财务三表",
            FinancialQueryType.US_FINANCIAL_STATEMENTS: "美股财务三表",
        }

        return display_names.get(self, self.value)


class Frequency(Enum):
    """
    时间频率枚举

    定义财务数据的时间聚合频率，支持年度数据和原始报告期数据。
    """

    ANNUAL = "annual"      # 年度数据（每年最后一份报告）
    QUARTERLY = "quarterly"  # 季度数据（原始报告期）

    def get_display_name(self) -> str:
        """
        获取频率的显示名称

        Returns:
            用户友好的显示名称
        """
        display_names = {
            Frequency.ANNUAL: "年度数据",
            Frequency.QUARTERLY: "报告期数据",
        }

        return display_names.get(self, self.value)


class MCPErrorType(Enum):
    """
    MCP错误类型枚举

    定义MCP调用中可能出现的各种错误类型，便于错误处理和调试。
    """

    # 参数错误
    INVALID_SYMBOL = "invalid_symbol"              # 无效的股票代码
    INVALID_MARKET = "invalid_market"              # 无效的市场类型
    INVALID_QUERY_TYPE = "invalid_query_type"      # 无效的查询类型
    INVALID_FIELDS = "invalid_fields"              # 无效的字段列表
    INVALID_DATE_RANGE = "invalid_date_range"      # 无效的日期范围
    INVALID_FREQUENCY = "invalid_frequency"        # 无效的时间频率

    # 数据错误
    DATA_NOT_FOUND = "data_not_found"              # 数据未找到
    FIELD_NOT_FOUND = "field_not_found"            # 字段未找到
    INSUFFICIENT_DATA = "insufficient_data"        # 数据不足

    # 系统错误
    CACHE_ERROR = "cache_error"                    # 缓存错误
    API_ERROR = "api_error"                        # API调用错误
    NETWORK_ERROR = "network_error"                # 网络错误
    INTERNAL_ERROR = "internal_error"              # 内部错误

    def get_display_name(self) -> str:
        """
        获取错误类型的显示名称

        Returns:
            用户友好的显示名称
        """
        display_names = {
            # 参数错误
            MCPErrorType.INVALID_SYMBOL: "无效股票代码",
            MCPErrorType.INVALID_MARKET: "无效市场类型",
            MCPErrorType.INVALID_QUERY_TYPE: "无效查询类型",
            MCPErrorType.INVALID_FIELDS: "无效字段列表",
            MCPErrorType.INVALID_DATE_RANGE: "无效日期范围",
            MCPErrorType.INVALID_FREQUENCY: "无效时间频率",

            # 数据错误
            MCPErrorType.DATA_NOT_FOUND: "数据未找到",
            MCPErrorType.FIELD_NOT_FOUND: "字段未找到",
            MCPErrorType.INSUFFICIENT_DATA: "数据不足",

            # 系统错误
            MCPErrorType.CACHE_ERROR: "缓存错误",
            MCPErrorType.API_ERROR: "API调用错误",
            MCPErrorType.NETWORK_ERROR: "网络错误",
            MCPErrorType.INTERNAL_ERROR: "内部错误",
        }

        return display_names.get(self, self.value)


# 类型别名
QueryType = FinancialQueryType
ErrorType = MCPErrorType