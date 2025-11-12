"""
字段映射数据模型

包含字段信息、市场配置等核心数据结构
这些数据类被多个模块共享使用
"""

from typing import Dict, List
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

    @property
    def field_id(self) -> str:
        """获取字段ID（用于向后兼容）"""
        return self.name.upper().replace(' ', '_')


@dataclass
class MarketConfig:
    """市场配置"""
    name: str
    currency: str
    fields: Dict[str, FieldInfo]


__all__ = ['FieldInfo', 'MarketConfig']