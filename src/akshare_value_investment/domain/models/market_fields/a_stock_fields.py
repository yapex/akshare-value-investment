"""
A股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class AStockMarketFields(StandardFields):
    """
    A股市场字段 = IFRS标准字段 + A股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        AStockMarketFields (A股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[AStockMarketFields.TOTAL_REVENUE]

        # A股特定字段 (未来添加)
        # minority = df[AStockMarketFields.MINORITY_INTEREST]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加A股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== A股特定字段 (未来添加) ==========
    # 示例:
    # MINORITY_INTEREST = "a_minority_interest"  # 少数股东权益
    # CONSTRUCTION_IN_PROGRESS = "a_construction_in_progress"  # 在建工程
