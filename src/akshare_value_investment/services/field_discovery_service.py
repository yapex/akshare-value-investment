"""
字段发现服务

帮助用户发现和了解可用的财务指标字段。
"""

from typing import List
from .interfaces import IFieldDiscoveryService, IQueryService


class FieldDiscoveryService(IFieldDiscoveryService):
    """字段发现服务实现"""

    def __init__(self, query_service: IQueryService):
        """
        初始化字段发现服务

        Args:
            query_service: 查询服务
        """
        self.query_service = query_service

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
        try:
            # 执行查询获取数据
            result = self.query_service.query(symbol)

            if not result.success or not result.data:
                return []

            # 提取字段
            fields = self._extract_fields_from_data(result.data)

            # 应用关键词过滤
            if keyword_filter:
                fields = self._apply_keyword_filter(fields, keyword_filter)

            # 限制结果数量
            return fields[:max_results]

        except Exception:
            # 出错时返回空列表
            return []

    def _extract_fields_from_data(self, data) -> List[str]:
        """从数据中提取字段列表"""
        fields = set()

        if hasattr(data, '__iter__'):
            for record in data:
                if hasattr(record, 'indicators') and record.indicators:
                    fields.update(record.indicators.keys())

        return sorted(list(fields))

    def _apply_keyword_filter(self, fields: List[str], keyword: str) -> List[str]:
        """应用关键词过滤"""
        if not keyword:
            return fields

        keyword_lower = keyword.lower()
        filtered_fields = []

        for field in fields:
            if (keyword_lower in field.lower() or
                keyword_lower in field or
                keyword_lower in field.replace('_', ' ').replace('-', ' ')):
                filtered_fields.append(field)

        return filtered_fields