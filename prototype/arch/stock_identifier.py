#!/usr/bin/env python3
"""
智能股票代码识别器

自动识别股票代码所属市场并标准化格式。
"""

import re
from typing import Tuple, Optional
from data_models import MarketType


class StockIdentifier:
    """智能股票代码识别器"""

    @staticmethod
    def identify_market(symbol: str, default_market: Optional[MarketType] = None) -> Tuple[MarketType, str]:
        """
        识别股票代码市场类型并标准化代码格式

        Args:
            symbol: 原始股票代码
            default_market: 默认市场（当无法识别时使用）

        Returns:
            (市场类型, 标准化后的股票代码)
        """
        if not symbol:
            if default_market:
                return default_market, ""
            raise ValueError("股票代码不能为空")

        symbol = symbol.strip()

        # 1. 显式前缀匹配 (优先级最高)
        prefix_mapping = {
            "CN.": MarketType.A_STOCK,
            "HK.": MarketType.HK_STOCK,
            "US.": MarketType.US_STOCK,
            "A.": MarketType.A_STOCK,
            "H.": MarketType.HK_STOCK,
            "U.": MarketType.US_STOCK,
        }

        for prefix, market in prefix_mapping.items():
            if symbol.upper().startswith(prefix):
                clean_symbol = symbol[len(prefix):]
                return market, clean_symbol

        # 2. 后缀模式匹配
        suffix_patterns = {
            r"\.SS$": MarketType.A_STOCK,
            r"\.SZ$": MarketType.A_STOCK,
            r"\.HK$": MarketType.HK_STOCK,
            r"\.O$": MarketType.US_STOCK,
            r"\.NASDAQ$": MarketType.US_STOCK,
            r"\.NYSE$": MarketType.US_STOCK,
        }

        for pattern, market in suffix_patterns.items():
            if re.search(pattern, symbol, re.IGNORECASE):
                clean_symbol = re.sub(pattern, "", symbol, flags=re.IGNORECASE)
                return market, clean_symbol

        # 3. 格式推断
        # A股：6位数字
        if re.fullmatch(r"\d{6}", symbol):
            return MarketType.A_STOCK, symbol

        # 港股：5位数字，可能以0开头
        if re.fullmatch(r"0\d{4}", symbol) or re.fullmatch(r"\d{5}", symbol):
            return MarketType.HK_STOCK, symbol

        # 美股：字母代码
        if re.fullmatch(r"[A-Za-z]{1,5}", symbol):
            return MarketType.US_STOCK, symbol.upper()

        # 4. 默认市场回退
        if default_market:
            return default_market, symbol

        # 5. 无法识别，抛出异常
        raise ValueError(f"无法识别股票代码 {symbol} 的市场类型，请使用显式前缀如 CN., HK., US.")

    @staticmethod
    def format_symbol(market: MarketType, symbol: str) -> str:
        """
        格式化股票代码显示

        Args:
            market: 市场类型
            symbol: 股票代码

        Returns:
            格式化后的股票代码字符串
        """
        if market == MarketType.A_STOCK:
            return f"{symbol}"
        elif market == MarketType.HK_STOCK:
            # 港股代码标准化为5位数字
            if len(symbol) < 5:
                symbol = symbol.zfill(5)
            return f"{symbol}"
        elif market == MarketType.US_STOCK:
            return f"{symbol}"
        else:
            return symbol

    @staticmethod
    def get_market_display_name(market: MarketType) -> str:
        """获取市场的显示名称"""
        display_names = {
            MarketType.A_STOCK: "A股",
            MarketType.HK_STOCK: "港股",
            MarketType.US_STOCK: "美股"
        }
        return display_names.get(market, "未知市场")


# 便捷函数
def identify_stock(symbol: str, default_market: Optional[MarketType] = None) -> Tuple[MarketType, str]:
    """便捷的股票代码识别函数"""
    return StockIdentifier.identify_market(symbol, default_market)


if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "600519",      # A股
        "CN.000001",   # A股（显式前缀）
        "00700",       # 港股
        "HK.00941",    # 港股（显式前缀）
        "TSLA",        # 美股
        "US.AAPL",     # 美股（显式前缀）
        "BABA",        # 美股
    ]

    print("🔍 股票代码识别测试")
    print("=" * 50)

    for symbol in test_cases:
        try:
            market, clean_symbol = identify_stock(symbol)
            display_name = StockIdentifier.get_market_display_name(market)
            formatted_symbol = StockIdentifier.format_symbol(market, clean_symbol)
            print(f"{symbol:<12} -> {display_name} {formatted_symbol}")
        except Exception as e:
            print(f"{symbol:<12} -> 错误: {e}")