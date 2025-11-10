"""
市场适配器实现 - 简化版本

实现A股、港股、美股三个市场的财务数据获取适配器。
简化版本：直接返回原始数据，不进行字段映射。
"""

from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

import akshare as ak

from .interfaces import IMarketAdapter
from .models import MarketType, FinancialIndicator, PeriodType


class AStockAdapter(IMarketAdapter):
    """A股市场适配器 - 简化版本"""

    def __init__(self):
        """
        初始化A股适配器 - 简化版本，不需要字段映射器
        """
        self.market = MarketType.A_STOCK

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """
        获取A股财务数据

        Args:
            symbol: 股票代码

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            raw_data_list = self._get_a_stock_financial_data(symbol)
            return self._convert_to_financial_indicators(symbol, raw_data_list)
        except Exception as e:
            raise RuntimeError(f"获取A股 {symbol} 财务数据失败: {str(e)}")

    def _convert_to_financial_indicators(self, symbol: str, raw_data_list: List[Dict[str, Any]]) -> List[FinancialIndicator]:
        """
        将原始数据转换为财务指标 - 简化版本，保留原始数据

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

                # 解析报告期类型
                period_type = self._parse_period_type(raw_data.get("报告期", ""))

                # 创建财务指标对象 - 简化版本，indicators为空，raw_data包含所有原始字段
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=self.market,
                    company_name=self._get_company_name(symbol),
                    report_date=report_date,
                    period_type=period_type,
                    currency="CNY",
                    indicators={},  # 简化版本不进行字段映射
                    raw_data=raw_data  # 保留所有原始数据
                )

                indicators.append(indicator)

            except Exception as e:
                # 跳过无法解析的记录，继续处理其他记录
                print(f"警告: 跳过无效记录 {symbol}: {str(e)}")
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
            # 使用 akshare 获取A股财务数据
            data = ak.stock_financial_analysis_indicator(symbol=symbol)

            # 处理不同的返回类型
            if hasattr(data, 'empty') and data.empty:
                return []
            elif hasattr(data, 'to_dict'):
                # DataFrame 类型
                return data.to_dict('records')
            elif isinstance(data, list):
                # 已经是列表类型
                return data
            else:
                print(f"A股数据返回类型未知: {type(data)}")
                return []

        except Exception as e:
            print(f"获取A股数据异常: {e}")
            return []

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> datetime:
        """
        解析报告日期

        Args:
            raw_data: 原始数据

        Returns:
            报告日期
        """
        # 尝试多种可能的日期字段
        date_fields = ["日期", "报告日期", "report_date"]

        for field in date_fields:
            if field in raw_data and raw_data[field] is not None:
                date_str = str(raw_data[field])
                try:
                    # 尝试多种日期格式
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue

        # 默认返回当前日期
        return datetime.now()

    def _parse_period_type(self, period_str: str) -> PeriodType:
        """
        解析报告期类型

        Args:
            period_str: 报告期字符串

        Returns:
            报告期类型
        """
        period_str = str(period_str).lower()
        if "年报" in period_str or "年度" in period_str or "12-31" in period_str:
            return PeriodType.ANNUAL
        else:
            return PeriodType.QUARTERLY

    def _get_company_name(self, symbol: str) -> str:
        """
        获取公司名称

        Args:
            symbol: 股票代码

        Returns:
            公司名称
        """
        # 简化版本，返回股票代码作为公司名称
        # 实际实现中可以调用 akshare 的股票基本信息接口
        company_names = {
            "600036": "招商银行",
            "600519": "贵州茅台",
            "000001": "平安银行",
            "000002": "万科A",
        }
        return company_names.get(symbol, f"股票{symbol}")


