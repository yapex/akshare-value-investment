"""
UnitConverter单元测试

测试A股数据单位标准化转换器的功能
"""

import pytest
import pandas as pd
from akshare_value_investment.core.unit_converter import UnitConverter


class TestUnitConverter:
    """UnitConverter测试类"""

    def test_parse_value_with_unit_yi(self):
        """测试解析带"亿"单位的字符串"""
        assert UnitConverter.parse_value("592.96亿") == 592.96
        assert UnitConverter.parse_value("500亿") == 500.0
        assert UnitConverter.parse_value("123.45亿") == 123.45

    def test_parse_value_with_unit_wan(self):
        """测试解析带"万"单位的字符串"""
        assert UnitConverter.parse_value("123.45万") == 123.45
        assert UnitConverter.parse_value("100万") == 100.0

    def test_parse_value_false(self):
        """测试解析false值"""
        assert UnitConverter.parse_value(False) == 0.0

    def test_parse_value_none(self):
        """测试解析None值"""
        assert UnitConverter.parse_value(None) == 0.0

    def test_parse_value_empty_string(self):
        """测试解析空字符串"""
        assert UnitConverter.parse_value("") == 0.0
        assert UnitConverter.parse_value("   ") == 0.0

    def test_parse_value_number(self):
        """测试解析纯数字"""
        assert UnitConverter.parse_value(123) == 123.0
        assert UnitConverter.parse_value(123.45) == 123.45

    def test_parse_value_string_number(self):
        """测试解析数字字符串"""
        assert UnitConverter.parse_value("123") == 123.0
        assert UnitConverter.parse_value("123.45") == 123.45

    def test_parse_value_invalid_string(self):
        """测试解析无效字符串"""
        assert UnitConverter.parse_value("invalid") == 0.0
        assert UnitConverter.parse_value("abc亿") == 0.0

    def test_convert_dataframe_basic(self):
        """测试基本DataFrame转换"""
        df = pd.DataFrame({
            "货币资金": ["592.96亿", "500亿"],
            "短期借款": [False, False],
            "长期借款": [None, None],
            "报告期": ["2024-12-31", "2023-12-31"]
        })

        result_df, unit_map = UnitConverter.convert_dataframe(df)

        # 验证数据转换
        assert result_df["货币资金"].tolist() == [592.96, 500.0]
        assert result_df["短期借款"].tolist() == [0.0, 0.0]
        assert result_df["长期借款"].tolist() == [0.0, 0.0]
        assert result_df["报告期"].tolist() == ["2024-12-31", "2023-12-31"]

        # 验证单位映射
        assert unit_map["货币资金"] == "亿元"
        assert unit_map["短期借款"] == "亿元"
        assert unit_map["长期借款"] == "亿元"
        assert unit_map["报告期"] == "日期"

    def test_convert_dataframe_empty(self):
        """测试空DataFrame转换"""
        df = pd.DataFrame()
        result_df, unit_map = UnitConverter.convert_dataframe(df)

        assert result_df.empty
        assert unit_map == {}

    def test_convert_dataframe_mixed_values(self):
        """测试混合值DataFrame转换"""
        df = pd.DataFrame({
            "货币资金": ["592.96亿", "100", False, None],
            "报告期": ["2024-12-31", "2023-12-31", "2022-12-31", "2021-12-31"]
        })

        result_df, unit_map = UnitConverter.convert_dataframe(df)

        # 验证混合值转换
        assert result_df["货币资金"].tolist() == [592.96, 100.0, 0.0, 0.0]
        assert unit_map["货币资金"] == "亿元"

    def test_convert_dataframe_unit_patterns(self):
        """测试不同单位模式"""
        df = pd.DataFrame({
            "value_yi": ["100亿", "200亿"],
            "value_wan": ["300万", "400万"],
            "value_no_unit": ["500", "600"],
        })

        result_df, unit_map = UnitConverter.convert_dataframe(df)

        # 验证数值提取正确
        assert result_df["value_yi"].tolist() == [100.0, 200.0]
        assert result_df["value_wan"].tolist() == [300.0, 400.0]
        assert result_df["value_no_unit"].tolist() == [500.0, 600.0]

        # 验证单位映射统一为"亿元"
        assert unit_map["value_yi"] == "亿元"
        assert unit_map["value_wan"] == "亿元"
        assert unit_map["value_no_unit"] == "亿元"

    def test_convert_dataframe_preserves_non_numeric_fields(self):
        """测试保留非数值字段"""
        df = pd.DataFrame({
            "货币资金": ["592.96亿"],
            "报告期": ["2024-12-31"]
        })

        result_df, unit_map = UnitConverter.convert_dataframe(df)

        # 验证数值字段转换
        assert result_df["货币资金"].iloc[0] == 592.96

        # 验证非数值字段保持不变（报告期在NON_NUMERIC_FIELDS中）
        assert result_df["报告期"].iloc[0] == "2024-12-31"

        # 验证单位映射
        assert unit_map["货币资金"] == "亿元"
        assert unit_map["报告期"] == "日期"

    def test_a_stock_unit_constant(self):
        """测试A股单位常量"""
        assert UnitConverter.A_STOCK_UNIT == "亿元"

    def test_non_numeric_fields_constant(self):
        """测试非数值字段常量"""
        assert "报告期" in UnitConverter.NON_NUMERIC_FIELDS

    def test_unit_patterns_constant(self):
        """测试单位模式常量"""
        assert "亿" in UnitConverter.UNIT_PATTERNS
        assert "万" in UnitConverter.UNIT_PATTERNS
        assert UnitConverter.UNIT_PATTERNS["亿"] == "亿元"
        assert UnitConverter.UNIT_PATTERNS["万"] == "万元"
