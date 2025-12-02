"""美股数据查询器模块"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class USStockIndicatorQueryer(BaseDataQueryer):
    """美股财务指标查询器"""
    cache_query_type = 'us_indicators'
    cache_date_field = 'date'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务指标原始数据

        使用单季报数据以获取最完整的数据覆盖，包括季度和年度数据
        单季报数据量最大（约68条），覆盖2008-2025年，包含年度数据
        """
        return ak.stock_financial_us_analysis_indicator_em(symbol=symbol, indicator="单季报")


class USStockStatementQueryerBase(BaseDataQueryer):
    """美股财务报表查询器基类"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务报表原始数据

        使用单季报数据以获取最完整的数据覆盖，包括季度和年度数据
        单季报数据量最大，覆盖时间范围更广
        """
        df = ak.stock_financial_us_report_em(stock=symbol, symbol=self._get_statement_name(), indicator="单季报")
        return self._process_narrow_table(df)

    def _process_narrow_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理窄表数据"""
        if df is not None and not df.empty:
            required_fields = ["ITEM_NAME", "AMOUNT"]
            if all(field in df.columns for field in required_fields):
                return self._convert_narrow_to_wide_format(df)
        return self._create_empty_wide_format()

    def _convert_narrow_to_wide_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """将窄表格式转换为宽表格式"""
        df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"], errors="coerce")
        df = df.sort_values("REPORT_DATE", ascending=False)
        df = df.dropna(subset=["ITEM_NAME", "AMOUNT"])
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")
        wide_df = df.pivot_table(
            index=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
            columns='ITEM_NAME',
            values='AMOUNT',
            fill_value=0,
            aggfunc='first'
        ).reset_index()
        wide_df.columns.name = None
        wide_df['date'] = wide_df['REPORT_DATE'].dt.strftime('%Y-%m-%d')
        return wide_df

    def _create_empty_wide_format(self) -> pd.DataFrame:
        """创建空的宽表格式DataFrame"""
        return pd.DataFrame()

    def _get_statement_name(self) -> str:
        """获取报表名称 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 _get_statement_name 方法")


class USStockBalanceSheetQueryer(USStockStatementQueryerBase):
    """美股资产负债表查询器"""
    cache_query_type = 'us_balance_sheet'

    def _get_statement_name(self) -> str:
        return "资产负债表"


class USStockIncomeStatementQueryer(USStockStatementQueryerBase):
    """美股利润表查询器"""
    cache_query_type = 'us_income_statement'

    def _get_statement_name(self) -> str:
        return "综合损益表"


class USStockCashFlowQueryer(USStockStatementQueryerBase):
    """美股现金流量表查询器"""
    cache_query_type = 'us_cash_flow'

    def _get_statement_name(self) -> str:
        return "现金流量表"


# 测试所需的组合查询器
class USStockStatementQueryer(USStockStatementQueryerBase):
    """美股财务三表查询器 - 测试用"""
    cache_query_type = 'us_statements'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务三表原始数据

        使用单季报数据以获取最完整的数据覆盖，包括季度和年度数据
        """
        try:
            # 获取三种财务报表
            statements = ["资产负债表", "综合损益表", "现金流量表"]
            all_data = []

            for statement_name in statements:
                try:
                    df = ak.stock_financial_us_report_em(stock=symbol, symbol=statement_name, indicator="单季报")
                    if df is not None and not df.empty:
                        df = self._process_narrow_table(df)
                        all_data.append(df)
                except Exception:
                    continue

            if all_data:
                # 合并所有报表数据
                merged_df = all_data[0]
                for df in all_data[1:]:
                    if not df.empty:
                        merged_df = pd.merge(merged_df, df, on=['date', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'], how='outer')
                return merged_df.fillna(0)

            # 如果没有获取到任何数据，返回空的宽表结构
            return pd.DataFrame(columns=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'])
        except Exception:
            # 整体异常处理，返回空的宽表结构
            return pd.DataFrame(columns=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'])