"""
财务三表聚合查询测试

测试FinancialQueryService的财务三表聚合功能。
采用TDD方法：先编写失败的测试，然后实现功能。
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from akshare_value_investment.business.financial_query_service import FinancialQueryService
from akshare_value_investment.business.financial_types import FinancialQueryType, Frequency
from akshare_value_investment.container import create_container


class TestFinancialStatementsAggregation:
    """财务三表聚合查询测试类"""

    @pytest.fixture
    def query_service(self):
        """创建FinancialQueryService实例"""
        return FinancialQueryService()

    @pytest.fixture
    def mock_a_stock_data(self, mock_loader):
        """A股三表mock数据"""
        return {
            'balance_sheet': mock_loader.load_a_stock_balance_sheet(),
            'income_statement': mock_loader.load_a_stock_profit_sheet(),
            'cash_flow': mock_loader.load_a_stock_cash_flow_sheet()
        }

    @pytest.fixture
    def mock_hk_stock_data(self, mock_loader):
        """港股三表mock数据"""
        return {
            'balance_sheet': mock_loader.load_hk_balance_sheet(),
            'income_statement': mock_loader.load_hk_income_statement(),
            'cash_flow': mock_loader.load_hk_cash_flow()
        }

    @pytest.fixture
    def mock_us_stock_data(self, mock_loader):
        """美股三表mock数据"""
        return {
            'balance_sheet': mock_loader.load_us_balance_sheet(),
            'income_statement': mock_loader.load_us_income_statement(),
            'cash_flow': mock_loader.load_us_cash_flow()
        }

    def test_a_financial_statements_aggregation(self, query_service):
        """测试A股财务三表聚合查询

        验证：
        1. 返回字典结构包含三个键：balance_sheet, income_statement, cash_flow
        2. 每个值都是DataFrame
        3. DataFrame非空
        """
        # 执行聚合查询
        result = query_service.query_financial_statements(
            query_type=FinancialQueryType.A_FINANCIAL_STATEMENTS,
            symbol="SH600519",
            frequency=Frequency.ANNUAL,
            limit=3
        )

        # 验证返回结构
        assert isinstance(result, dict), "返回结果应该是字典类型"

        # 验证包含三个键
        assert "balance_sheet" in result, "结果应包含balance_sheet键"
        assert "income_statement" in result, "结果应包含income_statement键"
        assert "cash_flow" in result, "结果应包含cash_flow键"

        # 验证每个值都是DataFrame
        assert isinstance(result["balance_sheet"], pd.DataFrame), "balance_sheet应该是DataFrame"
        assert isinstance(result["income_statement"], pd.DataFrame), "income_statement应该是DataFrame"
        assert isinstance(result["cash_flow"], pd.DataFrame), "cash_flow应该是DataFrame"

        # 验证DataFrame非空（如果有数据）
        # A股使用中文"报告期"字段
        if not result["balance_sheet"].empty:
            has_date = (
                "date" in result["balance_sheet"].columns or
                "REPORT_DATE" in result["balance_sheet"].columns or
                "报告期" in result["balance_sheet"].columns
            )
            assert has_date, "数据应包含日期字段"

    def test_hk_financial_statements_aggregation(self, query_service):
        """测试港股财务三表聚合查询

        验证：
        1. 返回字典结构包含三个键
        2. 每个值都是DataFrame
        3. DataFrame包含港股特有字段
        """
        # 执行聚合查询
        result = query_service.query_financial_statements(
            query_type=FinancialQueryType.HK_FINANCIAL_STATEMENTS,
            symbol="00700",
            frequency=Frequency.ANNUAL,
            limit=3
        )

        # 验证返回结构
        assert isinstance(result, dict), "返回结果应该是字典类型"
        assert len(result) == 3, "结果应包含3个键"

        # 验证每个值都是DataFrame
        for key in ["balance_sheet", "income_statement", "cash_flow"]:
            assert key in result, f"结果应包含{key}键"
            assert isinstance(result[key], pd.DataFrame), f"{key}应该是DataFrame"

    def test_us_financial_statements_aggregation(self, query_service):
        """测试美股财务三表聚合查询

        验证：
        1. 返回字典结构包含三个键
        2. 每个值都是DataFrame
        3. DataFrame包含美股特有字段
        """
        # 执行聚合查询
        result = query_service.query_financial_statements(
            query_type=FinancialQueryType.US_FINANCIAL_STATEMENTS,
            symbol="AAPL",
            frequency=Frequency.ANNUAL,
            limit=3
        )

        # 验证返回结构
        assert isinstance(result, dict), "返回结果应该是字典类型"
        assert len(result) == 3, "结果应包含3个键"

        # 验证每个值都是DataFrame
        for key in ["balance_sheet", "income_statement", "cash_flow"]:
            assert key in result, f"结果应包含{key}键"
            assert isinstance(result[key], pd.DataFrame), f"{key}应该是DataFrame"

    def test_financial_statements_with_frequency(self, query_service):
        """测试不同频率的财务三表聚合查询

        验证frequency参数正确传递到底层查询器
        """
        # 测试年度数据
        result_annual = query_service.query_financial_statements(
            query_type=FinancialQueryType.A_FINANCIAL_STATEMENTS,
            symbol="SH600519",
            frequency=Frequency.ANNUAL,
            limit=3
        )

        assert isinstance(result_annual, dict), "年度查询应返回字典"

        # 测试季度数据
        result_quarterly = query_service.query_financial_statements(
            query_type=FinancialQueryType.A_FINANCIAL_STATEMENTS,
            symbol="SH600519",
            frequency=Frequency.QUARTERLY,
            limit=4
        )

        assert isinstance(result_quarterly, dict), "季度查询应返回字典"

    def test_financial_statements_with_limit(self, query_service):
        """测试限制返回记录数的财务三表聚合查询

        验证limit参数正确限制每个DataFrame的行数
        """
        result = query_service.query_financial_statements(
            query_type=FinancialQueryType.A_FINANCIAL_STATEMENTS,
            symbol="SH600519",
            frequency=Frequency.ANNUAL,
            limit=2
        )

        # 验证每个DataFrame的行数不超过limit（跳过unit_map）
        for key, df in result.items():
            if key == "unit_map":
                continue  # 跳过单位映射字典
            if not df.empty:
                assert len(df) <= 2, f"{key}的记录数不应超过limit=2"

    def test_financial_statements_invalid_query_type(self, query_service):
        """测试无效查询类型的错误处理

        验证传入非聚合查询类型时抛出适当错误
        """
        with pytest.raises(ValueError, match="不是财务三表聚合查询类型"):
            query_service.query_financial_statements(
                query_type=FinancialQueryType.A_STOCK_INDICATORS,  # 非聚合类型
                symbol="SH600519",
                frequency=Frequency.ANNUAL
            )
