"""
适配器策略具体实现

实现各种数据获取、分析和转换策略。
"""

from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
import akshare as ak

from .adapter_strategies import (
    IDataFetcher, IDateColumnAnalyzer, IPeriodAnalyzer,
    IDataConverter, ICompanyInfoProvider, IFinancialDataProcessor
)
from .models import MarketType, FinancialIndicator, PeriodType


class AStockDataFetcher(IDataFetcher):
    """A股数据获取策略"""

    def fetch_financial_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取A股财务数据

        Args:
            symbol: 股票代码

        Returns:
            原始数据列表
        """
        try:
            # 获取财务指标数据 - 宽表格式
            data = ak.stock_financial_abstract(symbol=symbol)
            return data.to_dict('records')
        except Exception as e:
            raise RuntimeError(f"获取A股 {symbol} 财务数据失败: {str(e)}")


class DateColumnAnalyzer(IDateColumnAnalyzer):
    """日期列分析策略"""

    def extract_date_columns(self, raw_data: List[Dict[str, Any]]) -> List[str]:
        """
        从原始数据中提取日期列

        Args:
            raw_data: 原始数据列表

        Returns:
            排序后的日期列列表（最新在前）
        """
        if not raw_data:
            return []

        date_columns = []
        for key in raw_data[0].keys():
            # 识别日期列：8位数字格式 (YYYYMMDD)
            if key not in ['选项', '指标'] and len(key) == 8 and key.isdigit():
                date_columns.append(key)

        # 按日期排序，最新的在前
        date_columns.sort(reverse=True)
        return date_columns


class PeriodAnalyzer(IPeriodAnalyzer):
    """期间类型分析策略"""

    def determine_period_type(self, date_str: str) -> PeriodType:
        """
        根据日期字符串确定报告期类型

        Args:
            date_str: 日期字符串 (YYYYMMDD格式)

        Returns:
            报告期类型
        """
        try:
            date = datetime.strptime(date_str, "%Y%m%d")

            # 根据月日判断报告期类型
            month_day = date.strftime("%m%d")

            if month_day == "1231":
                return PeriodType.ANNUAL  # 年报
            elif month_day in ["0630", "0930", "0331"]:
                return PeriodType.QUARTERLY  # 季报
            else:
                # 默认为年报
                return PeriodType.ANNUAL

        except ValueError:
            # 如果日期格式不正确，默认为年报
            return PeriodType.ANNUAL


class AStockDataConverter(IDataConverter):
    """A股数据转换策略"""

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
        try:
            # 解析报告日期
            report_date = datetime.strptime(date_str, "%Y%m%d")
            period_type = period_analyzer.determine_period_type(date_str)

            # 收集该期的所有财务指标数据
            period_indicators = {}
            raw_data_processed = {}

            for raw_data in raw_data_list:
                indicator_name = raw_data.get('指标', '')
                indicator_value = raw_data.get(date_str)

                if indicator_name and indicator_value is not None:
                    # 转换为Decimal确保精确计算
                    try:
                        decimal_value = Decimal(str(indicator_value))
                        period_indicators[indicator_name] = decimal_value
                        raw_data_processed[indicator_name] = indicator_value
                    except (ValueError, TypeError):
                        # 无法转换的值跳过
                        continue

            # 添加元数据到原始数据
            raw_data_processed.update({
                'symbol': symbol,
                'market': market.value,
                'report_date': date_str,
                'period_type': period_type.value if period_type else 'annual'
            })

            return FinancialIndicator(
                symbol=symbol,
                market=market,
                company_name="",  # 将在后续步骤中设置
                report_date=report_date,
                period_type=period_type,
                currency="CNY",  # A股默认人民币
                indicators=period_indicators,
                raw_data=raw_data_processed
            )

        except Exception as e:
            raise RuntimeError(f"转换财务数据失败: {str(e)}")


class AStockCompanyInfoProvider(ICompanyInfoProvider):
    """A股公司信息提供者"""

    def get_company_name(self, symbol: str) -> str:
        """
        获取A股公司名称

        Args:
            symbol: 股票代码

        Returns:
            公司名称
        """
        try:
            # 使用akshare获取公司名称
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            if not stock_info.empty and 'item' in stock_info.columns and 'value' in stock_info.columns:
                name_row = stock_info[stock_info['item'] == '公司简称']
                if not name_row.empty:
                    return name_row.iloc[0]['value']

            # 如果获取失败，返回股票代码作为后备
            return f"股票{symbol}"

        except Exception:
            return f"股票{symbol}"


class AStockFinancialDataProcessor(IFinancialDataProcessor):
    """A股财务数据处理器 - 协调各个策略组件"""

    def __init__(self,
                 data_fetcher: IDataFetcher = None,
                 date_analyzer: IDateColumnAnalyzer = None,
                 period_analyzer: IPeriodAnalyzer = None,
                 data_converter: IDataConverter = None,
                 company_info_provider: ICompanyInfoProvider = None):
        """
        初始化财务数据处理器

        Args:
            data_fetcher: 数据获取器
            date_analyzer: 日期列分析器
            period_analyzer: 期间分析器
            data_converter: 数据转换器
            company_info_provider: 公司信息提供者
        """
        self.data_fetcher = data_fetcher or AStockDataFetcher()
        self.date_analyzer = date_analyzer or DateColumnAnalyzer()
        self.period_analyzer = period_analyzer or PeriodAnalyzer()
        self.data_converter = data_converter or AStockDataConverter()
        self.company_info_provider = company_info_provider or AStockCompanyInfoProvider()

    def process_financial_data(self,
                              symbol: str,
                              raw_data_list: List[Dict[str, Any]],
                              data_fetcher: IDataFetcher = None,
                              date_analyzer: IDateColumnAnalyzer = None,
                              period_analyzer: IPeriodAnalyzer = None,
                              data_converter: IDataConverter = None,
                              company_info_provider: ICompanyInfoProvider = None) -> List[FinancialIndicator]:
        """
        处理完整的财务数据流程

        Args:
            symbol: 股票代码
            raw_data_list: 原始数据列表
            data_fetcher: 数据获取器（可选，使用实例默认值）
            date_analyzer: 日期列分析器（可选，使用实例默认值）
            period_analyzer: 期间分析器（可选，使用实例默认值）
            data_converter: 数据转换器（可选，使用实例默认值）
            company_info_provider: 公司信息提供者（可选，使用实例默认值）

        Returns:
            处理后的财务指标列表
        """
        # 使用提供的策略或实例默认值
        fetcher = data_fetcher or self.data_fetcher
        analyzer = date_analyzer or self.date_analyzer
        analyzer_period = period_analyzer or self.period_analyzer
        converter = data_converter or self.data_converter
        info_provider = company_info_provider or self.company_info_provider

        # 如果没有提供原始数据，使用数据获取器获取
        if not raw_data_list:
            raw_data_list = fetcher.fetch_financial_data(symbol)

        # 提取日期列
        date_columns = analyzer.extract_date_columns(raw_data_list)

        # 获取公司名称（只获取一次）
        company_name = info_provider.get_company_name(symbol)

        # 转换每个报告期的数据
        indicators = []
        for date_col in date_columns:
            try:
                indicator = converter.convert_period_data(
                    symbol, MarketType.A_STOCK, date_col, raw_data_list, analyzer_period
                )
                # 设置公司名称
                indicator.company_name = company_name
                indicators.append(indicator)
            except Exception as e:
                # 单个期间转换失败不中断整体流程
                print(f"警告: 转换期间 {date_col} 失败: {str(e)}")
                continue

        return indicators