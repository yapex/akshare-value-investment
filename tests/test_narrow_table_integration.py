#!/usr/bin/env python3
"""
窄表结构集成测试

测试美股财务三表窄表结构的完整集成功能，包括：
1. 窄表配置加载
2. 字段映射
3. 数据提取
4. MCP查询集成
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import pandas as pd

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.akshare_value_investment.business.mapping.namespaced_config_loader import NamespacedMultiConfigLoader
from src.akshare_value_investment.business.mapping.unified_field_mapper import UnifiedFieldMapper
from src.akshare_value_investment.business.mapping.market_inferrer import DefaultMarketInferrer
from src.akshare_value_investment.business.mapping.field_searcher import DefaultFieldSearcher
from src.akshare_value_investment.services.narrow_table_service import NarrowTableService


class TestNarrowTableConfig:
    """测试窄表配置加载"""

    def test_load_narrow_table_config(self):
        """测试窄表配置正确加载"""
        config_loader = NamespacedMultiConfigLoader()
        success = config_loader.load_configs()

        assert success, "配置加载应该成功"

        us_config = config_loader.get_market_config("us_stock")
        assert us_config is not None, "美股配置应该存在"

        # 检查窄表字段
        narrow_fields = [
            field for field in us_config.fields.values()
            if hasattr(field, 'is_narrow_table_field') and field.is_narrow_table_field()
        ]

        assert len(narrow_fields) > 0, "应该有窄表字段"

        # 检查总资产字段配置
        total_assets_field = None
        for field in narrow_fields:
            if field.name == "总资产":
                total_assets_field = field
                break

        assert total_assets_field is not None, "应该有总资产字段"
        assert total_assets_field.is_narrow_table_field(), "总资产应该是窄表字段"

        mapping = total_assets_field.get_narrow_table_mapping()
        assert mapping is not None, "应该有窄表映射配置"
        assert mapping['api_field'] == "ITEM_NAME", "API字段应该是ITEM_NAME"
        assert mapping['filter_value'] == "总资产", "筛选值应该是总资产"
        assert mapping['value_field'] == "AMOUNT", "数值字段应该是AMOUNT"

    def test_field_mapping_narrow_table(self):
        """测试窄表字段映射"""
        config_loader = NamespacedMultiConfigLoader()
        config_loader.load_configs()

        market_inferrer = DefaultMarketInferrer()
        field_searcher = DefaultFieldSearcher(config_loader)
        field_mapper = UnifiedFieldMapper(
            config_loader=config_loader,
            field_searcher=field_searcher,
            market_inferrer=market_inferrer
        )

        # 测试AAPL的字段映射
        test_cases = [
            ("AAPL", "总资产", True),
            ("AAPL", "应收账款", True),
            ("AAPL", "现金及现金等价物", True),
            ("AAPL", "净利润", False),  # 这是标准字段，不是窄表字段
            ("AAPL", "不存在的字段", False),
        ]

        for symbol, query, should_be_narrow in test_cases:
            mapped_fields, suggestions = field_mapper.resolve_fields_sync(symbol, [query])

            if should_be_narrow:
                assert mapped_fields, f"'{query}' 应该映射成功"
                field_id = mapped_fields[0]
                field_info = field_mapper.get_field_details(field_id, "us_stock")

                assert field_info is not None, f"应该能获取字段详情: {field_id}"
                assert field_info.is_narrow_table_field(), f"'{query}' 应该是窄表字段"

                mapping = field_info.get_narrow_table_mapping()
                assert mapping is not None, "应该有窄表映射"
            elif query == "净利润":
                # 净利润应该是标准字段
                assert mapped_fields, f"'{query}' 应该映射成功"
                field_id = mapped_fields[0]
                field_info = field_mapper.get_field_details(field_id, "us_stock")

                if field_info:  # 如果存在，应该是标准字段
                    assert not field_info.is_narrow_table_field(), f"'{query}' 应该是标准字段"
            else:
                # 不存在的字段应该映射失败
                assert not mapped_fields, f"'{query}' 不应该映射成功"


class TestNarrowTableService:
    """测试窄表数据服务"""

    def test_validate_narrow_table_structure(self):
        """测试窄表结构验证"""
        service = NarrowTableService()

        # 创建窄表数据
        narrow_df = pd.DataFrame({
            'ITEM_NAME': ['总资产', '总负债', '现金及现金等价物'],
            'AMOUNT': [1000, 500, 200],
            'REPORT_DATE': ['2024-12-31', '2024-12-31', '2024-12-31']
        })

        is_narrow, missing_fields = service.validate_narrow_table_structure(narrow_df)
        assert is_narrow, "应该识别为窄表结构"
        assert len(missing_fields) == 0, "不应该缺少字段"

        # 创建非窄表数据
        wide_df = pd.DataFrame({
            'TOTAL_ASSETS': [1000],
            'TOTAL_LIABILITIES': [500],
            'CASH': [200]
        })

        is_narrow, missing_fields = service.validate_narrow_table_structure(wide_df)
        assert not is_narrow, "不应该识别为窄表结构"
        assert len(missing_fields) == 2, "应该缺少2个字段"  # ITEM_NAME和AMOUNT

    def test_extract_field_data(self):
        """测试字段数据提取"""
        service = NarrowTableService()

        # 创建测试数据
        test_df = pd.DataFrame({
            'ITEM_NAME': ['总资产', '总负债', '现金及现金等价物', '其他项目'],
            'AMOUNT': [1000000000, 500000000, 200000000, 100000000],
            'REPORT_DATE': ['2024-12-31', '2024-12-31', '2024-12-31', '2024-12-31']
        })

        # 创建字段信息
        from src.akshare_value_investment.business.mapping.models import FieldInfo
        field_info = FieldInfo(
            name="总资产",
            keywords=["总资产", "资产总额"],
            priority=1,
            description="总资产字段",
            api_field="ITEM_NAME",
            filter_value="总资产",
            value_field="AMOUNT",
            field_type="narrow"
        )

        # 提取数据
        result = service.extract_field_data(test_df, field_info, "AAPL")

        assert result is not None, "应该能提取到数据"
        assert result['field_name'] == "总资产", "字段名应该正确"
        assert result['filter_value'] == "总资产", "筛选值应该正确"
        assert result['symbol'] == "AAPL", "股票代码应该正确"
        assert result['value'] == 1000000000, "数值应该正确"

    @patch('akshare.stock_financial_us_report_em')
    def test_real_data_integration(self, mock_akshare):
        """测试真实数据集成"""
        # 模拟akshare返回数据
        mock_data = pd.DataFrame({
            'SECUCODE': ['00002'],
            'SECURITY_CODE': ['AAPL'],
            'SECURITY_NAME_ABBR': ['苹果'],
            'REPORT_DATE': ['2024-09-28'],
            'REPORT_TYPE': ['年报'],
            'REPORT': ['合并'],
            'STD_ITEM_CODE': ['310050'],
            'AMOUNT': [6803000000],
            'ITEM_NAME': ['总资产']
        })
        mock_akshare.return_value = mock_data

        # 测试数据获取
        import akshare as ak
        df = ak.stock_financial_us_report_em(symbol="AAPL")

        assert not df.empty, "应该获取到数据"
        assert "ITEM_NAME" in df.columns, "应该有ITEM_NAME字段"
        assert "AMOUNT" in df.columns, "应该有AMOUNT字段"

        # 验证窄表结构
        service = NarrowTableService()
        is_narrow, missing_fields = service.validate_narrow_table_structure(df)
        assert is_narrow, "应该是窄表结构"
        assert len(missing_fields) == 0, "不应该缺少字段"


class TestMCPIntegration:
    """测试MCP集成"""

    @patch('akshare.stock_financial_us_report_em')
    def test_mcp_query_narrow_table_field(self, mock_akshare):
        """测试MCP查询窄表字段"""
        # 模拟akshare返回数据
        mock_data = pd.DataFrame({
            'SECUCODE': ['00002'],
            'SECURITY_CODE': ['AAPL'],
            'SECURITY_NAME_ABBR': ['苹果'],
            'REPORT_DATE': ['2024-09-28'],
            'REPORT_TYPE': ['年报'],
            'REPORT': ['合并'],
            'STD_ITEM_CODE': ['310050'],
            'AMOUNT': [6803000000],
            'ITEM_NAME': ['总资产']
        })
        mock_akshare.return_value = mock_data

        # 这里应该测试MCP处理器，但需要依赖注入
        # 暂时测试窄表服务
        service = NarrowTableService()

        # 创建字段信息
        from src.akshare_value_investment.business.mapping.models import FieldInfo
        field_info = FieldInfo(
            name="总资产",
            keywords=["总资产", "资产总额"],
            priority=1,
            description="总资产字段",
            api_field="ITEM_NAME",
            filter_value="总资产",
            value_field="AMOUNT",
            field_type="narrow"
        )

        # 提取数据
        result = service.extract_field_data(mock_data, field_info, "AAPL")

        assert result is not None, "应该能提取到数据"
        assert result['value'] == 6803000000, "应该提取到正确的总资产数值"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])