"""
市场推断器

根据股票代码推断市场类型的具体实现
遵循单一职责原则（SRP），只关注市场推断逻辑
"""

import re
from typing import Optional, Dict, List
from .interfaces import IMarketInferrer


class DefaultMarketInferrer:
    """默认市场推断器实现

    基于股票代码格式推断市场类型
    支持A股、港股、美股的代码格式识别
    """

    def __init__(self):
        """初始化市场推断器"""
        # 定义各市场的股票代码模式
        self._patterns = {
            'a_stock': [
                r'^[0-9]{6}$',  # 6位纯数字：600000, 000001, 300001
                r'^60[0-9]{4}$',  # 沪市主板：60开头
                r'^00[0-9]{4}$',  # 深市主板/中小板：00开头
                r'^30[0-9]{4}$',  # 创业板：30开头
            ],
            'hk_stock': [
                r'^[0-9]{4,5}$',  # 4-5位数字：00700, 09988
                r'^[0-9]{5}\.HK$',  # 5位数字+.HK：09988.HK
                r'^[0-9]{4}\.HK$',  # 4位数字+.HK：00700.HK
            ],
            'us_stock': [
                r'^[A-Z]{1,5}$',  # 1-5位大写字母：AAPL, MSFT, TSLA
                r'^[A-Z]{1,5}\.US$',  # 带.US后缀：AAPL.US
                r'^[A-Z]{1,5}\.NASDAQ$',  # 带NASDAQ后缀：AAPL.NASDAQ
                r'^[A-Z]{1,5}\.NYSE$',  # 带NYSE后缀：BRK.NYSE
            ]
        }

        # 编译正则表达式模式
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        for market, patterns in self._patterns.items():
            self._compiled_patterns[market] = [re.compile(pattern) for pattern in patterns]

    def infer_market_type(self, symbol: str) -> Optional[str]:
        """
        根据股票代码推断市场类型

        Args:
            symbol: 股票代码

        Returns:
            市场ID (如 'a_stock', 'hk_stock', 'us_stock')，如果无法推断则返回None
        """
        if not symbol:
            return None

        symbol = symbol.strip().upper()

        # 优先级检查：先检查明确的带后缀格式
        if symbol.endswith('.HK'):
            return 'hk_stock'
        elif symbol.endswith(('.US', '.NASDAQ', '.NYSE')):
            return 'us_stock'

        # 移除可能存在的后缀再检查
        clean_symbol = symbol
        if '.' in clean_symbol:
            clean_symbol = clean_symbol.split('.')[0]

        # 按市场优先级检查
        for market_id, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(clean_symbol):
                    return market_id

        return None

    def supports_symbol(self, symbol: str) -> bool:
        """
        检查是否支持指定的股票代码

        Args:
            symbol: 股票代码

        Returns:
            是否支持
        """
        return self.infer_market_type(symbol) is not None

    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """
        获取支持的股票代码模式

        Returns:
            市场ID到正则表达式模式的映射
        """
        return self._patterns.copy()

    def add_custom_pattern(self, market_id: str, pattern: str) -> bool:
        """
        添加自定义模式（可选的扩展方法）

        Args:
            market_id: 市场ID
            pattern: 正则表达式模式

        Returns:
            是否添加成功
        """
        try:
            compiled_pattern = re.compile(pattern)

            if market_id not in self._patterns:
                self._patterns[market_id] = []
                self._compiled_patterns[market_id] = []

            self._patterns[market_id].append(pattern)
            self._compiled_patterns[market_id].append(compiled_pattern)

            return True
        except re.error:
            return False

    def get_market_statistics(self, symbols: List[str]) -> Dict[str, int]:
        """
        统计股票代码的市场分布（额外的实用方法）

        Args:
            symbols: 股票代码列表

        Returns:
            市场ID到股票数量的映射
        """
        statistics = {
            'a_stock': 0,
            'hk_stock': 0,
            'us_stock': 0,
            'unknown': 0
        }

        for symbol in symbols:
            market = self.infer_market_type(symbol)
            if market:
                statistics[market] += 1
            else:
                statistics['unknown'] += 1

        return statistics