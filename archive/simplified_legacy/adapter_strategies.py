"""
适配器策略接口定义

遵循单一职责原则，将适配器功能拆分为多个独立的策略组件。
"""

from typing import List, Dict, Any
from datetime import datetime
from typing import Protocol

from .models import MarketType, FinancialIndicator, PeriodType


class IDataFetcher(Protocol):
    """数据获取策略接口"""

    def fetch_financial_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取原始财务数据

        Args:
            symbol: 股票代码

        Returns:
            原始数据列表
        """
        ...


class IDateColumnAnalyzer(Protocol):
    """日期列分析策略接口"""

    def extract_date_columns(self, raw_data: List[Dict[str, Any]]) -> List[str]:
        """
        从原始数据中提取日期列

        Args:
            raw_data: 原始数据列表

        Returns:
            排序后的日期列列表（最新在前）
        """
        ...


class IPeriodAnalyzer(Protocol):
    """期间类型分析策略接口"""

    def determine_period_type(self, date_str: str) -> PeriodType:
        """
        根据日期字符串确定报告期类型

        Args:
            date_str: 日期字符串 (YYYYMMDD格式)

        Returns:
            报告期类型
        """
        ...


class IDataConverter(Protocol):
    """数据转换策略接口"""

    def convert_period_data(self,
                           symbol: str,
                           market: MarketType,
                           date_str: str,
                           raw_data_list: List[Dict[str, Any]],
                           period_analyzer: IPeriodAnalyzer) -> FinancialIndicator:
        """
        转换单个报告期的数据

        Args:
            symbol: 股票代码
            market: 市场类型
            date_str: 日期字符串
            raw_data_list: 原始数据列表
            period_analyzer: 期间分析器

        Returns:
            转换后的财务指标对象
        """
        ...


class ICompanyInfoProvider(Protocol):
    """公司信息提供者接口"""

    def get_company_name(self, symbol: str) -> str:
        """
        获取公司名称

        Args:
            symbol: 股票代码

        Returns:
            公司名称
        """
        ...


class IFinancialDataProcessor(Protocol):
    """财务数据处理器接口"""

    def process_financial_data(self,
                              symbol: str,
                              raw_data_list: List[Dict[str, Any]],
                              data_fetcher: IDataFetcher,
                              date_analyzer: IDateColumnAnalyzer,
                              period_analyzer: IPeriodAnalyzer,
                              data_converter: IDataConverter,
                              company_info_provider: ICompanyInfoProvider) -> List[FinancialIndicator]:
        """
        处理完整的财务数据流程

        Args:
            symbol: 股票代码
            raw_data_list: 原始数据列表
            data_fetcher: 数据获取器
            date_analyzer: 日期列分析器
            period_analyzer: 期间分析器
            data_converter: 数据转换器
            company_info_provider: 公司信息提供者

        Returns:
            处理后的财务指标列表
        """
        ...