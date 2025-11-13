"""
美股数据查询器

实现美股财务指标和财务三表（统一API）的数据查询器。
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class USStockIndicatorQueryer(BaseDataQueryer):
    """美股财务指标查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务指标数据"""
        return ak.stock_financial_us_analysis_indicator_em(symbol=symbol)


class USStockStatementQueryer(BaseDataQueryer):
    """美股财务三表查询器"""

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询美股财务三表数据"""
        return ak.stock_financial_us_report_em(symbol=symbol)