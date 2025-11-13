"""
智能SQLite缓存装饰器

生产级装饰器实现，支持：
1. 透明的缓存集成
2. 智能增量更新
3. 多种日期字段支持
4. 灵活的查询类型配置
5. 详细的日志和监控
"""

import functools
import logging
from typing import Callable, Any, Optional, List, Dict
from datetime import datetime, timedelta
from .sqlite_cache import SQLiteCache

logger = logging.getLogger(__name__)


def smart_sqlite_cache(
    date_field: str = 'date',
    query_type: str = 'indicators',
    cache_adapter: Optional[SQLiteCache] = None,
    cache_path: str = "cache/financial_data.db",
    enable_logging: bool = True
):
    """
    智能SQLite缓存装饰器

    Args:
        date_field: 日期字段名（date/report_date/end_date）
        query_type: 查询类型（indicators/profit/balance/cashflow）
        cache_adapter: 外部缓存适配器实例（可选）
        cache_path: 缓存数据库路径
        enable_logging: 是否启用详细日志

    Returns:
        装饰好的函数

    Usage:
        # 基础用法
        @smart_sqlite_cache(date_field='date', query_type='indicators')
        def get_financial_indicators(symbol, start_date, end_date):
            return akshare.stock_financial_indicators(symbol=symbol)

        # 自定义缓存适配器
        adapter = SQLiteCache("custom/cache.db")
        @smart_sqlite_cache(date_field='report_date', query_type='profit', cache_adapter=adapter)
        def get_profit_statement(symbol, start_date, end_date):
            return akshare.stock_profit_sheet(symbol=symbol)
    """
    def decorator(func: Callable) -> Callable:
        # 初始化缓存适配器
        if cache_adapter is None:
            adapter = SQLiteCache(cache_path)
        else:
            adapter = cache_adapter

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 参数解析 - 期望(symbol, start_date, end_date) 或关键字参数
            symbol, start_date, end_date = _parse_function_args(func, args, kwargs)

            if enable_logging:
                logger.debug(f"🔍 查询 {symbol} {query_type} {start_date} 到 {end_date}")

            # 1. 检查是否需要增量更新
            missing_ranges = adapter._get_missing_date_ranges(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                date_field=date_field,
                query_type=query_type
            )

            # 获取缓存覆盖情况，用于详细日志
            if enable_logging:
                if not missing_ranges:
                    # 完全缓存命中
                    logger.debug(f"✅ 缓存完全命中")
                    # 返回已缓存的完整数据
                    cached_results = adapter.query_by_date_range(
                        symbol, start_date, end_date, date_field, query_type
                    )
                    import pandas as pd
                    return pd.DataFrame(cached_results)
                else:
                    # 有缓存缺失，检查是否需要增量补充
                    is_incremental = len(missing_ranges) == 1 and (
                        (missing_ranges[0]['start'] == start_date and missing_ranges[0]['end'] != end_date) or
                        (missing_ranges[0]['start'] != start_date and missing_ranges[0]['end'] == end_date)
                    )
                    if is_incremental:
                        logger.debug(f"🔄 检测到单边缺失，将按需增量补充")
                    else:
                        logger.debug(f"🔄 检测到多边缺失，将重新获取完整数据")

            # 3. 根据缺失范围调用原函数
            if not missing_ranges:
                # 完全缓存命中，在上面已经返回
                pass
            elif len(missing_ranges) == 1 and (missing_ranges[0]['start'] != start_date or missing_ranges[0]['end'] != end_date):
                # 增量更新：只获取缺失部分
                missing_range = missing_ranges[0]
                logger.debug(f"📡 增量获取缺失数据: {missing_range['start']} 到 {missing_range['end']}")

                # 调用原函数获取缺失数据
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()

                # 更新日期参数为缺失范围
                if 'start_date' in bound_args.arguments:
                    bound_args.arguments['start_date'] = missing_range['start']
                if 'end_date' in bound_args.arguments:
                    bound_args.arguments['end_date'] = missing_range['end']

                api_results = func(*bound_args.args, **bound_args.kwargs)

                # 获取现有缓存数据并合并
                if api_results is not None:
                    # 安全的DataFrame空值检查
                    import pandas as pd
                    if hasattr(api_results, 'empty') and not api_results.empty:
                        saved_count = adapter.save_records(
                            symbol=symbol,
                            records=api_results,
                            date_field=date_field,
                            query_type=query_type
                        )
                        # 保存记录的日志已在sqlite_cache.py中处理，这里不再重复

                # 返回完整范围的合并数据
                cached_results = adapter.query_by_date_range(
                    symbol, start_date, end_date, date_field, query_type
                )
                import pandas as pd
                return pd.DataFrame(cached_results)
            else:
                # 完整重新获取
                logger.debug(f"📡 完整获取数据: {start_date} 到 {end_date}")
                api_results = func(*args, **kwargs)

            if api_results is None or (hasattr(api_results, 'empty') and api_results.empty):
                if enable_logging:
                    logger.warning(f"⚠️ API返回空数据: {symbol}")
                return []

            # 4. 保存到缓存
            saved_count = adapter.save_records(
                symbol=symbol,
                records=api_results,
                date_field=date_field,
                query_type=query_type
            )

            # 保存记录的日志已在sqlite_cache.py中处理，这里不再重复

            return api_results

        # 添加缓存管理方法到包装函数
        wrapper.cache_adapter = adapter

        return wrapper

    return decorator


