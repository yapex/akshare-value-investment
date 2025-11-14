"""
pytest fixtures and configuration

提供测试共享的 fixtures 和配置，包括 MockDataLoader 和其他测试工具。
"""

import os
import sys
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime
import pytest

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
        return self._load_csv("hk_stock_statements_sample.csv")

    def load_us_stock_indicators(self) -> pd.DataFrame:
        """加载美股财务指标样本数据"""
        return self._load_csv("us_stock_indicators_sample.csv")

    def load_us_stock_statements(self) -> pd.DataFrame:
        """加载美股财务三表样本数据（窄表格式）"""
        return self._load_csv("us_stock_statements_sample.csv")

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
        """
        if start_date is None and end_date is None:
            return df

        # 查找日期列
        date_columns = ['date', 'REPORT_DATE', 'report_date', '公布日期', 'STD_REPORT_DATE']
        date_col = None

        for col in date_columns:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            return df

        # 转换日期列为datetime类型
        if date_col != 'date' or not pd.api.types.is_datetime64_any_dtype(df[date_col]):
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