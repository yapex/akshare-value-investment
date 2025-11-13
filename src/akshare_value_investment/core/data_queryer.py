"""
数据查询器核心接口

定义IDataQueryer接口和IFinancialDataService聚合接口。
"""

from typing import Protocol, List, Optional
import pandas as pd
from .models import MarketType


class IDataQueryer(Protocol):
    """数据查询器接口"""

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询数据并返回DataFrame，支持日期范围

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的财务数据
        """
        ...


class IFinancialDataService(Protocol):
    """财务服务聚合接口"""

    def query_indicators(self, symbol: str, market: MarketType,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """查询财务指标"""
        ...

    def query_balance_sheet(self, symbol: str, market: MarketType,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """查询资产负债表"""
        ...

    def query_income_statement(self, symbol: str, market: MarketType,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> pd.DataFrame:
        """查询利润表"""
        ...

    def query_cash_flow(self, symbol: str, market: MarketType,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """查询现金流量表"""
        ...