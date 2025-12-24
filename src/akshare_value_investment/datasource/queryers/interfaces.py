from typing import Protocol, Optional
import pandas as pd


class IDataQueryer(Protocol):
    """
    数据查询器接口

    定义所有数据查询器必须实现的基本接口。提供统一的数据访问方法，
    适配AKShare API的实际能力：不支持日期参数，总是返回全量历史数据。

    ## 🎯 接口设计原则

    ### 实际性
    - 基于AKShare API的实际限制设计
    - AKShare不支持日期参数，总是返回全量历史数据
    - 接口保持向后兼容，但明确说明行为

    ### 统一性
    - 所有查询器实现相同的query方法签名
    - 统一的参数命名和类型定义
    - 标准化的DataFrame返回格式

    ### 缓存优化
    - 使用diskcache缓存全量数据
    - 避免重复的API调用
    - 用户可自行进行日期过滤

    ### 容错性
    - 优雅处理API调用失败
    - 提供清晰的错误信息
    - 支持部分数据返回
    """

    def query(self, symbol: str, start_date: Optional[str] = None,
              end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询数据并返回DataFrame

        这是所有查询器的核心方法，提供统一的数据访问接口。
        由于AKShare API的限制，总是返回全量的历史数据，不进行服务端日期过滤。

        Args:
            symbol (str): 股票代码，支持不同市场的标准格式
                - A股: 6位数字 (600519, 000001) 或交易所前缀格式 (SH600519, SZ000001)
                - 港股: 5位数字 (00700, 09988) 或标准格式 (0700)
                - 美股: 英文代码 (AAPL, MSFT)，自动转换为大写
            start_date (Optional[str]): 开始日期，YYYY-MM-DD格式
                - 参数保留以保持接口兼容性，但不被使用
                - AKShare API不支持日期参数
            end_date (Optional[str]): 结束日期，YYYY-MM-DD格式
                - 参数保留以保持接口兼容性，但不被使用
                - AKShare API不支持日期参数

        Returns:
            pd.DataFrame: 包含全量历史财务数据的DataFrame，具有以下特征：
                - **时间列**: 包含日期信息（date, report_date等）
                - **股票代码**: 标识股票的唯一代码
                - **财务数据**: 各项财务指标的具体数值
                - **数据格式**: 根据不同市场可能使用中英文字段名
                - **时间排序**: 通常按时间倒序排列（最新在前）
                - **全量数据**: 包含所有可用的历史数据记录

        Raises:
            ValueError: 当股票代码格式无效时
            ConnectionError: 当网络连接失败时
            Exception: 其他API调用或数据处理异常

        Examples:
            >>> queryer = SomeDataQueryer()
            >>> # 查询全部历史数据
            >>> data = queryer.query("600519")
            >>>
            >>> # 查询数据（start_date和end_date参数被忽略）
            >>> data = queryer.query("600519", "2023-01-01", "2023-12-31")
            >>>
            >>> # 如需日期过滤，请在返回的DataFrame上自行过滤
            >>> full_data = queryer.query("600519")
            >>> filtered_data = full_data[full_data['report_date'] >= '2023-01-01']

        Note:
            - AKShare API不支持日期参数，总是返回全量历史数据
            - start_date和end_date参数仅保持接口兼容性
            - 实际使用缓存系统优化性能，避免重复API调用
            - 如需特定日期范围的数据，请自行在返回的DataFrame上过滤
            - 不同市场的数据格式和字段名称可能不同
        """
        ...
