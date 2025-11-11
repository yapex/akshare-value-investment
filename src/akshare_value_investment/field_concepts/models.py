"""
字段概念映射系统数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class MarketField:
    """市场字段信息"""
    name: str                    # 字段名
    unit: str                   # 单位
    priority: int              # 优先级
    latest_value: Optional[float] = None  # 最新值

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "unit": self.unit,
            "priority": self.priority,
            "latest_value": self.latest_value
        }


@dataclass
class ConceptSearchResult:
    """概念搜索结果"""
    concept_id: str                        # 概念ID
    concept_name: str                      # 概念名称
    confidence: float                      # 置信度 (0-1)
    description: str                       # 描述
    available_fields: Dict[str, List[MarketField]]  # 各市场可用字段

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "concept_id": self.concept_id,
            "concept_name": self.concept_name,
            "confidence": self.confidence,
            "description": self.description,
            "available_fields": {
                market: [field.to_dict() for field in fields]
                for market, fields in self.available_fields.items()
            }
        }


class ConceptConfig:
    """概念配置管理"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConceptConfig':
        """从字典创建配置对象"""
        cls.validate_config(config_dict)
        return cls(config_dict)

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """验证配置文件格式"""
        required_fields = ['version', 'concepts']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"配置文件缺少必需字段: {field}")

        # 验证概念结构
        for concept_id, concept_data in config.get('concepts', {}).items():
            if 'market_mappings' not in concept_data:
                raise ValueError(f"概念 {concept_id} 缺少市场映射")

    @property
    def version(self) -> str:
        """获取配置版本"""
        return self.config.get('version', '1.0.0')

    @property
    def concepts(self) -> Dict[str, Any]:
        """获取概念配置"""
        return self.config.get('concepts', {})

    def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """获取指定概念配置"""
        return self.concepts.get(concept_id)

    def get_all_concept_names(self) -> List[str]:
        """获取所有概念名称列表"""
        names = []
        for concept_data in self.concepts.values():
            names.append(concept_data.get('name', ''))
            names.extend(concept_data.get('aliases', []))
        return [name for name in names if name]

    def get_all_keywords(self) -> List[str]:
        """获取所有关键词列表"""
        keywords = []
        for concept_data in self.concepts.values():
            keywords.extend(concept_data.get('keywords', []))
        return list(set(keywords))