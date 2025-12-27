"""
测试 services/calculators/net_income_valuation.py

测试净利润估值计算器（PE倍数法）
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# 添加 webapp 目录到 Python 路径
webapp_path = Path(__file__).parent.parent.parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))

from services.calculators.net_income_valuation import calculate
import services.data_service as data_service


class TestNetIncomeValuationCalculator:
    """测试净利润估值计算器"""

    @pytest.fixture
    def mock_api_response(self):
        """Mock API 响应"""
        return {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "五、净利润": 100000000000,  # 1000亿（单位：元）
                            "REPORT_DATE": "2023-12-31"
                        },
                        {
                            "date": "2022-12-31",
                            "五、净利润": 90000000000,  # 900亿
                            "REPORT_DATE": "2022-12-31"
                        },
                        {
                            "date": "2021-12-31",
                            "五、净利润": 80000000000,  # 800亿
                            "REPORT_DATE": "2021-12-31"
                        },
                    ]
                }
            }
        }

    @pytest.fixture
    def mock_api_requests(self, mock_api_response):
        """Mock API 请求"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response
            yield mock_get

    def test_calculate_success(self, mock_api_requests):
        """测试成功计算净利润估值"""
        result = calculate(
            symbol="600519",
            market="A股",
            years=10,
            growth_rate=0.10,  # 10%
            pe_multiple=25.0
        )

        # 验证返回值结构
        assert isinstance(result, tuple)
        assert len(result) == 3

        df, display_columns, stats = result

        # 验证 DataFrame
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

        # 验证显示列
        assert isinstance(display_columns, list)
        assert len(display_columns) > 0

        # 验证统计字典
        assert isinstance(stats, dict)

    def test_valuation_calculation_correctness(self, mock_api_requests):
        """测试估值计算正确性"""
        # 当前净利润：1000亿（100000000000元 = 1000亿元）
        # 增长率：10%
        # PE倍数：25倍
        # 三年后净利润 = 1000 * (1.1)^3 = 1331亿
        # 企业价值 = 1331 * 25 = 33275亿

        df, display_columns, stats = calculate(
            symbol="600519",
            market="A股",
            years=10,
            growth_rate=0.10,
            pe_multiple=25.0
        )

        # 验证 stats 中的估值结果
        assert "current_net_income" in stats
        assert "year3_net_income" in stats
        assert "enterprise_value" in stats

        # 验证计算结果（允许一定误差）
        expected_year3_income = 133100000000  # 1000亿 * 1.1^3
        expected_enterprise_value = expected_year3_income * 25

        assert stats["year3_net_income"] == pytest.approx(expected_year3_income, rel=0.01)
        assert stats["enterprise_value"] == pytest.approx(expected_enterprise_value, rel=0.01)

    def test_prediction_dataframe_structure(self, mock_api_requests):
        """测试预测数据框结构"""
        df, display_columns, stats = calculate(
            symbol="600519",
            market="A股",
            years=10,
            growth_rate=0.10,
            pe_multiple=25.0
        )

        # 验证包含历史数据和预测数据
        assert "年份" in df.columns
        assert "历史净利润" in df.columns or "预测净利润" in df.columns

    def test_historical_growth_rate_calculation(self, mock_api_requests):
        """测试历史增长率计算"""
        df, display_columns, stats = calculate(
            symbol="600519",
            market="A股",
            years=10,
            growth_rate=0.10,
            pe_multiple=25.0
        )

        # 验证历史增长率被计算
        # 历史：800 -> 900 -> 1000
        # 增长率 = (1000/800)^(1/2) - 1 ≈ 11.8%
        assert "historical_growth_rate" in stats
        assert stats["historical_growth_rate"] > 0

    def test_different_growth_rates(self, mock_api_requests):
        """测试不同增长率"""
        # 低增长率
        _, _, stats_low = calculate("600519", "A股", 10, 0.05, 25.0)

        # 高增长率
        _, _, stats_high = calculate("600519", "A股", 10, 0.20, 25.0)

        # 高增长率的估值应该更高
        assert stats_high["year3_net_income"] > stats_low["year3_net_income"]
        assert stats_high["enterprise_value"] > stats_low["enterprise_value"]

    def test_different_pe_multiples(self, mock_api_requests):
        """测试不同 PE 倍数"""
        # 低PE倍数
        _, _, stats_low_pe = calculate("600519", "A股", 10, 0.10, 15.0)

        # 高PE倍数
        _, _, stats_high_pe = calculate("600519", "A股", 10, 0.10, 30.0)

        # 第三年净利润应该相同
        assert stats_low_pe["year3_net_income"] == stats_high_pe["year3_net_income"]

        # 高PE的企业价值应该更高
        assert stats_high_pe["enterprise_value"] > stats_low_pe["enterprise_value"]

    def test_hk_stock_valuation(self):
        """测试港股估值"""
        # Mock 港股数据
        api_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "股东应占溢利": 80000000000,  # 800亿港元
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_get.return_value = mock_response

            result = calculate("00700", "港股", 10, 0.10, 25.0)

            # 验证成功返回
            assert result is not None
            df, display_columns, stats = result
            assert not df.empty
            assert stats["current_net_income"] > 0

    def test_us_stock_valuation(self):
        """测试美股估值"""
        # Mock 美股数据
        api_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "净利润": 90000000000,  # 900亿美元
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_get.return_value = mock_response

            result = calculate("AAPL", "美股", 10, 0.10, 25.0)

            # 验证成功返回
            assert result is not None
            df, display_columns, stats = result
            assert not df.empty
            assert stats["current_net_income"] > 0

    def test_api_error_handling(self):
        """测试 API 错误处理"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            with pytest.raises(data_service.APIServiceUnavailableError):
                calculate("600519", "A股", 10, 0.10, 25.0)

    def test_no_income_data(self):
        """测试缺少利润表数据"""
        empty_response = {"data": {}}

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = empty_response
            mock_get.return_value = mock_response

            with pytest.raises(data_service.DataServiceError, match="没有利润表数据"):
                calculate("600519", "A股", 10, 0.10, 25.0)

    def test_missing_net_income_field(self):
        """测试缺少净利润字段"""
        # Mock 数据缺少净利润字段
        api_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "营业收入": 200000000000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="净利润字段.*不存在"):
                calculate("600519", "A股", 10, 0.10, 25.0)

    def test_unsupported_market_type(self):
        """测试不支持的市场类型"""
        with pytest.raises(ValueError, match="不支持的市场类型"):
            calculate("600519", " unsupported_market", 10, 0.10, 25.0)

    def test_growth_rate_edge_cases(self, mock_api_requests):
        """测试增长率边界情况"""
        # 零增长率
        df, _, stats = calculate("600519", "A股", 10, 0.0, 25.0)

        # 零增长率时，第三年净利润应该等于当前净利润
        assert stats["year3_net_income"] == pytest.approx(stats["current_net_income"], rel=0.01)

    def test_single_year_historical_data(self):
        """测试只有一年历史数据的情况"""
        # Mock 只有一年的数据
        api_response = {
            "data": {
                "income_statement": {
                    "data": [
                        {
                            "date": "2023-12-31",
                            "五、净利润": 100000000000,
                            "REPORT_DATE": "2023-12-31"
                        }
                    ]
                }
            }
        }

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_get.return_value = mock_response

            df, display_columns, stats = calculate("600519", "A股", 10, 0.10, 25.0)

            # 历史增长率应该为 0（因为只有一年数据）
            assert stats["historical_growth_rate"] == 0.0
