"""
快速修复指南：修复测试中的常见问题
"""

# 主要问题：组件测试中的 mock 路径不正确
# 解决方案：使用正确的导入路径

# 问题 1: ROIC 组件测试
# 错误: with patch('components.roic.calculate_roic')
# 正确:
with patch('services.calculators.roic.calculate') as mock_calculate:
    # ...

# 问题 2: 净利润估值组件测试
# 错误: with patch('components.net_income_valuation.calculate_net_income_valuation')
# 正确:
with patch('services.calculators.net_income_valuation.calculate') as mock_calculate:
    # ...

# 问题 3: DCF 估值组件测试
# 正确:
with patch('services.calculators.dcf_valuation.calculate') as mock_calculate:
    # ...
