"""
A股数据查询器

实现A股财务指标和财务三表（三个独立API）的数据查询器。
使用同花顺(ths)数据源API，提供完整的财务报表数据。
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class AStockIndicatorQueryer(BaseDataQueryer):
    """A股财务指标查询器"""

    cache_query_type = 'a_stock_indicators'  # A股财务指标

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股财务指标数据"""
        return ak.stock_financial_abstract_ths(symbol=symbol)


class AStockBalanceSheetQueryer(BaseDataQueryer):
    """A股资产负债表查询器

    注意：使用同花顺的 debt API，实际包含完整的资产负债表数据，包括：
    - 资产类：流动资产、非流动资产、总资产
    - 负债类：流动负债、非流动负债、总负债
    - 权益类：股东权益、少数股东权益
    """

    cache_query_type = 'a_stock_balance'  # A股资产负债表
    cache_date_field = 'report_date'  # 资产负债表使用report_date字段

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股资产负债表数据"""
        return ak.stock_financial_debt_ths(symbol=symbol)


class AStockIncomeStatementQueryer(BaseDataQueryer):
    """A股利润表查询器

    注意：使用同花顺的 benefit API，实际包含完整的利润表数据，包括：
    - 收入类：营业总收入、营业收入
    - 成本费用类：营业成本、销售费用、管理费用、研发费用
    - 利润类：营业利润、利润总额、净利润
    - 每股收益：基本每股收益、稀释每股收益
    """

    cache_query_type = 'a_stock_profit'  # A股利润表
    cache_date_field = 'report_date'  # 利润表使用report_date字段

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股利润表数据"""
        return ak.stock_financial_benefit_ths(symbol=symbol)


class AStockCashFlowQueryer(BaseDataQueryer):
    """A股现金流量表查询器

    注意：使用同花顺的 cash API，包含完整的现金流量表数据，包括：
    - 经营活动现金流：销售商品收款、购买商品付款等
    - 投资活动现金流：投资收回、购建资产等
    - 筹资活动现金流：吸收投资、偿还债务、分红等
    - 现金净变动：现金及现金等价物净增加额
    - 补充资料：间接法调节过程
    """

    cache_query_type = 'a_stock_cashflow'  # A股现金流量表
    cache_date_field = 'report_date'  # 现金流量表使用report_date字段

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股现金流量表数据"""
        return ak.stock_financial_cash_ths(symbol=symbol)