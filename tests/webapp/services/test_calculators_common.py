"""
测试 services/calculators/common.py

测试可重用的基础计算函数：
- calculate_cagr: 复合年增长率
- calculate_interest_bearing_debt: 有息债务计算
- calculate_ebit: EBIT 和 EBIT 利润率
- calculate_free_cash_flow: 自由现金流计算
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# 添加 webapp 目录到 Python 路径
webapp_path = Path(__file__).parent.parent.parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))

from services.calculators.common import (
    calculate_cagr,
    calculate_interest_bearing_debt,
    calculate_ebit,
    calculate_free_cash_flow
)


class TestCalculateCAGR:
    """测试复合年增长率计算"""

    def test_normal_growth(self):
        """测试正常增长情况"""
        series = pd.Series([100, 110, 121])
        result = calculate_cagr(series)
        assert result == pytest.approx(10.0, rel=0.01), "CAGR 应为 10%"

    def test_high_growth(self):
        """测试高增长情况"""
        series = pd.Series([100, 150, 225])
        result = calculate_cagr(series)
        assert result == pytest.approx(50.0, rel=0.01), "CAGR 应为 50%"

    def test_negative_growth(self):
        """测试负增长情况"""
        series = pd.Series([100, 90, 81])
        result = calculate_cagr(series)
        assert result == pytest.approx(-10.0, rel=0.01), "CAGR 应为 -10%"

    def test_single_value(self):
        """测试单个值情况"""
        series = pd.Series([100])
        result = calculate_cagr(series)
        assert result == 0.0, "单个值应返回 0"

    def test_zero_initial_value(self):
        """测试初始值为零"""
        series = pd.Series([0, 100, 200])
        result = calculate_cagr(series)
        assert result == 0.0, "初始值为零应返回 0"

    def test_negative_initial_value(self):
        """测试初始值为负"""
        series = pd.Series([-100, 100, 200])
        result = calculate_cagr(series)
        assert result == 0.0, "初始值为负应返回 0"


class TestCalculateInterestBearingDebt:
    """测试有息债务计算"""

    @pytest.fixture
    def sample_balance_df(self):
        """创建样本资产负债表数据"""
        return pd.DataFrame({
            "年份": [2023, 2022],
            "短期借款": [100000, 90000],
            "长期借款": [200000, 180000],
            "应付债券": [50000, 45000],
            "一年内到期的非流动负债": [30000, 27000],
        })

    def test_a_stock_full_fields(self, sample_balance_df):
        """测试 A股 完整字段"""
        result = calculate_interest_bearing_debt(sample_balance_df, "A股")

        expected = pd.Series([380000, 342000])  # 100k+200k+50k+30k
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )

    def test_a_stock_missing_optional_fields(self):
        """测试 A股 缺少可选字段"""
        df = pd.DataFrame({
            "年份": [2023],
            "短期借款": [100000],
            "长期借款": [200000],
        })
        result = calculate_interest_bearing_debt(df, "A股")

        expected = pd.Series([300000])  # 100k+200k
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )

    def test_hk_stock(self):
        """测试港股"""
        df = pd.DataFrame({
            "年份": [2023],
            "短期贷款": [80000],
            "长期贷款": [150000],
        })
        result = calculate_interest_bearing_debt(df, "港股")

        expected = pd.Series([230000])  # 80k+150k
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )

    def test_us_stock(self):
        """测试美股"""
        df = pd.DataFrame({
            "年份": [2023],
            "短期债务": [70000],
            "长期负债": [140000],
            "长期负债(本期部分)": [25000],
        })
        result = calculate_interest_bearing_debt(df, "美股")

        expected = pd.Series([235000])  # 70k+140k+25k
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )

    def test_missing_fields_with_zero(self):
        """测试字段缺失时返回零"""
        df = pd.DataFrame({
            "年份": [2023, 2022],
        })
        result = calculate_interest_bearing_debt(df, "A股")

        expected = pd.Series([0, 0])
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )

    def test_nan_values_treated_as_zero(self):
        """测试 NaN 值处理为零"""
        df = pd.DataFrame({
            "年份": [2023],
            "短期借款": [100000],
            "长期借款": [pd.NA],
        })
        result = calculate_interest_bearing_debt(df, "A股")

        expected = pd.Series([100000])  # 只计入短期借款
        pd.testing.assert_series_equal(
            result,
            expected,
            check_names=False
        )


class TestCalculateEBIT:
    """测试 EBIT 计算"""

    @pytest.fixture
    def a_stock_income_data(self):
        """A股利润表数据"""
        return {
            "income_statement": pd.DataFrame({
                "年份": [2023, 2022],
                "五、净利润": [1000000, 900000],
                "减：所得税费用": [200000, 180000],
                "其中：利息费用": [50000, 45000],
                "其中：营业收入": [2000000, 1800000],
            })
        }

    @pytest.fixture
    def hk_stock_income_data(self):
        """港股利润表数据"""
        return {
            "income_statement": pd.DataFrame({
                "年份": [2023, 2022],
                "除税前溢利": [1250000, 1125000],
                "营业额": [2000000, 1800000],
            })
        }

    @pytest.fixture
    def us_stock_income_data(self):
        """美股利润表数据"""
        return {
            "income_statement": pd.DataFrame({
                "年份": [2023, 2022],
                "持续经营税前利润": [1250000, 1125000],
                "营业收入": [2000000, 1800000],
            })
        }

    def test_a_stock_ebit_calculation(self, a_stock_income_data):
        """测试 A股 EBIT 计算"""
        result_df, display_columns = calculate_ebit(a_stock_income_data, "A股")

        # 验证 EBIT = 净利润 + 所得税 + 利息费用
        assert "EBIT" in result_df.columns
        assert result_df["EBIT"].iloc[0] == 1250000  # 1000000 + 200000 + 50000

        # 验证 EBIT 利润率
        assert "EBIT利润率" in result_df.columns
        assert result_df["EBIT利润率"].iloc[0] == pytest.approx(62.5, rel=0.01)  # 1250000/2000000*100

    def test_a_stock_display_columns(self, a_stock_income_data):
        """测试 A股 显示列"""
        result_df, display_columns = calculate_ebit(a_stock_income_data, "A股")

        expected_columns = ["年份", "净利润", "所得税费用", "利息费用", "收入", "EBIT", "EBIT利润率"]
        assert display_columns == expected_columns

    def test_hk_stock_ebit_calculation(self, hk_stock_income_data):
        """测试港股 EBIT 计算"""
        result_df, display_columns = calculate_ebit(hk_stock_income_data, "港股")

        # 验证 EBIT 直接等于除税前溢利
        assert result_df["EBIT"].iloc[0] == 1250000

        # 验证 EBIT 利润率
        assert result_df["EBIT利润率"].iloc[0] == pytest.approx(62.5, rel=0.01)

    def test_hk_stock_alternate_revenue_field(self):
        """测试港股使用'经营收入总额'字段"""
        data = {
            "income_statement": pd.DataFrame({
                "年份": [2023],
                "除税前溢利": [1250000],
                "经营收入总额": [2000000],  # 使用此字段而非"营业额"
            })
        }
        result_df, _ = calculate_ebit(data, "港股")

        assert "收入" in result_df.columns
        assert result_df["收入"].iloc[0] == 2000000

    def test_hk_stock_missing_revenue_field(self):
        """测试港股缺少收入字段"""
        data = {
            "income_statement": pd.DataFrame({
                "年份": [2023],
                "除税前溢利": [1250000],
            })
        }
        with pytest.raises(ValueError, match="缺少收入字段"):
            calculate_ebit(data, "港股")

    def test_us_stock_ebit_calculation(self, us_stock_income_data):
        """测试美股 EBIT 计算"""
        result_df, display_columns = calculate_ebit(us_stock_income_data, "美股")

        # 验证 EBIT 直接等于持续经营税前利润
        assert result_df["EBIT"].iloc[0] == 1250000

        # 验证 EBIT 利润率
        assert result_df["EBIT利润率"].iloc[0] == pytest.approx(62.5, rel=0.01)

    def test_us_stock_alternate_revenue_field(self):
        """测试美股使用'收入总额'字段"""
        data = {
            "income_statement": pd.DataFrame({
                "年份": [2023],
                "持续经营税前利润": [1250000],
                "收入总额": [2000000],  # 使用此字段而非"营业收入"
            })
        }
        result_df, _ = calculate_ebit(data, "美股")

        assert "收入" in result_df.columns
        assert result_df["收入"].iloc[0] == 2000000

    def test_us_stock_missing_revenue_field(self):
        """测试美股缺少收入字段"""
        data = {
            "income_statement": pd.DataFrame({
                "年份": [2023],
                "持续经营税前利润": [1250000],
            })
        }
        with pytest.raises(ValueError, match="缺少收入字段"):
            calculate_ebit(data, "美股")


class TestCalculateFreeCashFlow:
    """测试自由现金流计算"""

    @pytest.fixture
    def a_stock_cashflow_data(self):
        """A股现金流量表数据"""
        return {
            "cash_flow": pd.DataFrame({
                "年份": [2023, 2022],
                "经营活动产生的现金流量净额": [1200000, 1100000],
                "购建固定资产、无形资产和其他长期资产支付的现金": [-300000, -280000],
            })
        }

    @pytest.fixture
    def hk_stock_cashflow_data(self):
        """港股现金流量表数据"""
        return {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "经营业务现金净额": [1200000],
                "购建固定资产": [-200000],
                "购建无形资产及其他资产": [-100000],
            })
        }

    @pytest.fixture
    def us_stock_cashflow_data(self):
        """美股现金流量表数据"""
        return {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "经营活动产生的现金流量净额": [1200000],
                "购买固定资产": [-200000],
                "购建无形资产及其他资产": [-100000],
            })
        }

    def test_a_stock_fcf_calculation(self, a_stock_cashflow_data):
        """测试 A股 自由现金流计算"""
        result_df, display_columns = calculate_free_cash_flow(a_stock_cashflow_data, "A股")

        # 验证自由现金流 = 经营现金流 - 资本支出
        assert "自由现金流" in result_df.columns
        # 资本支出取绝对值: 300000
        # FCF = 1200000 - 300000 = 900000
        assert result_df["自由现金流"].iloc[0] == 900000

        # 验证资本支出取绝对值
        assert result_df["资本支出"].iloc[0] == 300000

    def test_a_stock_display_columns(self, a_stock_cashflow_data):
        """测试 A股 显示列"""
        result_df, display_columns = calculate_free_cash_flow(a_stock_cashflow_data, "A股")

        expected_columns = ["年份", "经营性现金流量净额", "资本支出", "自由现金流"]
        assert display_columns == expected_columns

    def test_hk_stock_fcf_calculation(self, hk_stock_cashflow_data):
        """测试港股自由现金流计算"""
        result_df, display_columns = calculate_free_cash_flow(hk_stock_cashflow_data, "港股")

        # FCF = 1200000 - (200000 + 100000) = 900000
        assert result_df["自由现金流"].iloc[0] == 900000

    def test_hk_stock_missing_capex_field(self):
        """测试港股缺少资本支出字段"""
        data = {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "经营业务现金净额": [1200000],
                "购建固定资产": [-200000],
                # 缺少"购建无形资产及其他资产"
            })
        }
        result_df, _ = calculate_free_cash_flow(data, "港股")

        # 应正常计算，缺失字段按 0 处理
        assert result_df["自由现金流"].iloc[0] == 1000000  # 1200000 - 200000

    def test_us_stock_fcf_calculation(self, us_stock_cashflow_data):
        """测试美股自由现金流计算"""
        result_df, display_columns = calculate_free_cash_flow(us_stock_cashflow_data, "美股")

        # FCF = 1200000 - (200000 + 100000) = 900000
        assert result_df["自由现金流"].iloc[0] == 900000

    def test_a_stock_missing_operating_cashflow(self):
        """测试缺少经营性现金流字段"""
        data = {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "购建固定资产、无形资产和其他长期资产支付的现金": [-300000],
            })
        }
        with pytest.raises(ValueError, match="经营性现金流量净额字段.*不存在"):
            calculate_free_cash_flow(data, "A股")

    def test_a_stock_missing_capex(self):
        """测试缺少资本支出字段"""
        data = {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "经营活动产生的现金流量净额": [1200000],
            })
        }
        with pytest.raises(ValueError, match="资本支出字段.*不存在"):
            calculate_free_cash_flow(data, "A股")

    def test_negative_capex_handling(self):
        """测试负资本支出处理（取绝对值）"""
        data = {
            "cash_flow": pd.DataFrame({
                "年份": [2023],
                "经营活动产生的现金流量净额": [1200000],
                "购建固定资产、无形资产和其他长期资产支付的现金": [300000],  # 正数
            })
        }
        result_df, _ = calculate_free_cash_flow(data, "A股")

        # 负数应取绝对值，所以资本支出仍为 300000
        # FCF = 1200000 - 300000 = 900000
        assert result_df["资本支出"].iloc[0] == 300000
        assert result_df["自由现金流"].iloc[0] == 900000
