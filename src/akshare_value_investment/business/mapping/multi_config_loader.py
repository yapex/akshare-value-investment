"""
多配置文件加载器
支持加载多个YAML配置文件并合并
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .config_loader import FieldInfo, MarketConfig


class MultiConfigLoader:
    """多配置文件加载器"""

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        初始化多配置加载器

        Args:
            config_paths: 配置文件路径列表，如果为None则使用默认路径
        """
        if config_paths is None:
            current_dir = Path(__file__).parent.parent.parent / "datasource" / "config"
            config_paths = [
                str(current_dir / "financial_indicators.yaml"),  # 财务指标
                str(current_dir / "financial_statements.yaml")   # 财务三表
            ]

        self.config_paths = config_paths
        self._configs: List[Dict[str, Any]] = []
        self._markets: Dict[str, MarketConfig] = {}

    def load_configs(self) -> bool:
        """
        加载所有配置文件

        Returns:
            是否加载成功
        """
        try:
            self._configs = []

            for config_path in self.config_paths:
                if Path(config_path).exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        self._configs.append(config)
                        print(f"✅ 成功加载配置: {config_path}")
                else:
                    print(f"⚠️ 配置文件不存在: {config_path}")

            # 合并配置
            self._merge_configs()
            return True

        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False

    def _merge_configs(self):
        """合并多个配置文件"""
        self._markets = {}

        for config in self._configs:
            markets_data = config.get('markets', {})

            for market_id, market_data in markets_data.items():
                # 跳过元数据字段
                if market_id in ['name', 'currency'] and not isinstance(market_data, dict):
                    continue

                # 获取或创建市场配置
                if market_id not in self._markets:
                    # 解析市场基本信息
                    market_name = market_data.get('name', market_id)
                    market_currency = market_data.get('currency', 'CNY')

                    self._markets[market_id] = MarketConfig(
                        name=market_name,
                        currency=market_currency,
                        fields={}
                    )

                # 合并字段配置
                existing_market = self._markets[market_id]
                for field_id, field_data in market_data.items():
                    if isinstance(field_data, dict) and 'keywords' in field_data:
                        # 如果字段已存在，跳过（保持原有配置优先级）
                        if field_id in existing_market.fields:
                            print(f"⚠️ 字段已存在，跳过: {market_id}.{field_id}")
                            continue

                        field_info = FieldInfo(
                            name=field_data.get('name', field_id),
                            keywords=field_data.get('keywords', []),
                            priority=field_data.get('priority', 1),
                            description=field_data.get('description', '')
                        )
                        existing_market.fields[field_id] = field_info

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
        获取合并后的配置元数据

        Returns:
            元数据字典
        """
        all_metadata = {}
        for i, config in enumerate(self._configs):
            metadata = config.get('metadata', {})
            all_metadata[f'config_{i+1}'] = metadata

        return all_metadata

    def get_categories_info(self) -> Dict[str, Any]:
        """
        获取分类信息

        Returns:
            分类信息字典
        """
        all_categories = {}
        for i, config in enumerate(self._configs):
            categories = config.get('categories', {})
            all_categories[f'config_{i+1}'] = categories

        return all_categories

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要信息

        Returns:
            配置摘要
        """
        summary = {
            'total_markets': len(self._markets),
            'total_fields': sum(len(market.fields) for market in self._markets.values()),
            'config_files': len(self._configs),
            'markets_detail': {}
        }

        for market_id, market_config in self._markets.items():
            summary['markets_detail'][market_id] = {
                'name': market_config.name,
                'currency': market_config.currency,
                'fields_count': len(market_config.fields)
            }

        return summary