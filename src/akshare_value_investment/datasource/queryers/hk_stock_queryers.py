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

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """查询港股财务指标数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        # AkShare 港股指标API本身不支持日期参数，所以这里忽略日期参数
        # 日期过滤将由上层的缓存和过滤逻辑处理
        return ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)


class HKStockStatementQueryer(BaseDataQueryer):
    """港股财务三表查询器 - 自动转换为宽表格式"""

    # 重置缓存配置
    cache_query_type = 'statements'

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """查询港股财务三表数据（返回统一宽表格式）

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        # AkShare 港股财务三表API本身不支持日期参数，所以这里忽略日期参数
        # 日期过滤将由上层的缓存和过滤逻辑处理
        df = ak.stock_financial_hk_report_em(stock=symbol)

        # 验证是否为窄表结构并进行数据处理
        if df is not None and not df.empty:
            required_fields = ["STD_ITEM_NAME", "AMOUNT"]
            if all(field in df.columns for field in required_fields):
                # 确认为窄表结构，转换为宽表格式
                df = self._convert_narrow_to_wide_format(df, symbol)
        else:
            # 如果没有数据，返回空的宽表结构
            df = self._create_empty_wide_format(symbol)

        return df

    def _convert_narrow_to_wide_format(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """将窄表格式转换为宽表格式

        Args:
            df: 窄表格式的财务三表数据
            symbol: 股票代码

        Returns:
            宽表格式的财务三表数据
        """
        # 数据预处理
        if "REPORT_DATE" in df.columns:
            df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"], errors="coerce")
            df = df.sort_values("REPORT_DATE", ascending=False)

        # 移除空值行
        df = df.dropna(subset=["STD_ITEM_NAME", "AMOUNT"])

        # 确保AMOUNT是数值类型
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")

        # 转换为宽表格式
        wide_df = df.pivot_table(
            index=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
            columns='STD_ITEM_NAME',
            values='AMOUNT',
            fill_value=0,
            aggfunc='first'  # 如果有重复，取第一个
        ).reset_index()

        # 重置列名
        wide_df.columns.name = None
        wide_df = wide_df.reset_index(drop=True)

        # 添加统一的date字段（用于缓存）
        wide_df['date'] = pd.to_datetime(wide_df['REPORT_DATE']).dt.strftime('%Y-%m-%d')

        return wide_df

    def _create_empty_wide_format(self, symbol: str) -> pd.DataFrame:
        """创建空的宽表结构

        Args:
            symbol: 股票代码

        Returns:
            空的宽表结构DataFrame
        """
        # 定义常见的财务项目列
        common_items = [
            '资产总计', '负债合计', '所有者权益合计',
            '流动资产合计', '流动负债合计', '非流动资产合计', '非流动负债合计',
            '营业收入', '营业成本', '净利润', '现金及现金等价物余额'
        ]

        # 创建空DataFrame
        columns = ['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'] + common_items
        empty_df = pd.DataFrame(columns=columns)

        return empty_df

    