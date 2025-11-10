"""
查询服务实现 - 简化版本

实现财务指标查询的核心业务逻辑 - 简化版本，不进行字段映射。
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date

from .interfaces import IQueryService, IMarketIdentifier, IMarketAdapter
from .models import MarketType, FinancialIndicator, QueryResult, PeriodType


class FinancialQueryService(IQueryService):
    """财务查询服务 - 简化版本"""

    def __init__(self, market_identifier: IMarketIdentifier, adapter_manager):
        """
        初始化查询服务 - 简化版本，不需要字段映射器

        Args:
            market_identifier: 市场识别器
            adapter_manager: 适配器管理器
        """
        self.market_identifier = market_identifier
        self.adapter_manager = adapter_manager

    def query(self, symbol: str, **kwargs) -> QueryResult:
        """
        查询单只股票的财务数据 - 简化版本

        Args:
            symbol: 股票代码
            **kwargs: 其他查询参数（如日期范围等）

        Returns:
            查询结果
        """
        try:
            # 1. 识别市场和标准化代码
            market, standard_symbol = self.market_identifier.identify(symbol)

            # 2. 获取对应市场的适配器
            adapter = self.adapter_manager.get_adapter(market)

            # 3. 获取财务数据
            indicators = adapter.get_financial_data(standard_symbol)

            # 4. 应用过滤器（如果提供）
            filtered_indicators = self._apply_filters(indicators, **kwargs)

            # 5. 返回查询结果
            return QueryResult(
                success=True,
                data=filtered_indicators,
                message=None,
                total_records=len(filtered_indicators)
            )

        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"查询失败: {str(e)}",
                total_records=0
            )

    def get_available_fields(self, market: Optional[MarketType] = None):
        """
        获取可用字段 - 简化版本

        Args:
            market: 市场类型，如果为None则返回所有市场的字段

        Returns:
            可用字段列表或字典
        """
        # 简化版本：由于不进行字段映射，返回空列表
        # 用户可以通过 raw_data 访问所有原始字段
        if market is None:
            return {
                MarketType.A_STOCK: [],
                MarketType.HK_STOCK: [],
                MarketType.US_STOCK: []
            }
        else:
            return []

    def _apply_filters(self, indicators: List[FinancialIndicator], **kwargs) -> List[FinancialIndicator]:
        """
        应用过滤器 - 简化版本

        Args:
            indicators: 财务指标列表
            **kwargs: 过滤参数

        Returns:
            过滤后的财务指标列表
        """
        filtered_indicators = indicators

        # 日期范围过滤
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if start_date or end_date:
            filtered_indicators = self._filter_by_date_range(
                filtered_indicators, start_date, end_date
            )

        # 报告期类型过滤
        period_type = kwargs.get('period_type')
        if period_type:
            filtered_indicators = self._filter_by_period_type(
                filtered_indicators, period_type
            )

        return filtered_indicators

    def _filter_by_date_range(
        self,
        indicators: List[FinancialIndicator],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[FinancialIndicator]:
        """
        按日期范围过滤

        Args:
            indicators: 财务指标列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            过滤后的财务指标列表
        """
        if not start_date and not end_date:
            return indicators

        filtered = []

        for indicator in indicators:
            include_record = True

            if start_date:
                if isinstance(start_date, str):
                    start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
                else:
                    start_date_parsed = start_date

                if indicator.report_date.date() < start_date_parsed:
                    include_record = False

            if end_date:
                if isinstance(end_date, str):
                    end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
                else:
                    end_date_parsed = end_date

                if indicator.report_date.date() > end_date_parsed:
                    include_record = False

            if include_record:
                filtered.append(indicator)

        return filtered

    def _filter_by_period_type(
        self,
        indicators: List[FinancialIndicator],
        period_type: PeriodType
    ) -> List[FinancialIndicator]:
        """
        按报告期类型过滤

        Args:
            indicators: 财务指标列表
            period_type: 报告期类型

        Returns:
            过滤后的财务指标列表
        """
        return [
            indicator for indicator in indicators
            if indicator.period_type == period_type
        ]