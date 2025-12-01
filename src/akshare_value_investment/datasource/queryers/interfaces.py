"""
数据查询器模块接口定义

定义查询器模块的核心接口，为整个查询器模块提供统一的抽象层，
确保不同实现的查询器都遵循相同的行为契约。
"""

from typing import Protocol, Optional
import pandas as pd
from ...core.models import MarketType


class IDataQueryer(Protocol):
    """
    数据查询器接口

    定义所有数据查询器必须实现的基本接口。提供统一的查询方法，
    支持日期范围过滤和标准化的数据返回格式。

    ## 🎯 接口设计原则

    ### 统一性
    - 所有查询器实现相同的query方法签名
    - 统一的参数命名和类型定义
    - 标准化的DataFrame返回格式

    ### 可扩展性
    - 支持可选的日期范围参数
    - 允许子类扩展特定市场功能
    - 兼容缓存和性能优化

    ### 容错性
    - 优雅处理API调用失败
    - 提供清晰的错误信息
    - 支持部分数据返回
    """

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询数据并返回DataFrame，支持日期范围过滤

        这是所有查询器的核心方法，提供统一的数据访问接口。
        内部实现可能包含缓存、API调用、数据转换等逻辑。

        Args:
            symbol (str): 股票代码，支持不同市场的标准格式
                - A股: 6位数字 (600519, 000001)
                - 港股: 5位数字 (00700, 09988)
                - 美股: 英文代码 (AAPL, MSFT)
            start_date (Optional[str]): 开始日期，YYYY-MM-DD格式
                - 用于过滤指定时间范围的数据
                - 如果为None，通常返回最早的数据
                - 支持缓存系统的智能增量更新
            end_date (Optional[str]): 结束日期，YYYY-MM-DD格式
                - 用于过滤指定时间范围的数据
                - 如果为None，通常返回最新的数据
                - 与start_date组合使用进行范围查询

        Returns:
            pd.DataFrame: 包含财务数据的DataFrame，具有以下特征：
                - **时间列**: 包含日期信息（date, report_date等）
                - **股票代码**: 标识股票的唯一代码
                - **财务数据**: 各项财务指标的具体数值
                - **数据格式**: 根据不同市场可能使用中英文字段名
                - **时间排序**: 通常按时间倒序排列（最新在前）

        Raises:
            ValueError: 当股票代码格式无效时
            ConnectionError: 当网络连接失败时
            Exception: 其他API调用或数据处理异常

        Examples:
            >>> queryer = SomeDataQueryer()
            >>> # 查询全部历史数据
            >>> data = queryer.query("600519")
            >>>
            >>> # 查询指定时间范围数据
            >>> data = queryer.query("600519", "2023-01-01", "2023-12-31")
            >>>
            >>> # 查询指定日期之后的数据
            >>> data = queryer.query("600519", start_date="2023-01-01")

        Note:
            - 实际实现可能使用缓存系统优化性能
            - 不同市场的数据格式和字段名称可能不同
            - 部分API可能不支持日期参数，返回全量数据
            - 建议参考具体查询器的详细文档
        """
        ...

