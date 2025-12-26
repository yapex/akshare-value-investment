"""
财务指标计算器（已弃用）

⚠️ 警告：此类已弃用！请使用 services/calculators/ 下的专用计算器。

新架构：
- services/calculators/*.py - 各组件专用计算器（与 components 一一对应）
- services/calculators/common.py - 可重用的基础计算函数

迁移完成：
- ✅ roic.py -> calculators/roic.py
- ✅ dcf_valuation.py -> calculators/dcf_valuation.py
- ✅ cash_flow_pattern.py -> calculators/cash_flow_pattern.py
- ✅ revenue_growth.py -> calculators/revenue_growth.py
- ✅ ebit_margin.py -> calculators/ebit_margin.py
- ✅ net_profit_cash_ratio.py -> calculators/net_profit_cash_ratio.py
- ✅ free_cash_flow_ratio.py -> calculators/free_cash_flow_ratio.py
  - 包含 calculate() 和 calculate_investment_intensity_ratio()
- ✅ debt_to_equity.py -> calculators/debt_to_equity.py
- ✅ debt_to_fcf_ratio.py -> calculators/debt_to_fcf_ratio.py
- ✅ roe.py -> calculators/roe.py
- ✅ liquidity_ratio.py -> calculators/liquidity_ratio.py
  - 包含 calculate() 和 calculate_interest_coverage_ratio()

所有方法已迁移完成，Calculator 类已清空。
"""

import warnings


class Calculator:
    """财务指标计算器（已弃用）

    ⚠️ 此类已完全弃用！请使用 services/calculators/ 下的专用计算器！

    迁移示例：
    - 旧：from services.calculator import Calculator
          Calculator.calculate_roic(symbol, market, years)
    - 新：from services.calculators.roic import calculate as calculate_roic
          calculate_roic(symbol, market, years)

    各计算器模块：
    - services.calculators.roic
    - services.calculators.dcf_valuation
    - services.calculators.cash_flow_pattern
    - services.calculators.revenue_growth
    - services.calculators.ebit_margin
    - services.calculators.net_profit_cash_ratio
    - services.calculators.free_cash_flow_ratio
    - services.calculators.debt_to_equity
    - services.calculators.debt_to_fcf_ratio
    - services.calculators.roe
    - services.calculators.liquidity_ratio
    - services.calculators.common
    """

    def __init__(self):
        warnings.warn(
            "Calculator 类已完全弃用！请使用 services/calculators/ 下的专用计算器。\n"
            "例如：from services.calculators.roic import calculate as calculate_roic\n"
            "完整列表请参阅文档字符串。",
            DeprecationWarning,
            stacklevel=2
        )
