"""
财务数据聚合服务

组合多个Queryer，提供统一的财务数据查询接口。
"""

import pandas as pd
from typing import Optional

from ..core.data_queryer import IFinancialDataService
from ..core.models import MarketType
from ..datasource.queryers import (
    AStockIndicatorQueryer,
    AStockBalanceSheetQueryer,
    AStockIncomeStatementQueryer,
    AStockCashFlowQueryer,
    HKStockIndicatorQueryer,
    HKStockStatementQueryer,
    USStockIndicatorQueryer,
    USStockStatementQueryer
)


class FinancialDataService(IFinancialDataService):
    """财务数据聚合服务"""

    def __init__(
        self,
        a_stock_indicators: AStockIndicatorQueryer,
        a_stock_balance_sheet: AStockBalanceSheetQueryer,
        a_stock_income_statement: AStockIncomeStatementQueryer,
        a_stock_cash_flow: AStockCashFlowQueryer,
        hk_stock_indicators: HKStockIndicatorQueryer,
        hk_stock_statement: HKStockStatementQueryer,
        us_stock_indicators: USStockIndicatorQueryer,
        us_stock_statement: USStockStatementQueryer
    ):
        """
        初始化财务数据服务

        Args:
            a_stock_indicators: A股财务指标查询器
            a_stock_balance_sheet: A股资产负债表查询器
            a_stock_income_statement: A股利润表查询器
            a_stock_cash_flow: A股现金流量表查询器
            hk_stock_indicators: 港股财务指标查询器
            hk_stock_statement: 港股财务三表查询器
            us_stock_indicators: 美股财务指标查询器
            us_stock_statement: 美股财务三表查询器
        """
        self.queryers = {
            (MarketType.A_STOCK, 'indicators'): a_stock_indicators,
            (MarketType.A_STOCK, 'balance_sheet'): a_stock_balance_sheet,
            (MarketType.A_STOCK, 'income_statement'): a_stock_income_statement,
            (MarketType.A_STOCK, 'cash_flow'): a_stock_cash_flow,
            (MarketType.HK_STOCK, 'indicators'): hk_stock_indicators,
            (MarketType.HK_STOCK, 'balance_sheet'): hk_stock_statement,
            (MarketType.HK_STOCK, 'income_statement'): hk_stock_statement,
            (MarketType.HK_STOCK, 'cash_flow'): hk_stock_statement,
            (MarketType.US_STOCK, 'indicators'): us_stock_indicators,
            (MarketType.US_STOCK, 'balance_sheet'): us_stock_statement,
            (MarketType.US_STOCK, 'income_statement'): us_stock_statement,
            (MarketType.US_STOCK, 'cash_flow'): us_stock_statement,
        }

    def _get_queryer(self, market: MarketType, query_type: str):
        """获取对应的查询器"""
        queryer = self.queryers.get((market, query_type))
        if queryer is None:
            raise ValueError(f"不支持的市场和查询类型组合: {market}, {query_type}")
        return queryer

    def query_indicators(self, symbol: str, market: MarketType,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """查询财务指标"""
        queryer = self._get_queryer(market, 'indicators')
        return queryer.query(symbol, start_date, end_date)

    def query_balance_sheet(self, symbol: str, market: MarketType,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """查询资产负债表"""
        queryer = self._get_queryer(market, 'balance_sheet')
        return queryer.query(symbol, start_date, end_date)

    def query_income_statement(self, symbol: str, market: MarketType,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> pd.DataFrame:
        """查询利润表"""
        queryer = self._get_queryer(market, 'income_statement')
        return queryer.query(symbol, start_date, end_date)

    def query_cash_flow(self, symbol: str, market: MarketType,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """查询现金流量表"""
        queryer = self._get_queryer(market, 'cash_flow')
        return queryer.query(symbol, start_date, end_date)