def _parse_function_args(func: Callable, args: tuple, kwargs: dict) -> tuple:
    """
    解析函数参数，提取(symbol, start_date, end_date)

    支持多种调用方式：
    1. 位置参数：func(symbol, start_date, end_date)
    2. 关键字参数：func(symbol="SH600519", start_date="2023-01-01", end_date="2023-12-31")
    3. 混合参数：func("SH600519", start_date="2023-01-01", end_date="2023-12-31")
    """
    import inspect

    sig = inspect.signature(func)
    bound_args = sig.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()

    # 尝试多种常见的参数名
    param_names = ['symbol', 'start_date', 'end_date', 'symbol_code', 'begin_date', 'finish_date']

    result = []
    for expected_name in ['symbol', 'start_date', 'end_date']:
        value = None

        # 1. 首先尝试精确匹配
        if expected_name in bound_args.arguments:
            value = bound_args.arguments[expected_name]
        else:
            # 2. 尝试模糊匹配
            for param_name, param_value in bound_args.arguments.items():
                if expected_name in param_name.lower() or param_name.lower() in expected_name:
                    value = param_value
                    break

        if value is None:
            raise ValueError(f"无法找到参数: {expected_name}. 可用参数: {list(bound_args.arguments.keys())}")

        result.append(value)

    return tuple(result)


class CacheManager:
    """
    简化的缓存管理器 - 提供基本的缓存统计和清理功能
    """

    def __init__(self, cache_path: str = "cache/financial_data.db"):
        self.adapter = SQLiteCache(cache_path)

    def get_global_stats(self) -> dict:
        """获取全局缓存统计"""
        cache_stats = self.adapter.get_cache_stats()

        return {
            'total_records': cache_stats.total_records,
            'total_queries': cache_stats.total_queries,
            'cache_hits': cache_stats.cache_hits,
            'cache_misses': cache_stats.cache_misses,
            'cache_hit_rate': f"{cache_stats.cache_hit_rate:.2%}"
        }

    def get_all_symbols_summary(self) -> Dict[str, Dict]:
        """获取所有股票的缓存概要"""
        conn = self.adapter._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT symbol FROM financial_data ORDER BY symbol
        """)

        symbols = list(row[0] for row in cursor.fetchall())
        return symbols

    def close(self) -> None:
        """关闭缓存管理器"""
        self.adapter.close()


# 全局缓存管理器实例
_global_cache_manager = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager