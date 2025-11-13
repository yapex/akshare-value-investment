"""
智能字段路由器数据模型

定义字段路由相关的数据结构和枚举类型
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .models import FieldInfo


class DataSourceType(Enum):
    """数据源类型枚举"""
    FINANCIAL_INDICATORS = "financial_indicators"
    FINANCIAL_STATEMENTS = "financial_statements"
    UNKNOWN = "unknown"


class QueryIntent(Enum):
    """查询意图枚举"""
    FINANCIAL_INDICATORS = "financial_indicators"
    FINANCIAL_STATEMENTS = "financial_statements"
    AMBIGUOUS = "ambiguous"


@dataclass
class FieldCandidate:
    """候选字段"""
    field_id: str                      # 字段ID
    market_id: str                     # 市场ID
    field_info: Optional[FieldInfo]    # 字段信息
    source_type: DataSourceType        # 数据源类型
    priority: int                      # 优先级
    similarity: float                  # 相似度得分
    context: Dict[str, Any] = None    # 上下文信息

    def __post_init__(self):
        """后初始化处理"""
        if self.context is None:
            self.context = {}


@dataclass
class FieldRouteResult:
    """字段路由结果"""
    field_id: str                      # 最终选择的字段ID
    market_id: str                     # 市场ID
    field_info: FieldInfo              # 字段信息
    source_type: DataSourceType        # 数据源类型
    confidence_score: float            # 置信度得分 (0-1)
    context: Dict[str, Any]           # 上下文信息
    routing_metadata: Dict[str, Any]  # 路由元数据

    def __post_init__(self):
        """后初始化处理"""
        if self.routing_metadata is None:
            self.routing_metadata = {}


@dataclass
class QueryContext:
    """查询上下文"""
    symbol: str                        # 股票代码
    market_id: str                     # 市场ID
    query: str                         # 原始查询
    industry: Optional[str] = None     # 行业信息
    market_cap: Optional[str] = None   # 市值信息
    user_preferences: Dict[str, Any] = None  # 用户偏好

    def __post_init__(self):
        """后初始化处理"""
        if self.user_preferences is None:
            self.user_preferences = {}


@dataclass
class RoutingMetrics:
    """路由性能指标"""
    total_candidates: int              # 总候选字段数
    processed_candidates: int          # 处理的候选字段数
    intent_confidence: float          # 意图识别置信度
    processing_time_ms: float         # 处理时间（毫秒）
    cache_hit: bool                   # 是否命中缓存
    fallback_used: bool               # 是否使用了降级策略