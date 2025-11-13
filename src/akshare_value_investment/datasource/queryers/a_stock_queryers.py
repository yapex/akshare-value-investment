"""
A股数据查询器

实现A股财务指标和财务三表（三个独立API）的数据查询器。
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class AStockIndicatorQueryer(BaseDataQueryer):
    """A股财务指标查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股财务指标数据"""
        return ak.stock_financial_abstract(symbol=symbol)


class AStockBalanceSheetQueryer(BaseDataQueryer):
    """A股资产负债表查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股资产负债表数据"""
        return ak.stock_balance_sheet_by_report_em(symbol=symbol)


class AStockIncomeStatementQueryer(BaseDataQueryer):
    """A股利润表查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股利润表数据"""
        return ak.stock_profit_sheet_by_report_em(symbol=symbol)


class AStockCashFlowQueryer(BaseDataQueryer):
    """A股现金流量表查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股现金流量表数据"""
        return ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)