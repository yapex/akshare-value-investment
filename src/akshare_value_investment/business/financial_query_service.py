"""
财务查询服务

为MCP（Model Context Protocol）提供统一的财务数据查询接口。
集成查询路由、字段裁剪、时间频率处理等功能，专门为MCP场景优化。

## 🎯 核心功能

1. **查询路由**: 将market+query_type路由到对应的queryer
2. **字段裁剪**: 严格按需返回字段，减少MCP传输开销
3. **时间处理**: 支持年度聚合和报告期原始数据
4. **错误处理**: MCP友好的标准化错误响应
5. **字段发现**: 提供可用字段查询接口

## 📊 支持的查询类型

### A股市场 (4个接口)
- 财务指标
- 资产负债表
- 利润表
- 现金流量表

### 港股市场 (2个接口)
- 财务指标
- 财务三表

### 美股市场 (4个接口)
- 财务指标
- 资产负债表
- 利润表
- 现金流量表
"""

import logging
from typing import List, Optional, Dict, Any

import pandas as pd

from ..core.models import MarketType
from ..container import create_container
from .financial_types import FinancialQueryType, Frequency, MCPErrorType
from .mcp_response import MCPResponse
from .field_discovery_service import FieldDiscoveryService


class FinancialQueryService:
    """
    MCP财务查询服务

    统一的财务数据访问接口，为MCP提供查询路由、字段裁剪、
    时间频率处理等核心功能，专门优化MCP调用场景。
    """

    def __init__(self, container=None):
        """
        初始化财务查询服务

        Args:
            container: 依赖注入容器，如果为None则创建默认容器
        """
        self.container = container or create_container()
        self.logger = logging.getLogger(__name__)

        # 初始化字段发现服务
        self.field_discovery = FieldDiscoveryService(self.container)

        # 构建查询器映射
        self._build_queryer_mapping()

    def _build_queryer_mapping(self):
        """构建查询类型到查询器的映射关系"""
        self.queryer_mapping = {
            # A股查询器
            FinancialQueryType.A_STOCK_INDICATORS: self.container.a_stock_indicators(),
            FinancialQueryType.A_STOCK_BALANCE_SHEET: self.container.a_stock_balance_sheet(),
            FinancialQueryType.A_STOCK_INCOME_STATEMENT: self.container.a_stock_income_statement(),
            FinancialQueryType.A_STOCK_CASH_FLOW: self.container.a_stock_cash_flow(),

            # 港股查询器
            FinancialQueryType.HK_STOCK_INDICATORS: self.container.hk_stock_indicators(),
            FinancialQueryType.HK_STOCK_STATEMENTS: self.container.hk_stock_statement(),

            # 美股查询器
            FinancialQueryType.US_STOCK_INDICATORS: self.container.us_stock_indicators(),
            FinancialQueryType.US_STOCK_BALANCE_SHEET: self.container.us_stock_balance_sheet(),
            FinancialQueryType.US_STOCK_INCOME_STATEMENT: self.container.us_stock_income_statement(),
            FinancialQueryType.US_STOCK_CASH_FLOW: self.container.us_stock_cash_flow(),
        }

    def query(
        self,
        market: MarketType,
        query_type: FinancialQueryType,
        symbol: str,
        fields: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Frequency = Frequency.ANNUAL
    ) -> Dict[str, Any]:
        """
        统一查询接口

        为MCP提供财务数据查询的核心接口，支持字段裁剪、时间频率处理等功能。

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
            fields: 需要返回的字段列表，None表示返回所有字段
            start_date: 开始日期，YYYY-MM-DD格式
            end_date: 结束日期，YYYY-MM-DD格式
            frequency: 时间频率，年度数据或报告期数据

        Returns:
            MCP标准化的响应格式，包含查询结果或错误信息

        Examples:
            >>> service = FinancialQueryService()
            >>>
            >>> # 查询A股财务指标，只返回特定字段
            >>> response = service.query(
            ...     market=MarketType.A_STOCK,
            ...     query_type=FinancialQueryType.A_STOCK_INDICATORS,
            ...     symbol="600519",
            ...     fields=["报告期", "净利润", "净资产收益率"]
            ... )
            >>>
            >>> # 查询年度数据
            >>> response = service.query(
            ...     market=MarketType.A_STOCK,
            ...     query_type=FinancialQueryType.A_STOCK_INDICATORS,
            ...     symbol="600519",
            ...     start_date="2020-01-01",
            ...     end_date="2023-12-31",
            ...     frequency=Frequency.ANNUAL
            ... )
        """
        # 记录查询信息
        query_info = {
            "market": market.value,
            "query_type": query_type.value,
            "symbol": symbol,
            "fields": fields,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency.value
        }

        try:
            # 1. 参数验证
            validation_error = self._validate_parameters(market, query_type, symbol, fields, frequency)
            if validation_error:
                return MCPResponse.validation_error(
                    field=validation_error["field"],
                    value=validation_error["value"],
                    allowed_values=validation_error.get("allowed_values"),
                    query_info=query_info
                )

            # 2. 获取查询器并查询数据
            queryer = self._get_queryer(query_type)
            if queryer is None:
                return MCPResponse.error(
                    error_type=MCPErrorType.INVALID_QUERY_TYPE,
                    message=f"不支持的查询类型: {query_type.value}",
                    query_info=query_info
                )

            # 3. 执行查询
            raw_data = queryer.query(symbol, start_date, end_date)

            if raw_data.empty:
                return MCPResponse.data_not_found_error(
                    symbol=symbol,
                    market=market.value,
                    query_type=query_type.get_display_name(),
                    query_info=query_info
                )

            # 4. 时间频率处理
            processed_data = self._process_frequency(raw_data, frequency)

            # 5. 字段裁剪
            try:
                final_data = self._apply_field_filter(processed_data, fields)
            except ValueError as e:
                if "字段不存在" in str(e):
                    # 提取缺失字段信息
                    import re
                    missing_fields_match = re.search(r'字段不存在: \[(.*?)\]', str(e))
                    if missing_fields_match:
                        missing_fields_str = missing_fields_match.group(1)
                        # 清理字段名
                        missing_fields = [field.strip().strip("'\"") for field in missing_fields_str.split(',')]
                    else:
                        missing_fields = []

                    available_fields = list(processed_data.columns)
                    return MCPResponse.field_not_found_error(
                        missing_fields=missing_fields,
                        available_fields=available_fields,
                        query_info=query_info
                    )
                else:
                    # 其他ValueError异常
                    raise

            # 6. 构建响应
            metadata = {
                "market": market.value,
                "query_type": query_type.get_display_name(),
                "symbol": symbol,
                "frequency": frequency.get_display_name(),
                "original_record_count": len(raw_data),
                "processed_record_count": len(processed_data),
                "returned_field_count": len(final_data.columns)
            }

            if start_date or end_date:
                metadata["date_range"] = {
                    "start_date": start_date,
                    "end_date": end_date
                }

            return MCPResponse.success(
                data=final_data,
                metadata=metadata,
                query_info=query_info
            )

        except Exception as e:
            self.logger.error(f"查询失败: {e}", exc_info=True)
            return MCPResponse.internal_error(
                original_error=e,
                operation=f"财务数据查询 ({query_type.get_display_name()})",
                query_info=query_info
            )

    def get_available_fields(
        self,
        market: MarketType,
        query_type: FinancialQueryType
    ) -> Dict[str, Any]:
        """
        获取指定查询类型下的所有可用字段

        为MCP客户端提供字段发现功能，便于客户端了解可用字段
        和构建字段请求。

        Args:
            market: 市场类型
            query_type: 查询类型

        Returns:
            MCP标准化的响应格式，包含可用字段列表

        Examples:
            >>> service = FinancialQueryService()
            >>> response = service.get_available_fields(
            ...     market=MarketType.A_STOCK,
            ...     query_type=FinancialQueryType.A_STOCK_INDICATORS
            ... )
            >>>
            >>> if MCPResponse.is_success_response(response):
            ...     fields = response["metadata"]["available_fields"]
            ...     print(f"可用字段: {fields}")
        """
        query_info = {
            "market": market.value,
            "query_type": query_type.value
        }

        try:
            # 参数验证
            if query_type.get_market() != market:
                return MCPResponse.validation_error(
                    field="query_type",
                    value=query_type.value,
                    allowed_values=[qt.value for qt in FinancialQueryType.get_query_types_by_market(market)],
                    query_info=query_info
                )

            # 使用字段发现服务获取字段
            available_fields = self._discover_fields(query_type)

            if not available_fields:
                return MCPResponse.data_not_found_error(
                    symbol="字段发现",
                    market=market.value,
                    query_type=query_type.get_display_name(),
                    query_info=query_info
                )

            metadata = {
                "market": market.value,
                "query_type": query_type.get_display_name(),
                "available_fields": available_fields,
                "field_count": len(available_fields)
            }

            # 返回空的DataFrame但包含字段信息
            empty_df = pd.DataFrame(columns=available_fields)

            return MCPResponse.success(
                data=empty_df,
                metadata=metadata,
                query_info=query_info
            )

        except Exception as e:
            self.logger.error(f"字段发现失败: {e}", exc_info=True)
            return MCPResponse.internal_error(
                original_error=e,
                operation=f"字段发现 ({query_type.get_display_name()})",
                query_info=query_info
            )

    def _validate_parameters(
        self,
        market: MarketType,
        query_type: FinancialQueryType,
        symbol: str,
        fields: Optional[List[str]],
        frequency: Frequency
    ) -> Optional[Dict[str, Any]]:
        """
        验证查询参数

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
            fields: 字段列表
            frequency: 时间频率

        Returns:
            验证错误信息，验证通过返回None
        """
        # 验证市场和查询类型的匹配
        if query_type.get_market() != market:
            return {
                "field": "query_type",
                "value": query_type.value,
                "allowed_values": [qt.value for qt in FinancialQueryType.get_query_types_by_market(market)]
            }

        # 验证股票代码
        if not symbol or not isinstance(symbol, str):
            return {
                "field": "symbol",
                "value": symbol,
                "allowed_values": ["非空字符串"]
            }

        # 验证字段列表
        if fields is not None:
            if not isinstance(fields, list):
                return {
                    "field": "fields",
                    "value": fields,
                    "allowed_values": ["字段名列表或None"]
                }

            if not all(isinstance(field, str) for field in fields):
                return {
                    "field": "fields",
                    "value": fields,
                    "allowed_values": ["字符串列表"]
                }

        # 验证频率
        if not isinstance(frequency, Frequency):
            return {
                "field": "frequency",
                "value": frequency,
                "allowed_values": [freq.value for freq in Frequency]
            }

        return None

    def _get_queryer(self, query_type: FinancialQueryType):
        """
        根据查询类型获取对应的查询器

        Args:
            query_type: 查询类型

        Returns:
            对应的查询器实例，不支持则返回None
        """
        return self.queryer_mapping.get(query_type)

    def _process_frequency(self, data: pd.DataFrame, frequency: Frequency) -> pd.DataFrame:
        """
        处理时间频率

        Args:
            data: 原始数据
            frequency: 时间频率

        Returns:
            处理后的数据
        """
        if frequency == Frequency.QUARTERLY:
            # 报告期数据，直接返回
            return data.copy()

        if frequency == Frequency.ANNUAL:
            # 年度数据，取每年最后一份报告
            return self._convert_to_annual_data(data)

        return data.copy()

    def _convert_to_annual_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        将报告期数据转换为年度数据

        采用选项A：取每年最后一份报告（如2024-12-31代表2024年）

        Args:
            data: 原始报告期数据

        Returns:
            年度数据
        """
        if data.empty:
            return data.copy()

        # 查找日期字段
        date_field = self._find_date_field(data)
        if date_field is None:
            # 找不到日期字段，返回原数据
            self.logger.warning("未找到日期字段，无法转换为年度数据")
            return data.copy()

        # 确保日期字段是datetime类型
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy[date_field]):
            data_copy[date_field] = pd.to_datetime(data_copy[date_field], errors='coerce')

        # 提取年份
        data_copy['year'] = data_copy[date_field].dt.year

        # 按年份分组，取每年最后一条记录
        annual_data = data_copy.loc[data_copy.groupby('year')[date_field].idxmax()]

        # 删除临时列
        annual_data = annual_data.drop(columns=['year'])

        return annual_data.reset_index(drop=True)

    def _find_date_field(self, data: pd.DataFrame) -> Optional[str]:
        """
        查找日期字段

        Args:
            data: 数据DataFrame

        Returns:
            日期字段名，找不到返回None
        """
        # 常见的日期字段名模式
        date_patterns = [
            'report_date', 'REPORT_DATE', '报告期', 'date', 'DATE',
            'datetime', 'DATETIME', 'time', 'TIME'
        ]

        for pattern in date_patterns:
            for col in data.columns:
                if pattern.lower() in col.lower():
                    return col

        return None

    def _apply_field_filter(self, data: pd.DataFrame, fields: Optional[List[str]]) -> pd.DataFrame:
        """
        应用字段过滤器

        严格的字段裁剪：如果请求的字段不存在，抛出错误而不是忽略

        Args:
            data: 原始数据
            fields: 需要保留的字段列表

        Returns:
            过滤后的数据

        Raises:
            ValueError: 当请求的字段不存在时
        """
        if fields is None:
            # 未指定字段，返回所有字段
            return data.copy()

        if not fields:
            # 空字段列表，返回空DataFrame（保留结构）
            return data.iloc[:0].copy()

        # 检查字段是否存在
        missing_fields = [field for field in fields if field not in data.columns]
        if missing_fields:
            raise ValueError(f"字段不存在: {missing_fields}")

        # 过滤字段
        available_fields = [field for field in fields if field in data.columns]
        return data[available_fields].copy()

    def _discover_fields(self, query_type: FinancialQueryType) -> List[str]:
        """
        发现指定查询类型的可用字段

        Args:
            query_type: 查询类型

        Returns:
            可用字段列表
        """
        try:
            # 使用字段发现服务
            discovery_method_map = {
                # A股
                FinancialQueryType.A_STOCK_INDICATORS: self.field_discovery.discover_a_stock_indicator_fields,
                FinancialQueryType.A_STOCK_BALANCE_SHEET: self.field_discovery.discover_a_stock_balance_sheet_fields,
                FinancialQueryType.A_STOCK_INCOME_STATEMENT: self.field_discovery.discover_a_stock_income_statement_fields,
                FinancialQueryType.A_STOCK_CASH_FLOW: self.field_discovery.discover_a_stock_cash_flow_fields,

                # 港股
                FinancialQueryType.HK_STOCK_INDICATORS: self.field_discovery.discover_hk_stock_indicator_fields,
                FinancialQueryType.HK_STOCK_STATEMENTS: self.field_discovery.discover_hk_stock_statement_fields,

                # 美股
                FinancialQueryType.US_STOCK_INDICATORS: self.field_discovery.discover_us_stock_indicator_fields,
                FinancialQueryType.US_STOCK_BALANCE_SHEET: self.field_discovery.discover_us_stock_balance_sheet_fields,
                FinancialQueryType.US_STOCK_INCOME_STATEMENT: self.field_discovery.discover_us_stock_income_statement_fields,
                FinancialQueryType.US_STOCK_CASH_FLOW: self.field_discovery.discover_us_stock_cash_flow_fields,
            }

            discovery_method = discovery_method_map.get(query_type)
            if discovery_method:
                return discovery_method()
            else:
                self.logger.warning(f"未找到查询类型 {query_type.value} 的字段发现方法")
                return []

        except Exception as e:
            self.logger.error(f"字段发现失败: {e}", exc_info=True)
            return []