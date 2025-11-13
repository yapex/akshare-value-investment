"""
SQLite智能缓存模块

提供高性能的财务数据缓存解决方案，支持：
- 智能增量更新：自动识别数据缺失，按需补充
- 高效查询：基于SQL BETWEEN的范围查询
- 多类型支持：财务指标、资产负债表、利润表、现金流量表
- 线程安全：支持高并发访问
"""

from .sqlite_cache import SQLiteCache
from .smart_decorator import smart_sqlite_cache

__all__ = [
    'SQLiteCache',
    'smart_sqlite_cache'
]

__version__ = '1.0.0'