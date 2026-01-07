"""
港股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class HKStockMarketFields(StandardFields):
    """
    港股市场字段 = IFRS标准字段 + 港股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        HKStockMarketFields (港股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[HKStockMarketFields.TOTAL_REVENUE]

        # 港股特定字段 (未来添加)
        # goodwill = df[HKStockMarketFields.GOODWILL]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加港股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== 港股特定字段 (未来添加) ==========
    # 示例:
    # GOODWILL = "hk_goodwill"  # 商誉
    # ASSOCIATES_INVESTMENT = "hk_associates_investment"  # 于联营公司投资
