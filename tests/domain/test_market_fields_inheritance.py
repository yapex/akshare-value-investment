"""
测试市场字段继承机制

测试继承架构和冲突检测机制:
1. 验证继承标准字段
2. 验证市场特定字段可以添加
3. 验证不能覆盖标准字段(冲突检测)
4. 验证字段数量正确
"""

import pytest
from src.akshare_value_investment.domain.models.financial_standard import StandardFields
from src.akshare_value_investment.domain.models.market_fields.a_stock_fields import AStockMarketFields
from src.akshare_value_investment.domain.models.market_fields.hk_stock_fields import HKStockMarketFields
from src.akshare_value_investment.domain.models.market_fields.us_stock_fields import USStockMarketFields
from src.akshare_value_investment.domain.models.base_fields import FieldConflictError


class TestMarketFieldsInheritance:
    """测试市场字段继承机制"""

    def test_inherits_standard_fields(self):
        """测试: 继承所有标准字段"""
        # 验证继承关系
        assert issubclass(AStockMarketFields, StandardFields)
        assert issubclass(HKStockMarketFields, StandardFields)
        assert issubclass(USStockMarketFields, StandardFields)

        # 验证标准字段可用
        assert hasattr(AStockMarketFields, 'TOTAL_REVENUE')
        assert hasattr(AStockMarketFields, 'NET_INCOME')
        assert hasattr(AStockMarketFields, 'TOTAL_ASSETS')

        # 验证值正确
        assert AStockMarketFields.TOTAL_REVENUE == "total_revenue"
        assert HKStockMarketFields.TOTAL_REVENUE == "total_revenue"
        assert USStockMarketFields.TOTAL_REVENUE == "total_revenue"

    def test_new_market_fields_allowed(self):
        """测试: 可以正常添加新字段"""

        # 这应该成功 - 添加新字段
        class GoodMarketFields(StandardFields):
            NEW_FIELD = "new_field"

        assert GoodMarketFields.NEW_FIELD == "new_field"

        # 继承的标准字段也可用
        assert GoodMarketFields.TOTAL_REVENUE == "total_revenue"

    def test_cannot_override_standard_fields(self):
        """测试: 不能覆盖标准字段"""
        with pytest.raises(FieldConflictError) as exc_info:
            class BadMarketFields(StandardFields):
                TOTAL_REVENUE = "bad_revenue"  # ❌ 冲突!

        # 验证错误信息
        error_msg = str(exc_info.value)
        assert "TOTAL_REVENUE" in error_msg
        assert "试图覆盖父类字段" in error_msg
        assert "bad_revenue" in error_msg

    def test_idempotent_redefinition_allowed(self):
        """测试: 值相同的重新定义允许(幂等性)"""
        # 这应该成功 - 值相同
        class IdempotentFields(StandardFields):
            TOTAL_REVENUE = "total_revenue"  # ✅ 值相同,允许

        assert IdempotentFields.TOTAL_REVENUE == "total_revenue"

    def test_field_count(self):
        """测试: 字段数量正确"""
        # StandardFields: 65个 (29个原有 + 36个新增) - IFRS 100%覆盖!
        standard_count = len([
            attr for attr in dir(StandardFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        # AStockMarketFields: 65个(暂时没有特有字段)
        a_stock_count = len([
            attr for attr in dir(AStockMarketFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        # HKStockMarketFields: 65个(暂时没有特有字段)
        hk_stock_count = len([
            attr for attr in dir(HKStockMarketFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        # USStockMarketFields: 65个(暂时没有特有字段)
        us_stock_count = len([
            attr for attr in dir(USStockMarketFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        # 所有市场应该有相同数量的字段(暂时)
        assert standard_count == 65
        assert a_stock_count == 65
        assert hk_stock_count == 65
        assert us_stock_count == 65

    def test_all_65_standard_fields_accessible(self):
        """测试: 所有65个标准字段都可访问"""
        expected_fields = [
            # 基础字段
            'REPORT_DATE',

            # 利润表字段
            'TOTAL_REVENUE', 'OPERATING_INCOME', 'GROSS_PROFIT',
            'NET_INCOME', 'INCOME_TAX', 'INTEREST_EXPENSE',

            # 资产负债表字段
            'TOTAL_ASSETS', 'CURRENT_ASSETS', 'TOTAL_LIABILITIES',
            'CURRENT_LIABILITIES', 'TOTAL_EQUITY', 'SHORT_TERM_DEBT',
            'LONG_TERM_DEBT',

            # 现金流量表字段
            'OPERATING_CASH_FLOW', 'INVESTING_CASH_FLOW', 'FINANCING_CASH_FLOW',

            # 每股指标
            'BASIC_EPS', 'DILUTED_EPS',

            # 营运资本字段
            'CASH_AND_EQUIVALENTS', 'ACCOUNTS_RECEIVABLE',
            'INVENTORY', 'ACCOUNTS_PAYABLE',

            # 现金流量分析字段
            'CAPITAL_EXPENDITURE', 'DIVIDENDS_PAID', 'DEPRECIATION_AMORTIZATION',

            # 利润表扩展字段
            'COST_OF_SALES', 'RD_EXPENSES',

            # 资产负债表扩展字段
            'PPE_NET',

            # 资产负债表扩展字段 (新增6个)
            'INTANGIBLE_ASSETS',
            'GOODWILL',
            'LONG_TERM_EQUITY_INVESTMENT',
            'INVESTMENT_PROPERTY',
            'DEFERRED_TAX_ASSETS',
            'DEFERRED_TAX_LIABILITIES',

            # 利润表扩展字段 (新增3个)
            'SELLING_EXPENSES',
            'ADMIN_EXPENSES',
            'OTHER_INCOME',

            # 股东权益字段 (新增3个)
            'ISSUED_CAPITAL',
            'RETAINED_EARNINGS',
            'OTHER_COMPREHENSIVE_INCOME',

            # 股东权益字段 (新增2个)
            'SHARE_PREMIUM',
            'MINORITY_INTEREST',

            # 其他资产负债表字段 (新增6个)
            'CONTRACT_ASSETS',
            'FINANCIAL_ASSETS',
            'PREPAYMENTS',
            'OTHER_CURRENT_ASSETS',
            'CONTRACT_LIABILITIES',
            'CURRENT_TAX_LIABILITIES',

            # 现金流量表详细字段 (新增3个)
            'RECEIPTS_FROM_CUSTOMERS',
            'CASH_PAID_TO_SUPPLIERS',
            'PROCEEDS_FROM_BORROWINGS',

            # 阶段1新增: 高优先级 (2个)
            'NON_CURRENT_ASSETS',
            'CURRENT_PORTION_LONG_TERM_DEBT',

            # 阶段2新增: 中优先级 (6个)
            'OTHER_CURRENT_LIABILITIES',
            'PROVISIONS',
            'FINANCE_INCOME',
            'PROFIT_OF_ASSOCIATES',
            'CASH_PAID_TO_EMPLOYEES',
            'INCOME_TAXES_PAID',

            # 阶段3新增: 低优先级 (5个)
            'RIGHT_OF_USE_ASSETS',
            'LEASE_LIABILITIES_CURRENT',
            'LEASE_LIABILITIES_NON_CURRENT',
            'PROCEEDS_FROM_ISSUING_SHARES',
            'REPAYMENT_OF_BORROWINGS',
        ]

        # 验证所有市场都有这些字段
        for market_fields_class in [AStockMarketFields, HKStockMarketFields, USStockMarketFields]:
            for field in expected_fields:
                assert hasattr(market_fields_class, field), f"{market_fields_class.__name__} 缺少字段: {field}"

    def test_market_fields_independence(self):
        """测试: 各市场字段类互不影响"""
        # 创建一个自定义类添加新字段
        class AStockWithCustomField(AStockMarketFields):
            CUSTOM_FIELD = "custom_field"

        # 港股不应该有这个自定义字段
        assert not hasattr(HKStockMarketFields, 'CUSTOM_FIELD')

        # 但是标准字段仍然可用
        assert hasattr(HKStockMarketFields, 'TOTAL_REVENUE')
        # 新增的标准字段也可用
        assert hasattr(HKStockMarketFields, 'MINORITY_INTEREST')

