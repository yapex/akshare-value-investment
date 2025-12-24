"""
组件接口规范

定义所有分析组件必须实现的接口规范，使用 Protocol 提供类型检查。
"""

from typing import Protocol


class AnalysisComponent(Protocol):
    """分析组件协议（接口规范）

    定义所有分析组件必须实现的接口规范。

    使用 Protocol 而非 ABC 的原因：
    1. 更灵活：不需要继承
    2. 类型安全：mypy 会检查是否符合接口
    3. 结构化类型：鸭子类型 + 类型检查

    示例：
        >>> class MyComponent:
        ...     title = "我的组件"
        ...
        ...     @staticmethod
        ...     def render(symbol: str, market: str, years: int) -> bool:
        ...         return True
    """

    # 类属性（必需）
    title: str  # 组件显示标题

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染组件

        Args:
            symbol: 股票代码
            market: 市场类型（A股/港股/美股）
            years: 查询年数

        Returns:
            bool: 是否成功渲染（True=成功，False=失败）
        """
        ...
