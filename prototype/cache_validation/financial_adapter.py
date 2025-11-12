"""
财务数据适配器 - 验证装饰器缓存效果
模拟真实的业务场景
"""

from cache_decorators import smart_cache
from mock_akshare import mock_akshare_call
from typing import Dict, Any

class FinancialAdapter:
    """财务数据适配器"""

    def __init__(self):
        """初始化适配器"""
        self.market = "a_stock"

    @smart_cache("astock")
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """获取财务数据 - 添加缓存装饰器

        Args:
            symbol: 股票代码

        Returns:
            财务数据字典
        """
        # 模拟真实的akshare API调用
        data = mock_akshare_call(symbol, "financial")

        # 模拟数据预处理
        processed_data = {
            'market': self.market,
            'raw_data': data,
            'processed_at': 'mock_timestamp'
        }

        return processed_data

    @smart_cache("astock")
    def get_financial_indicator(self, symbol: str, indicator: str) -> Dict[str, Any]:
        """获取特定财务指标 - 验证参数敏感性

        Args:
            symbol: 股票代码
            indicator: 指标名称

        Returns:
            指标数据
        """
        # 获取基础数据
        base_data = self.get_financial_data(symbol)

        # 提取特定指标
        indicator_value = base_data['raw_data'].get(indicator, 0)

        return {
            'symbol': symbol,
            'indicator': indicator,
            'value': indicator_value,
            'source': 'extracted_from_base_data'
        }