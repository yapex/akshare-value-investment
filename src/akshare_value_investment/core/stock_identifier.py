"""
智能股票代码识别器

自动识别股票代码所属市场并标准化格式。
"""

import re
from typing import Tuple, Optional, List
from .models import MarketType


class StockIdentifier:
    """智能股票代码识别器"""

    def __init__(self):
        """初始化股票识别器"""
        self._build_prefix_mapping()
        self._build_suffix_patterns()

    def _build_prefix_mapping(self):
        """构建前缀映射"""
        self.prefix_mapping = {
            "CN.": MarketType.A_STOCK,
            "A.": MarketType.A_STOCK,
            "HK.": MarketType.HK_STOCK,
            "H.": MarketType.HK_STOCK,
            "US.": MarketType.US_STOCK,
            "U.": MarketType.US_STOCK,
        }

    def _build_suffix_patterns(self):
        """构建后缀模式"""
        self.suffix_patterns = {
            r"\.SS$": MarketType.A_STOCK,
            r"\.SZ$": MarketType.A_STOCK,
            r"\.HK$": MarketType.HK_STOCK,
            r"\.O$": MarketType.US_STOCK,
            r"\.NASDAQ$": MarketType.US_STOCK,
            r"\.NYSE$": MarketType.US_STOCK,
        }

    def identify(self, symbol: str, default_market: Optional[MarketType] = None) -> Tuple[MarketType, str]:
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
            return MarketType.US_STOCK, ""  # 默认美股

        symbol = symbol.strip()

        # 1. 显式前缀匹配 (优先级最高)
        for prefix, market in self.prefix_mapping.items():
            if symbol.upper().startswith(prefix):
                clean_symbol = symbol[len(prefix):]
                return market, clean_symbol

        # 2. 后缀模式匹配
        for pattern, market in self.suffix_patterns.items():
            if re.search(pattern, symbol, re.IGNORECASE):
                clean_symbol = re.sub(pattern, "", symbol, flags=re.IGNORECASE)
                return market, clean_symbol

        # 3. 格式推断
        # A股：6位数字
        if re.fullmatch(r"\d{6}", symbol):
            return MarketType.A_STOCK, symbol

        # 港股：5位数字，优先匹配以0开头的
        if re.fullmatch(r"0\d{4}", symbol):
            return MarketType.HK_STOCK, symbol
        elif re.fullmatch(r"\d{5}", symbol):
            return MarketType.HK_STOCK, symbol

        # 美股：字母代码
        if re.fullmatch(r"[A-Za-z]{1,5}", symbol):
            return MarketType.US_STOCK, symbol.upper()

        # 4. 默认市场回退
        if default_market:
            return default_market, symbol

        # 5. 无法识别，默认美股
        return MarketType.US_STOCK, symbol

    def format_symbol(self, market: MarketType, symbol: str) -> str:
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
                return symbol.zfill(5)
            return symbol
        elif market == MarketType.US_STOCK:
            return symbol.upper()
        else:
            return symbol

    def get_supported_markets(self) -> List[MarketType]:
        """
        获取支持的市场类型列表

        Returns:
            支持的市场类型列表
        """
        return list(MarketType)

    def validate_symbol(self, symbol: str, market: MarketType) -> bool:
        """
        验证股票代码格式是否正确

        Args:
            symbol: 股票代码
            market: 市场类型

        Returns:
            是否格式正确
        """
        if not symbol:
            return False

        if market == MarketType.A_STOCK:
            return bool(re.fullmatch(r"\d{6}", symbol))
        elif market == MarketType.HK_STOCK:
            return bool(re.fullmatch(r"\d{5}", symbol))
        elif market == MarketType.US_STOCK:
            return bool(re.fullmatch(r"[A-Za-z]{1,5}", symbol))
        return False