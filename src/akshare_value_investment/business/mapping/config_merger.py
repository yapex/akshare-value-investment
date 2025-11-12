"""
配置合并器

专门负责配置文件的合并逻辑
遵循单一职责原则（SRP），只关注配置合并功能
"""

from typing import Dict, List, Any, Optional, Tuple
from .interfaces import IMergerStrategy
from .models import MarketConfig, FieldInfo


class DefaultMergerStrategy:
    """默认合并策略实现

    按照优先级和加载顺序进行配置合并
    支持字段冲突检测和解决
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
        merged_markets = existing_markets.copy()

        for market_id, new_market in new_markets.items():
            if market_id in merged_markets:
                # 合并现有市场
                existing_market = merged_markets[market_id]
                merged_market = self._merge_market_config(existing_market, new_market)
                merged_markets[market_id] = merged_market
            else:
                # 添加新市场
                merged_markets[market_id] = new_market

        return merged_markets

    def resolve_conflict(
        self,
        market_id: str,
        field_id: str,
        existing_field: FieldInfo,
        new_field: FieldInfo
    ) -> FieldInfo:
        """
        解决字段冲突

        策略：保留优先级更高的字段，如果优先级相同则保留现有字段

        Args:
            market_id: 市场ID
            field_id: 字段ID
            existing_field: 现有字段
            new_field: 新字段

        Returns:
            解决冲突后的字段
        """
        # 比较优先级，数字越大优先级越高
        if new_field.priority > existing_field.priority:
            print(f"✅ 字段冲突解决: {market_id}.{field_id} - 使用新字段 (优先级: {new_field.priority} > {existing_field.priority})")
            return new_field
        elif new_field.priority < existing_field.priority:
            print(f"🔄 字段冲突解决: {market_id}.{field_id} - 保留现有字段 (优先级: {existing_field.priority} > {new_field.priority})")
            return existing_field
        else:
            # 优先级相同，保留现有字段（先加载的优先）
            print(f"⚖️ 字段冲突解决: {market_id}.{field_id} - 保留现有字段 (优先级相同)")
            return existing_field

    def _merge_market_config(self, existing: MarketConfig, new: MarketConfig) -> MarketConfig:
        """
        合并单个市场配置

        Args:
            existing: 现有市场配置
            new: 新市场配置

        Returns:
            合并后的市场配置
        """
        # 合并字段
        merged_fields = existing.fields.copy()

        for field_id, new_field in new.fields.items():
            if field_id in merged_fields:
                # 解决冲突
                resolved_field = self.resolve_conflict(
                    existing.name, field_id, merged_fields[field_id], new_field
                )
                merged_fields[field_id] = resolved_field
            else:
                # 添加新字段
                merged_fields[field_id] = new_field

        # 使用现有市场的基本信息（名称、货币）
        return MarketConfig(
            name=existing.name,
            currency=existing.currency,
            fields=merged_fields
        )


class ConfigMerger:
    """配置合并器

    专门负责多个配置文件的合并处理
    支持不同的合并策略
    """

    def __init__(self, merger_strategy: Optional[IMergerStrategy] = None):
        """
        初始化配置合并器

        Args:
            merger_strategy: 合并策略，如果为None则使用默认策略
        """
        self._merger_strategy = merger_strategy or DefaultMergerStrategy()
        self._merge_history: List[Dict[str, Any]] = []

    def merge_configs(self, configs: List[Dict[str, Any]]) -> Dict[str, MarketConfig]:
        """
        合并多个配置文件

        Args:
            configs: 配置内容列表

        Returns:
            合并后的市场配置字典
        """
        merged_markets = {}

        for i, config in enumerate(configs):
            self._record_merge_step(i, config)

            # 解析市场配置
            markets_data = config.get('markets', {})
            current_markets = self._parse_markets_data(markets_data, config)

            # 合并到结果中
            merged_markets = self._merger_strategy.merge_markets(merged_markets, current_markets)

        return merged_markets

    def _parse_markets_data(self, markets_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, MarketConfig]:
        """
        解析市场数据

        Args:
            markets_data: 市场数据字典
            config: 原始配置字典

        Returns:
            解析后的市场配置字典
        """
        parsed_markets = {}

        for market_id, market_data in markets_data.items():
            # 跳过元数据字段
            if market_id in ['name', 'currency'] and not isinstance(market_data, dict):
                continue

            # 解析市场基本信息
            market_name = market_data.get('name', market_id)
            market_currency = market_data.get('currency', 'CNY')

            # 解析字段
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

            # 创建市场配置
            market_config = MarketConfig(
                name=market_name,
                currency=market_currency,
                fields=fields
            )

            parsed_markets[market_id] = market_config

        return parsed_markets

    def _record_merge_step(self, step: int, config: Dict[str, Any]) -> None:
        """
        记录合并步骤

        Args:
            step: 步骤编号
            config: 配置内容
        """
        merge_info = {
            'step': step,
            'timestamp': self._get_timestamp(),
            'config_version': config.get('version', 'unknown'),
            'config_description': config.get('metadata', {}).get('description', ''),
            'markets_count': len(config.get('markets', {})),
            'total_fields': self._count_fields_in_config(config)
        }

        self._merge_history.append(merge_info)

    def _count_fields_in_config(self, config: Dict[str, Any]) -> int:
        """
        统计配置中的字段数量

        Args:
            config: 配置字典

        Returns:
            字段总数
        """
        total_fields = 0
        markets_data = config.get('markets', {})

        for market_data in markets_data.values():
            if isinstance(market_data, dict):
                for field_data in market_data.values():
                    if isinstance(field_data, dict) and 'keywords' in field_data:
                        total_fields += 1

        return total_fields

    def get_merge_summary(self) -> Dict[str, Any]:
        """
        获取合并摘要

        Returns:
            合并摘要信息
        """
        if not self._merge_history:
            return {
                'total_steps': 0,
                'total_configs_merged': 0,
                'total_fields_merged': 0,
                'merge_history': []
            }

        total_configs = len(self._merge_history)
        total_fields = sum(step['total_fields'] for step in self._merge_history)

        return {
            'total_steps': total_configs,
            'total_configs_merged': total_configs,
            'total_fields_merged': total_fields,
            'merge_history': self._merge_history,
            'merge_strategy': type(self._merger_strategy).__name__
        }

    def validate_merge_result(self, merged_markets: Dict[str, MarketConfig]) -> Dict[str, Any]:
        """
        验证合并结果

        Args:
            merged_markets: 合并后的市场配置

        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'statistics': {}
        }

        total_markets = len(merged_markets)
        total_fields = 0
        fields_without_keywords = 0
        duplicate_field_names = []

        all_field_names = []

        for market_id, market_config in merged_markets.items():
            market_fields = len(market_config.fields)
            total_fields += market_fields

            for field_id, field_info in market_config.fields.items():
                # 检查关键字
                if not field_info.keywords:
                    fields_without_keywords += 1
                    validation_result['issues'].append(
                        f"字段 {market_id}.{field_id} 缺少关键字"
                    )

                # 检查重复字段名
                if field_info.name in all_field_names:
                    duplicate_field_names.append(field_info.name)
                else:
                    all_field_names.append(field_info.name)

        # 统计信息
        validation_result['statistics'] = {
            'total_markets': total_markets,
            'total_fields': total_fields,
            'fields_without_keywords': fields_without_keywords,
            'duplicate_field_names': len(duplicate_field_names),
            'unique_field_names': len(set(all_field_names))
        }

        # 验证是否有效
        if fields_without_keywords > 0:
            validation_result['is_valid'] = False
            validation_result['issues'].insert(0, f"存在 {fields_without_keywords} 个字段缺少关键字")

        if duplicate_field_names:
            validation_result['is_valid'] = False
            validation_result['issues'].insert(0, f"存在 {len(duplicate_field_names)} 个重复字段名")

        return validation_result

    def set_merger_strategy(self, strategy: IMergerStrategy) -> None:
        """
        设置合并策略

        Args:
            strategy: 新的合并策略
        """
        self._merger_strategy = strategy
        self._merge_history.append({
            'event': 'strategy_changed',
            'timestamp': self._get_timestamp(),
            'new_strategy': type(strategy).__name__
        })

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()