"""
多配置文件加载器（重构版）

基于组合模式的配置加载器，使用拆分后的专门组件
遵循单一职责原则（SRP），作为各组件的协调者
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .models import FieldInfo, MarketConfig
from .interfaces import IConfigLoader
from .config_file_reader import ConfigFileReader
from .config_merger import ConfigMerger, DefaultMergerStrategy


class MultiConfigLoader(IConfigLoader):
    """多配置文件加载器（重构版）

    使用组合模式，将原本的多重职责分离到专门的组件中
    现在只负责协调各个组件，符合单一职责原则
    """

    def __init__(
        self,
        config_paths: Optional[List[str]] = None,
        file_reader: Optional[ConfigFileReader] = None,
        config_merger: Optional[ConfigMerger] = None
    ):
        """
        初始化多配置加载器

        Args:
            config_paths: 配置文件路径列表，如果为None则使用默认路径
            file_reader: 文件读取器实例，如果为None则创建默认实例
            config_merger: 配置合并器实例，如果为None则创建默认实例
        """
        if config_paths is None:
            current_dir = Path(__file__).parent.parent.parent / "datasource" / "config"
            config_paths = [
                str(current_dir / "financial_indicators.yaml"),  # 财务指标
                str(current_dir / "financial_statements.yaml")   # 财务三表
            ]

        # 组合各个专门组件
        self._file_reader = file_reader or ConfigFileReader(config_paths)
        self._config_merger = config_merger or ConfigMerger(DefaultMergerStrategy())

        # 内部状态
        self._markets: Dict[str, MarketConfig] = {}
        self._is_loaded: bool = False

    def load_configs(self) -> bool:
        """
        加载所有配置文件

        使用组合的组件进行文件读取和配置合并

        Returns:
            是否加载成功
        """
        try:
            # 1. 使用文件读取器读取配置
            configs = self._file_reader.read_all_configs()

            if not configs:
                print("⚠️ 没有找到有效的配置文件")
                return False

            # 2. 使用配置合并器合并配置
            self._markets = self._config_merger.merge_configs(configs)

            # 3. 验证合并结果
            validation_result = self._config_merger.validate_merge_result(self._markets)
            if not validation_result['is_valid']:
                print("⚠️ 配置合并验证发现问题:")
                for issue in validation_result['issues']:
                    print(f"   - {issue}")

            # 4. 标记为已加载
            self._is_loaded = True

            # 5. 输出统计信息
            merge_summary = self._config_merger.get_merge_summary()
            print(f"✅ 配置加载完成: {merge_summary['total_configs_merged']} 个配置, "
                  f"{merge_summary['total_fields_merged']} 个字段")

            return True

        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return False

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

    def is_loaded(self) -> bool:
        """
        检查配置是否已加载

        Returns:
            是否已加载
        """
        return self._is_loaded

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取配置元数据

        Returns:
            元数据字典
        """
        if not self._is_loaded:
            return {}

        # 从文件读取器获取文件信息
        files_info = self._file_reader.get_all_files_info()
        metadata = {}

        for i, file_info in enumerate(files_info):
            if file_info['exists']:
                key = f'config_{i+1}'
                metadata[key] = {
                    'path': file_info['path'],
                    'version': file_info.get('version', 'unknown'),
                    'description': file_info.get('description', ''),
                    'size_bytes': file_info.get('size_bytes', 0),
                    'markets_count': file_info.get('markets_count', 0)
                }

        return metadata

    def get_categories_info(self) -> Dict[str, Any]:
        """
        获取分类信息

        Returns:
            分类信息字典
        """
        if not self._is_loaded:
            return {}

        # 基于配置合并器的历史信息
        merge_summary = self._config_merger.get_merge_summary()
        categories = {}

        for i, step in enumerate(merge_summary.get('merge_history', [])):
            key = f'config_{i+1}'
            categories[key] = {
                'version': step.get('config_version', 'unknown'),
                'description': step.get('config_description', ''),
                'fields_count': step.get('total_fields', 0),
                'markets_count': step.get('markets_count', 0)
            }

        return categories

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置摘要
        """
        if not self._is_loaded:
            return {}

        total_fields = sum(len(market.fields) for market in self._markets.values())
        markets_detail = {}

        for market_id, market_config in self._markets.items():
            # 分析字段优先级分布
            priority_distribution = {}
            for field_info in market_config.fields.values():
                priority = field_info.priority
                priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

            markets_detail[market_id] = {
                'name': market_config.name,
                'currency': market_config.currency,
                'fields_count': len(market_config.fields),
                'priority_distribution': priority_distribution
            }

        merge_summary = self._config_merger.get_merge_summary()

        return {
            'total_markets': len(self._markets),
            'total_fields': total_fields,
            'config_files': merge_summary.get('total_configs_merged', 0),
            'markets_detail': markets_detail,
            'merge_strategy': merge_summary.get('merge_strategy', 'unknown'),
            'load_timestamp': merge_summary.get('merge_history', [{}])[-1].get('timestamp', 'unknown')
        }

    def get_file_reader_stats(self) -> Dict[str, Any]:
        """
        获取文件读取器统计信息

        Returns:
            文件读取统计
        """
        return self._file_reader.get_file_stats()

    def get_merge_summary(self) -> Dict[str, Any]:
        """
        获取合并摘要

        Returns:
            合并摘要信息
        """
        return self._config_merger.get_merge_summary()

    def validate_configuration(self) -> Dict[str, Any]:
        """
        验证当前配置

        Returns:
            验证结果
        """
        if not self._is_loaded:
            return {
                'is_valid': False,
                'issues': ['配置未加载'],
                'statistics': {}
            }

        return self._config_merger.validate_merge_result(self._markets)

    def reload_configs(self) -> bool:
        """
        重新加载配置

        Returns:
            是否重新加载成功
        """
        print("🔄 重新加载配置...")
        self._markets.clear()
        self._is_loaded = False
        return self.load_configs()


# 为了向后兼容，保留原有的类名作为别名
__all__ = ['MultiConfigLoader']