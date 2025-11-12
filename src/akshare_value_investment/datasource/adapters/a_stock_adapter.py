"""
A股市场适配器

专门处理A股市场的财务数据获取和处理。
继承自BaseMarketAdapter，实现A股特定的数据转换逻辑。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import akshare as ak

from .base_adapter import BaseMarketAdapter
from ...core.models import FinancialIndicator, PeriodType, MarketType


class AStockAdapter(BaseMarketAdapter):
    """A股市场适配器"""

    def __init__(self):
        """初始化A股适配器"""
        super().__init__(market=MarketType.A_STOCK)

    def get_financial_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[FinancialIndicator]:
        """
        获取A股财务数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            raw_data_list = self._get_a_stock_financial_data(symbol)
            indicators = self._convert_to_financial_indicators(symbol, raw_data_list)

            # 应用时间范围过滤
            if start_date or end_date:
                indicators = self._filter_by_date_range(indicators, start_date, end_date)

            return indicators
        except Exception as e:
            raise RuntimeError(f"获取A股 {symbol} 财务数据失败: {str(e)}")

    def _convert_to_financial_indicators(self, symbol: str, raw_data_list: List[Dict[str, Any]]) -> List[FinancialIndicator]:
        """
        将原始数据转换为财务指标 - 重新设计以支持多年份数据

        处理 akshare stock_financial_abstract 返回的宽表数据：
        - 每行是一个财务指标
        - 每列是一个报告期（日期）
        - 需要转换为按报告期组织的财务指标对象

        Args:
            symbol: 股票代码
            raw_data_list: 原始数据列表

        Returns:
            财务指标列表，每个代表一个报告期的所有财务数据
        """
        if not raw_data_list:
            return []

        # 收集所有日期列（排除非日期列）
        date_columns = []
        for key in raw_data_list[0].keys():
            if key not in ['选项', '指标'] and len(key) == 8 and key.isdigit():
                date_columns.append(key)

        # 按日期排序，最新的在前
        date_columns.sort(reverse=True)

        indicators = []

        for date_col in date_columns:
            try:
                # 解析报告日期
                report_date = datetime.strptime(date_col, "%Y%m%d")

                # 解析报告期类型（根据日期判断）
                period_type = self._determine_period_type(date_col)

                # 收集该期的所有财务指标数据
                period_data = {}
                raw_data_processed = {}

                for raw_data in raw_data_list:
                    indicator_name = raw_data.get('指标', '')
                    indicator_value = raw_data.get(date_col)

                    if indicator_name and indicator_value is not None:
                        period_data[indicator_name] = indicator_value
                        raw_data_processed[indicator_name] = indicator_value

                # 添加元数据
                raw_data_processed.update({
                    'symbol': symbol,
                    'market': self.market,
                    'report_date': date_col,
                    'period_type': period_type.value if period_type else 'annual'
                })

                # 创建财务指标对象
                indicator = self._create_financial_indicator(
                    symbol=symbol,
                    raw_data=raw_data_processed,
                    report_date=report_date.strftime("%Y-%m-%d"),
                    period_type=period_type,
                    company_name=self._get_company_name(symbol),
                    currency="CNY"
                )

                indicators.append(indicator)

            except Exception as e:
                # 跳过无法解析的日期记录
                continue

        return indicators

    def _get_a_stock_financial_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取A股原始财务数据

        Args:
            symbol: 股票代码

        Returns:
            原始数据列表
        """
        try:
            # 使用 akshare 获取A股财务数据 - 使用 stock_financial_abstract
            data = ak.stock_financial_abstract(symbol=symbol)

            # 处理不同的返回类型
            if hasattr(data, 'empty') and data.empty:
                return []
            elif hasattr(data, 'to_dict'):
                # DataFrame 类型 - 转置数据以适应我们的格式
                records = []
                for _, row in data.iterrows():
                    # 将每行转换为我们的数据格式
                    record = {
                        '指标': row.get('指标', ''),
                        '选项': row.get('选项', ''),
                    }
                    # 添加所有日期列
                    for col in data.columns:
                        if col not in ['选项', '指标']:
                            record[col] = row.get(col)
                    records.append(record)
                return records
            elif isinstance(data, list):
                # 已经是列表类型
                return data
            else:
                print(f"A股数据返回类型未知: {type(data)}")
                return []

        except Exception as e:
            print(f"获取A股数据异常: {e}")
            return []

    def _determine_period_type(self, date_str: str) -> PeriodType:
        """
        根据日期字符串确定报告期类型

        Args:
            date_str: 日期字符串 (YYYYMMDD格式)

        Returns:
            报告期类型
        """
        if len(date_str) != 8 or not date_str.isdigit():
            return PeriodType.QUARTERLY

        # 解析月日部分
        month_day = date_str[4:]  # MMDD

        # 1231是年报，其他都归类为季报（简化设计）
        if month_day == "1231":
            return PeriodType.ANNUAL
        else:
            return PeriodType.QUARTERLY

    def _get_company_name(self, symbol: str) -> str:
        """
        获取公司名称 - 简化版本，由大语言模型处理

        Args:
            symbol: 股票代码

        Returns:
            股票代码（由大语言模型进行公司名称识别）
        """
        # 简化版本：直接返回股票代码
        # 公司名称的识别和展示交给上层应用或大语言模型处理
        return f"股票{symbol}"