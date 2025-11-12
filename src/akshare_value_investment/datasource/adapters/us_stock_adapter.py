"""
美股市场适配器

专门处理美股市场的财务数据获取和处理。
继承自BaseMarketAdapter，实现美股特定的数据转换逻辑。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import akshare as ak

from .base_adapter import BaseMarketAdapter
from ...core.models import FinancialIndicator, PeriodType, MarketType


class USStockAdapter(BaseMarketAdapter):
    """美股市场适配器"""

    def __init__(self):
        """初始化美股适配器"""
        super().__init__(market=MarketType.US_STOCK)

    def get_financial_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[FinancialIndicator]:
        """
        获取美股财务数据

        Args:
            symbol: 股票代码

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            raw_data_list = self._get_us_stock_financial_data(symbol)
            indicators = self._convert_to_financial_indicators(symbol, raw_data_list)

            # 应用时间范围过滤
            if start_date or end_date:
                indicators = self._filter_by_date_range(indicators, start_date, end_date)

            return indicators
        except Exception as e:
            raise RuntimeError(f"获取美股 {symbol} 财务数据失败: {str(e)}")

    def _convert_to_financial_indicators(self, symbol: str, raw_data_list: List[Dict[str, Any]]) -> List[FinancialIndicator]:
        """
        将原始数据转换为财务指标 - 简化版本

        Args:
            symbol: 股票代码
            raw_data_list: 原始数据列表

        Returns:
            财务指标列表
        """
        indicators = []

        for raw_data in raw_data_list:
            try:
                # 解析报告日期
                report_date = self._parse_report_date(raw_data)

                # 解析报告期类型 - 美股通常是季度数据
                period_type = self._parse_period_type(raw_data.get("REPORT_TYPE", ""))

                # 创建财务指标对象 - 简化版本
                indicator = self._create_financial_indicator(
                    symbol=symbol,
                    raw_data=raw_data,
                    report_date=report_date,
                    period_type=period_type,
                    company_name=self._get_company_name(symbol),
                    currency="USD"
                )

                indicators.append(indicator)

            except Exception as e:
                continue

        return indicators

    def _get_us_stock_financial_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取美股原始财务数据

        Args:
            symbol: 股票代码

        Returns:
            原始数据列表
        """
        try:
            # 使用 akshare 获取美股财务数据
            data = ak.stock_financial_us_analysis_indicator_em(symbol=symbol)

            # 处理不同的返回类型
            if hasattr(data, 'empty') and data.empty:
                return []
            elif hasattr(data, 'to_dict'):
                return data.to_dict('records')
            elif isinstance(data, list):
                return data
            else:
                print(f"美股数据返回类型未知: {type(data)}")
                return []

        except Exception as e:
            print(f"获取美股数据异常: {e}")
            return []

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> str:
        """解析报告日期"""
        date_fields = ["REPORT_DATE", "日期", "报告日期", "report_date", "DATE", "END_DATE"]

        for field in date_fields:
            if field in raw_data and raw_data[field] is not None:
                date_str = str(raw_data[field])
                try:
                    # 处理pandas时间戳格式
                    if hasattr(date_str, 'strftime'):
                        return date_str.strftime("%Y-%m-%d")
                    # 处理字符串格式
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            return date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except Exception:
                    continue

        return datetime.now().strftime("%Y-%m-%d")

    def _parse_period_type(self, period_str: str) -> PeriodType:
        """解析报告期类型"""
        period_str = str(period_str).lower()
        if "annual" in period_str or "年报" in period_str or "年度" in period_str or "12-31" in period_str:
            return PeriodType.ANNUAL
        elif "q1" in period_str or "q2" in period_str or "q3" in period_str or "q4" in period_str:
            return PeriodType.QUARTERLY
        else:
            return PeriodType.QUARTERLY  # 美股默认为季度

    def _get_company_name(self, symbol: str) -> str:
        """获取公司名称"""
        company_names = {
            "AAPL": "苹果",
            "MSFT": "微软",
            "GOOGL": "谷歌",
            "AMZN": "亚马逊",
            "TSLA": "特斯拉",
        }
        return company_names.get(symbol, f"美股{symbol}")