"""
pytest fixtures and configuration

提供测试共享的 fixtures 和配置，包括 MockDataLoader 和其他测试工具。
"""

import os
import sys
import pandas as pd
import tempfile
import shutil
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import pytest
import diskcache

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))


class MockDataLoader:
    """通用Mock数据加载器"""

    def __init__(self, sample_data_dir: str = "tests/sample_data"):
        """
        初始化Mock数据加载器

        Args:
            sample_data_dir: 样本数据目录路径
        """
        self.sample_data_dir = sample_data_dir
        self._data_cache: Dict[str, pd.DataFrame] = {}

        # 验证样本数据目录存在
        if not os.path.exists(sample_data_dir):
            raise FileNotFoundError(f"样本数据目录不存在: {sample_data_dir}")

    def load_a_stock_indicators(self) -> pd.DataFrame:
        """加载A股财务指标样本数据"""
        return self._load_csv("a_stock_indicators_sample.csv")

    def load_a_stock_balance_sheet(self) -> pd.DataFrame:
        """加载A股资产负债表样本数据"""
        return self._load_csv("a_stock_balance_sheet_sample.csv")

    def load_a_stock_profit_sheet(self) -> pd.DataFrame:
        """加载A股利润表样本数据"""
        return self._load_csv("a_stock_profit_sheet_sample.csv")

    def load_a_stock_cash_flow_sheet(self) -> pd.DataFrame:
        """加载A股现金流量表样本数据"""
        return self._load_csv("a_stock_cash_flow_sheet_sample.csv")

    def load_hk_stock_indicators(self) -> pd.DataFrame:
        """加载港股财务指标样本数据"""
        return self._load_csv("hk_stock_indicators_sample.csv")

    def load_hk_stock_statements(self) -> pd.DataFrame:
        """加载港股财务三表样本数据（窄表格式）"""
        # 使用最新的00700数据
        return self._load_csv("hk_00700_balance_sheet_20251218.csv")

    def load_us_stock_indicators(self) -> pd.DataFrame:
        """加载美股财务指标样本数据"""
        return self._load_csv("us_stock_indicators_sample.csv")

    def load_us_stock_statements(self) -> pd.DataFrame:
        """加载美股财务三表样本数据（窄表格式）"""
        # 使用最新的AAPL数据
        return self._load_csv("us_AAPL_balance_sheet_20251218.csv")

    # 新增：港股财务三表分别加载方法
    def load_hk_balance_sheet(self, symbol: str = "00700") -> pd.DataFrame:
        """加载港股资产负债表样本数据"""
        latest_date = self._get_latest_date_for_symbol("hk", symbol, "balance_sheet")
        return self._load_csv(f"hk_{symbol}_balance_sheet_{latest_date}.csv")

    def load_hk_income_statement(self, symbol: str = "00700") -> pd.DataFrame:
        """加载港股利润表样本数据"""
        latest_date = self._get_latest_date_for_symbol("hk", symbol, "income_statement")
        return self._load_csv(f"hk_{symbol}_income_statement_{latest_date}.csv")

    def load_hk_cash_flow(self, symbol: str = "00700") -> pd.DataFrame:
        """加载港股现金流量表样本数据"""
        latest_date = self._get_latest_date_for_symbol("hk", symbol, "cash_flow")
        return self._load_csv(f"hk_{symbol}_cash_flow_{latest_date}.csv")

    # 新增：美股财务三表分别加载方法
    def load_us_balance_sheet(self, symbol: str = "AAPL") -> pd.DataFrame:
        """加载美股资产负债表样本数据"""
        latest_date = self._get_latest_date_for_symbol("us", symbol, "balance_sheet")
        return self._load_csv(f"us_{symbol}_balance_sheet_{latest_date}.csv")

    def load_us_income_statement(self, symbol: str = "AAPL") -> pd.DataFrame:
        """加载美股利润表样本数据"""
        latest_date = self._get_latest_date_for_symbol("us", symbol, "income_statement")
        return self._load_csv(f"us_{symbol}_income_statement_{latest_date}.csv")

    def load_us_cash_flow(self, symbol: str = "AAPL") -> pd.DataFrame:
        """加载美股现金流量表样本数据"""
        latest_date = self._get_latest_date_for_symbol("us", symbol, "cash_flow")
        return self._load_csv(f"us_{symbol}_cash_flow_{latest_date}.csv")

    def _get_latest_date_for_symbol(self, market: str, symbol: str, statement_type: str) -> str:
        """获取指定股票和报表类型的最新日期文件"""
        import glob

        pattern = f"{market}_{symbol}_{statement_type}_*.csv"
        files = glob.glob(f"{self.sample_data_dir}/{pattern}")

        if not files:
            raise FileNotFoundError(f"未找到匹配的样本数据文件: {pattern}")

        # 提取日期并选择最新文件
        latest_file = max(files)
        filename = os.path.basename(latest_file)
        # 提取日期部分，例如从 hk_00700_balance_sheet_20251218.csv 中提取 20251218
        date_part = filename.split('_')[-1].replace('.csv', '')
        return date_part

    def _load_csv(self, filename: str) -> pd.DataFrame:
        """
        加载CSV文件并进行数据预处理

        Args:
            filename: CSV文件名

        Returns:
            处理后的DataFrame
        """
        if filename in self._data_cache:
            return self._data_cache[filename].copy()

        filepath = os.path.join(self.sample_data_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"样本数据文件不存在: {filepath}")

        # 读取CSV文件
        df = pd.read_csv(filepath)

        # 数据预处理
        df = self._preprocess_dataframe(df, filename)

        # 缓存数据
        self._data_cache[filename] = df.copy()

        return df.copy()

    def _preprocess_dataframe(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """
        对DataFrame进行预处理

        Args:
            df: 原始DataFrame
            filename: 文件名（用于确定预处理逻辑）

        Returns:
            预处理后的DataFrame
        """
        # 确保缓存需要的日期字段存在
        if 'date' not in df.columns:
            if 'REPORT_DATE' in df.columns:
                # 添加标准化的date字段
                df['date'] = pd.to_datetime(df['REPORT_DATE']).dt.strftime('%Y-%m-%d')
            elif 'report_date' in df.columns:
                df['date'] = pd.to_datetime(df['report_date']).dt.strftime('%Y-%m-%d')

        return df

    def get_a_stock_indicators_mock(self,
                                   symbol: str = "SH600519",
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   limit: int = None) -> pd.DataFrame:
        """
        获取A股财务指标的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_a_stock_indicators().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_a_stock_balance_sheet_mock(self,
                                      symbol: str = "SH600519",
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None,
                                      limit: int = None) -> pd.DataFrame:
        """
        获取A股资产负债表的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_a_stock_balance_sheet().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_a_stock_profit_sheet_mock(self,
                                     symbol: str = "SH600519",
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None,
                                     limit: int = None) -> pd.DataFrame:
        """
        获取A股利润表的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_a_stock_profit_sheet().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_a_stock_cash_flow_sheet_mock(self,
                                        symbol: str = "SH600519",
                                        start_date: Optional[str] = None,
                                        end_date: Optional[str] = None,
                                        limit: int = None) -> pd.DataFrame:
        """
        获取A股现金流量表的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_a_stock_cash_flow_sheet().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_hk_stock_indicators_mock(self,
                                   symbol: str = "00700",
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   limit: int = None) -> pd.DataFrame:
        """
        获取港股财务指标的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_hk_stock_indicators().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_hk_stock_statements_mock(self,
                                    symbol: str = "00700",
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    item_names: List[str] = None,
                                    limit: int = None) -> pd.DataFrame:
        """
        获取港股财务三表的mock数据（窄表格式）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            item_names: 指定财务项目名称列表
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_hk_stock_statements().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 财务项目过滤
        if item_names is not None and len(item_names) > 0:
            if 'STD_ITEM_NAME' in df.columns:
                df = df[df['STD_ITEM_NAME'].isin(item_names)]

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_us_stock_indicators_mock(self,
                                   symbol: str = "AAPL",
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   limit: int = None) -> pd.DataFrame:
        """
        获取美股财务指标的mock数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_us_stock_indicators().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def get_us_stock_statements_mock(self,
                                    symbol: str = "AAPL",
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    item_names: List[str] = None,
                                    limit: int = None) -> pd.DataFrame:
        """
        获取美股财务三表的mock数据（窄表格式）

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            item_names: 指定财务项目名称列表
            limit: 限制返回记录数

        Returns:
            Mock数据DataFrame
        """
        df = self.load_us_stock_statements().copy()

        # 替换股票代码
        if 'symbol' in df.columns:
            df['symbol'] = symbol
        elif 'SECURITY_CODE' in df.columns:
            df['SECURITY_CODE'] = symbol

        # 财务项目过滤
        if item_names is not None and len(item_names) > 0:
            if 'ITEM_NAME' in df.columns:
                df = df[df['ITEM_NAME'].isin(item_names)]

        # 日期过滤
        df = self._filter_by_date_range(df, start_date, end_date)

        # 记录数限制
        if limit is not None and len(df) > limit:
            df = df.head(limit)

        return df

    def _filter_by_date_range(self, df: pd.DataFrame, start_date: Optional[str], end_date: Optional[str]) -> pd.DataFrame:
        """
        根据日期范围过滤DataFrame

        Args:
            df: 原始DataFrame
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的DataFrame

        Raises:
            ValueError: 如果找不到日期字段
        """
        if start_date is None and end_date is None:
            return df

        # 按优先级查找日期列
        # 统一的日期字段名（按市场优先级排序）
        date_columns = [
            # 优先使用英文字段名
            'REPORT_DATE', 'STD_REPORT_DATE', 'FINANCIAL_DATE', 'NOTICE_DATE', 'START_DATE',
            'date',
            # A股特定的中文日期字段
            '报告期',
            # 其他可能的日期字段
            'report_date', '公布日期', 'DATE_TYPE_CODE', 'DATE_TYPE'
        ]

        date_col = None
        found_columns = []

        # 查找存在的日期列
        for col in date_columns:
            if col in df.columns:
                found_columns.append(col)
                # 优先使用REPORT_DATE，如果存在的话
                if col == 'REPORT_DATE':
                    date_col = col
                    break

        # 如果没有REPORT_DATE但找到了其他日期字段，使用第一个找到的
        if date_col is None and found_columns:
            date_col = found_columns[0]

        # 严格检查：如果找不到任何日期字段，抛出错误
        if date_col is None:
            available_columns = list(df.columns)
            raise ValueError(
                f"❌ 数据中未找到有效的日期字段！\n"
                f"查找的日期字段: {date_columns}\n"
                f"可用字段: {available_columns}\n"
                f"请在数据中包含以下任一字段: {date_columns}"
            )

        # 转换日期列为datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        # 应用日期过滤
        if start_date is not None:
            start_dt = pd.to_datetime(start_date)
            df = df[df[date_col] >= start_dt]

        if end_date is not None:
            end_dt = pd.to_datetime(end_date)
            df = df[df[date_col] <= end_dt]

        return df

    def get_sample_data_info(self) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        获取所有样本数据的信息摘要

        Returns:
            样本数据信息字典
        """
        info = {}

        files = {
            'a_stock_indicators': self.load_a_stock_indicators(),
            'a_stock_balance_sheet': self.load_a_stock_balance_sheet(),
            'a_stock_profit_sheet': self.load_a_stock_profit_sheet(),
            'a_stock_cash_flow_sheet': self.load_a_stock_cash_flow_sheet(),
            'hk_stock_indicators': self.load_hk_stock_indicators(),
            'hk_stock_statements': self.load_hk_stock_statements(),
            'us_stock_indicators': self.load_us_stock_indicators(),
            'us_stock_statements': self.load_us_stock_statements(),
        }

        for name, df in files.items():
            info[name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'has_date': 'date' in df.columns,
            }

        return info


# 测试缓存fixtures
@pytest.fixture
def temp_cache_dir():
    """创建临时缓存目录的fixture"""
    temp_dir = tempfile.mkdtemp(prefix="test_cache_")
    yield temp_dir
    # 测试结束后清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True, scope="function")
def clear_project_cache():
    """
    自动清理项目缓存的fixture（每个测试前后执行）

    确保测试之间不会受到缓存影响：
    1. 创建并设置环境变量指向临时缓存目录
    2. 备份并隐藏原有项目缓存（如果存在）
    3. 测试结束后清理所有缓存
    4. 恢复原有缓存（如果存在）
    """
    # 创建临时缓存目录
    temp_dir = tempfile.mkdtemp(prefix="test_cache_")

    # 测试开始前：设置环境变量使用临时缓存目录
    original_cache_dir = os.environ.get('AKSHARE_CACHE_DIR')
    os.environ['AKSHARE_CACHE_DIR'] = os.path.join(temp_dir, "diskcache")

    # 备份并隐藏原有的项目缓存
    project_cache = ".cache"
    backup_cache = None

    if os.path.exists(project_cache):
        # 如果存在项目缓存，临时备份
        import time
        backup_cache = f"{project_cache}_backup_{int(time.time())}"
        shutil.move(project_cache, backup_cache)

    yield

    # 测试结束后：恢复环境变量
    if original_cache_dir is not None:
        os.environ['AKSHARE_CACHE_DIR'] = original_cache_dir
    else:
        os.environ.pop('AKSHARE_CACHE_DIR', None)

    # 清理临时缓存目录
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 删除可能创建的项目缓存
    if os.path.exists(project_cache):
        shutil.rmtree(project_cache, ignore_errors=True)

    # 恢复原有的缓存（如果存在）
    if backup_cache and os.path.exists(backup_cache):
        shutil.move(backup_cache, project_cache)


@pytest.fixture
def test_cache(temp_cache_dir):
    """创建测试专用的diskcache实例"""
    cache_path = os.path.join(temp_cache_dir, "test_cache")
    cache = diskcache.Cache(cache_path)
    yield cache
    # 清理缓存
    cache.clear()


@pytest.fixture(scope="function")
def test_container(test_cache):
    """创建测试专用的容器实例，使用临时缓存"""
    from akshare_value_investment.container import ProductionContainer
    from dependency_injector import providers
    from akshare_value_investment.datasource.queryers.hk_stock_queryers import (
        HKStockIndicatorQueryer,
        HKStockBalanceSheetQueryer,
        HKStockIncomeStatementQueryer,
        HKStockCashFlowQueryer
    )
    from akshare_value_investment.datasource.queryers.us_stock_queryers import (
        USStockIndicatorQueryer,
        USStockBalanceSheetQueryer,
        USStockIncomeStatementQueryer,
        USStockCashFlowQueryer
    )
    from akshare_value_investment.datasource.queryers.a_stock_queryers import (
        AStockIndicatorQueryer,
        AStockBalanceSheetQueryer,
        AStockIncomeStatementQueryer,
        AStockCashFlowQueryer
    )

    # 创建测试专用的容器类
    class TestContainer(ProductionContainer):
        # 覆盖diskcache配置，使用测试缓存
        diskcache = providers.Singleton(
            lambda: test_cache
        )

        # 覆盖A股查询器配置，使用测试缓存
        a_stock_indicators = providers.Factory(
            AStockIndicatorQueryer,
            cache=test_cache
        )
        a_stock_balance_sheet = providers.Factory(
            AStockBalanceSheetQueryer,
            cache=test_cache
        )
        a_stock_income_statement = providers.Factory(
            AStockIncomeStatementQueryer,
            cache=test_cache
        )
        a_stock_cash_flow = providers.Factory(
            AStockCashFlowQueryer,
            cache=test_cache
        )

        # 覆盖港股查询器配置，使用测试缓存
        hk_stock_indicators = providers.Factory(
            HKStockIndicatorQueryer,
            cache=test_cache
        )
        hk_stock_balance_sheet = providers.Factory(
            HKStockBalanceSheetQueryer,
            cache=test_cache
        )
        hk_stock_income_statement = providers.Factory(
            HKStockIncomeStatementQueryer,
            cache=test_cache
        )
        hk_stock_cash_flow = providers.Factory(
            HKStockCashFlowQueryer,
            cache=test_cache
        )

        # 覆盖美股查询器配置，使用测试缓存
        us_stock_indicators = providers.Factory(
            USStockIndicatorQueryer,
            cache=test_cache
        )
        us_stock_balance_sheet = providers.Factory(
            USStockBalanceSheetQueryer,
            cache=test_cache
        )
        us_stock_income_statement = providers.Factory(
            USStockIncomeStatementQueryer,
            cache=test_cache
        )
        us_stock_cash_flow = providers.Factory(
            USStockCashFlowQueryer,
            cache=test_cache
        )

    container = TestContainer()
    yield container


@pytest.fixture(scope="function")
def queryer_with_test_cache(test_cache):
    """
    提供带有测试缓存的查询器实例创建函数

    用于测试中直接创建查询器实例时使用临时缓存

    Returns:
        function: 接受查询器类，返回带测试缓存的实例
    """
    def _create_queryer(queryer_class):
        """创建带测试缓存的查询器实例"""
        return queryer_class(cache=test_cache)

    return _create_queryer


# pytest fixtures
@pytest.fixture(scope="session")
def mock_loader():
    """Session级别的MockDataLoader fixture"""
    return MockDataLoader()


@pytest.fixture(scope="session")
def sample_data_info(mock_loader):
    """获取样本数据信息的fixture"""
    return mock_loader.get_sample_data_info()


# 常用测试数据的fixtures
@pytest.fixture
def a_stock_indicators_data(mock_loader):
    """A股财务指标测试数据"""
    return mock_loader.get_a_stock_indicators_mock(limit=1)


@pytest.fixture
def a_stock_balance_sheet_data(mock_loader):
    """A股资产负债表测试数据"""
    return mock_loader.get_a_stock_balance_sheet_mock(limit=1)


@pytest.fixture
def a_stock_profit_sheet_data(mock_loader):
    """A股利润表测试数据"""
    return mock_loader.get_a_stock_profit_sheet_mock(limit=1)


@pytest.fixture
def a_stock_cash_flow_sheet_data(mock_loader):
    """A股现金流量表测试数据"""
    return mock_loader.get_a_stock_cash_flow_sheet_mock(limit=1)


@pytest.fixture
def hk_stock_indicators_data(mock_loader):
    """港股财务指标测试数据"""
    return mock_loader.get_hk_stock_indicators_mock(limit=1)


@pytest.fixture
def hk_stock_statements_data(mock_loader):
    """港股财务三表测试数据"""
    return mock_loader.get_hk_stock_statements_mock(limit=1)


@pytest.fixture
def us_stock_indicators_data(mock_loader):
    """美股财务指标测试数据"""
    return mock_loader.get_us_stock_indicators_mock(limit=1)


@pytest.fixture
def us_stock_statements_data(mock_loader):
    """美股财务三表测试数据"""
    return mock_loader.get_us_stock_statements_mock(limit=1)


# pytest配置
def pytest_configure(config):
    """pytest配置"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "production: marks tests that call real APIs"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集，自动为生产环境测试添加标记"""
    for item in items:
        # 为包含production字段的测试自动添加标记
        if "production" in item.nodeid:
            item.add_marker(pytest.mark.production)
            item.add_marker(pytest.mark.slow)