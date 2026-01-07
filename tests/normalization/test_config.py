"""
测试字段映射配置模块
"""

import pytest
from akshare_value_investment.normalization.config import (
    get_a_stock_mappings,
    get_hk_stock_mappings,
    get_us_stock_mappings,
    load_market_mappings,
)
from akshare_value_investment.domain.models.financial_standard import StandardFields


class TestConfigModule:
    """测试配置模块的功能"""

    def test_a_stock_mappings_not_empty(self):
        """验证A股映射配置不为空"""
        mappings = get_a_stock_mappings()
        assert len(mappings) > 0
        assert StandardFields.TOTAL_REVENUE in mappings
        # 验证包含所有必要的别名
        assert "营业总收入" in mappings[StandardFields.TOTAL_REVENUE]
        assert "一、营业总收入" in mappings[StandardFields.TOTAL_REVENUE]

    def test_hk_stock_mappings_not_empty(self):
        """验证港股映射配置不为空"""
        mappings = get_hk_stock_mappings()
        assert len(mappings) > 0
        assert StandardFields.TOTAL_REVENUE in mappings
        # 港股应该有多个别名
        assert len(mappings[StandardFields.TOTAL_REVENUE]) >= 3

    def test_us_stock_mappings_not_empty(self):
        """验证美股映射配置不为空"""
        mappings = get_us_stock_mappings()
        assert len(mappings) > 0
        assert StandardFields.TOTAL_REVENUE in mappings
        # 美股应该有多个别名
        assert len(mappings[StandardFields.TOTAL_REVENUE]) >= 3

    def test_load_market_mappings_structure(self):
        """验证加载的映射配置结构正确"""
        config = load_market_mappings()
        assert isinstance(config, dict)
        assert 'a_stock' in config
        assert 'hk_stock' in config
        assert 'us_stock' in config

        # 验证每个市场的配置都是字典
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            assert isinstance(config[market], dict)
            # 至少应该有基础字段
            assert StandardFields.REPORT_DATE in config[market]

    def test_all_markets_have_core_fields(self):
        """验证所有市场都配置了核心字段"""
        config = load_market_mappings()
        core_fields = [
            StandardFields.REPORT_DATE,
            StandardFields.TOTAL_REVENUE,
            StandardFields.NET_INCOME,
            StandardFields.TOTAL_ASSETS,
            StandardFields.TOTAL_LIABILITIES,
            StandardFields.TOTAL_EQUITY,
        ]

        for market in ['a_stock', 'hk_stock', 'us_stock']:
            market_config = config[market]
            for field in core_fields:
                assert field in market_config, f"{market} 缺少核心字段: {field}"
                assert len(market_config[field]) > 0, f"{market}.{field} 的映射列表为空"

    def test_config_values_are_lists(self):
        """验证配置值都是列表类型"""
        config = load_market_mappings()
        for market, mappings in config.items():
            for standard_field, raw_fields in mappings.items():
                assert isinstance(raw_fields, list), \
                    f"{market}.{standard_field} 应该是列表类型，实际是 {type(raw_fields)}"
                assert len(raw_fields) > 0, \
                    f"{market}.{standard_field} 的映射列表不应为空"

    def test_a_stock_has_chinese_fields(self):
        """验证A股配置使用中文字段名"""
        mappings = get_a_stock_mappings()
        # A股应该包含中文字段
        total_revenue_raw = mappings[StandardFields.TOTAL_REVENUE]
        assert any('营业' in field for field in total_revenue_raw)

    def test_extended_fields_mappings(self):
        """验证扩展字段（每股指标、营运资本）的映射"""
        config = load_market_mappings()

        # 验证每股指标
        assert StandardFields.BASIC_EPS in config['a_stock']
        assert StandardFields.DILUTED_EPS in config['a_stock']
        assert StandardFields.BASIC_EPS in config['hk_stock']
        assert StandardFields.DILUTED_EPS in config['hk_stock']

    def test_priority_1_fields_mappings(self):
        """验证Priority 1扩展字段的映射"""
        config = load_market_mappings()

        # 验证所有市场都有Priority 1字段
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            # 现金流量分析字段
            assert StandardFields.CAPITAL_EXPENDITURE in config[market]
            assert StandardFields.DIVIDENDS_PAID in config[market]
            assert StandardFields.DEPRECIATION_AMORTIZATION in config[market]

            # 利润表扩展字段
            assert StandardFields.COST_OF_SALES in config[market]
            assert StandardFields.RD_EXPENSES in config[market]

            # 资产负债表扩展字段
            assert StandardFields.PPE_NET in config[market]

    def test_priority_2_fields_mappings(self):
        """验证Priority 2扩展字段的映射（新增11个字段）"""
        config = load_market_mappings()

        # 验证所有市场都有Priority 2字段
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            # 资产负债表扩展字段 (7个)
            assert StandardFields.INTANGIBLE_ASSETS in config[market]
            assert StandardFields.GOODWILL in config[market]
            assert StandardFields.LONG_TERM_EQUITY_INVESTMENT in config[market]
            assert StandardFields.INVESTMENT_PROPERTY in config[market]
            assert StandardFields.DEFERRED_TAX_ASSETS in config[market]
            assert StandardFields.DEFERRED_TAX_LIABILITIES in config[market]

            # 利润表扩展字段 (3个)
            assert StandardFields.SELLING_EXPENSES in config[market]
            assert StandardFields.ADMIN_EXPENSES in config[market]
            assert StandardFields.OTHER_INCOME in config[market]

            # 股东权益字段 (3个)
            assert StandardFields.ISSUED_CAPITAL in config[market]
            assert StandardFields.RETAINED_EARNINGS in config[market]
            assert StandardFields.OTHER_COMPREHENSIVE_INCOME in config[market]

    def test_total_field_count(self):
        """验证标准字段总数"""
        # 标准字段应该有 65 个 (29个原有 + 36个新增)
        field_count = len([
            attr for attr in dir(StandardFields)
            if attr.isupper() and not attr.startswith('_')
        ])
        assert field_count == 65, f"预期有65个标准字段，实际有{field_count}个"

    def test_priority_4_fields_mappings(self):
        """验证Priority 4扩展字段的映射（IFRS 100%覆盖 - 新增13个字段）"""
        config = load_market_mappings()

        # 验证所有市场都有Priority 4字段 (阶段1: 2个高优先级)
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            # 阶段1: 高优先级 (2个)
            assert StandardFields.NON_CURRENT_ASSETS in config[market]
            assert StandardFields.CURRENT_PORTION_LONG_TERM_DEBT in config[market]

            # 阶段2: 中优先级 (6个)
            assert StandardFields.OTHER_CURRENT_LIABILITIES in config[market]
            assert StandardFields.PROVISIONS in config[market]
            assert StandardFields.FINANCE_INCOME in config[market]
            assert StandardFields.PROFIT_OF_ASSOCIATES in config[market]
            assert StandardFields.CASH_PAID_TO_EMPLOYEES in config[market]
            assert StandardFields.INCOME_TAXES_PAID in config[market]

            # 阶段3: 低优先级 (5个)
            assert StandardFields.RIGHT_OF_USE_ASSETS in config[market]
            assert StandardFields.LEASE_LIABILITIES_CURRENT in config[market]
            assert StandardFields.LEASE_LIABILITIES_NON_CURRENT in config[market]
            assert StandardFields.PROCEEDS_FROM_ISSUING_SHARES in config[market]
            assert StandardFields.REPAYMENT_OF_BORROWINGS in config[market]

    def test_priority_3_fields_mappings(self):
        """验证Priority 3扩展字段的映射（新增11个字段）"""
        config = load_market_mappings()

        # 验证所有市场都有Priority 3字段
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            # 股东权益扩展 (2个)
            assert StandardFields.SHARE_PREMIUM in config[market]
            assert StandardFields.MINORITY_INTEREST in config[market]

            # 其他资产负债表字段 (6个)
            assert StandardFields.CONTRACT_ASSETS in config[market]
            assert StandardFields.FINANCIAL_ASSETS in config[market]
            assert StandardFields.PREPAYMENTS in config[market]
            assert StandardFields.OTHER_CURRENT_ASSETS in config[market]
            assert StandardFields.CONTRACT_LIABILITIES in config[market]
            assert StandardFields.CURRENT_TAX_LIABILITIES in config[market]

            # 现金流量表详细字段 (3个)
            assert StandardFields.RECEIPTS_FROM_CUSTOMERS in config[market]
            assert StandardFields.CASH_PAID_TO_SUPPLIERS in config[market]
            assert StandardFields.PROCEEDS_FROM_BORROWINGS in config[market]

    def test_capital_expenditure_a_stock(self):
        """验证A股资本支出字段映射"""
        config = load_market_mappings()
        a_mappings = config['a_stock']
        assert "购建固定资产、无形资产和其他长期资产支付的现金" in a_mappings[StandardFields.CAPITAL_EXPENDITURE]

    def test_dividends_paid_market_differences(self):
        """验证支付股利字段的市场差异"""
        config = load_market_mappings()

        # 港股是纯股息
        assert "已付股息" in config['hk_stock'][StandardFields.DIVIDENDS_PAID]

        # A股和美股包含利息(简化版)
        assert "分配股利、利润或偿付利息支付的现金" in config['a_stock'][StandardFields.DIVIDENDS_PAID]
        assert "分配股利、利润或偿付利息支付的现金" in config['us_stock'][StandardFields.DIVIDENDS_PAID]
