"""
财务指标配置加载器 [DEPRECATED]

⚠️ 已弃用，请使用 MultiConfigLoader

负责加载和解析财务指标字段配置文件
此版本已被 multi_config_loader.py 中的 MultiConfigLoader 替代
建议迁移到新的多配置文件架构以获得更好的扩展性和维护性

迁移指南：
1. 替换导入：from .multi_config_loader import MultiConfigLoader
2. 更新初始化：loader = MultiConfigLoader()
3. 配置文件路径：支持多文件路径列表

@deprecated 使用 MultiConfigLoader 替代
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FieldInfo:
    """字段信息"""
    name: str
    keywords: List[str]
    priority: int
    description: str

    def matches_keyword(self, keyword: str) -> bool:
        """检查是否匹配关键字"""
        keyword_lower = keyword.lower()
        return any(keyword_lower == kw.lower() or kw.lower() in keyword_lower or keyword_lower in kw.lower()
                  for kw in self.keywords)

    def get_similarity(self, keyword: str) -> float:
        """计算与关键字的相似度"""
        keyword_lower = keyword.lower()
        best_match = 0.0

        for kw in self.keywords:
            kw_lower = kw.lower()
            # 简单的包含关系匹配
            if keyword_lower == kw_lower:
                return 1.0
            elif keyword_lower in kw_lower or kw_lower in keyword_lower:
                return 0.8
            elif any(char in kw_lower for char in keyword_lower):
                match_chars = sum(1 for char in keyword_lower if char in kw_lower)
                similarity = match_chars / max(len(keyword_lower), len(kw_lower))
                best_match = max(best_match, similarity * 0.5)

        return best_match


@dataclass
class MarketConfig:
    """市场配置"""
    name: str
    currency: str
    fields: Dict[str, FieldInfo]


class FinancialFieldConfigLoader:
    """财务指标字段配置加载器 [DEPRECATED]

    ⚠️ 此类已被弃用，请使用 MultiConfigLoader
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            current_dir = Path(__file__).parent.parent.parent / "datasource" / "config"
            config_path = str(current_dir / "financial_indicators.yaml")

        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._markets: Dict[str, MarketConfig] = {}

    def load_config(self) -> bool:
        """
        加载配置文件

        Returns:
            是否加载成功
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)

            # 解析市场配置
            self._parse_markets()
            return True

        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False

    def _parse_markets(self):
        """解析市场配置"""
        markets_data = self._config.get('markets', {})

        for market_id, market_data in markets_data.items():
            # 跳过元数据字段
            if market_id in ['name', 'currency'] and not isinstance(market_data, dict):
                continue

            # 解析市场基本信息
            market_name = market_data.get('name', market_id)
            market_currency = market_data.get('currency', 'CNY')

            # 解析字段配置
            fields = {}
            for field_id, field_data in market_data.items():
                if isinstance(field_data, dict) and 'keywords' in field_data:
                    field_info = FieldInfo(
                        name=field_data.get('name', field_id),
                        keywords=field_data.get('keywords', []),
                        priority=field_data.get('priority', 1),
                        description=field_data.get('description', '')
                    )
                    fields[field_id] = field_info

            self._markets[market_id] = MarketConfig(
                name=market_name,
                currency=market_currency,
                fields=fields
            )

    def get_market_config(self, market_id: str) -> Optional[MarketConfig]:
        """
        获取指定市场的配置

        Args:
            market_id: 市场ID (如 'a_stock', 'hk_stock', 'us_stock')

        Returns:
            市场配置对象，如果不存在则返回None
        """
        return self._markets.get(market_id)

    def get_available_markets(self) -> List[str]:
        """
        获取所有可用的市场列表

        Returns:
            市场ID列表
        """
        return list(self._markets.keys())

    def search_fields_by_keyword(self, keyword: str, market_id: Optional[str] = None, limit: int = 10) -> List[Tuple[str, float, FieldInfo]]:
        """
        根据关键字搜索字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID，如果为None则搜索所有市场
            limit: 最大返回数量

        Returns:
            搜索结果列表，每个元素为 (field_id, similarity, field_info)
        """
        results = []
        keyword_lower = keyword.lower().strip()

        markets_to_search = [market_id] if market_id else self._markets.keys()

        for market_id_to_search in markets_to_search:
            market_config = self._markets.get(market_id_to_search)
            if not market_config:
                continue

            for field_id, field_info in market_config.fields.items():
                if field_info.matches_keyword(keyword_lower):
                    # 精确匹配，相似度为1.0
                    similarity = 1.0
                else:
                    # 计算相似度
                    similarity = field_info.get_similarity(keyword_lower)

                if similarity > 0.3:  # 相似度阈值
                    results.append((field_id, similarity, field_info, market_id_to_search))

        # 按相似度和优先级排序
        results.sort(key=lambda x: (x[1], -x[2].priority), reverse=True)

        # 限制返回数量
        return results[:limit]

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取配置元数据

        Returns:
            元数据字典
        """
        return self._config.get('metadata', {})

    def get_categories_info(self) -> Dict[str, Any]:
        """
        获取分类信息

        Returns:
            分类信息字典
        """
        return self._config.get('categories', {})