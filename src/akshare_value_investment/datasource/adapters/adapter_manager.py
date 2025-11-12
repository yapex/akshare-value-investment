"""
适配器管理器

管理和协调不同市场适配器的核心组件。
实现IQueryService接口，为上层提供统一的查询服务。
"""

from typing import List, Optional

from .a_stock_adapter import AStockAdapter
from .hk_stock_adapter import HKStockAdapter
from .us_stock_adapter import USStockAdapter
from ...core.models import MarketType, QueryResult
from ...core.stock_identifier import StockIdentifier


class AdapterManager:
    """适配器管理器 - 简化版本，实现IQueryService接口"""

    def __init__(self, stock_identifier: Optional[StockIdentifier] = None):
        """
        初始化适配器管理器 - 简化版本，不需要字段映射器

        Args:
            stock_identifier: 股票识别器实例
        """
        # 创建适配器实例 - 先创建适配器，再获取其market属性
        a_stock_adapter = AStockAdapter()
        hk_stock_adapter = HKStockAdapter()
        us_stock_adapter = USStockAdapter()

        self.adapters = {
            a_stock_adapter.market: a_stock_adapter,
            hk_stock_adapter.market: hk_stock_adapter,
            us_stock_adapter.market: us_stock_adapter,
        }

        # 股票识别器
        self.stock_identifier = stock_identifier or StockIdentifier()

    def get_adapter(self, market: MarketType):
        """
        获取指定市场的适配器

        Args:
            market: 市场类型

        Returns:
            市场适配器

        Raises:
            ValueError: 当市场类型不支持时
        """
        if market not in self.adapters:
            raise ValueError(f"不支持的市场类型: {market}")

        return self.adapters[market]

    def get_supported_markets(self) -> List[MarketType]:
        """
        获取支持的市场类型列表

        Returns:
            支持的市场类型列表
        """
        return list(self.adapters.keys())

    # IQueryService接口实现
    def query(self, symbol: str, **kwargs):
        """
        实现IQueryService接口的查询方法

        Args:
            symbol: 股票代码
            **kwargs: 其他查询参数 (start_date, end_date等)

        Returns:
            查询结果
        """
        try:
            # 识别市场类型
            market, _ = self.stock_identifier.identify(symbol)
            adapter = self.get_adapter(market)

            # 获取财务数据（传递时间参数）
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            data = adapter.get_financial_data(symbol, start_date=start_date, end_date=end_date)

            # 构建查询结果
            return QueryResult(
                success=True,
                data=data,
                message=f"成功获取{symbol}的财务数据",
                total_records=len(data)
            )
        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"查询失败: {str(e)}",
                total_records=0
            )

    def get_available_fields(self, market: MarketType = None):
        """
        实现IQueryService接口的获取可用字段方法

        Args:
            market: 市场类型

        Returns:
            空列表，简化版本通过raw_data访问原始字段
        """
        # 简化版本：用户通过FinancialIndicator.raw_data访问所有原始字段
        return []