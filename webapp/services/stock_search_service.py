"""
股票代码搜索服务

结合历史记录管理和股票识别器
"""
from typing import List
from akshare_value_investment.core.stock_identifier import StockIdentifier
from akshare_value_investment.core.models import MarketType
from utils.stock_history_manager import StockHistoryManager


class StockSearchService:
    """股票搜索服务"""

    def __init__(
        self,
        stock_identifier: StockIdentifier,
        history_manager: StockHistoryManager
    ):
        """
        初始化搜索服务

        Args:
            stock_identifier: 股票识别器
            history_manager: 历史记录管理器
        """
        self.identifier = stock_identifier
        self.history = history_manager

    def search(self, searchterm: str) -> List[tuple]:
        """
        搜索股票代码

        Args:
            searchterm: 搜索词

        Returns:
            list of (显示文本, 股票代码) 元组
        """
        # 1. 从历史记录中搜索
        history_results = self.history.search(searchterm, limit=8)

        # 2. 如果有搜索词，尝试识别新股票
        if searchterm and len(searchterm) >= 1:
            try:
                market, symbol = self.identifier.identify(searchterm)
                # 使用 format_symbol 获得真正标准化的代码（用于去重）
                standardized_symbol = self.identifier.format_symbol(market, symbol)

                # 构建市场标签
                market_labels = {
                    MarketType.A_STOCK: "A股",
                    MarketType.HK_STOCK: "港股",
                    MarketType.US_STOCK: "美股"
                }
                market_label = market_labels.get(market, "未知")

                # 检查是否已经在历史结果中（使用标准化代码比较）
                existing_symbols = [s for _, s in history_results]
                if standardized_symbol not in existing_symbols:
                    new_result = (f"{standardized_symbol} [{market_label}] ⭐", standardized_symbol)
                    history_results.insert(0, new_result)  # 插入到开头
            except Exception:
                # 识别失败，忽略
                pass

        return history_results

    def record_query(self, symbol: str, market: str, original_input: str):
        """
        记录查询

        Args:
            symbol: 标准化股票代码
            market: 市场类型
            original_input: 用户原始输入
        """
        self.history.add_record(symbol, market, original_input)