class HKStockAdapter(IMarketAdapter):
    """港股市场适配器 - 简化版本"""

    def __init__(self):
        """
        初始化港股适配器 - 简化版本，不需要字段映射器
        """
        self.market = MarketType.HK_STOCK

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """
        获取港股财务数据

        Args:
            symbol: 股票代码

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            raw_data_list = self._get_hk_stock_financial_data(symbol)
            return self._convert_to_financial_indicators(symbol, raw_data_list)
        except Exception as e:
            raise RuntimeError(f"获取港股 {symbol} 财务数据失败: {str(e)}")

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

                # 解析报告期类型
                period_type = self._parse_period_type(raw_data.get("报告期", ""))

                # 创建财务指标对象 - 简化版本
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=self.market,
                    company_name=self._get_company_name(symbol),
                    report_date=report_date,
                    period_type=period_type,
                    currency="HKD",
                    indicators={},  # 简化版本不进行字段映射
                    raw_data=raw_data  # 保留所有原始数据
                )

                indicators.append(indicator)

            except Exception as e:
                print(f"警告: 跳过无效记录 {symbol}: {str(e)}")
                continue

        return indicators

    def _get_hk_stock_financial_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取港股原始财务数据

        Args:
            symbol: 股票代码

        Returns:
            原始数据列表
        """
        try:
            # 使用 akshare 获取港股财务数据
            data = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)

            # 处理不同的返回类型
            if hasattr(data, 'empty') and data.empty:
                return []
            elif hasattr(data, 'to_dict'):
                return data.to_dict('records')
            elif isinstance(data, list):
                return data
            else:
                print(f"港股数据返回类型未知: {type(data)}")
                return []

        except Exception as e:
            print(f"获取港股数据异常: {e}")
            return []

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> datetime:
        """解析报告日期"""
        date_fields = ["日期", "报告日期", "report_date", "DATE"]

        for field in date_fields:
            if field in raw_data and raw_data[field] is not None:
                date_str = str(raw_data[field])
                try:
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue

        return datetime.now()

    def _parse_period_type(self, period_str: str) -> PeriodType:
        """解析报告期类型"""
        period_str = str(period_str).lower()
        if "年报" in period_str or "年度" in period_str or "12-31" in period_str:
            return PeriodType.ANNUAL
        else:
            return PeriodType.QUARTERLY

    def _get_company_name(self, symbol: str) -> str:
        """获取公司名称"""
        company_names = {
            "00700": "腾讯控股",
            "00941": "中国移动",
            "01299": "友邦保险",
            "03690": "美团-W",
        }
        return company_names.get(symbol, f"港股{symbol}")


class USStockAdapter(IMarketAdapter):
    """美股市场适配器 - 简化版本"""

    def __init__(self):
        """
        初始化美股适配器 - 简化版本，不需要字段映射器
        """
        self.market = MarketType.US_STOCK

    def get_financial_data(self, symbol: str) -> List[FinancialIndicator]:
        """
        获取美股财务数据

        Args:
            symbol: 股票代码

        Returns:
            财务指标列表（包含原始数据）
        """
        try:
            raw_data_list = self._get_us_stock_financial_data(symbol)
            return self._convert_to_financial_indicators(symbol, raw_data_list)
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

                # 解析报告期类型
                period_type = self._parse_period_type(raw_data.get("报告期", ""))

                # 创建财务指标对象 - 简化版本
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=self.market,
                    company_name=self._get_company_name(symbol),
                    report_date=report_date,
                    period_type=period_type,
                    currency="USD",
                    indicators={},  # 简化版本不进行字段映射
                    raw_data=raw_data  # 保留所有原始数据
                )

                indicators.append(indicator)

            except Exception as e:
                print(f"警告: 跳过无效记录 {symbol}: {str(e)}")
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

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> datetime:
        """解析报告日期"""
        date_fields = ["日期", "报告日期", "report_date", "DATE", "endDate"]

        for field in date_fields:
            if field in raw_data and raw_data[field] is not None:
                date_str = str(raw_data[field])
                try:
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue

        return datetime.now()

    def _parse_period_type(self, period_str: str) -> PeriodType:
        """解析报告期类型"""
        period_str = str(period_str).lower()
        if "年报" in period_str or "年度" in period_str or "12-31" in period_str or "FY" in period_str.upper():
            return PeriodType.ANNUAL
        else:
            return PeriodType.QUARTERLY

    def _get_company_name(self, symbol: str) -> str:
        """获取公司名称"""
        company_names = {
            "AAPL": "苹果",
            "TSLA": "特斯拉",
            "MSFT": "微软",
            "GOOGL": "谷歌",
            "AMZN": "亚马逊",
        }
        return company_names.get(symbol, f"美股{symbol}")


class AdapterManager:
    """适配器管理器 - 简化版本"""

    def __init__(self):
        """
        初始化适配器管理器 - 简化版本，不需要字段映射器
        """
        # 创建适配器实例
        self.adapters = {
            MarketType.A_STOCK: AStockAdapter(),
            MarketType.HK_STOCK: HKStockAdapter(),
            MarketType.US_STOCK: USStockAdapter(),
        }

    def get_adapter(self, market: MarketType) -> IMarketAdapter:
        """
        获取指定市场的适配器

        Args:
            market: 市场类型

        Returns:
            市场适配器

        Raises:
            ValueError: 当市场类型不支持时
        """
        if market not in self.adapters:
            raise ValueError(f"不支持的市场类型: {market}")

        return self.adapters[market]

    def get_supported_markets(self) -> List[MarketType]:
        """
        获取支持的市场类型列表

        Returns:
            支持的市场类型列表
        """
        return list(self.adapters.keys())