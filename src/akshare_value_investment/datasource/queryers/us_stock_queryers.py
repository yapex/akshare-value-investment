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

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """查询美股财务指标数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        # AkShare 美股指标API本身不支持日期参数，所以这里忽略日期参数
        # 日期过滤将由上层的缓存和过滤逻辑处理
        return ak.stock_financial_us_analysis_indicator_em(symbol=symbol)


class USStockStatementQueryer(BaseDataQueryer):
    """美股财务三表查询器 - 自动转换为宽表格式"""

    # 重置缓存配置
    cache_query_type = 'statements'

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """查询美股财务三表数据（返回统一宽表格式）

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        # AkShare 美股财务三表API需要特殊参数，获取三张表的数据并合并
        # 日期过滤将由上层的缓存和过滤逻辑处理

        all_data = []

        # 获取三张表的数据
        statements = [
            {"symbol": "资产负债表", "indicator": "年报"},
            {"symbol": "综合损益表", "indicator": "年报"},
            {"symbol": "现金流量表", "indicator": "年报"}
        ]

        for statement_config in statements:
            try:
                df = ak.stock_financial_us_report_em(
                    stock=symbol,
                    symbol=statement_config["symbol"],
                    indicator=statement_config["indicator"]
                )

                if df is not None and not df.empty:
                    # 添加报表类型标识
                    df['STATEMENT_TYPE'] = statement_config["symbol"]
                    all_data.append(df)
            except Exception as e:
                print(f"获取 {statement_config['symbol']} 数据时出错: {e}")
                continue

        # 合并所有报表数据
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
        else:
            df = pd.DataFrame()

        # 验证是否为窄表结构并进行数据处理
        if df is not None and not df.empty:
            required_fields = ["ITEM_NAME", "AMOUNT"]
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
        df = df.dropna(subset=["ITEM_NAME", "AMOUNT"])

        # 确保AMOUNT是数值类型
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")

        # 转换为宽表格式
        wide_df = df.pivot_table(
            index=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
            columns='ITEM_NAME',
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
        # 定义常见的财务项目列（美股）
        # 注意：真实API返回中文字段名，这里应该使用中文字段名
        common_items = [
            '总资产', '总负债', '所有者权益合计',
            '流动资产合计', '流动负债合计', '非流动资产合计', '非流动负债合计',
            '营业收入', '营业成本', '净利润', '现金及现金等价物'
        ]

        # 创建空DataFrame
        columns = ['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'] + common_items
        empty_df = pd.DataFrame(columns=columns)

        return empty_df