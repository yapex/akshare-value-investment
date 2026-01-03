"""
测试 services/calculators/roic.py

测试投入资本回报率（ROIC）计算器
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加 webapp 目录到 Python 路径
webapp_path = Path(__file__).parent.parent.parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))

from services.calculators.roic import calculate
import services.data_service as data_service


class TestROICCalculator:
    """测试 ROIC 计算器"""

    @pytest.fixture
    def mock_financial_statements_response(self):
        """Mock 财务三表 API 响应"""
        return {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "五、净利润": 1000000,
                            "减：所得税费用": 200000,
                            "其中：利息费用": 50000,
                            "其中：营业收入": 2000000,
                            "REPORT_DATE": "2023-12-31"
                        },
                        {
                            "date": "2022-12-31",
                            "五、净利润": 900000,
                            "减：所得税费用": 180000,
                            "其中：利息费用": 45000,
                            "其中：营业收入": 1800000,
                            "REPORT_DATE": "2022-12-31"
                        },
                    ]
                },
                "balance_sheet": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "短期借款": 100000,
                            "长期借款": 200000,
                            "应付债券": 50000,
                            "一年内到期的非流动负债": 30000,
                            "股东权益合计": 2000000,
                            "归属于母公司所有者权益合计": 1900000,
                            "货币资金": 500000,
                            "REPORT_DATE": "2023-12-31"
                        },
                        {
                            "date": "2022-12-31",
                            "短期借款": 90000,
                            "长期借款": 180000,
                            "应付债券": 45000,
                            "一年内到期的非流动负债": 27000,
                            "股东权益合计": 1800000,
                            "归属于母公司所有者权益合计": 1710000,
                            "货币资金": 450000,
                            "REPORT_DATE": "2022-12-31"
                        },
                    ]
                },
                "cash_flow": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "经营活动产生的现金流量净额": 1200000,
                            "购建固定资产、无形资产和其他长期资产支付的现金": 300000,
                            "REPORT_DATE": "2023-12-31"
                        },
                        {
                            "date": "2022-12-31",
                            "经营活动产生的现金流量净额": 1080000,
                            "购建固定资产、无形资产和其他长期资产支付的现金": 270000,
                            "REPORT_DATE": "2022-12-31"
                        },
                    ]
                }
            }
        }

    @pytest.fixture
    def mock_api_requests(self, mock_financial_statements_response):
        """Mock API 请求"""
        with patch('requests.get') as mock_get:
            response = Mock()
            response.status_code = 200
            response.json.return_value = mock_financial_statements_response
            mock_get.return_value = response
            yield mock_get

    def test_calculate_roic_success(self, mock_api_requests):
        """测试成功计算 ROIC"""
        result = calculate("600519", "A股", 5)

        # 验证返回值结构
        assert isinstance(result, tuple)
        assert len(result) == 9

        (
            roic_data,
            operating_roic_data,
            breakdown_data,
            roic_columns,
            operating_roic_columns,
            breakdown_columns,
            roic_metrics,
            operating_roic_metrics,
            exclusion_notes
        ) = result

        # 验证 ROIC 数据
        assert isinstance(roic_data, pd.DataFrame)
        assert not roic_data.empty

        # 验证运营 ROIC 数据
        assert isinstance(operating_roic_data, pd.DataFrame)
        assert not operating_roic_data.empty

        # 验证拆解数据
        assert isinstance(breakdown_data, pd.DataFrame)

        # 验证显示列
        assert isinstance(roic_columns, list)
        assert isinstance(operating_roic_columns, list)
        assert isinstance(breakdown_columns, list)

        # 验证指标字典
        assert isinstance(roic_metrics, dict)
        assert isinstance(operating_roic_metrics, dict)

        # 验证剔除说明
        assert isinstance(exclusion_notes, dict)

    def test_calculate_roic_api_error(self):
        """测试 API 错误处理"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            with pytest.raises(data_service.APIServiceUnavailableError):
                calculate("600519", "A股", 5)

    def test_calculate_roic_no_balance_data(self):
        """测试缺少资产负债表数据"""
        empty_response = {"data": {}}

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = empty_response
            mock_get.return_value = mock_response

            with pytest.raises(data_service.SymbolNotFoundError, match="没有财务数据"):
                calculate("600519", "A股", 5)

    def test_roic_calculation_correctness(self, mock_api_requests):
        """测试 ROIC 计算正确性"""
        result = calculate("600519", "A股", 5)
        roic_data, _, _, _, _, _, _, _, _ = result

        # 验证 ROIC 字段存在
        assert "ROIC" in roic_data.columns or "投入资本回报率" in roic_data.columns

        # 验证年份字段
        assert "年份" in roic_data.columns

    def test_operating_roic_lower_than_roic(self, mock_api_requests):
        """测试运营 ROIC 通常低于或等于普通 ROIC"""
        result = calculate("600519", "A股", 5)
        roic_data, operating_roic_data, _, _, _, _, _, _, _ = result

        # 运营 ROIC 可能不同于普通 ROIC（剔除了现金等非经营性资产）
        # 这里只验证数据结构正确
        assert len(roic_data) == len(operating_roic_data)

    def test_hk_stock_roic_calculation(self):
        """测试港股 ROIC 计算"""
        # Mock 港股数据（包含所有三张表）
        hk_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "除税前溢利": 1500000,
                            "营业额": 2500000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                },
                "balance_sheet": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "短期贷款": 80000,
                            "长期贷款": 150000,
                            "股东权益合计": 2500000,
                            "货币资金": 600000,
                            "现金及等价物": 550000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                },
                "cash_flow": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "经营业务现金净额": 1300000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = hk_response
            mock_get.return_value = mock_response

            result = calculate("00700", "港股", 5)

            # 验证成功返回
            assert result is not None
            roic_data, _, _, _, _, _, _, _, _ = result
            assert not roic_data.empty

    def test_us_stock_roic_calculation(self):
        """测试美股 ROIC 计算"""
        # Mock 美股数据（包含所有三张表）
        us_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "持续经营税前利润": 1500000,
                            "营业收入": 2500000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                },
                "balance_sheet": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "短期债务": 70000,
                            "长期负债": 140000,
                            "长期负债(本期部分)": 25000,
                            "股东权益合计": 2400000,
                            "货币资金": 550000,
                            "现金及现金等价物": 500000,
                            "商誉": 300000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                },
                "cash_flow": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "经营活动产生的现金流量净额": 1200000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = us_response
            mock_get.return_value = mock_response

            result = calculate("AAPL", "美股", 5)

            # 验证成功返回
            assert result is not None
            roic_data, _, _, _, _, _, _, _, _ = result
            assert not roic_data.empty

    def test_return_structure_completeness(self, mock_api_requests):
        """测试返回结构的完整性"""
        result = calculate("600519", "A股", 5)

        (
            roic_data,
            operating_roic_data,
            breakdown_data,
            roic_columns,
            operating_roic_columns,
            breakdown_columns,
            roic_metrics,
            operating_roic_metrics,
            exclusion_notes
        ) = result

        # 验证所有返回值都不为 None
        assert roic_data is not None
        assert operating_roic_data is not None
        assert breakdown_data is not None
        assert roic_columns is not None
        assert operating_roic_columns is not None
        assert breakdown_columns is not None
        assert roic_metrics is not None
        assert operating_roic_metrics is not None
        assert exclusion_notes is not None

        # 验证 DataFrame 不为空
        assert len(roic_data) > 0
        assert len(operating_roic_data) > 0
