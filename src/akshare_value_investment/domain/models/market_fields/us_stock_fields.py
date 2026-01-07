"""
美股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class USStockMarketFields(StandardFields):
    """
    美股市场字段 = IFRS标准字段 + 美股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        USStockMarketFields (美股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[USStockMarketFields.TOTAL_REVENUE]

        # 美股特定字段 (未来添加)
        # goodwill = df[USStockMarketFields.GOODWILL]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加美股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== 美股特定字段 (未来添加) ==========
    # 示例:
    # GOODWILL = "us_goodwill"  # 商誉
    # CONTINUING_OPERATIONS_INCOME = "us_continuing_operations_income"  # 持续经营收入
