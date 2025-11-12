"""
统一字段映射器

基于SOLID原则重构的统一字段映射器实现
使用依赖注入架构，支持可插拔的组件
遵循单一职责原则（SRP）和依赖倒置原则（DIP）
"""

import asyncio
import concurrent.futures
from typing import List, Optional, Dict, Tuple, Any
from .interfaces import (
    IFieldMapper, IConfigLoader, IFieldSearcher,
    IMarketInferrer, IConfigAnalyzer
)
from .models import FieldInfo


class UnifiedFieldMapper:
    """统一字段映射器

    基于依赖注入架构的字段映射器实现
    组合多个专门的服务组件，遵循组合优于继承原则
    """

    def __init__(
        self,
        config_loader: IConfigLoader,
        field_searcher: IFieldSearcher,
        market_inferrer: IMarketInferrer,
        config_analyzer: Optional[IConfigAnalyzer] = None
    ):
        """
        初始化统一字段映射器

        Args:
            config_loader: 配置加载器实现
            field_searcher: 字段搜索器实现
            market_inferrer: 市场推断器实现
            config_analyzer: 配置分析器实现（可选）
        """
        self._config_loader = config_loader
        self._field_searcher = field_searcher
        self._market_inferrer = market_inferrer
        self._config_analyzer = config_analyzer

    def ensure_loaded(self) -> bool:
        """
        确保配置已加载

        Returns:
            是否加载成功
        """
        return self._config_loader.is_loaded() or self._config_loader.load_configs()

    async def resolve_fields(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        异步解析和映射字段名 - 实现IFieldMapper接口

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        return self.resolve_fields_sync(symbol, fields)

    def resolve_fields_sync(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        同步解析和映射字段名

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        if not fields:
            return [], []

        if not self.ensure_loaded():
            # 如果配置加载失败，返回原始字段
            return fields, ["配置加载失败，返回原始字段"]

        # 推断市场类型
        market_id = self._market_inferrer.infer_market_type(symbol)
        if not market_id:
            return fields, [f"无法推断股票代码 '{symbol}' 的市场类型"]

        mapped_fields = []
        suggestions = []

        for field in fields:
            # 使用字段搜索器进行映射
            search_results = self._field_searcher.search_fields_by_keyword(
                field, market_id, limit=1
            )

            if search_results:
                # 取最佳匹配
                best_match = search_results[0]
                field_id, similarity, field_info, result_market_id = best_match
                mapped_fields.append(field_id)

                if field_id != field:
                    suggestions.append(
                        f"• '{field}' → '{field_info.name}' "
                        f"(智能匹配，相似度: {similarity:.2f})"
                    )
            else:
                # 未找到匹配，添加到建议列表
                suggestions.append(f"• '{field}' → 未找到匹配字段")

        return mapped_fields, suggestions

    def map_keyword_to_field(
        self,
        keyword: str,
        market_id: Optional[str] = None
    ) -> Optional[Tuple[str, float, FieldInfo, Optional[str]]]:
        """
        将关键字映射到字段

        Args:
            keyword: 关键字
            market_id: 市场ID

        Returns:
            (field_id, similarity, field_info, market_id) 或 None
        """
        if not self.ensure_loaded():
            return None

        return self._field_searcher.map_keyword_to_field(keyword, market_id or "a_stock")

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
        if not self.ensure_loaded():
            return []

        return self._field_searcher.search_similar_fields(keyword, market_id, max_results)

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
        if not self.ensure_loaded():
            return []

        similar_fields = self.search_similar_fields(keyword, market_id)
        return [field_info.name for _, _, field_info, _ in similar_fields]

    def get_available_fields(self, market_id: Optional[str] = None) -> List[str]:
        """
        获取可用字段列表

        Args:
            market_id: 市场ID，如果为None则返回所有市场字段

        Returns:
            字段名列表
        """
        if not self.ensure_loaded():
            return []

        if market_id:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config:
                return [field_info.name for field_info in market_config.fields.values()]
            return []
        else:
            all_fields = []
            for market_id_key in self._config_loader.get_available_markets():
                market_config = self._config_loader.get_market_config(market_id_key)
                if market_config:
                    all_fields.extend([field_info.name for field_info in market_config.fields.values()])
            return list(set(all_fields))  # 去重

    def get_field_details(
        self,
        field_name: str,
        market_id: Optional[str] = None
    ) -> Optional[FieldInfo]:
        """
        获取字段详细信息

        Args:
            field_name: 字段名
            market_id: 市场ID

        Returns:
            字段信息或None
        """
        if not self.ensure_loaded():
            return None

        markets_to_search = [market_id] if market_id else self._config_loader.get_available_markets()

        for market_id_key in markets_to_search:
            market_config = self._config_loader.get_market_config(market_id_key)
            if market_config:
                for field_id, field_info in market_config.fields.items():
                    if field_info.name == field_name or field_id == field_name:
                        return field_info

        return None

    def is_field_available(self, field_name: str, market_id: str) -> bool:
        """
        检查字段是否在指定市场可用

        Args:
            field_name: 字段名
            market_id: 市场ID

        Returns:
            是否可用
        """
        field_info = self.get_field_details(field_name, market_id)
        return field_info is not None

    def get_all_keywords(self, market_id: Optional[str] = None) -> List[str]:
        """
        获取所有关键字

        Args:
            market_id: 市场ID

        Returns:
            关键字列表
        """
        if not self.ensure_loaded():
            return []

        all_keywords = []
        markets_to_search = [market_id] if market_id else self._config_loader.get_available_markets()

        for market_id_key in markets_to_search:
            market_config = self._config_loader.get_market_config(market_id_key)
            if market_config:
                for field_info in market_config.fields.values():
                    all_keywords.extend(field_info.keywords)

        return list(set(all_keywords))  # 去重

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置摘要信息
        """
        if not self.ensure_loaded():
            return {}

        if self._config_analyzer:
            return self._config_analyzer.get_config_summary()

        # 如果没有配置分析器，提供基本摘要
        available_markets = self._config_loader.get_available_markets()
        total_fields = 0
        markets_detail = {}

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config:
                total_fields += len(market_config.fields)
                markets_detail[market_id] = {
                    'name': market_config.name,
                    'currency': market_config.currency,
                    'fields_count': len(market_config.fields)
                }

        return {
            'total_markets': len(available_markets),
            'total_fields': total_fields,
            'config_files': 1,  # 无法准确统计，使用默认值
            'markets_detail': markets_detail
        }


# 为了向后兼容，保持类名导出
__all__ = ['UnifiedFieldMapper', 'UnifiedFieldMapper']