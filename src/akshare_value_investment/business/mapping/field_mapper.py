"""
财务指标字段映射器

实现关键字到字段名的智能映射，兼容IFieldMapper接口
"""

from typing import List, Optional, Dict, Tuple, Any, Protocol, runtime_checkable
from .config_loader import FinancialFieldConfigLoader, FieldInfo


@runtime_checkable
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


class FinancialFieldMapper:
    """财务指标字段映射器 - 兼容IFieldMapper接口"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化字段映射器

        Args:
            config_path: 配置文件路径
        """
        self.config_loader = FinancialFieldConfigLoader(config_path)
        self._is_loaded = False

    def ensure_loaded(self) -> bool:
        """
        确保配置已加载

        Returns:
            是否加载成功
        """
        if not self._is_loaded:
            self._is_loaded = self.config_loader.load_config()
        return self._is_loaded

    async def resolve_fields(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        解析和映射字段名 - 实现IFieldMapper接口

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
            return fields, []

        # 推断市场类型
        market_id = self._infer_market_type(symbol)

        mapped_fields = []
        suggestions = []

        for field in fields:
            # 1. 使用新系统进行智能映射
            mapped_field_info = self.config_loader.search_fields_by_keyword(
                field, market_id, limit=1
            )

            if mapped_field_info:
                field_id, similarity, field_info, _ = mapped_field_info[0]
                mapped_fields.append(field_id)
                if field_id != field:
                    suggestions.append(f"• '{field}' → '{field_info.name}' (智能匹配，相似度: {similarity:.2f})")
                continue

            # 2. 如果智能映射失败，添加到建议
            suggestions.append(f"• '{field}' → 未找到匹配字段")

        return mapped_fields, suggestions

    def resolve_fields_sync(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        同步版本的字段解析 - 为MCP服务器提供

        Args:
            symbol: 股票代码
            fields: 请求的字段列表

        Returns:
            (映射后的字段列表, 映射建议列表)
        """
        import asyncio

        # 如果已在事件循环中，使用run_coroutine_threadsafe
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(self.resolve_fields(symbol, fields)))
                return future.result()
        except RuntimeError:
            # 没有运行的事件循环，可以直接运行
            return asyncio.run(self.resolve_fields(symbol, fields))

    def map_keyword_to_field(self, keyword: str, market_id: Optional[str] = None) -> Optional[Tuple[str, float, FieldInfo]]:
        """
        将关键字映射到字段名

        Args:
            keyword: 输入关键字
            market_id: 市场ID (如 'a_stock', 'hk_stock', 'us_stock')

        Returns:
            (field_id, similarity, field_info) 或 None
        """
        if not self.ensure_loaded():
            return None

        if not market_id:
            # 如果没有指定市场，尝试推断
            return None

        results = self.config_loader.search_fields_by_keyword(keyword, market_id, limit=1)
        # 返回 (field_id, similarity, field_info) 格式以保持兼容性
        if results:
            field_id, similarity, field_info, _ = results[0]
            return (field_id, similarity, field_info)
        return None

    def search_similar_fields(self, keyword: str, market_id: Optional[str] = None, max_results: int = 5) -> List[Tuple[str, float, FieldInfo, str]]:
        """
        搜索相似的字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID
            max_results: 最大结果数量

        Returns:
            排序的字段列表 [(field_id, similarity, field_info), ...]
        """
        if not self.ensure_loaded():
            return []

        return self.config_loader.search_fields_by_keyword(keyword, market_id, max_results)

    def get_field_suggestions(self, keyword: str, market_id: Optional[str] = None) -> List[str]:
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

        results = self.search_similar_fields(keyword, market_id)
        return [field_info.name for _, _, field_info, _ in results]

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
            market_config = self.config_loader.get_market_config(market_id)
            if market_config:
                return [field_info.name for field_info in market_config.fields.values()]
            return []
        else:
            all_fields = []
            for market_id_key in self.config_loader.get_available_markets():
                market_config = self.config_loader.get_market_config(market_id_key)
                if market_config:
                    all_fields.extend([field_info.name for field_info in market_config.fields.values()])
            return list(set(all_fields))  # 去重

    def get_field_details(self, field_name: str, market_id: Optional[str] = None) -> Optional[FieldInfo]:
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

        markets_to_search = [market_id] if market_id else self.config_loader.get_available_markets()

        for market_id_key in markets_to_search:
            market_config = self.config_loader.get_market_config(market_id_key)
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
        markets_to_search = [market_id] if market_id else self.config_loader.get_available_markets()

        for market_id_key in markets_to_search:
            market_config = self.config_loader.get_market_config(market_id_key)
            if market_config:
                for field_info in market_config.fields.values():
                    all_keywords.extend(field_info.keywords)

        return list(set(all_keywords))  # 去重

    def get_config_info(self) -> Dict[str, any]:
        """
        获取配置信息

        Returns:
            配置信息字典
        """
        if not self.ensure_loaded():
            return {}

        metadata = self.config_loader.get_metadata()
        available_markets = self.config_loader.get_available_markets()
        categories_info = self.config_loader.get_categories_info()

        total_fields = 0
        for market_id in available_markets:
            market_config = self.config_loader.get_market_config(market_id)
            if market_config:
                total_fields += len(market_config.fields)

        return {
            'metadata': metadata,
            'available_markets': available_markets,
            'categories': categories_info,
            'total_fields': total_fields,
            'fields_by_market': {
                market_id: len(market_config.fields) if market_config else 0
                for market_id, market_config in
                [(mid, self.config_loader.get_market_config(mid)) for mid in available_markets]
            }
        }

    def _infer_market_type(self, symbol: str) -> Optional[str]:
        """
        推断股票市场类型

        Args:
            symbol: 股票代码

        Returns:
            市场ID或None
        """
        # 简单的市场类型推断逻辑
        if symbol.endswith(('.HK', '.SS', '.SZ')):
            if symbol.endswith(('.SS', '.SZ')):
                return 'a_stock'
            elif symbol.endswith('.HK'):
                return 'hk_stock'
        elif '.' not in symbol and len(symbol) == 6:
            # 纯数字A股代码
            if symbol.startswith(('0', '3', '6')):
                return 'a_stock'
        elif '.' in symbol and symbol.split('.')[-1].isalpha():
            # 美股代码 (如 AAPL, MSFT)
            return 'us_stock'

        return None

    def map_field_name(self, symbol: str, field_name: str) -> Optional[str]:
        """
        映射单个字段名 - 兼容旧接口

        Args:
            symbol: 股票代码
            field_name: 原始字段名

        Returns:
            映射后的字段名，如果无法映射则返回None
        """
        market_id = self._infer_market_type(symbol)
        if not market_id:
            return None

        mapped_result = self.map_keyword_to_field(field_name, market_id)
        if mapped_result:
            _, _, field_info = mapped_result
            return field_info.name

        return None

    def get_field_mapping_suggestions(self, symbol: str, field_name: str) -> List[str]:
        """
        获取字段映射建议 - 兼容旧接口

        Args:
            symbol: 股票代码
            field_name: 原始字段名

        Returns:
            映射建议列表
        """
        market_id = self._infer_market_type(symbol)
        return self.get_field_suggestions(field_name, market_id)


# 为了向后兼容，导出两个类
__all__ = ['FinancialFieldMapper', 'IFieldMapper']