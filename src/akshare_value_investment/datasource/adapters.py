"""
市场适配器实现 - 简化版本

实现A股、港股、美股三个市场的财务数据获取适配器。
简化版本：直接返回原始数据，不进行字段映射。
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

import akshare as ak

from ..core.interfaces import IMarketAdapter, IQueryService
from ..core.models import MarketType, FinancialIndicator, PeriodType, QueryResult
from ..core.stock_identifier import StockIdentifier
from ..smart_cache import smart_cache


class AStockAdapter(IMarketAdapter):
    """A股市场适配器 - 简化版本"""

    def __init__(self):
        """
        初始化A股适配器 - 简化版本，不需要字段映射器
        """
        self.market = MarketType.A_STOCK

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
                    'market': self.market.value,
                    'report_date': date_col,
                    'period_type': period_type.value if period_type else 'annual'
                })

                # 创建财务指标对象
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=self.market,
                    company_name=self._get_company_name(symbol),
                    report_date=report_date,
                    period_type=period_type,
                    currency="CNY",
                    indicators=period_data,  # 使用解析后的指标数据
                    raw_data=raw_data_processed  # 保留完整的原始数据
                )

                indicators.append(indicator)

            except Exception as e:
                # 跳过无法解析的日期记录
                continue

        return indicators

    def _filter_by_date_range(self, indicators: List[FinancialIndicator], start_date: Optional[str], end_date: Optional[str]) -> List[FinancialIndicator]:
        """
        根据时间范围过滤财务指标

        Args:
            indicators: 财务指标列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            过滤后的财务指标列表
        """
        if not start_date and not end_date:
            return indicators

        filtered_indicators = []

        # 转换日期字符串为datetime对象
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print(f"⚠️ 开始日期格式无效: {start_date}")
                start_datetime = None

        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                # 包含结束日期，所以设置为23:59:59
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            except ValueError:
                print(f"⚠️ 结束日期格式无效: {end_date}")
                end_datetime = None

        # 过滤指标
        for indicator in indicators:
            if start_datetime and indicator.report_date < start_datetime:
                continue
            if end_datetime and indicator.report_date > end_datetime:
                continue
            filtered_indicators.append(indicator)

        return filtered_indicators

    @smart_cache("astock_financial", ttl=3600)  # 1小时缓存
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

    def _parse_report_date(self, raw_data: Dict[str, Any]) -> datetime:
        """
        解析报告日期

        Args:
            raw_data: 原始数据

        Returns:
            报告日期
        """
        # 对于stock_financial_abstract数据，日期存储在不同的列中
        # 我们需要获取最新的日期列作为报告日期

        latest_date = None
        latest_date_str = ""

        for key, value in raw_data.items():
            if key not in ['选项', '指标'] and value is not None:
                # 尝试解析日期字段 YYYYMMDD
                if isinstance(key, str) and len(key) == 8 and key.isdigit():
                    try:
                        date_obj = datetime.strptime(key, '%Y%m%d')
                        if latest_date is None or date_obj > latest_date:
                            latest_date = date_obj
                            latest_date_str = key
                    except ValueError:
                        continue

        if latest_date:
            return latest_date

        # 如果没有找到日期，使用默认日期
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

        # 1231是年报，其他是季报
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


class HKStockAdapter(IMarketAdapter):
    """港股市场适配器 - 简化版本"""

    def __init__(self):
        """
        初始化港股适配器 - 简化版本，不需要字段映射器
        """
        self.market = MarketType.HK_STOCK

    def get_financial_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[FinancialIndicator]:
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
                continue

        return indicators

    @smart_cache("hkstock_financial", ttl=3600)  # 1小时缓存
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
        date_fields = ["REPORT_DATE", "日期", "报告日期", "report_date", "DATE"]

        for field in date_fields:
            if field in raw_data and raw_data[field] is not None:
                date_str = str(raw_data[field])
                try:
                    # 处理pandas时间戳格式
                    if hasattr(date_str, 'strftime'):
                        return date_str
                    # 处理字符串格式
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"]:
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
            return self._convert_to_financial_indicators(symbol, raw_data_list)
        except Exception as e:
            raise RuntimeError(f"获取美股 {symbol} 财务数据失败: {str(e)}")

    def _convert_to_financial_indicators(self, symbol: str, raw_data_list: List[Dict[str, Any]]) -> List[FinancialIndicator]:
        """
        将美股原始数据转换为财务指标 - 更新版本以支持多年份数据

        美股数据处理：akshare返回的是长表格式，每行代表一个报告期的所有财务数据

        Args:
            symbol: 股票代码
            raw_data_list: 原始数据列表

        Returns:
            财务指标列表，每个代表一个报告期的所有财务数据
        """
        indicators = []

        for raw_data in raw_data_list:
            try:
                # 解析报告日期 - 美股使用REPORT_DATE字段
                report_date_str = raw_data.get("REPORT_DATE", "")
                if not report_date_str:
                    # 如果没有REPORT_DATE，尝试其他日期字段
                    report_date_str = raw_data.get("NOTICE_DATE", "") or raw_data.get("FINANCIAL_DATE", "")

                if report_date_str:
                    if isinstance(report_date_str, str):
                        # 尝试解析日期字符串
                        if len(report_date_str) > 10:  # 包含时间信息的日期
                            report_date = datetime.strptime(report_date_str.split()[0], "%Y-%m-%d")
                        else:
                            report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
                    else:
                        report_date = report_date_str  # 已经是datetime对象
                else:
                    # 如果没有日期信息，跳过这条记录
                    continue

                # 解析报告期类型 - 美股通常按季度报告，但苹果是自然年财年
                period_type = PeriodType.QUARTERLY  # 默认为季报

                # 收集该期的所有财务指标数据（排除元数据字段）
                period_data = {}
                raw_data_processed = {}

                # 美股数据中的元数据字段
                metadata_fields = {
                    'SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'ORG_CODE',
                    'SECURITY_INNER_CODE', 'ACCOUNTING_STANDARDS', 'NOTICE_DATE',
                    'START_DATE', 'REPORT_DATE', 'FINANCIAL_DATE', 'CURRENCY_ABBR'
                }

                for field_name, field_value in raw_data.items():
                    if field_name not in metadata_fields and field_value is not None:
                        period_data[field_name] = field_value
                        raw_data_processed[field_name] = field_value

                # 添加元数据
                raw_data_processed.update({
                    'symbol': symbol,
                    'market': self.market.value,
                    'report_date': report_date_str,
                    'period_type': period_type.value if period_type else 'quarterly'
                })

                # 创建财务指标对象
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=self.market,
                    company_name=self._get_company_name(symbol),
                    report_date=report_date,
                    period_type=period_type,
                    currency="USD",
                    indicators=period_data,  # 使用解析后的指标数据
                    raw_data=raw_data_processed  # 保留完整的原始数据
                )

                indicators.append(indicator)

            except Exception as e:
                continue

        # 按报告日期排序，最新的在前
        indicators.sort(key=lambda x: x.report_date, reverse=True)
        return indicators

    @smart_cache("usstock_financial", ttl=3600)  # 1小时缓存
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


class AdapterManager(IQueryService):
    """适配器管理器 - 简化版本，实现IQueryService接口"""

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

        # 股票识别器
        self.stock_identifier = StockIdentifier()

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

    # IQueryService接口实现
    def query(self, symbol: str, **kwargs) -> QueryResult:
        """
        实现IQueryService接口的查询方法

        Args:
            symbol: 股票代码
            **kwargs: 其他查询参数 (start_date, end_date等)

        Returns:
            查询结果
        """
        try:
            # 识别市场类型
            market, _ = self.stock_identifier.identify(symbol)
            adapter = self.get_adapter(market)

            # 获取财务数据（传递时间参数）
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            data = adapter.get_financial_data(symbol, start_date=start_date, end_date=end_date)

            # 构建查询结果
            return QueryResult(
                success=True,
                data=data,
                message=f"成功获取{symbol}的财务数据",
                total_records=len(data)
            )
        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"查询失败: {str(e)}",
                total_records=0
            )

    def get_available_fields(self, market: MarketType = None):
        """
        实现IQueryService接口的获取可用字段方法

        Args:
            market: 市场类型

        Returns:
            空列表，简化版本通过raw_data访问原始字段
        """
        # 简化版本：用户通过FinancialIndicator.raw_data访问所有原始字段
        return []