"""
优化版数据查询器基类

提供更智能的缓存策略，支持按日期范围缓存和查询优化。
"""

from typing import Optional, Tuple
import pandas as pd
from datetime import datetime
import hashlib

from ...core.data_queryer import IDataQueryer
from ...smart_cache import smart_cache


class OptimizedBaseDataQueryer(IDataQueryer):
    """优化版数据查询器基类 - 智能缓存策略"""

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        智能查询策略：
        1. 如果查询的是最近数据（如最近3年），使用全量缓存
        2. 如果查询的是特定历史范围，考虑精确查询
        3. 自动选择最优查询策略

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的财务数据
        """
        # 智能策略选择
        query_strategy = self._determine_query_strategy(start_date, end_date)

        if query_strategy == "full_cached":
            # 策略1：查询全量数据并缓存（适合近期数据查询）
            df = self._query_raw_cached(symbol)
            return self._filter_by_date_range(df, start_date, end_date)

        elif query_strategy == "direct":
            # 策略2：直接查询精确范围（如果API支持）
            # 注意：这需要akshare API支持日期参数，目前大部分不支持
            df = self._query_raw(symbol)
            return self._filter_by_date_range(df, start_date, end_date)

        else:
            # 策略3：默认使用缓存数据
            df = self._query_raw_cached(symbol)
            return self._filter_by_date_range(df, start_date, end_date)

    def _determine_query_strategy(self, start_date: Optional[str],
                                 end_date: Optional[str]) -> str:
        """
        智能确定查询策略

        Returns:
            "full_cached": 查询并缓存全量数据
            "direct": 直接查询精确范围
            "default": 使用默认策略
        """
        if not start_date and not end_date:
            # 无日期限制，使用全量缓存
            return "full_cached"

        try:
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                now = datetime.now()

                # 如果查询的是最近3年内的数据，使用全量缓存
                if (now - end_dt).days <= 3 * 365:
                    return "full_cached"

            return "default"

        except ValueError:
            return "default"

    @smart_cache("financial_full_data")  # 缓存全量数据
    def _query_raw_cached(self, symbol: str) -> pd.DataFrame:
        """
        查询并缓存全量数据

        Args:
            symbol: 股票代码

        Returns:
            DataFrame格式的完整财务数据
        """
        return self._query_raw(symbol)

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        实际查询逻辑 - 子类实现

        Args:
            symbol: 股票代码

        Returns:
            DataFrame格式的财务数据
        """
        raise NotImplementedError("子类必须实现 _query_raw 方法")

    def _filter_by_date_range(self, df: pd.DataFrame, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        优化的日期过滤逻辑

        Args:
            df: 原始DataFrame
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的DataFrame
        """
        if not start_date and not end_date:
            return df

        # 快速路径：如果数据量小，直接使用原始过滤
        if len(df) <= 100:
            return self._filter_by_date_range_naive(df, start_date, end_date)

        # 优化路径：大数据量时的智能过滤
        return self._filter_by_date_range_optimized(df, start_date, end_date)

    def _filter_by_date_range_naive(self, df: pd.DataFrame, start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> pd.DataFrame:
        """
        简单日期过滤（适用于小数据集）
        """
        # 原有的过滤逻辑...
        # 这里复用之前的实现
        if not start_date and not end_date:
            return df

        # 尝试从DataFrame中识别日期列
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or '时间' in col.lower() or '报告期' in col.lower():
                date_columns.append(col)

        if not date_columns:
            return df

        # 转换日期格式并过滤
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
            return df

        filtered_dfs = []
        for date_col in date_columns:
            try:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')

                mask = pd.Series([True] * len(df_copy))
                if start_dt is not None:
                    mask = mask & (df_copy[date_col] >= start_dt)
                if end_dt is not None:
                    mask = mask & (df_copy[date_col] <= end_dt)

                filtered_df = df_copy[mask]
                if not filtered_df.empty:
                    filtered_dfs.append(filtered_df)
            except Exception:
                continue

        return filtered_dfs[0] if filtered_dfs else df

    def _filter_by_date_range_optimized(self, df: pd.DataFrame, start_date: Optional[str] = None,
                                       end_date: Optional[str] = None) -> pd.DataFrame:
        """
        优化版日期过滤（适用于大数据集）
        """
        # 预编译日期格式，提高性能
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
            return df

        # 智能日期列识别和缓存
        date_col = self._find_best_date_column(df)
        if not date_col:
            return df

        # 使用vectorized操作进行过滤
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')

            # 移除NaT行，提高过滤性能
            df_copy = df_copy.dropna(subset=[date_col])

            # 构建过滤条件
            conditions = []
            if start_dt is not None:
                conditions.append(df_copy[date_col] >= start_dt)
            if end_dt is not None:
                conditions.append(df_copy[date_col] <= end_dt)

            if conditions:
                mask = conditions[0]
                for condition in conditions[1:]:
                    mask = mask & condition
                df_copy = df_copy[mask]

            return df_copy

        except Exception:
            # 如果优化过滤失败，回退到简单过滤
            return self._filter_by_date_range_naive(df, start_date, end_date)

    def _find_best_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        智能识别最佳日期列

        Returns:
            最适合用于日期过滤的列名
        """
        # 优先级排序的日期列名
        date_column_priorities = [
            'REPORT_DATE', 'report_date',  # 港股美股常用
            '日期', 'DATE', 'date',        # 通用日期列
            '报告期', 'period',           # 报告期
            'END_DATE', 'end_date',      # 结束日期
            'NOTICE_DATE', 'notice_date'  # 公告日期
        ]

        # 按优先级查找存在的日期列
        for col in date_column_priorities:
            if col in df.columns:
                return col

        # 如果没找到，进行模糊匹配
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', '时间', '报告期', '时间']):
                return col

        return None

    def get_cache_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            缓存命中率和性能统计
        """
        # 这里可以集成SmartCache的统计功能
        return {
            "strategy": "optimized_intelligent_cache",
            "note": "使用智能缓存策略，根据查询模式自动优化"
        }