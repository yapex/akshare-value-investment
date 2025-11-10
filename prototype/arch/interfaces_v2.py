#!/usr/bin/env python3
"""
核心接口定义 v2

使用I前缀的命名规范，保持最小化和实用性。
"""

from typing import Protocol, Dict, Any, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from data_models import MarketType, FinancialIndicator


# === 核心业务接口 ===

class IMarketAdapter(Protocol):
    """市场适配器接口 - 核心业务接口"""

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """获取指定股票的财务数据"""
        ...


class IFieldMapper(Protocol):
    """字段映射接口 - 核心业务接口"""

    def get_market_field(self, unified_field: str, market: MarketType) -> Optional[str]:
        """获取统一字段在指定市场的实际字段名"""
        ...

    def is_field_available(self, unified_field: str, market: MarketType) -> bool:
        """检查字段在指定市场是否可用"""
        ...


class IMarketIdentifier(Protocol):
    """市场识别接口 - 核心业务接口"""

    def identify(self, symbol: str, default_market: Optional[MarketType] = None) -> Tuple[MarketType, str]:
        """识别股票代码市场类型并标准化"""
        ...


class IQueryExecutor(Protocol):
    """查询执行接口 - 核心业务接口"""

    def execute(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
        """执行查询逻辑"""
        ...


class IQueryFilter(Protocol):
    """查询过滤器接口 - 核心业务接口"""

    def apply(self, data: List[FinancialIndicator], **kwargs) -> List[FinancialIndicator]:
        """应用过滤器"""
        ...


class IResultBuilder(Protocol):
    """结果构建接口 - 核心业务接口"""

    def build_success(self, data: List[FinancialIndicator], **kwargs) -> Any:
        """构建成功结果"""
        ...

    def build_error(self, error: Exception, context: str) -> Any:
        """构建错误结果"""
        ...


class IComparisonEngine(Protocol):
    """对比引擎接口 - 核心业务接口"""

    def compare(self, symbols: List[str], data: Dict[str, List[FinancialIndicator]]) -> Dict[str, Any]:
        """对比多只股票的财务指标"""
        ...


# === 配置管理接口 ===

class IMappingProvider(Protocol):
    """映射提供者接口 - 配置相关"""

    def get_mappings(self) -> List[Any]:
        """获取映射配置"""
        ...


class IConfigManager(Protocol):
    """配置管理器接口 - 配置相关"""

    def get_field_mapper(self) -> IFieldMapper:
        """获取字段映射器"""
        ...

    def get_available_fields(self, market: MarketType) -> List[str]:
        """获取指定市场的可用字段"""
        ...


# === 服务工厂接口 ===

class IServiceFactory(Protocol):
    """服务工厂接口 - 依赖注入相关"""

    def create_adapter(self, market: MarketType) -> IMarketAdapter:
        """创建市场适配器"""
        ...

    def create_query_service(self) -> Any:
        """创建查询服务"""
        ...


class IServiceContainer(Protocol):
    """服务容器接口 - 依赖注入相关"""

    def get(self, interface: type) -> Any:
        """获取服务实例"""
        ...

    def register(self, interface: type, implementation: Any, singleton: bool = False):
        """注册服务"""
        ...


# === 验证和监控接口 ===

class IDataValidator(Protocol):
    """数据验证接口 - 可选扩展"""

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证数据完整性和有效性"""
        ...


class ILogger(Protocol):
    """日志接口 - 可选扩展"""

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        ...

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        ...

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        ...


class IMetricsCollector(Protocol):
    """指标收集接口 - 可选扩展"""

    def record_query_time(self, market: MarketType, duration_ms: float):
        """记录查询耗时"""
        ...

    def record_success_rate(self, market: MarketType, success: bool):
        """记录成功率"""
        ...


# === 缓存接口 ===

class ICacheProvider(Protocol):
    """缓存提供者接口 - 性能优化相关"""

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        ...

    def delete(self, key: str):
        """删除缓存值"""
        ...


# === 数据源接口（未来扩展） ===

class IAkshareClient(Protocol):
    """Akshare客户端接口 - 未来直接集成时使用"""

    def get_stock_financial_data(self, symbol: str, market: MarketType) -> List[Dict[str, Any]]:
        """获取股票财务数据"""
        ...


class IRealTimeDataProvider(Protocol):
    """实时数据提供者接口 - 未来扩展"""

    def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """获取实时价格"""
        ...


# === 说明 ===
"""
接口设计原则：

1. 最小化 - 只定义真正需要的方法
2. 实用性 - 聚焦核心业务需求
3. 前缀规范 - 所有接口以I开头
4. 职责单一 - 每个接口职责明确
5. 易扩展 - 便于添加新功能

核心接口（必须实现）：
- IMarketAdapter: 市场适配器
- IFieldMapper: 字段映射
- IMarketIdentifier: 市场识别
- IQueryExecutor: 查询执行
- IQueryFilter: 查询过滤
- IResultBuilder: 结果构建
- IComparisonEngine: 指标对比

可选接口（按需实现）：
- IConfigManager: 配置管理
- IServiceFactory: 服务工厂
- ILogger: 日志记录
- IMetricsCollector: 指标收集
- ICacheProvider: 缓存管理

移除的接口（不需要）：
- DataFetcher: 直接使用akshare API
- DateParser: 内置在适配器中
- MockDataProvider: 仅用于测试
- 各种工具类接口: 直接使用具体类
"""