"""A股数据查询器模块"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


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
    cache_date_field = 'REPORT_DATE'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股资产负债表原始数据"""
        return ak.stock_financial_debt_ths(symbol=symbol)


class AStockIncomeStatementQueryer(BaseDataQueryer):
    """A股利润表查询器"""

    cache_query_type = 'a_stock_profit'
    cache_date_field = 'REPORT_DATE'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股利润表原始数据"""
        return ak.stock_financial_benefit_ths(symbol=symbol)


class AStockCashFlowQueryer(BaseDataQueryer):
    """A股现金流量表查询器"""

    cache_query_type = 'a_stock_cashflow'
    cache_date_field = 'REPORT_DATE'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股现金流量表原始数据"""
        return ak.stock_financial_cash_ths(symbol=symbol)