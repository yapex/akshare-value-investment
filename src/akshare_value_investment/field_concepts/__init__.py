"""
字段概念映射系统

提供自然语言到财务指标字段的映射功能，支持中文查询到跨市场字段名的转换。
"""

from .models import (
    MarketField,
    ConceptSearchResult,
    ConceptConfig,
)

from .config_manager import ConfigManager
from .search_engine import ConceptSearchEngine

__all__ = [
    "MarketField",
    "ConceptSearchResult",
    "ConceptConfig",
    "ConfigManager",
    "ConceptSearchEngine",
]

__version__ = "1.0.0"