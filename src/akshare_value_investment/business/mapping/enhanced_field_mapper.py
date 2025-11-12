"""
增强版财务指标字段映射器
支持多配置文件合并，兼容IFieldMapper接口
"""

from typing import List, Optional, Dict, Tuple, Any, Protocol, runtime_checkable
from .config_loader import FieldInfo
from .multi_config_loader import MultiConfigLoader
from .field_mapper import IFieldMapper


class EnhancedFinancialFieldMapper:
    """增强版财务指标字段映射器 - 支持多配置文件"""

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        初始化字段映射器

        Args:
            config_paths: 配置文件路径列表，如果为None则使用默认路径
        """
        self.config_loader = MultiConfigLoader(config_paths)
        self._is_loaded = False

    def ensure_loaded(self) -> bool:
        """
        确保配置已加载

        Returns:
            是否加载成功
        """
        if not self._is_loaded:
            self._is_loaded = self.config_loader.load_configs()

        return self._is_loaded

    async def resolve_fields(self, symbol: str, fields: List[str]) -> Tuple[List[str], List[str]]:
        """
        异步解析和映射字段名

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
        if not self.ensure_loaded():
            return fields, ["配置加载失败，返回原始字段"]

        market_id = self._infer_market_type(symbol)
        mapped_fields = []
        suggestions = []

        for field in fields:
            # 搜索匹配的字段
            search_results = self.config_loader.search_fields_by_keyword(
                field, market_id, limit=5
            )

            if search_results:
                # 取最佳匹配
                best_match = search_results[0]
                mapped_fields.append(best_match[0])  # field_id
            else:
                # 未找到匹配，添加到建议列表
                suggestions.append(f"未找到匹配字段: '{field}'，请检查字段名称")

        return mapped_fields, suggestions

    def map_keyword_to_field(self, keyword: str, market_id: Optional[str] = None) -> Optional[Tuple[str, float, FieldInfo, Optional[str]]]:
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

        search_results = self.config_loader.search_fields_by_keyword(
            keyword, market_id, limit=1
        )

        if search_results:
            result = search_results[0]
            return (result[0], result[1], result[2], result[3] if len(result) > 3 else None)

        return None

    def _infer_market_type(self, symbol: str) -> Optional[str]:
        """
        根据股票代码推断市场类型

        Args:
            symbol: 股票代码

        Returns:
            市场ID (如 'a_stock', 'hk_stock', 'us_stock')
        """
        symbol = symbol.upper()

        # A股判断
        if (symbol.startswith(('60', '00', '30')) and
            len(symbol) == 6 and symbol.isdigit()):
            return 'a_stock'

        # 港股判断
        if symbol.endswith('.HK') or (len(symbol) == 5 and symbol[0].isdigit()):
            return 'hk_stock'

        # 美股判断
        if symbol.isalpha() and len(symbol) <= 5:
            return 'us_stock'

        # 默认返回A股
        return 'a_stock'

    def get_available_markets(self) -> List[str]:
        """
        获取所有可用的市场

        Returns:
            市场ID列表
        """
        if not self.ensure_loaded():
            return []

        return self.config_loader.get_available_markets()

    def get_market_config(self, market_id: str):
        """
        获取市场配置

        Args:
            market_id: 市场ID

        Returns:
            市场配置对象
        """
        if not self.ensure_loaded():
            return None

        return self.config_loader.get_market_config(market_id)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置摘要信息
        """
        if not self.ensure_loaded():
            return {}

        return self.config_loader.get_config_summary()