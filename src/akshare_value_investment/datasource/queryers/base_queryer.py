"""
数据查询器基类

提供通用的数据查询功能，使用SQLite智能缓存（支持增量更新）。
"""

from typing import Optional, ClassVar
import pandas as pd

from ...core.data_queryer import IDataQueryer
from ...cache.smart_decorator import smart_sqlite_cache as smart_cache


def create_cached_query_method(cache_date_field: str, cache_query_type: str):
    """
    工厂函数：创建带缓存装饰器的查询方法

    Args:
        cache_date_field: 日期字段名
        cache_query_type: 查询类型

    Returns:
        装饰好的查询方法
    """
    @smart_cache(date_field=cache_date_field, query_type=cache_query_type)
    def cached_query(self, symbol: str, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> pd.DataFrame:
        """
        实际查询逻辑 - 带缓存装饰器的方法

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的财务数据
        """
        # 直接获取原始数据，日期过滤由缓存层处理
        return self._query_raw(symbol, start_date, end_date)

    return cached_query


class BaseDataQueryer(IDataQueryer):
    """数据查询器基类 - 使用SQLite智能缓存"""

    # 子类可配置的缓存参数
    cache_date_field: ClassVar[str] = 'date'
    cache_query_type: ClassVar[str] = 'indicators'  # 默认为财务指标

    def __init__(self):
        """初始化查询器"""
        # 使用工厂函数创建带缓存装饰器的查询方法
        self._query_with_dates = create_cached_query_method(
            cache_date_field=self.cache_date_field,
            cache_query_type=self.cache_query_type
        ).__get__(self, type(self))

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

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取原始财务数据 - 子类实现

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame格式的原始财务数据
        """
        raise NotImplementedError("子类必须实现 _query_raw 方法")

  