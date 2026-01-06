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
        assert StandardFields.BASIC_EPS in config['us_stock']
        assert StandardFields.DILUTED_EPS in config['us_stock']

        # 验证营运资本字段
        assert StandardFields.CASH_AND_EQUIVALENTS in config['a_stock']
        assert StandardFields.ACCOUNTS_RECEIVABLE in config['a_stock']
        assert StandardFields.INVENTORY in config['a_stock']
        assert StandardFields.ACCOUNTS_PAYABLE in config['a_stock']

        # 验证所有市场都有营运资本字段
        for market in ['a_stock', 'hk_stock', 'us_stock']:
            assert StandardFields.CASH_AND_EQUIVALENTS in config[market]
            assert StandardFields.INVENTORY in config[market]
