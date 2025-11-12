"""
SOLID重构：抽象接口层

基于SOLID原则定义的核心抽象接口，实现依赖倒置原则（DIP）
支持依赖注入和接口隔离原则（ISP）
"""

from typing import Dict, List, Any, Optional, Tuple, Protocol, runtime_checkable
from .models import FieldInfo, MarketConfig


@runtime_checkable
class IConfigLoader(Protocol):
    """配置加载器接口

    负责配置文件的加载、合并和管理
    遵循单一职责原则，只关注配置相关操作
    """

    def load_configs(self) -> bool:
        """
        加载所有配置文件

        Returns:
            是否加载成功
        """
        ...

    def get_market_config(self, market_id: str) -> Optional[MarketConfig]:
        """
        获取指定市场的配置

        Args:
            market_id: 市场ID (如 'a_stock', 'hk_stock', 'us_stock')

        Returns:
            市场配置对象，如果不存在则返回None
        """
        ...

    def get_available_markets(self) -> List[str]:
        """
        获取所有可用的市场列表

        Returns:
            市场ID列表
        """
        ...

    def is_loaded(self) -> bool:
        """
        检查配置是否已加载

        Returns:
            是否已加载
        """
        ...


@runtime_checkable
class IFieldSearcher(Protocol):
    """字段搜索器接口

    负责字段搜索和相似度匹配
    遵循单一职责原则，只关注搜索功能
    """

    def search_fields_by_keyword(
        self,
        keyword: str,
        market_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[str, float, FieldInfo, Optional[str]]]:
        """
        根据关键字搜索字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID，如果为None则搜索所有市场
            limit: 最大返回数量

        Returns:
            搜索结果列表，每个元素为 (field_id, similarity, field_info, market_id)
        """
        ...

    def map_keyword_to_field(
        self,
        keyword: str,
        market_id: str
    ) -> Optional[Tuple[str, float, FieldInfo, str]]:
        """
        将关键字映射到最佳匹配字段

        Args:
            keyword: 关键字
            market_id: 市场ID

        Returns:
            (field_id, similarity, field_info, market_id) 或 None
        """
        ...

    def search_similar_fields(
        self,
        keyword: str,
        market_id: Optional[str] = None,
        max_results: int = 5
    ) -> List[Tuple[str, float, FieldInfo, str]]:
        """
        搜索相似的字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID
            max_results: 最大结果数量

        Returns:
            排序的字段列表
        """
        ...


@runtime_checkable
class IMarketInferrer(Protocol):
    """市场推断器接口

    负责根据股票代码推断市场类型
    遵循单一职责原则，只关注市场推断逻辑
    """

    def infer_market_type(self, symbol: str) -> Optional[str]:
        """
        根据股票代码推断市场类型

        Args:
            symbol: 股票代码

        Returns:
            市场ID (如 'a_stock', 'hk_stock', 'us_stock')，如果无法推断则返回None
        """
        ...

    def supports_symbol(self, symbol: str) -> bool:
        """
        检查是否支持指定的股票代码

        Args:
            symbol: 股票代码

        Returns:
            是否支持
        """
        ...

    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """
        获取支持的股票代码模式

        Returns:
            市场ID到正则表达式模式的映射
        """
        ...


@runtime_checkable
class IConfigAnalyzer(Protocol):
    """配置分析器接口

    负责配置统计和分析功能
    遵循单一职责原则，只关注分析功能
    """

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取配置元数据

        Returns:
            元数据字典
        """
        ...

    def get_categories_info(self) -> Dict[str, Any]:
        """
        获取分类信息

        Returns:
            分类信息字典
        """
        ...

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置摘要信息
        """
        ...

    def analyze_field_coverage(self, market_id: str) -> Dict[str, Any]:
        """
        分析指定市场的字段覆盖情况

        Args:
            market_id: 市场ID

        Returns:
            覆盖分析结果
        """
        ...


@runtime_checkable
class IFieldMapper(Protocol):
    """字段映射器接口

    统一的字段映射服务接口
    符合接口隔离原则，客户端只依赖需要的方法
    """

    async def resolve_fields(
        self,
        symbol: str,
        fields: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        异步解析和映射字段名

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        ...

    def resolve_fields_sync(
        self,
        symbol: str,
        fields: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        同步解析和映射字段名

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        ...

    def get_field_suggestions(
        self,
        keyword: str,
        market_id: Optional[str] = None
    ) -> List[str]:
        """
        获取字段建议

        Args:
            keyword: 输入关键字
            market_id: 市场ID

        Returns:
            建议字段名列表
        """
        ...


@runtime_checkable
class IMergerStrategy(Protocol):
    """配置合并策略接口

    支持不同的配置合并策略
    遵循开闭原则，可扩展新策略
    """

    def merge_markets(
        self,
        existing_markets: Dict[str, MarketConfig],
        new_markets: Dict[str, MarketConfig]
    ) -> Dict[str, MarketConfig]:
        """
        合并市场配置

        Args:
            existing_markets: 现有市场配置
            new_markets: 新市场配置

        Returns:
            合并后的市场配置
        """
        ...

    def resolve_conflict(
        self,
        market_id: str,
        field_id: str,
        existing_field: FieldInfo,
        new_field: FieldInfo
    ) -> FieldInfo:
        """
        解决字段冲突

        Args:
            market_id: 市场ID
            field_id: 字段ID
            existing_field: 现有字段
            new_field: 新字段

        Returns:
            解决冲突后的字段
        """
        ...


# 导出所有接口
__all__ = [
    'IConfigLoader',
    'IFieldSearcher',
    'IMarketInferrer',
    'IConfigAnalyzer',
    'IFieldMapper',
    'IMergerStrategy'
]