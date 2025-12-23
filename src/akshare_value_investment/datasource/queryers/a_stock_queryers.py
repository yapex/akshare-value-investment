"""A股数据查询器模块"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any

from .base_queryer import BaseDataQueryer
from ...core.unit_converter import UnitConverter


class AStockIndicatorQueryer(BaseDataQueryer):
    """A股财务指标查询器"""

    cache_query_type = 'a_stock_indicators'
    cache_date_field = '报告期'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股财务指标原始数据"""
        return ak.stock_financial_abstract_ths(symbol=symbol)


class AStockBalanceSheetQueryer(BaseDataQueryer):
    """A股资产负债表查询器"""

    cache_query_type = 'a_stock_balance'
    cache_date_field = '报告期'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股资产负债表原始数据"""
        return ak.stock_financial_debt_ths(symbol=symbol)

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        查询A股资产负债表数据（带单位标准化）

        Returns:
            Dict[str, Any]: 包含data（DataFrame）和unit_map（单位映射）的字典
        """
        # 调用父类query方法获取原始DataFrame
        df = super().query(symbol, start_date, end_date)

        # 单位标准化
        normalized_df, unit_map = UnitConverter.convert_dataframe(df)

        return {
            "data": normalized_df,
            "unit_map": unit_map
        }


class AStockIncomeStatementQueryer(BaseDataQueryer):
    """A股利润表查询器"""

    cache_query_type = 'a_stock_profit'
    cache_date_field = '报告期'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股利润表原始数据"""
        return ak.stock_financial_benefit_ths(symbol=symbol)

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        查询A股利润表数据（带单位标准化）

        Returns:
            Dict[str, Any]: 包含data（DataFrame）和unit_map（单位映射）的字典
        """
        # 调用父类query方法获取原始DataFrame
        df = super().query(symbol, start_date, end_date)

        # 单位标准化
        normalized_df, unit_map = UnitConverter.convert_dataframe(df)

        return {
            "data": normalized_df,
            "unit_map": unit_map
        }


class AStockCashFlowQueryer(BaseDataQueryer):
    """A股现金流量表查询器"""

    cache_query_type = 'a_stock_cashflow'
    cache_date_field = '报告期'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股现金流量表原始数据"""
        return ak.stock_financial_cash_ths(symbol=symbol)

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        查询A股现金流量表数据（带单位标准化）

        Returns:
            Dict[str, Any]: 包含data（DataFrame）和unit_map（单位映射）的字典
        """
        # 调用父类query方法获取原始DataFrame
        df = super().query(symbol, start_date, end_date)

        # 单位标准化
        normalized_df, unit_map = UnitConverter.convert_dataframe(df)

        return {
            "data": normalized_df,
            "unit_map": unit_map
        }