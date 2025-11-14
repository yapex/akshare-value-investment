"""
窄表数据处理服务

专门处理美股财务报表的窄表结构（ITEM_NAME + AMOUNT字段模式）。
支持基于配置的字段映射和数据提取。
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from ..business.mapping.models import FieldInfo


class NarrowTableService:
    """窄表数据处理服务

    专门处理美股财务报表的窄表结构，其中：
    - ITEM_NAME字段存储财务项目名称
    - AMOUNT字段存储对应的数值
    - 需要基于配置进行字段映射和筛选
    """

    def __init__(self):
        """初始化窄表服务"""
        pass

    def extract_field_data(
        self,
        df: pd.DataFrame,
        field_info: FieldInfo,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从窄表中提取指定字段的数据

        Args:
            df: 窄表DataFrame
            field_info: 字段信息（包含窄表映射配置）
            symbol: 股票代码（可选）

        Returns:
            提取的字段数据
        """
        if not field_info.is_narrow_table_field():
            return {}

        mapping = field_info.get_narrow_table_mapping()
        if not mapping:
            return {}

        try:
            api_field = mapping['api_field']
            filter_value = mapping['filter_value']
            value_field = mapping['value_field']

            # 检查必需字段是否存在
            if api_field not in df.columns or value_field not in df.columns:
                return {}

            # 筛选匹配的行
            filtered_rows = df[df[api_field] == filter_value]

            if filtered_rows.empty:
                return {}

            # 提取数值数据
            result_data = {}

            # 添加基础信息
            result_data['field_name'] = field_info.name
            result_data['field_id'] = field_info.field_id
            result_data['filter_value'] = filter_value
            if symbol:
                result_data['symbol'] = symbol

            # 提取所有时间点的数值
            for _, row in filtered_rows.iterrows():
                # 获取时间信息（如果有日期列）
                date_info = self._extract_date_info(row)
                amount_value = row[value_field]

                # 添加到结果中
                if date_info:
                    result_data[date_info] = amount_value
                else:
                    # 如果没有日期信息，使用单个数值
                    result_data['value'] = amount_value

            return result_data

        except Exception as e:
            # 数据提取失败
            return {}

    def extract_multiple_fields(
        self,
        df: pd.DataFrame,
        fields_info: List[FieldInfo],
        symbol: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        从窄表中提取多个字段的数据

        Args:
            df: 窄表DataFrame
            fields_info: 字段信息列表
            symbol: 股票代码（可选）

        Returns:
            字段数据字典 {field_name: field_data}
        """
        results = {}

        # 只处理窄表字段
        narrow_fields = [f for f in fields_info if f.is_narrow_table_field()]

        for field_info in narrow_fields:
            field_data = self.extract_field_data(df, field_info, symbol)
            if field_data:
                results[field_info.name] = field_data

        return results

    def get_available_items(
        self,
        df: pd.DataFrame,
        item_name_field: str = "ITEM_NAME"
    ) -> List[str]:
        """
        获取窄表中所有可用的财务项目

        Args:
            df: 窄表DataFrame
            item_name_field: 项目名称字段

        Returns:
            可用财务项目列表
        """
        if item_name_field not in df.columns:
            return []

        unique_items = df[item_name_field].dropna().unique()
        return sorted([str(item) for item in unique_items])

    def validate_narrow_table_structure(
        self,
        df: pd.DataFrame,
        required_fields: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        验证DataFrame是否为窄表结构

        Args:
            df: 待验证的DataFrame
            required_fields: 必需的字段列表

        Returns:
            (是否为窄表, 缺失字段列表)
        """
        if required_fields is None:
            required_fields = ["ITEM_NAME", "AMOUNT"]

        missing_fields = []
        for field in required_fields:
            if field not in df.columns:
                missing_fields.append(field)

        is_narrow = len(missing_fields) == 0
        return is_narrow, missing_fields

    def convert_to_wide_table(
        self,
        df: pd.DataFrame,
        item_name_field: str = "ITEM_NAME",
        value_field: str = "AMOUNT",
        date_field: Optional[str] = None
    ) -> pd.DataFrame:
        """
        将窄表转换为宽表格式

        Args:
            df: 窄表DataFrame
            item_name_field: 项目名称字段
            value_field: 数值字段
            date_field: 日期字段（可选）

        Returns:
            宽表格式的DataFrame
        """
        try:
            if item_name_field not in df.columns or value_field not in df.columns:
                return df

            # 如果有日期字段，按日期和项目名称进行透视
            if date_field and date_field in df.columns:
                wide_df = df.pivot_table(
                    index=date_field,
                    columns=item_name_field,
                    values=value_field,
                    aggfunc='first'
                ).reset_index()
            else:
                # 没有日期字段，简单重塑
                wide_df = df.pivot_table(
                    columns=item_name_field,
                    values=value_field,
                    aggfunc='first'
                ).reset_index()

            return wide_df

        except Exception as e:
            # 转换失败，返回原始数据
            return df

    def _extract_date_info(self, row: pd.Series) -> Optional[str]:
        """
        从行数据中提取日期信息

        Args:
            row: DataFrame行

        Returns:
            日期字符串或None
        """
        # 常见的日期字段名
        date_fields = ['date', 'DATE', '时间', '报告期', '报告日期', '报告时间']

        for field in date_fields:
            if field in row.index and pd.notna(row[field]):
                return str(row[field])

        return None

    def get_narrow_table_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取窄表数据摘要

        Args:
            df: 窄表DataFrame

        Returns:
            窄表摘要信息
        """
        summary = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'is_narrow_table': False,
            'item_count': 0,
            'date_columns': [],
            'numeric_columns': []
        }

        # 检查是否为窄表结构
        is_narrow, missing_fields = self.validate_narrow_table_structure(df)
        summary['is_narrow_table'] = is_narrow
        if not is_narrow:
            summary['missing_narrow_fields'] = missing_fields

        # 统计财务项目数量
        if "ITEM_NAME" in df.columns:
            summary['item_count'] = df["ITEM_NAME"].nunique()
            summary['available_items'] = self.get_available_items(df)

        # 识别日期列
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', '时间', '报告期', '时间']):
                summary['date_columns'].append(col)

        # 识别数值列
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        summary['numeric_columns'] = [col for col in numeric_cols if col != 'AMOUNT']

        return summary