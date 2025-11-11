"""
重构后的市场适配器实现

遵循SOLID原则，使用策略模式实现职责分离的适配器架构。
"""

from typing import List, Dict, Any

from .interfaces import IMarketAdapter
from .models import MarketType, FinancialIndicator
from .adapter_strategies_impl import AStockFinancialDataProcessor, AStockDataFetcher


class AStockAdapterRefactored(IMarketAdapter):
    """重构后的A股市场适配器 - 职责单一"""

    def __init__(self, data_processor=None):
        """
        初始化A股适配器 - 重构版本

        Args:
            data_processor: 财务数据处理器（可选，使用默认实现）
        """
        self.market = MarketType.A_STOCK
        self.data_processor = data_processor or AStockFinancialDataProcessor()

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """
        获取A股财务数据 - 重构版本，职责委托给专门的处理器

        Args:
            symbol: 股票代码

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            # 委托给专门的处理器处理所有复杂逻辑
            return self.data_processor.process_financial_data(symbol, raw_data_list=[])
        except Exception as e:
            raise RuntimeError(f"获取A股 {symbol} 财务数据失败: {str(e)}")

    @property
    def market_type(self) -> MarketType:
        """获取市场类型"""
        return self.market


class HKStockAdapterRefactored(IMarketAdapter):
    """重构后的港股市场适配器"""

    def __init__(self, data_processor=None):
        """
        初始化港股适配器

        Args:
            data_processor: 财务数据处理器
        """
        self.market = MarketType.HK_STOCK
        # 注意：港股数据处理器需要不同的实现策略
        # self.data_processor = data_processor or HKStockFinancialDataProcessor()

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """获取港股财务数据"""
        # TODO: 实现港股数据获取逻辑
        return []

    @property
    def market_type(self) -> MarketType:
        """获取市场类型"""
        return self.market


class USStockAdapterRefactored(IMarketAdapter):
    """重构后的美股市场适配器"""

    def __init__(self, data_processor=None):
        """
        初始化美股适配器

        Args:
            data_processor: 财务数据处理器
        """
        self.market = MarketType.US_STOCK
        # 注意：美股数据处理器需要不同的实现策略
        # self.data_processor = data_processor or USStockFinancialDataProcessor()

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """获取美股财务数据"""
        # TODO: 实现美股数据获取逻辑
        return []

    @property
    def market_type(self) -> MarketType:
        """获取市场类型"""
        return self.market


class AdapterFactory:
    """适配器工厂 - 负责创建适配器实例"""

    @staticmethod
    def create_adapter(market: MarketType, **kwargs) -> IMarketAdapter:
        """
        创建指定市场的适配器

        Args:
            market: 市场类型
            **kwargs: 适配器配置参数

        Returns:
            市场适配器实例

        Raises:
            ValueError: 当市场类型不支持时
        """
        adapter_classes = {
            MarketType.A_STOCK: AStockAdapterRefactored,
            MarketType.HK_STOCK: HKStockAdapterRefactored,
            MarketType.US_STOCK: USStockAdapterRefactored,
        }

        adapter_class = adapter_classes.get(market)
        if not adapter_class:
            raise ValueError(f"不支持的市场类型: {market}")

        return adapter_class(**kwargs)

    @staticmethod
    def create_all_adapters(**kwargs) -> Dict[MarketType, IMarketAdapter]:
        """
        创建所有市场的适配器

        Args:
            **kwargs: 适配器配置参数

        Returns:
            市场类型到适配器的映射字典
        """
        adapters = {}
        for market in MarketType:
            try:
                adapters[market] = AdapterFactory.create_adapter(market, **kwargs)
            except ValueError:
                # 跳过不支持的市场类型
                continue
        return adapters