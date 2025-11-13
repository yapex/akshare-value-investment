"""
港股数据查询器

实现港股财务指标和财务三表的数据查询器。
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer
from ...core.models import MarketType


class HKStockIndicatorQueryer(BaseDataQueryer):
    """港股财务指标查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询港股财务指标数据"""
        return ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)


class HKStockStatementQueryer(BaseDataQueryer):
    """港股财务三表查询器 - 解决腾讯净资产问题"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询港股财务三表数据"""
        return ak.stock_financial_hk_report_em(stock=symbol)