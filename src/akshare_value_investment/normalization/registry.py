from typing import Dict, List

class FieldMappingRegistry:
    """
    字段映射注册表。

    职责：
    - 维护 '市场 -> {原始字段: 标准字段}' 的映射关系
    - 支持批量加载配置
    - 提供字段映射查询服务
    """

    def __init__(self):
        # 内部存储结构: {market_name: {raw_field_name: standard_field_name}}
        self._mappings: Dict[str, Dict[str, str]] = {}

    def register_mapping(self, market: str, standard_field: str, raw_fields: List[str]):
        """
        为特定市场注册字段映射。

        Args:
            market: 市场标识符 (如 'a_stock', 'hk_stock')
            standard_field: 标准字段名 (来自 StandardFields)
            raw_fields: 原始字段名列表
        """
        if market not in self._mappings:
            self._mappings[market] = {}

        for raw in raw_fields:
            self._mappings[market][raw] = standard_field

    def load_mappings_config(self, config: Dict[str, Dict[str, List[str]]]):
        """
        批量加载字段映射配置

        Args:
            config: 配置字典，格式为 {market: {standard_field: [raw_fields, ...]}}

        Example:
            >>> config = {
            ...     'a_stock': {
            ...         'total_revenue': ['营业总收入', '一、营业总收入']
            ...     }
            ... }
            >>> registry = FieldMappingRegistry()
            >>> registry.load_mappings_config(config)
        """
        for market, mappings in config.items():
            for standard_field, raw_fields in mappings.items():
                self.register_mapping(market, standard_field, raw_fields)

    @classmethod
    def from_config(cls, config: Dict[str, Dict[str, List[str]]]) -> 'FieldMappingRegistry':
        """
        从配置字典创建注册表实例（工厂方法）

        Args:
            config: 配置字典，格式为 {market: {standard_field: [raw_fields, ...]}}

        Returns:
            配置好的 FieldMappingRegistry 实例

        Example:
            >>> config = load_market_mappings()
            >>> registry = FieldMappingRegistry.from_config(config)
        """
        registry = cls()
        registry.load_mappings_config(config)
        return registry

    def get_mapping(self, market: str) -> Dict[str, str]:
        """
        获取特定市场的映射字典。

        Args:
            market: 市场标识符

        Returns:
            Dict[原始字段, 标准字段]
        """
        return self._mappings.get(market, {}).copy()

