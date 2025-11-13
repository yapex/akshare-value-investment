"""
命名空间配置系统接口定义

基于SOLID原则重构，实现接口隔离和依赖倒置
"""

from typing import Dict, List, Optional, Any, Protocol, runtime_checkable

from .models import FieldInfo


@runtime_checkable
class INamespacedConfigLoader(Protocol):
    """命名空间配置加载器接口"""

    def load_all_configs(self) -> bool:
        """加载所有配置"""
        ...

    def get_namespaced_config(self, market_id: str) -> Optional['NamespacedMarketConfig']:
        """获取指定市场的命名空间配置"""
        ...

    def is_loaded(self) -> bool:
        """检查配置是否已加载"""
        ...


@runtime_checkable
class IConfigSearcher(Protocol):
    """配置搜索器接口"""

    def search_fields(self, keyword: str, market_id: str = None) -> List[Dict[str, Any]]:
        """搜索字段"""
        ...


@runtime_checkable
class ICrossMarketAnalyzer(Protocol):
    """跨市场分析器接口"""

    def get_cross_market_fields(self, field_id: str) -> Dict[str, FieldInfo]:
        """获取跨市场字段对比"""
        ...


@runtime_checkable
class IConfigManager(Protocol):
    """配置管理器接口"""

    def reload_config(self, config_path: str = None) -> bool:
        """重新加载配置"""
        ...

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        ...


@runtime_checkable
class IConfigParser(Protocol):
    """配置文件解析器接口"""

    def parse_config_file(self, config_path: str) -> Dict[str, Any]:
        """解析配置文件"""
        ...

    def validate_config_data(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据"""
        ...


@runtime_checkable
class ISourceAnalyzer(Protocol):
    """字段来源类型分析器接口"""

    def infer_source_type(self, field_id: str, context: Dict[str, Any]) -> str:
        """推断字段来源类型"""
        ...


@runtime_checkable
class IFieldIndexer(Protocol):
    """配置字段索引器接口"""

    def build_search_index(self, configs: Dict[str, 'NamespacedMarketConfig']) -> Dict[str, Any]:
        """构建搜索索引"""
        ...

    def search_fields(self, keyword: str, index: Dict[str, Any], market_id: str = None) -> List[Dict[str, Any]]:
        """基于索引搜索字段"""
        ...