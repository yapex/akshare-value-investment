"""
计算器注册表 - 管理所有检查项计算器
"""

from typing import Dict, List, Type, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_calculator import BaseCalculator
from models.base_models import ChecklistCategory

# 全局计算器注册表
_CALCULATOR_REGISTRY: Dict[str, Type[BaseCalculator]] = {}
_CALCULATOR_INSTANCES: Dict[str, BaseCalculator] = {}


def register_calculator(calculator_class: Type[BaseCalculator]) -> None:
    """注册计算器

    Args:
        calculator_class: 计算器类，必须继承自BaseCalculator
    """
    # 验证是否为有效的计算器
    if not issubclass(calculator_class, BaseCalculator):
        raise ValueError(f"计算器 {calculator_class.__name__} 必须继承自 BaseCalculator")

    # 获取检查项ID
    calculator_instance = calculator_class()
    question_id = calculator_instance.question_id

    if not question_id:
        raise ValueError(f"计算器 {calculator_class.__name__} 必须定义 question_id")

    # 注册计算器
    _CALCULATOR_REGISTRY[question_id] = calculator_class


def get_calculator(question_id: str) -> Optional[BaseCalculator]:
    """获取指定ID的计算器实例

    Args:
        question_id: 检查项ID

    Returns:
        计算器实例，如果不存在则返回None
    """
    if question_id not in _CALCULATOR_REGISTRY:
        return None

    # 如果已有实例，直接返回
    if question_id in _CALCULATOR_INSTANCES:
        return _CALCULATOR_INSTANCES[question_id]

    # 创建新实例
    calculator_class = _CALCULATOR_REGISTRY[question_id]
    instance = calculator_class()
    _CALCULATOR_INSTANCES[question_id] = instance

    return instance


def get_all_calculators() -> Dict[str, BaseCalculator]:
    """获取所有已注册的计算器实例

    Returns:
        计算器ID到实例的映射字典
    """
    calculators = {}
    for question_id in _CALCULATOR_REGISTRY:
        calculator = get_calculator(question_id)
        if calculator:
            calculators[question_id] = calculator
    return calculators


def get_calculators_by_category(category: ChecklistCategory) -> List[BaseCalculator]:
    """根据分类获取计算器列表

    Args:
        category: 检查分类

    Returns:
        该分类下的所有计算器实例
    """
    calculators = get_all_calculators()
    filtered = []
    for calculator in calculators.values():
        if calculator.category == category:
            filtered.append(calculator)

    # 按question_id排序
    filtered.sort(key=lambda x: x.question_id)
    return filtered


def get_registered_question_ids() -> List[str]:
    """获取所有已注册的检查项ID

    Returns:
        检查项ID列表
    """
    return list(_CALCULATOR_REGISTRY.keys())


def clear_registry() -> None:
    """清空注册表（主要用于测试）"""
    global _CALCULATOR_REGISTRY, _CALCULATOR_INSTANCES
    _CALCULATOR_REGISTRY.clear()
    _CALCULATOR_INSTANCES.clear()


def get_registry_info() -> Dict[str, Dict[str, str]]:
    """获取注册表信息，用于调试

    Returns:
        注册表信息字典
    """
    calculators = get_all_calculators()
    info = {}
    for question_id, calculator in calculators.items():
        info[question_id] = {
            "class": calculator.__class__.__name__,
            "question": calculator.question,
            "category": calculator.category.value,
            "description": calculator.description
        }
    return info