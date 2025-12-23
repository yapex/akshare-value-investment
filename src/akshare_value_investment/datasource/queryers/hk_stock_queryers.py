"""港股数据查询器模块"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any, Tuple

from .base_queryer import BaseDataQueryer
from ...core.unit_converter import UnitConverter


class HKStockIndicatorQueryer(BaseDataQueryer):
    """港股财务指标查询器"""

    cache_date_field = 'date'
    cache_query_type = 'hk_indicators'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询港股财务指标原始数据"""
        raw_data = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol, indicator="年度")

        if raw_data.empty:
            return pd.DataFrame()

        if 'REPORT_DATE' in raw_data.columns:
            raw_data = raw_data.copy()
            raw_data['date'] = pd.to_datetime(raw_data['REPORT_DATE'])
            raw_data = raw_data.sort_values('date', ascending=False).reset_index(drop=True)

        return raw_data


class HKStockStatementQueryerBase(BaseDataQueryer):
    """港股财务报表查询器基类"""

    cache_date_field = 'date'  # 报表查询器的日期字段是转换后生成的date

    # 港股财务数据单位转换比例：从元转换为亿元（除以1亿）
    UNIT_CONVERSION_FACTOR = 1e8

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        查询港股财务报表数据（带单位标准化）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 包含data（DataFrame）和unit_map（单位映射）的字典
        """
        # 调用父类query方法获取原始DataFrame
        df = super().query(symbol, start_date, end_date)

        if df.empty:
            return {
                "data": df,
                "unit_map": {}
            }

        # 单位标准化：将元转换为亿元
        normalized_df, unit_map = self._convert_units(df)

        return {
            "data": normalized_df,
            "unit_map": unit_map
        }

    def _convert_units(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        将港股财务数据从元转换为亿元

        Args:
            df: 原始DataFrame

        Returns:
            (转换后的DataFrame, 单位映射字典)
        """
        result_df = df.copy()
        unit_map = {}

        # 定义不需要转换的字段
        non_numeric_fields = {
            'date', 'REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'
        }

        # 转换每一列
        for col in df.columns:
            if col in non_numeric_fields:
                # 非数值字段：保持原值，不转换
                if col == 'date':
                    unit_map[col] = "日期"
                elif col == 'REPORT_DATE':
                    unit_map[col] = "日期"
                else:
                    unit_map[col] = "文本"
            elif pd.api.types.is_numeric_dtype(df[col]):
                # 数值字段：从元转换为亿元
                result_df[col] = df[col] / self.UNIT_CONVERSION_FACTOR
                unit_map[col] = "亿元"
            else:
                # 其他非数值字段（如object类型）：保持原值
                unit_map[col] = "文本"

        return result_df, unit_map

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询港股财务报表原始数据

        使用年度数据以获取完整的年度财务数据
        """
        df = ak.stock_financial_hk_report_em(stock=symbol, symbol=self._get_statement_name(), indicator="年度")

        if df is None or df.empty:
            return self._create_empty_wide_format()

        # 转换为宽表格式
        return self._convert_narrow_to_wide_format(df)

    def _convert_narrow_to_wide_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """将窄表格式转换为宽表格式"""
        if df.empty:
            return self._create_empty_wide_format()

        # 确保必要的列存在
        required_columns = ['REPORT_DATE', 'STD_ITEM_NAME', 'AMOUNT']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"港股财务报表数据缺少必要列: {missing_columns}")

        try:
            # 转换日期列
            df['date'] = pd.to_datetime(df['REPORT_DATE'])

            # 使用pivot_table进行宽表转换，避免数据丢失
            wide_df = df.pivot_table(
                index=['date', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
                columns='STD_ITEM_NAME',
                values='AMOUNT',
                aggfunc='first',  # 使用第一个值，避免重复数据
                fill_value=0  # 空值用0填充
            ).reset_index()

            wide_df.columns.name = None
            # 添加REPORT_DATE字段（从date转换回字符串格式）
            wide_df['REPORT_DATE'] = wide_df['date'].dt.strftime('%Y-%m-%d')

            # 按日期降序排列
            wide_df = wide_df.sort_values('date', ascending=False)

            return wide_df

        except Exception as e:
            # 如果转换失败，直接抛出异常
            raise ValueError(f"港股财务报表窄表转宽表失败: {e}")

    def _create_empty_wide_format(self) -> pd.DataFrame:
        """创建空的宽表格式DataFrame"""
        return pd.DataFrame({
            'date': pd.to_datetime([]),
            'REPORT_DATE': [],
            'SECURITY_CODE': [],
            'SECURITY_NAME_ABBR': []
        })

    def _get_statement_name(self) -> str:
        """获取报表名称 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 _get_statement_name 方法")


class HKStockBalanceSheetQueryer(HKStockStatementQueryerBase):
    """港股资产负债表查询器"""
    cache_query_type = 'hk_balance_sheet'

    def _get_statement_name(self) -> str:
        return "资产负债表"


class HKStockIncomeStatementQueryer(HKStockStatementQueryerBase):
    """港股利润表查询器"""
    cache_query_type = 'hk_income_statement'

    def _get_statement_name(self) -> str:
        return "利润表"


class HKStockCashFlowQueryer(HKStockStatementQueryerBase):
    """港股现金流量表查询器"""
    cache_query_type = 'hk_cash_flow'

    def _get_statement_name(self) -> str:
        return "现金流量表"


# 保持原有的三表合一查询器作为备用
class HKStockStatementQueryer(HKStockStatementQueryerBase):
    """港股财务三表查询器 - 三表合一（备用）"""
    cache_query_type = 'hk_statements'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询港股财务三表原始数据"""
        # 调用akshare API获取港股财务报表数据
        raw_data = ak.stock_financial_hk_report_em(stock=symbol, indicator="年度")

        if raw_data.empty:
            return pd.DataFrame()

        # 转换为宽表格式
        wide_data = self._convert_narrow_to_wide_format(raw_data, symbol)

        return wide_data

    def _get_statement_name(self) -> str:
        """获取报表名称 - 三表合一时不需要指定具体报表"""
        return ""

    def _convert_narrow_to_wide_format(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """将窄表格式转换为宽表格式"""
        if df.empty:
            return self._create_empty_wide_format(symbol)

        # 确保必要的列存在
        required_columns = ['REPORT_DATE', 'STD_ITEM_NAME', 'AMOUNT']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"港股财务三表数据缺少必要列: {missing_columns}")

        try:
            # 转换日期列
            df['date'] = pd.to_datetime(df['REPORT_DATE'])

            # 使用pivot_table进行宽表转换，避免数据丢失
            wide_df = df.pivot_table(
                index=['date', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
                columns='STD_ITEM_NAME',
                values='AMOUNT',
                aggfunc='first',  # 使用第一个值，避免重复数据
                fill_value=0  # 空值用0填充
            ).reset_index()

            # 添加REPORT_DATE字段（从date转换回字符串格式）
            wide_df['REPORT_DATE'] = wide_df['date'].dt.strftime('%Y-%m-%d')

            # 按日期降序排列
            wide_df = wide_df.sort_values('date', ascending=False)

            return wide_df

        except Exception as e:
            # 如果转换失败，直接抛出异常
            raise ValueError(f"港股财务三表窄表转宽表失败: {e}")

    def _create_empty_wide_format(self, symbol: str) -> pd.DataFrame:
        """创建空的宽表格式DataFrame"""
        return pd.DataFrame({
            'date': pd.to_datetime([]),
            'REPORT_DATE': [],
            'SECURITY_CODE': [],
            'SECURITY_NAME_ABBR': []
        })