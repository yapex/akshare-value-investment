"""
数据查询器基类

提供通用的数据查询功能，使用SQLite智能缓存（支持增量更新）。
"""

from typing import Optional
import pandas as pd
from datetime import datetime

from ...core.data_queryer import IDataQueryer
from ...cache.smart_decorator import smart_sqlite_cache


class BaseDataQueryer(IDataQueryer):
    """数据查询器基类 - 使用SQLite智能缓存"""

    # 子类可配置的缓存参数
    cache_date_field = 'date'
    cache_query_type = 'indicators'  # 默认为财务指标

    def __init__(self):
        """初始化查询器"""
        # 应用智能缓存装饰器
        self._query_with_dates = smart_sqlite_cache(
            date_field=self.cache_date_field,
            query_type=self.cache_query_type
        )(self._query_with_dates_original)

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询数据 - 带日期过滤和缓存

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的财务数据
        """
        return self._query_with_dates(symbol, start_date, end_date)

    def _query_with_dates_original(self, symbol: str, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """
        实际查询逻辑 - 原始查询方法（将被装饰器包装）

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的财务数据
        """
        # 获取原始数据
        df = self._query_raw(symbol)

        # 如果没有日期过滤要求，直接返回
        if not start_date and not end_date:
            return df

        # 应用日期过滤
        return self._filter_by_date_range(df, start_date, end_date)

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        获取原始财务数据 - 子类实现

        Args:
            symbol: 股票代码

        Returns:
            DataFrame格式的原始财务数据
        """
        raise NotImplementedError("子类必须实现 _query_raw 方法")

    def _filter_by_date_range(self, df: pd.DataFrame, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        日期过滤逻辑

        Args:
            df: 原始DataFrame
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的DataFrame
        """
        if not start_date and not end_date:
            return df

        # 尝试从DataFrame中识别日期列
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or '时间' in col.lower() or '报告期' in col.lower():
                date_columns.append(col)

        if not date_columns:
            # 如果没有找到日期列，返回原始数据
            return df

        # 转换日期格式
        try:
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_dt = None

            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_dt = None
        except ValueError:
            # 日期格式错误，返回原始数据
            return df

        # 对每个日期列进行过滤
        filtered_dfs = []
        for date_col in date_columns:
            try:
                # 尝试转换日期列
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')

                # 应用日期过滤
                mask = pd.Series([True] * len(df_copy))  # 默认包含所有行

                if start_dt is not None:
                    mask = mask & (df_copy[date_col] >= start_dt)
                if end_dt is not None:
                    mask = mask & (df_copy[date_col] <= end_dt)

                filtered_df = df_copy[mask]
                if not filtered_df.empty:
                    filtered_dfs.append(filtered_df)
            except Exception:
                # 如果转换失败，跳过此列
                continue

        # 如果有过滤后的数据，返回第一个；否则返回原始数据
        return filtered_dfs[0] if filtered_dfs else df