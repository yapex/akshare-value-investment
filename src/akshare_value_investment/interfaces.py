"""
核心接口定义 - 简化版本

使用I前缀的命名规范，保持最小化和实用性 - 简化版本，移除字段映射。
"""

from typing import Protocol, Dict, Any, List, Optional, Tuple
from .models import MarketType, FinancialIndicator, QueryResult


# === 核心业务接口 ===

class IMarketAdapter(Protocol):
    """市场适配器接口 - 核心业务接口"""

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """获取指定股票的财务数据"""
        ...


class IMarketIdentifier(Protocol):
    """市场识别接口 - 核心业务接口"""

    def identify(self, symbol: str, default_market: Optional[MarketType] = None) -> Tuple[MarketType, str]:
        """识别股票代码市场类型并标准化"""
        ...


class IQueryService(Protocol):
    """查询服务接口 - 核心业务接口 - 简化版本"""

    def query(self, symbol: str, **kwargs) -> QueryResult:
        """查询单只股票的财务数据"""
        ...

    def get_available_fields(self, market: Optional[MarketType] = None):
        """获取可用字段 - 简化版本返回空，通过raw_data访问原始字段"""
        ...