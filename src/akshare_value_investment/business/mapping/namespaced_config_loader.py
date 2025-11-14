"""
命名空间多配置加载器

GREEN阶段：最小实现满足TDD测试要求
实现命名空间隔离的配置加载，支持跨市场字段对比
"""

import yaml
import time
from pathlib import Path
from .models import MarketConfig  # 导入MarketConfig数据模型
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .models import FieldInfo


@dataclass
class NamespacedMarketConfig:
    """命名空间市场配置"""
    market_id: str                    # 市场ID: 'a_stock', 'hk_stock', 'us_stock'
    name: str                         # 市场名称: 'A股', '港股', '美股'
    currency: str                     # 货币: 'CNY', 'HKD', 'USD'
    fields: Dict[str, FieldInfo]      # 命名空间字段: {'TOTAL_REVENUE': FieldInfo}
    namespace: str = ""               # 命名空间前缀
    metadata: Dict[str, Any] = None   # 元数据信息

    def __post_init__(self):
        """后初始化处理"""
        if not self.namespace:
            self.namespace = self.market_id


class NamespacedMultiConfigLoader:
    """命名空间多配置加载器

    GREEN阶段：最小实现满足TDD测试要求
    核心功能：
    1. 一次性加载所有配置到内存
    2. 命名空间隔离，解决字段冲突
    3. 支持跨市场字段对比
    4. 高性能查询访问
    """

    def __init__(self, config_paths: List[str] = None):
        """
        初始化命名空间配置加载器

        Args:
            config_paths: 配置文件路径列表，如果为None则使用默认路径
        """
        # 默认配置文件路径
        if config_paths is None:
            config_dir = Path(__file__).parent.parent.parent / "datasource" / "config"
            config_paths = [
                str(config_dir / "financial_indicators.yaml"),
                str(config_dir / "financial_statements_a_stock.yaml"),
                str(config_dir / "financial_statements_hk_stock.yaml"),
                str(config_dir / "financial_statements_us_stock.yaml"),
            ]

        self._config_paths = config_paths
        self._namespaced_configs: Dict[str, NamespacedMarketConfig] = {}
        self._is_loaded = False
        self._load_history: List[Dict[str, Any]] = []

    def load_configs(self) -> bool:
        """
        加载所有配置文件 - 实现IConfigLoader接口

        Returns:
            bool: 加载是否成功
        """
        # 为了兼容性，保留原有方法
        return self.load_all_configs()

    def load_all_configs(self) -> bool:
        """
        一次性加载所有配置

        Returns:
            bool: 加载是否成功
        """
        if self._is_loaded:
            return True  # 避免重复加载

        start_time = time.time()

        try:
            # 加载每个配置文件
            for config_path in self._config_paths:
                if self._load_single_config(config_path):
                    self._load_history.append({
                        'config_path': config_path,
                        'load_time': time.time() - start_time,
                        'status': 'success'
                    })

            self._is_loaded = True
            load_time = time.time() - start_time

            print(f"✅ 成功加载 {len(self._namespaced_configs)} 个市场配置，耗时 {load_time:.3f}秒")
            return True

        except Exception as e:
            self._load_history.append({
                'config_path': config_path,
                'load_time': time.time() - start_time,
                'status': 'failed',
                'error': str(e)
            })

            print(f"❌ 配置加载失败: {e}")
            return False

    def _load_single_config(self, config_path: str) -> bool:
        """
        加载单个配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            bool: 加载是否成功
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                print(f"⚠️ 配置文件不存在: {config_path}")
                return False

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if not config_data or not isinstance(config_data, dict):
                print(f"⚠️ 配置文件格式错误: {config_path}")
                return False

            # 解析markets配置
            if 'markets' in config_data:
                for market_id, market_data in config_data['markets'].items():
                    if self._create_namespaced_config(market_id, market_data, config_data):
                        print(f"✅ 成功加载市场配置: {market_id}")

            return True

        except Exception as e:
            print(f"❌ 加载配置文件失败 {config_path}: {e}")
            return False

    def _create_namespaced_config(self, market_id: str, market_data: Dict[str, Any],
                                 full_config_data: Dict[str, Any]) -> bool:
        """
        创建命名空间市场配置

        Args:
            market_id: 市场ID
            market_data: 市场数据
            full_config_data: 完整配置数据

        Returns:
            bool: 创建是否成功
        """
        try:
            # 基本市场信息
            name = market_data.get('name', market_id)
            currency = market_data.get('currency', 'CNY')

            # 解析字段配置
            fields = {}
            for field_id, field_data in market_data.items():
                # 跳过非字段配置
                if field_id in ['name', 'currency', 'description']:
                    continue

                if isinstance(field_data, dict) and 'name' in field_data and 'keywords' in field_data:
                    # 检查是否为窄表字段
                    api_field = field_data.get('api_field')
                    filter_value = field_data.get('filter_value')
                    value_field = field_data.get('value_field')

                    # 判断字段类型
                    if api_field and filter_value and value_field:
                        field_type = "narrow"
                    else:
                        field_type = "standard"

                    # 创建FieldInfo对象，支持窄表结构
                    field_info = FieldInfo(
                        name=field_data['name'],
                        keywords=field_data['keywords'],
                        priority=field_data.get('priority', 1),
                        description=field_data.get('description', ''),
                        api_field=api_field,
                        filter_value=filter_value,
                        value_field=value_field,
                        field_type=field_type
                    )
                    # 存储来源类型信息在内部字典中（GREEN阶段 workaround）
                    field_info._source_type = self._infer_source_type(field_id, full_config_data)
                    fields[field_id] = field_info

            # 创建命名空间配置
            namespaced_config = NamespacedMarketConfig(
                market_id=market_id,
                name=name,
                currency=currency,
                fields=fields,
                namespace=market_id
            )

            self._namespaced_configs[market_id] = namespaced_config
            return True

        except Exception as e:
            print(f"❌ 创建命名空间配置失败 {market_id}: {e}")
            return False

    def _infer_source_type(self, field_id: str, config_data: Dict[str, Any]) -> str:
        """
        推断字段来源类型

        Args:
            field_id: 字段ID
            config_data: 配置数据

        Returns:
            str: 来源类型 ('financial_indicators', 'financial_statements', 'unknown')
        """
        # 从配置文件路径推断来源类型
        if 'financial_indicators' in str(config_data):
            return 'financial_indicators'
        elif 'financial_statements' in str(config_data):
            return 'financial_statements'
        else:
            # 从字段ID特征推断
            indicators_patterns = ['ROE', 'ROA', 'RATIO', 'RATE', 'MARGIN']
            statements_patterns = ['TOTAL_', 'NET_', 'GROSS_', 'OPERATING_', 'CURRENT_']

            if any(pattern in field_id for pattern in indicators_patterns):
                return 'financial_indicators'
            elif any(pattern in field_id for pattern in statements_patterns):
                return 'financial_statements'
            else:
                return 'unknown'

    def get_market_config(self, market_id: str) -> Optional[MarketConfig]:
        """
        获取指定市场的配置 - 实现IConfigLoader接口

        Args:
            market_id: 市场ID (如 'a_stock', 'hk_stock', 'us_stock')

        Returns:
            MarketConfig: 市场配置对象，如果不存在则返回None
        """
        namespaced_config = self._namespaced_configs.get(market_id)
        if namespaced_config:
            # 转换为MarketConfig格式
            return MarketConfig(
                name=namespaced_config.name,
                currency=namespaced_config.currency,
                fields=namespaced_config.fields
            )
        return None

    def get_namespaced_config(self, market_id: str) -> Optional[NamespacedMarketConfig]:
        """
        获取指定市场的命名空间配置

        Args:
            market_id: 市场ID

        Returns:
            NamespacedMarketConfig: 市场配置，如果不存在返回None
        """
        return self._namespaced_configs.get(market_id)

    def get_cross_market_fields(self, field_id: str) -> Dict[str, FieldInfo]:
        """
        获取跨市场字段对比

        Args:
            field_id: 字段ID

        Returns:
            Dict[str, FieldInfo]: {market_id: FieldInfo} 映射
        """
        result = {}
        for market_id, config in self._namespaced_configs.items():
            if field_id in config.fields:
                result[market_id] = config.fields[field_id]
        return result

    def get_available_markets(self) -> List[str]:
        """
        获取所有可用的市场列表 - 实现IConfigLoader接口

        Returns:
            List[str]: 市场ID列表
        """
        return list(self._namespaced_configs.keys())

    def get_all_markets(self) -> List[str]:
        """
        获取所有市场ID

        Returns:
            List[str]: 市场ID列表
        """
        return self.get_available_markets()  # 复用接口方法

    def get_field_count(self, market_id: str = None) -> Dict[str, int]:
        """
        获取字段数量统计

        Args:
            market_id: 指定市场ID，如果为None则返回所有市场统计

        Returns:
            Dict[str, int]: 字段数量统计
        """
        if market_id:
            config = self._namespaced_configs.get(market_id)
            return {market_id: len(config.fields) if config else 0}
        else:
            return {mid: len(config.fields) for mid, config in self._namespaced_configs.items()}

    def is_loaded(self) -> bool:
        """
        检查配置是否已加载

        Returns:
            bool: 是否已加载
        """
        return self._is_loaded

    def get_load_history(self) -> List[Dict[str, Any]]:
        """
        获取加载历史记录

        Returns:
            List[Dict]: 加载历史记录
        """
        return self._load_history.copy()

    def search_fields(self, keyword: str, market_id: str = None) -> List[Dict[str, Any]]:
        """
        搜索字段（简单实现，满足TDD测试要求）

        Args:
            keyword: 搜索关键字
            market_id: 指定市场ID，如果为None则搜索所有市场

        Returns:
            List[Dict]: 搜索结果
        """
        results = []

        markets_to_search = [market_id] if market_id else list(self._namespaced_configs.keys())

        for mid in markets_to_search:
            config = self._namespaced_configs.get(mid)
            if config:
                for field_id, field_info in config.fields.items():
                    # 简单的关键字匹配
                    if (keyword.lower() in field_info.name.lower() or
                        keyword.lower() in field_id.lower() or
                        any(keyword.lower() in kw.lower() for kw in field_info.keywords)):

                        results.append({
                            'market_id': mid,
                            'field_id': field_id,
                            'field_info': field_info,
                            'similarity': self._calculate_similarity(keyword, field_info)
                        })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results

    def _calculate_similarity(self, keyword: str, field_info: FieldInfo) -> float:
        """
        计算关键字与字段的相似度（简单实现）

        Args:
            keyword: 关键字
            field_info: 字段信息

        Returns:
            float: 相似度得分 (0-1)
        """
        keyword_lower = keyword.lower()

        # 精确匹配
        if keyword_lower == field_info.name.lower() or keyword_lower == field_info.field_id.lower():
            return 1.0

        # 包含匹配
        if keyword_lower in field_info.name.lower():
            return 0.9
        if keyword_lower in field_info.field_id.lower():
            return 0.8

        # 关键字匹配
        for kw in field_info.keywords:
            if keyword_lower == kw.lower():
                return 0.9
            if keyword_lower in kw.lower():
                return 0.7

        # 模糊匹配
        return 0.3

    def reload_config(self, config_path: str = None) -> bool:
        """
        重新加载配置

        Args:
            config_path: 指定配置文件路径，如果为None则重新加载所有配置

        Returns:
            bool: 重新加载是否成功
        """
        if config_path:
            # 重新加载指定配置文件
            return self._load_single_config(config_path)
        else:
            # 重新加载所有配置
            self._namespaced_configs.clear()
            self._is_loaded = False
            self._load_history.clear()
            return self.load_all_configs()

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要信息

        Returns:
            Dict[str, Any]: 配置摘要
        """
        total_fields = sum(len(config.fields) for config in self._namespaced_configs.values())

        return {
            'total_markets': len(self._namespaced_configs),
            'total_fields': total_fields,
            'is_loaded': self._is_loaded,
            'load_history_count': len(self._load_history),
            'market_details': {
                mid: {
                    'name': config.name,
                    'currency': config.currency,
                    'field_count': len(config.fields)
                }
                for mid, config in self._namespaced_configs.items()
            }
        }