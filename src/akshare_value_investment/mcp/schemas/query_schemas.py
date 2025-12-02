"""
MCP查询请求Schema定义

定义各种MCP工具的请求参数结构和验证规则。
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class MarketTypeSchema(str, Enum):
    """市场类型Schema"""
    A_STOCK = "a_stock"
    HK_STOCK = "hk_stock"
    US_STOCK = "us_stock"


class QueryTypeSchema(str, Enum):
    """查询类型Schema"""
    # A股查询类型
    A_STOCK_INDICATORS = "a_stock_indicators"
    A_STOCK_BALANCE_SHEET = "a_stock_balance_sheet"
    A_STOCK_INCOME_STATEMENT = "a_stock_income_statement"
    A_STOCK_CASH_FLOW = "a_stock_cash_flow"

    # 港股查询类型
    HK_STOCK_INDICATORS = "hk_stock_indicators"
    HK_STOCK_STATEMENTS = "hk_stock_statements"

    # 美股查询类型
    US_STOCK_INDICATORS = "us_stock_indicators"
    US_STOCK_BALANCE_SHEET = "us_stock_balance_sheet"
    US_STOCK_INCOME_STATEMENT = "us_stock_income_statement"
    US_STOCK_CASH_FLOW = "us_stock_cash_flow"


class FrequencySchema(str, Enum):
    """时间频率Schema"""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"


@dataclass
class FinancialQueryRequest:
    """
    财务数据查询请求Schema
    """
    market: MarketTypeSchema
    query_type: QueryTypeSchema
    symbol: str
    fields: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    frequency: FrequencySchema = FrequencySchema.ANNUAL

    def validate(self) -> List[str]:
        """
        验证请求参数

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        # 验证股票代码
        if not self.symbol or not isinstance(self.symbol, str):
            errors.append("股票代码不能为空且必须是字符串")

        # 验证日期格式
        if self.start_date and not self._is_valid_date(self.start_date):
            errors.append("开始日期格式无效，应为YYYY-MM-DD")

        if self.end_date and not self._is_valid_date(self.end_date):
            errors.append("结束日期格式无效，应为YYYY-MM-DD")

        # 验证日期范围
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors.append("开始日期不能晚于结束日期")

        # 验证字段列表
        if self.fields is not None:
            if not isinstance(self.fields, list):
                errors.append("字段列表必须是数组类型")
            elif not all(isinstance(field, str) for field in self.fields):
                errors.append("所有字段名必须是字符串")

        # 验证市场和查询类型的匹配
        if not self._is_valid_market_query_type_combination():
            errors.append(f"市场类型 {self.market.value} 与查询类型 {self.query_type.value} 不匹配")

        return errors

    def _is_valid_date(self, date_str: str) -> bool:
        """验证日期格式是否为YYYY-MM-DD"""
        try:
            from datetime import datetime
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_market_query_type_combination(self) -> bool:
        """验证市场和查询类型的组合是否有效"""
        valid_combinations = {
            MarketTypeSchema.A_STOCK: [
                QueryTypeSchema.A_STOCK_INDICATORS,
                QueryTypeSchema.A_STOCK_BALANCE_SHEET,
                QueryTypeSchema.A_STOCK_INCOME_STATEMENT,
                QueryTypeSchema.A_STOCK_CASH_FLOW
            ],
            MarketTypeSchema.HK_STOCK: [
                QueryTypeSchema.HK_STOCK_INDICATORS,
                QueryTypeSchema.HK_STOCK_STATEMENTS
            ],
            MarketTypeSchema.US_STOCK: [
                QueryTypeSchema.US_STOCK_INDICATORS,
                QueryTypeSchema.US_STOCK_BALANCE_SHEET,
                QueryTypeSchema.US_STOCK_INCOME_STATEMENT,
                QueryTypeSchema.US_STOCK_CASH_FLOW
            ]
        }

        return self.query_type in valid_combinations.get(self.market, [])


@dataclass
class GetAvailableFieldsRequest:
    """
    获取可用字段请求Schema
    """
    market: MarketTypeSchema
    query_type: QueryTypeSchema

    def validate(self) -> List[str]:
        """
        验证请求参数

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        # 验证市场和查询类型的匹配
        query_request = FinancialQueryRequest(
            market=self.market,
            query_type=self.query_type,
            symbol="dummy"  # 股票代码不影响字段查询
        )
        combination_errors = query_request._is_valid_market_query_type_combination()
        if not combination_errors:
            errors.append(f"市场类型 {self.market.value} 与查询类型 {self.query_type.value} 不匹配")

        return errors


@dataclass
class ValidateFieldsRequest:
    """
    字段验证请求Schema
    """
    market: MarketTypeSchema
    query_type: QueryTypeSchema
    fields: List[str]

    def validate(self) -> List[str]:
        """
        验证请求参数

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        # 验证字段列表
        if not self.fields or not isinstance(self.fields, list):
            errors.append("字段列表不能为空且必须是数组类型")
        elif not all(isinstance(field, str) for field in self.fields):
            errors.append("所有字段名必须是字符串")

        # 验证市场和查询类型的匹配
        query_request = FinancialQueryRequest(
            market=self.market,
            query_type=self.query_type,
            symbol="dummy"
        )
        if not query_request._is_valid_market_query_type_combination():
            errors.append(f"市场类型 {self.market.value} 与查询类型 {self.query_type.value} 不匹配")

        return errors


@dataclass
class DiscoverAllMarketFieldsRequest:
    """
    发现市场所有字段请求Schema
    """
    market: MarketTypeSchema

    def validate(self) -> List[str]:
        """
        验证请求参数

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        # 验证市场类型
        if self.market not in MarketTypeSchema:
            errors.append(f"无效的市场类型: {self.market}")

        return errors


# 工具函数：从字典创建Schema对象
def create_financial_query_request(data: Dict[str, Any]) -> FinancialQueryRequest:
    """
    从字典创建财务查询请求对象

    Args:
        data: 包含请求参数的字典

    Returns:
        FinancialQueryRequest对象
    """
    return FinancialQueryRequest(
        market=MarketTypeSchema(data.get("market")),
        query_type=QueryTypeSchema(data.get("query_type")),
        symbol=data.get("symbol", ""),
        fields=data.get("fields"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        frequency=FrequencySchema(data.get("frequency", "annual"))
    )


def create_get_available_fields_request(data: Dict[str, Any]) -> GetAvailableFieldsRequest:
    """
    从字典创建获取可用字段请求对象

    Args:
        data: 包含请求参数的字典

    Returns:
        GetAvailableFieldsRequest对象
    """
    return GetAvailableFieldsRequest(
        market=MarketTypeSchema(data.get("market")),
        query_type=QueryTypeSchema(data.get("query_type"))
    )


def create_validate_fields_request(data: Dict[str, Any]) -> ValidateFieldsRequest:
    """
    从字典创建字段验证请求对象

    Args:
        data: 包含请求参数的字典

    Returns:
        ValidateFieldsRequest对象
    """
    return ValidateFieldsRequest(
        market=MarketTypeSchema(data.get("market")),
        query_type=QueryTypeSchema(data.get("query_type")),
        fields=data.get("fields", [])
    )


def create_discover_all_market_fields_request(data: Dict[str, Any]) -> DiscoverAllMarketFieldsRequest:
    """
    从字典创建发现市场所有字段请求对象

    Args:
        data: 包含请求参数的字典

    Returns:
        DiscoverAllMarketFieldsRequest对象
    """
    return DiscoverAllMarketFieldsRequest(
        market=MarketTypeSchema(data.get("market"))
    )