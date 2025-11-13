"""
查询服务适配器

将新的IFinancialDataService适配到旧的IQueryService接口，确保向后兼容性。
"""

from typing import Dict, Any
from ...core.interfaces import IQueryService
from ...core.models import QueryResult, MarketType
from ...core.stock_identifier import StockIdentifier
from ...core.data_queryer import IFinancialDataService


class QueryServiceAdapter(IQueryService):
    """
    查询服务适配器

    将新的IFinancialDataService适配到IQueryService接口，
    确保现有代码无需修改即可使用新架构。
    """

    def __init__(self, financial_service: IFinancialDataService):
        """
        初始化适配器

        Args:
            financial_service: 新的财务数据服务
        """
        self.financial_service = financial_service
        self.stock_identifier = StockIdentifier()

    def query(self, symbol: str, **kwargs) -> QueryResult:
        """
        实现IQueryService接口的查询方法

        Args:
            symbol: 股票代码
            **kwargs: 其他查询参数

        Returns:
            查询结果对象
        """
        try:
            # 识别股票市场
            market, _ = self.stock_identifier.identify(symbol)

            # 获取查询参数
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            data_type = kwargs.get('data_type', 'indicators')  # 默认查询财务指标

            # 根据数据类型调用相应的服务方法
            if data_type == 'indicators':
                data = self.financial_service.query_indicators(
                    symbol, market, start_date, end_date
                )
            elif data_type == 'balance_sheet':
                data = self.financial_service.query_balance_sheet(
                    symbol, market, start_date, end_date
                )
            elif data_type == 'income_statement':
                data = self.financial_service.query_income_statement(
                    symbol, market, start_date, end_date
                )
            elif data_type == 'cash_flow':
                data = self.financial_service.query_cash_flow(
                    symbol, market, start_date, end_date
                )
            else:
                # 默认查询财务指标
                data = self.financial_service.query_indicators(
                    symbol, market, start_date, end_date
                )

            # 转换DataFrame为FinancialIndicator列表
            financial_indicators = self._dataframe_to_indicators(data, symbol, market)

            return QueryResult(
                success=True,
                data=financial_indicators,
                message=f"成功获取{symbol}的财务数据",
                total_records=len(financial_indicators)
            )

        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"查询失败: {str(e)}",
                total_records=0
            )

    def _dataframe_to_indicators(self, data, symbol: str, market: MarketType):
        """
        将DataFrame转换为FinancialIndicator列表

        Args:
            data: DataFrame数据
            symbol: 股票代码
            market: 市场类型

        Returns:
            FinancialIndicator列表
        """
        from ...core.models import FinancialIndicator, PeriodType
        from datetime import datetime

        indicators = []

        if data is None or data.empty:
            return indicators

        # 根据DataFrame的结构处理数据
        if hasattr(data, 'iterrows'):
            for _, row in data.iterrows():
                # 尝试从行数据中提取日期信息
                report_date = self._extract_report_date(row)

                # 创建FinancialIndicator对象
                indicator = FinancialIndicator(
                    symbol=symbol,
                    market=market,
                    company_name=f"股票{symbol}",
                    report_date=report_date,
                    period_type=PeriodType.QUARTERLY,  # 默认季度报告
                    currency=self._get_currency_for_market(market),
                    indicators=row.to_dict(),
                    raw_data=row.to_dict()
                )
                indicators.append(indicator)

        return indicators

    def _extract_report_date(self, row):
        """从行数据中提取报告日期"""
        from datetime import datetime

        # 尝试常见的日期字段
        date_fields = ['REPORT_DATE', 'report_date', '日期', 'DATE', 'date']

        for field in date_fields:
            if field in row and row[field] is not None:
                try:
                    if hasattr(row[field], 'strftime'):
                        return row[field]
                    else:
                        return datetime.strptime(str(row[field]), '%Y-%m-%d')
                except:
                    continue

        # 如果没有找到日期字段，使用当前日期
        return datetime.now()

    def _get_currency_for_market(self, market: MarketType) -> str:
        """根据市场类型获取货币"""
        currency_map = {
            MarketType.A_STOCK: "CNY",
            MarketType.HK_STOCK: "HKD",
            MarketType.US_STOCK: "USD"
        }
        return currency_map.get(market, "CNY")