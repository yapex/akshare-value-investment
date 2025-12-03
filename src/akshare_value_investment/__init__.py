"""
akshare-value-investment: 基于akshare和MCP的智能财务数据查询系统

提供跨市场（A股、港股、美股）财务数据查询和MCP协议访问功能。
核心特性：SQLite智能缓存、SOLID架构、MCP标准化接口。
"""

__version__ = "3.0.0"
__author__ = "akshare-value-investment team"

# 导出主要接口
from .core.models import MarketType
from .container import create_container

__all__ = [
    "create_container",
    "MarketType",
]
