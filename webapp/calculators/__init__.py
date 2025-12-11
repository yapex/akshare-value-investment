"""
检查项计算器模块
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from calculators.calculator_registry import (
    register_calculator,
    get_all_calculators,
    get_calculators_by_category,
    get_calculator,
    get_registry_info
)

# 导入所有计算器（自动注册）
from calculators.asset_checklists import (
    CashSafetyCalculator,
    CashAnomalyCalculator,
    NotesReceivableCalculator,
    ReceivablesCalculator,
    PrepaidExpensesCalculator,
    OtherReceivablesCalculator,
    BadDebtProvisionCalculator,
    InventoryRiskCalculator,
    FixedAssetDepreciationCalculator,
    FinancialFraudRiskCalculator
)

__all__ = [
    'register_calculator',
    'get_all_calculators',
    'get_calculators_by_category',
    'get_calculator',
    'get_registry_info',
    'CashSafetyCalculator',
    'CashAnomalyCalculator',
    'NotesReceivableCalculator',
    'ReceivablesCalculator',
    'PrepaidExpensesCalculator',
    'OtherReceivablesCalculator',
    'BadDebtProvisionCalculator',
    'InventoryRiskCalculator',
    'FixedAssetDepreciationCalculator',
    'FinancialFraudRiskCalculator'
]