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
        财年数据处理由上层服务根据frequency参数控制
        """
        return ak.stock_financial_us_analysis_indicator_em(symbol=symbol, indicator="单季报")


class USStockStatementQueryerBase(BaseDataQueryer):
    """美股财务报表查询器基类"""

    cache_date_field = 'date'  # 报表查询器的日期字段是转换后生成的date

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务报表原始数据

        美股财务三表使用年报数据，akshare已返回纯年报数据
        """
        df = ak.stock_financial_us_report_em(
            stock=symbol,
            symbol=self._get_statement_name(),
            indicator="年报"
        )
        if df is None or df.empty:
            return self._create_empty_wide_format()

        # 转换为宽表格式
        return self._process_narrow_table(df)

    def _process_fiscal_year_data_narrow(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理窄表格式的财年数据，进行数据清洗和格式化，但不进行财年过滤"""
        # 确保REPORT_DATE字段存在
        if 'REPORT_DATE' not in df.columns:
            return df

        # 从REPORT_DATE提取年份作为财年
        df_processed = df.copy()
        df_processed['REPORT_DATE'] = pd.to_datetime(df_processed['REPORT_DATE'], errors='coerce')
        df_processed = df_processed.dropna(subset=['REPORT_DATE'])

        # 创建财年字段
        df_processed['FISCAL_YEAR'] = df_processed['REPORT_DATE'].dt.year.astype('Int64')

        # 为每个指标和每个日期选择一条记录（如果有多条重复记录）
        df_best = df_processed.loc[df_processed.groupby(['REPORT_DATE', 'ITEM_NAME'])['REPORT_DATE'].idxmax()]

        # 按报告日期降序排列
        df_best = df_best.sort_values('REPORT_DATE', ascending=False)

        return df_best

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
        # 确保date字段是字符串格式，符合API期望
        wide_df['date'] = pd.to_datetime(wide_df['REPORT_DATE']).dt.strftime('%Y-%m-%d')

        # 调试：打印一些样例数据
        if hasattr(self, '_debug') and self._debug:
            print(f"Generated {len(wide_df)} records with date range: {wide_df['date'].min()} to {wide_df['date'].max()}")

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

        获取三种财务报表的原始数据，不进行财年过滤，
        财年过滤由上层业务服务根据frequency参数控制
        """
        try:
            # 获取三种财务报表
            statements = ["资产负债表", "综合损益表", "现金流量表"]
            all_data = []

            for statement_name in statements:
                try:
                    df = ak.stock_financial_us_report_em(stock=symbol, symbol=statement_name, indicator="年报")
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