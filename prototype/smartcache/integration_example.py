"""
SQLite智能缓存 - Queryer集成示例 (KISS原则)

展示如何将最小化缓存集成到现有的Queryer架构中。
只保留核心功能，去除所有不必要的复杂性。
"""

import pandas as pd
import logging
from typing import Dict
from simple_cache import simple_cache, SimpleCache

logger = logging.getLogger(__name__)


# 模拟真实akshare调用
def mock_akshare_call(symbol: str) -> pd.DataFrame:
    """模拟akshare.stock_financial_abstract调用"""
    logger.info(f"   📡 akshare.stock_financial_abstract: {symbol}")

    # 根据股票生成真实感的数据
    stock_data = {
        'SH600519': {'eps_base': 35.2, 'roe_base': 28.5, 'revenue_base': 1200},
        'SZ000001': {'eps_base': 2.8, 'roe_base': 12.3, 'revenue_base': 800},
        '00700': {'eps_base': 15.8, 'roe_base': 22.1, 'revenue_base': 6000},
        '00941': {'eps_base': 6.2, 'roe_base': 9.8, 'revenue_base': 8000},
        'AAPL': {'eps_base': 5.5, 'roe_base': 35.2, 'revenue_base': 394000},
        'TSLA': {'eps_base': 3.2, 'roe_base': 18.7, 'revenue_base': 81000}
    }

    base = stock_data.get(symbol, {'eps_base': 5.0, 'roe_base': 15.0, 'revenue_base': 1000})

    # 生成2023年季度数据
    data = []
    for q in range(1, 5):
        date = f"2023-{q*3:02d}-31"
        data.append({
            'symbol': symbol,
            'date': date,
            'basic_eps': round(base['eps_base'] * (1 + q * 0.05), 2),
            'roe': round(base['roe_base'] * (1 + q * 0.03), 2),
            'revenue': round(base['revenue_base'] * (1 + q * 0.1), 2)
        })

    return pd.DataFrame(data)


class BaseQueryer:
    """基础查询器 - 最小化实现"""

    def __init__(self, cache: SimpleCache = None):
        self.cache = cache

    def query(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """统一查询接口"""
        return self._query_with_dates(symbol, start_date, end_date)

    @simple_cache()
    def _query_with_dates(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """带缓存的查询逻辑"""
        # 获取原始数据
        df = self._query_raw(symbol)

        # 简单的日期过滤
        if start_date and 'date' in df.columns:
            df = df[df['date'] >= start_date]
        if end_date and 'date' in df.columns:
            df = df[df['date'] <= end_date]

        return df

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """原始数据查询 - 子类实现"""
        raise NotImplementedError


class AStockIndicatorQueryer(BaseQueryer):
    """A股财务指标查询器"""

    def __init__(self):
        super().__init__(SimpleCache("./a_stock_indicators.db"))

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股财务指标"""
        return mock_akshare_call(symbol)


class AStockBalanceSheetQueryer(BaseQueryer):
    """A股资产负债表查询器"""

    def __init__(self):
        super().__init__(SimpleCache("./a_stock_balance.db"))

    @simple_cache()
    def _query_with_dates(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """资产负债表使用report_date字段"""
        df = self._query_raw(symbol)

        # 使用report_date字段进行日期过滤
        if start_date and 'report_date' in df.columns:
            df = df[df['report_date'] >= start_date]
        if end_date and 'report_date' in df.columns:
            df = df[df['report_date'] <= end_date]

        return df

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """查询A股资产负债表"""
        # 重命名date为report_date以适配实际API
        df = mock_akshare_call(symbol)
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'report_date'})
        return df


class FinancialQueryService:
    """财务查询服务 - 统一入口"""

    def __init__(self):
        self.indicators_queryer = AStockIndicatorQueryer()
        self.balance_queryer = AStockBalanceSheetQueryer()

    def get_financial_indicators(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取财务指标"""
        return self.indicators_queryer.query(symbol, start_date, end_date)

    def get_balance_sheet(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取资产负债表"""
        return self.balance_queryer.query(symbol, start_date, end_date)

    def get_complete_data(self, symbol: str, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """获取完整财务数据"""
        return {
            'indicators': self.get_financial_indicators(symbol, start_date, end_date),
            'balance_sheet': self.get_balance_sheet(symbol, start_date, end_date)
        }


def demo_integration():
    """演示Queryer集成"""
    print("🎯 SQLite智能缓存 - Queryer集成")
    print("=" * 50)

    service = FinancialQueryService()
    symbols = ["SH600519", "SZ000001", "00700"]

    for symbol in symbols:
        print(f"\n🏢 {symbol}")
        print("-" * 30)

        # 第一次查询 - API调用
        indicators = service.get_financial_indicators(symbol, "2023-01-01", "2023-12-31")
        print(f"财务指标: {len(indicators)} 条记录")

        # 第二次查询 - 缓存命中
        indicators2 = service.get_financial_indicators(symbol, "2023-01-01", "2023-12-31")
        print(f"缓存命中: {len(indicators2)} 条记录")

        # 不同查询类型
        balance = service.get_balance_sheet(symbol, "2023-01-01", "2023-12-31")
        print(f"资产负债表: {len(balance)} 条记录")

    print(f"\n✅ 集成演示完成")
    print("\n💡 集成特点:")
    print("   - 装饰器透明集成")
    print("   - 不同类型独立缓存")
    print("   - 统一查询接口")
    print("   - 最小化代码侵入")


if __name__ == "__main__":
    demo_integration()