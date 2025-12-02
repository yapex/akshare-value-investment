from typing import Optional, ClassVar, Tuple
import pandas as pd

from .interfaces import IDataQueryer
from ...core.models import MarketType
from ...core.stock_identifier import StockIdentifier


def create_cached_query_method(cache_date_field: str, cache_query_type: str, cache=None):
    def cached_query(self, symbol: str, start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> pd.DataFrame:
        cache_key = f"{cache_query_type}:{symbol}"

        # 使用注入的缓存实例，如果没有则创建默认实例
        if cache is not None:
            cache_instance = cache
        else:
            import diskcache
            cache_instance = diskcache.Cache(".cache/diskcache")

        cached_data = cache_instance.get(cache_key)

        if cached_data is not None:
            if isinstance(cached_data, pd.DataFrame):
                return _filter_data_by_date_range(cached_data, start_date, end_date, cache_date_field)
            else:
                cache_instance.delete(cache_key)

        raw_data = self._query_raw(symbol)

        if raw_data is not None and not raw_data.empty:
            cache_instance.set(cache_key, raw_data, expire=30*24*3600)

        return _filter_data_by_date_range(raw_data, start_date, end_date, cache_date_field)

    return cached_query


def _filter_data_by_date_range(data: pd.DataFrame, start_date: Optional[str],
                              end_date: Optional[str], date_field: str) -> pd.DataFrame:
    """
    根据日期范围过滤数据

    Args:
        data: 完整的财务数据DataFrame
        start_date: 开始日期，YYYY-MM-DD格式
        end_date: 结束日期，YYYY-MM-DD格式
        date_field: 日期字段名

    Returns:
        过滤后的DataFrame
    """
    if data is None or data.empty:
        return data

    # 如果没有日期过滤条件，直接返回原数据
    if start_date is None and end_date is None:
        return data

    filtered_data = data.copy()

    # 确保日期字段是datetime类型
    if date_field not in filtered_data.columns:
        # 如果指定的日期字段不存在，尝试常见的日期字段名
        possible_date_fields = [date_field, 'date', 'DATE', 'report_date', 'REPORT_DATE', 'datetime', 'DATETIME']
        found_date_field = None
        for field in possible_date_fields:
            if field in filtered_data.columns:
                found_date_field = field
                break

        if found_date_field is None:
            # 如果找不到日期字段，返回原数据
            return data

        date_field = found_date_field

    if not pd.api.types.is_datetime64_any_dtype(filtered_data[date_field]):
        filtered_data[date_field] = pd.to_datetime(filtered_data[date_field], errors='coerce')

    # 应用日期过滤
    if start_date:
        start_dt = pd.to_datetime(start_date)
        filtered_data = filtered_data[filtered_data[date_field] >= start_dt]

    if end_date:
        end_dt = pd.to_datetime(end_date)
        filtered_data = filtered_data[filtered_data[date_field] <= end_dt]

    return filtered_data


class BaseDataQueryer(IDataQueryer):

    cache_date_field: ClassVar[str] = 'date'
    cache_query_type: ClassVar[str] = 'indicators'

    def __init__(self, stock_identifier: Optional[StockIdentifier] = None, cache=None):
        try:
            self._stock_identifier = stock_identifier or StockIdentifier()
            self._cache = cache  # 注入缓存实例

            cached_method = create_cached_query_method(
                cache_date_field=self.cache_date_field,
                cache_query_type=self.cache_query_type,
                cache=self._cache
            )

            self._query_with_dates = cached_method.__get__(self, type(self))

        except Exception as e:
            raise TypeError(f"初始化查询器失败，请检查缓存配置: {e}")

    def _format_symbol_for_api(self, symbol: str) -> str:
        try:
            if not symbol or not isinstance(symbol, str):
                raise ValueError(f"股票代码不能为空且必须为字符串：{symbol}")

            symbol = symbol.strip()
            if not symbol:
                raise ValueError("股票代码不能为空字符串")

            if symbol.startswith(("SH", "SZ")) and len(symbol) == 8 and symbol[2:].isdigit():
                return symbol

            market_type, standardized_symbol = self._identify_market_type(symbol)

            if market_type == MarketType.A_STOCK:
                if len(standardized_symbol) == 6:
                    if standardized_symbol.startswith('6'):
                        return f"SH{standardized_symbol}"
                    else:
                        return f"SZ{standardized_symbol}"
                else:
                    raise ValueError(f"A股代码格式不正确：{symbol} (标准化后：{standardized_symbol})")

            elif market_type == MarketType.HK_STOCK:
                formatted = self._stock_identifier.format_symbol(market_type, standardized_symbol)
                if len(formatted) != 5 or not formatted.isdigit():
                    raise ValueError(f"港股代码格式化失败：{symbol} → {formatted} (期望5位数字)")
                return formatted

            elif market_type == MarketType.US_STOCK:
                formatted = self._stock_identifier.format_symbol(market_type, standardized_symbol)
                # 美股代码格式检查：允许字母和连字符，长度1-10字符，大写
                if not (1 <= len(formatted) <= 10):
                    raise ValueError(f"美股代码格式化失败：{symbol} → {formatted} (期望1-10字符)")
                if not all(c.isupper() or c == '-' for c in formatted):
                    raise ValueError(f"美股代码格式化失败：{symbol} → {formatted} (期望大写字母和连字符)")
                return formatted

            else:
                raise ValueError(f"不支持的市场类型：{market_type}")

        except Exception as e:
            raise ValueError(f"股票代码格式转换失败：{symbol}，错误：{e}")

    def _identify_market_type(self, symbol: str) -> Tuple[MarketType, str]:
        if symbol.isdigit():
            if len(symbol) == 6:
                return MarketType.A_STOCK, symbol
            elif len(symbol) <= 5:
                return MarketType.HK_STOCK, symbol
            else:
                raise ValueError(f"无法识别的数字股票代码：{symbol}")
        else:
            try:
                return self._stock_identifier.identify(symbol)
            except Exception:
                return MarketType.US_STOCK, symbol.upper()

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        formatted_symbol = self._format_symbol_for_api(symbol)
        return self._query_with_dates(formatted_symbol, start_date, end_date)

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        raise NotImplementedError("子类必须实现 _query_raw 方法以提供具体的数据获取逻辑")