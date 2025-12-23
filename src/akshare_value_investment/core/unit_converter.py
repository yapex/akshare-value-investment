"""
A股财务数据单位标准化转换器

功能：
1. 将 "592.96亿" → 592.96 (float)
2. 处理 false → 0
3. 生成字段单位映射表

设计原则：
- KISS：简洁的单一职责转换逻辑
- DRY：统一的单位转换规则
"""

import pandas as pd
from typing import Any, Dict, Tuple


class UnitConverter:
    """A股数据单位转换器"""

    # A股财务三表统一单位
    A_STOCK_UNIT = "亿元"

    # 不需要转换的字段类型
    NON_NUMERIC_FIELDS = {"报告期"}

    # 单位识别模式
    UNIT_PATTERNS = {
        "亿": "亿元",
        "万": "万元",
    }

    @staticmethod
    def parse_value(value: Any) -> float:
        """
        解析单个值

        Args:
            value: 原始值 ("592.96亿" / false / None / 123.45)

        Returns:
            float: 转换后的数值

        Examples:
            >>> UnitConverter.parse_value("592.96亿")
            592.96
            >>> UnitConverter.parse_value(False)
            0.0
            >>> UnitConverter.parse_value(None)
            0.0
        """
        # 处理 false
        if value is False:
            return 0.0

        # 处理 None
        if value is None:
            return 0.0

        # 处理字符串
        if isinstance(value, str):
            value = value.strip()

            # 空字符串
            if not value:
                return 0.0

            # 提取数字部分（去除末尾单位）
            for unit_suffix in ["亿", "万"]:
                if value.endswith(unit_suffix):
                    number_str = value[:-1].strip()
                    try:
                        return float(number_str)
                    except ValueError:
                        return 0.0

            # 无单位，直接转换
            try:
                return float(value)
            except ValueError:
                return 0.0

        # 已经是数字
        if isinstance(value, (int, float)):
            return float(value)

        return 0.0

    @staticmethod
    def convert_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        批量转换DataFrame

        Args:
            df: 原始DataFrame

        Returns:
            (转换后的DataFrame, 单位映射字典)

        Examples:
            >>> df = pd.DataFrame({"货币资金": ["592.96亿"], "报告期": ["2024-12-31"]})
            >>> result_df, unit_map = UnitConverter.convert_dataframe(df)
            >>> result_df["货币资金"].iloc[0]
            592.96
            >>> unit_map["货币资金"]
            '亿元'
        """
        if df.empty:
            return df, {}

        # 创建结果副本
        result_df = df.copy()

        # 生成单位映射
        unit_map = {}

        # 转换每一列
        for col in df.columns:
            if col in UnitConverter.NON_NUMERIC_FIELDS:
                # 非数值字段（如报告期）
                unit_map[col] = "日期"
            else:
                # 数值字段，统一为"亿元"
                result_df[col] = df[col].apply(UnitConverter.parse_value)
                unit_map[col] = UnitConverter.A_STOCK_UNIT

        return result_df, unit_map
