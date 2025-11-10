"""
数据模型测试案例

Test Case 1-1: FinancialIndicator创建验证
Test Case 1-2: MarketType枚举验证
Test Case 1-3: QueryResult验证
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any

# 这些类将在步骤3.1中实现
try:
    from akshare_value_investment.models import MarketType, FinancialIndicator, QueryResult, PeriodType
except ImportError:
    pytest.skip("Models not implemented yet", allow_module_level=True)


class TestFinancialIndicator:
    """Test Case 1-1: FinancialIndicator创建验证"""

    def test_financial_indicator_creation_success(self):
        """Test Case 1-1: FinancialIndicator创建验证"""
        # Input: symbol="600519", market=MarketType.A_STOCK, company_name="贵州茅台", indicators={"basic_eps": Decimal("71.12")}
        symbol = "600519"
        market = MarketType.A_STOCK
        company_name = "贵州茅台"
        report_date = datetime(2024, 12, 31)
        period_type = PeriodType.ANNUAL
        currency = "CNY"
        indicators = {
            "basic_eps": Decimal("71.12"),
            "roe": Decimal("36.99"),
        }
        raw_data = {"摊薄每股收益(元)": 71.12, "净资产收益率(%)": 36.99}

        # Expected Output: FinancialIndicator对象，包含所有传入数据，类型正确
        indicator = FinancialIndicator(
            symbol=symbol,
            market=market,
            company_name=company_name,
            report_date=report_date,
            period_type=period_type,
            currency=currency,
            indicators=indicators,
            raw_data=raw_data
        )

        # Validation: 断言对象属性值与输入一致，类型检查通过
        assert indicator.symbol == symbol
        assert indicator.market == market
        assert indicator.company_name == company_name
        assert indicator.report_date == report_date
        assert indicator.period_type == period_type
        assert indicator.currency == currency
        assert indicator.indicators == indicators
        assert indicator.raw_data == raw_data

        # 类型检查
        assert isinstance(indicator.symbol, str)
        assert isinstance(indicator.market, MarketType)
        assert isinstance(indicator.company_name, str)
        assert isinstance(indicator.report_date, datetime)
        assert isinstance(indicator.period_type, PeriodType)
        assert isinstance(indicator.currency, str)
        assert isinstance(indicator.indicators, dict)
        assert all(isinstance(v, Decimal) for v in indicator.indicators.values())


class TestMarketType:
    """Test Case 1-2: MarketType枚举验证"""

    def test_market_type_enum_values(self):
        """Test Case 1-2: MarketType枚举验证"""
        # Input: 字符串值"A_STOCK", "HK_STOCK", "US_STOCK"
        # Expected Output: MarketType枚举值
        assert MarketType.A_STOCK.value == "a_stock"
        assert MarketType.HK_STOCK.value == "hk_stock"
        assert MarketType.US_STOCK.value == "us_stock"

        # Validation: 枚举转换正确，支持所有3个市场类型
        assert len(list(MarketType)) == 3
        assert MarketType.A_STOCK in MarketType
        assert MarketType.HK_STOCK in MarketType
        assert MarketType.US_STOCK in MarketType


class TestQueryResult:
    """Test Case 1-3: QueryResult验证"""

    def test_query_result_creation_success(self):
        """Test Case 1-3: QueryResult验证"""
        # Input: success=True, data=[FinancialIndicator], total_records=1
        success = True
        message = "查询成功"
        total_records = 1

        # 创建测试用的FinancialIndicator
        indicator = FinancialIndicator(
            symbol="600519",
            market=MarketType.A_STOCK,
            company_name="贵州茅台",
            report_date=datetime(2024, 12, 31),
            period_type=PeriodType.ANNUAL,
            currency="CNY",
            indicators={"basic_eps": Decimal("71.12")},
            raw_data={"摊薄每股收益(元)": 71.12}
        )
        data = [indicator]

        # Expected Output: QueryResult对象，包含查询结果和元数据
        result = QueryResult(
            success=success,
            message=message,
            data=data,
            total_records=total_records
        )

        # Validation: 结果状态和数据完整性验证
        assert result.success == success
        assert result.message == message
        assert result.data == data
        assert result.total_records == total_records
        assert len(result.data) == total_records
        assert isinstance(result.data[0], FinancialIndicator)

    def test_query_result_creation_failure(self):
        """测试查询失败情况"""
        # Input: success=False, data=[], message="股票代码无效"
        success = False
        message = "股票代码无效"
        data = []

        result = QueryResult(
            success=success,
            message=message,
            data=data,
            total_records=0
        )

        assert result.success is False
        assert result.message == message
        assert result.data == []
        assert result.total_records == 0


class TestPeriodType:
    """测试PeriodType枚举"""

    def test_period_type_enum_values(self):
        assert PeriodType.ANNUAL.value == "annual"
        assert PeriodType.QUARTERLY.value == "quarterly"
        assert len(list(PeriodType)) == 2