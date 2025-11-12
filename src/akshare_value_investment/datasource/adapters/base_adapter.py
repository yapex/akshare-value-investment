"""
基础市场适配器抽象类

定义所有市场适配器的通用接口和行为。
提供数据处理的公共方法，减少代码重复。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

from ...core.models import MarketType, FinancialIndicator, PeriodType


class BaseMarketAdapter(ABC):
    """基础市场适配器抽象类"""

    def __init__(self, market: MarketType):
        """
        初始化基础适配器

        Args:
            market: 市场类型
        """
        self.market = market

    @abstractmethod
    def get_financial_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[FinancialIndicator]:
        """
        获取指定股票的财务数据 - 抽象方法

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            财务指标列表
        """
        ...

    def _filter_by_date_range(self, indicators: List[FinancialIndicator], start_date: Optional[str], end_date: Optional[str]) -> List[FinancialIndicator]:
        """
        按日期范围过滤财务指标

        Args:
            indicators: 财务指标列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的财务指标列表
        """
        if not start_date and not end_date:
            return indicators

        filtered_indicators = []
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

        for indicator in indicators:
            try:
                indicator_date = datetime.strptime(indicator.report_date, "%Y-%m-%d")

                # 检查日期范围
                date_in_range = True
                if start_datetime and indicator_date < start_datetime:
                    date_in_range = False
                if end_datetime and indicator_date > end_datetime:
                    date_in_range = False

                if date_in_range:
                    filtered_indicators.append(indicator)

            except (ValueError, TypeError):
                # 如果日期解析失败，保留该指标
                filtered_indicators.append(indicator)

        return filtered_indicators

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> str:
        """
        从原始数据中解析报告日期

        Args:
            raw_data: 原始数据字典

        Returns:
            标准化的报告日期字符串 (YYYY-MM-DD)
        """
        # 常见的日期字段名
        date_fields = [
            "REPORT_DATE", "report_date", "日期", "DATE",
            "ann_date", "ANN_DATE", "公告日期"
        ]

        latest_date = None
        latest_date_str = ""

        for key, value in raw_data.items():
            # 检查是否是日期字段
            if any(date_field in key.upper() for date_field in date_fields):
                if isinstance(value, str):
                    try:
                        # 尝试解析各种日期格式
                        if " " in value:  # 处理 "2024-12-31 00:00:00" 格式
                            date_obj = datetime.strptime(value.split()[0], "%Y-%m-%d")
                        elif len(value) == 8:  # 处理 "20241231" 格式
                            date_obj = datetime.strptime(value, "%Y%m%d")
                        else:  # 处理 "2024-12-31" 格式
                            date_obj = datetime.strptime(value, "%Y-%m-%d")

                        if latest_date is None or date_obj > latest_date:
                            latest_date = date_obj
                            latest_date_str = date_obj.strftime("%Y-%m-%d")

                    except (ValueError, TypeError):
                        continue

        return latest_date_str if latest_date_str else ""

    def _parse_period_type(self, period_str: str) -> PeriodType:
        """
        解析报告期类型

        Args:
            period_str: 报告期字符串

        Returns:
            标准化的报告期类型
        """
        if not isinstance(period_str, str):
            return PeriodType.UNKNOWN

        period_str_lower = period_str.lower()

        if any(keyword in period_str for keyword in ["年报", "年度", "annual", "12-31"]):
            return PeriodType.ANNUAL
        elif any(keyword in period_str for keyword in ["中报", "半年报", "半年度", "interim", "06-30"]):
            return PeriodType.SEMI_ANNUAL
        elif any(keyword in period_str for keyword in ["一季报", "第一季度", "q1", "03-31"]):
            return PeriodType.QUARTERLY
        elif any(keyword in period_str for keyword in ["三季报", "第三季度", "q3", "09-30"]):
            return PeriodType.QUARTERLY

        return PeriodType.UNKNOWN

    def _determine_period_type(self, date_str: str) -> PeriodType:
        """
        根据日期确定报告期类型

        Args:
            date_str: 日期字符串

        Returns:
            报告期类型
        """
        try:
            if len(date_str) == 8:  # "20241231" 格式
                month_day = date_str[4:8]
            else:  # "2024-12-31" 格式
                month_day = date_str[5:10]

            if month_day == "12-31":
                return PeriodType.ANNUAL
            elif month_day == "06-30":
                return PeriodType.SEMI_ANNUAL
            elif month_day in ["03-31", "09-30"]:
                return PeriodType.QUARTERLY
            else:
                return PeriodType.UNKNOWN

        except (IndexError, ValueError):
            return PeriodType.UNKNOWN

    def _create_financial_indicator(self,
                                  symbol: str,
                                  raw_data: Dict[str, Any],
                                  report_date: str,
                                  period_type: PeriodType,
                                  company_name: Optional[str] = None,
                                  currency: Optional[str] = None) -> FinancialIndicator:
        """
        创建财务指标对象

        Args:
            symbol: 股票代码
            raw_data: 原始财务数据
            report_date: 报告日期
            period_type: 报告期类型
            company_name: 公司名称
            currency: 货币单位

        Returns:
            财务指标对象
        """
        return FinancialIndicator(
            symbol=symbol,
            market=self.market,
            company_name=company_name or "",
            report_date=report_date,
            period_type=period_type,
            currency=currency or self._get_default_currency(),
            indicators=raw_data.copy(),  # 将所有原始数据放入indicators
            raw_data=raw_data.copy()     # 保留原始数据副本
        )

    def _get_default_currency(self) -> str:
        """
        获取默认货币单位

        Returns:
            默认货币代码
        """
        currency_map = {
            MarketType.A_STOCK: "CNY",
            MarketType.HK_STOCK: "HKD",
            MarketType.US_STOCK: "USD"
        }
        return currency_map.get(self.market, "USD")