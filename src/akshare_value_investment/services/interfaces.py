"""
服务层接口定义

使用Python Protocol定义轻量级接口，用于依赖注入和单元测试。
专注于服务层接口，核心业务接口位于 core/interfaces.py
"""

from typing import List, Optional, Dict, Any, Tuple, Protocol


class IFieldMapper(Protocol):
    """字段映射服务接口"""

    async def resolve_fields(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        解析和映射字段名

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        ...


class IResponseFormatter(Protocol):
    """响应格式化接口"""

    def format_query_response(self,
                             result: Any,
                             symbol: str,
                             mapped_fields: List[str] = None,
                             prefer_annual: bool = True,
                             include_metadata: bool = True,
                             mapping_suggestions: List[str] = None) -> str:
        """
        格式化查询响应

        Args:
            result: 查询结果
            symbol: 股票代码
            mapped_fields: 映射后的字段
            prefer_annual: 是否优先年报
            include_metadata: 是否包含元数据
            mapping_suggestions: 映射建议列表

        Returns:
            格式化的响应文本
        """
        ...


class IConceptSearchEngine(Protocol):
    """概念搜索引擎接口"""

    async def search_concepts(self, query: str, market: str) -> List[Dict[str, Any]]:
        """
        搜索财务概念

        Args:
            query: 搜索查询
            market: 市场类型

        Returns:
            搜索结果列表
        """
        ...


class IFieldDiscoveryService(Protocol):
    """字段发现服务接口"""

    def discover_fields(self, symbol: str, keyword_filter: str = "", max_results: int = 20) -> List[str]:
        """
        发现可用字段

        Args:
            symbol: 股票代码
            keyword_filter: 关键词过滤
            max_results: 最大结果数

        Returns:
            可用字段列表
        """
        ...


class ITimeRangeProcessor(Protocol):
    """时间范围处理器接口"""

    def process_time_range(self,
                           start_date: Optional[str],
                           end_date: Optional[str],
                           default_years: int = 5) -> Tuple[str, str]:
        """
        处理时间范围参数

        Args:
            start_date: 开始日期
            end_date: 结束日期
            default_years: 默认年数

        Returns:
            (处理后的开始日期, 结束日期)
        """
        ...


class IDataStructureProcessor(Protocol):
    """数据结构处理器接口"""

    def extract_indicator_data(self, data: Any) -> Dict[str, Dict[str, Any]]:
        """
        提取指标数据结构

        Args:
            data: 原始数据

        Returns:
            指标数据字典 {field_name: {date: value}}
        """
        ...

    def extract_metadata(self, data: Any) -> Dict[str, Any]:
        """
        提取元数据

        Args:
            data: 原始数据

        Returns:
            元数据字典
        """
        ...