"""
财务查询服务

为FastAPI Web服务提供统一的财务数据查询接口。
集成查询路由、字段裁剪、时间频率处理等核心业务逻辑。

## 🎯 核心功能

1. **查询路由**: 将market+query_type路由到对应的queryer
2. **字段裁剪**: 严格按需返回字段，减少数据传输开销
3. **时间处理**: 支持年度聚合和报告期原始数据
4. **错误处理**: 标准化的错误响应格式
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
from typing import List, Optional, Dict, Any, Tuple

import pandas as pd

from ..core.models import MarketType
from ..container import create_container
from .financial_types import FinancialQueryType, Frequency, MCPErrorType
from .response_formatter import ResponseFormatter
from .field_discovery_service import FieldDiscoveryService


class FinancialQueryService:
    """
    财务查询服务

    统一的财务数据访问接口，为FastAPI提供查询路由、字段裁剪、
    时间频率处理等核心业务逻辑。
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
            FinancialQueryType.HK_STOCK_BALANCE_SHEET: self.container.hk_stock_balance_sheet(),
            FinancialQueryType.HK_STOCK_INCOME_STATEMENT: self.container.hk_stock_income_statement(),
            FinancialQueryType.HK_STOCK_CASH_FLOW: self.container.hk_stock_cash_flow(),

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
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Frequency = Frequency.ANNUAL
    ) -> Dict[str, Any]:
        """
        统一查询接口

        为FastAPI提供财务数据查询的核心接口，支持时间频率处理等功能。

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
            start_date: 开始日期，YYYY-MM-DD格式
            end_date: 结束日期，YYYY-MM-DD格式
            frequency: 时间频率，年度数据或报告期数据

        Returns:
            标准化的响应格式，包含查询结果或错误信息

        Examples:
            >>> service = FinancialQueryService()
            >>>
            >>> # 查询A股财务指标
            >>> response = service.query(
            ...     market=MarketType.A_STOCK,
            ...     query_type=FinancialQueryType.A_STOCK_INDICATORS,
            ...     symbol="600519"
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
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency.value
        }

        try:
            # 1. 参数验证
            validation_error = self._validate_parameters(market, query_type, symbol, frequency)
            if validation_error:
                return ResponseFormatter.validation_error(
                    field=validation_error["field"],
                    value=validation_error["value"],
                    allowed_values=validation_error.get("allowed_values"),
                    query_info=query_info
                )

            # 2. 获取查询器并查询数据
            queryer = self._get_queryer(query_type)
            if queryer is None:
                return ResponseFormatter.error(
                    error_type=MCPErrorType.INVALID_QUERY_TYPE,
                    message=f"不支持的查询类型: {query_type.value}",
                    query_info=query_info
                )

            # 3. 执行查询
            self.logger.info(f"执行查询: {market.value} {query_type.value} {symbol}")
            raw_data = queryer.query(symbol, start_date, end_date)

            if raw_data.empty:
                return ResponseFormatter.data_not_found_error(
                    symbol=symbol,
                    market=market.value,
                    query_type=query_type.get_display_name(),
                    query_info=query_info
                )

            # 4. 时间频率处理
            processed_data = self._process_frequency(raw_data, frequency, query_type)

            # 5. 构建成功响应
            metadata = {
                "market": market.value,
                "query_type": query_type.get_display_name(),
                "symbol": symbol,
                "frequency": frequency.get_display_name(),
                "original_record_count": len(raw_data),
                "processed_record_count": len(processed_data),
                "returned_field_count": len(processed_data.columns)
            }

            if start_date or end_date:
                metadata["date_range"] = {
                    "start_date": start_date,
                    "end_date": end_date
                }

            self.logger.info(f"查询成功: {len(processed_data)} 条记录, {len(processed_data.columns)} 个字段")

            return ResponseFormatter.success(
                data=processed_data,
                metadata=metadata,
                query_info=query_info
            )

        except Exception as e:
            self.logger.error(f"查询失败: {e}", exc_info=True)
            return ResponseFormatter.internal_error(
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

        为客户端提供字段发现功能，便于了解可用字段和构建字段请求。

        Args:
            market: 市场类型
            query_type: 查询类型

        Returns:
            标准化的响应格式，包含可用字段列表

        Examples:
            >>> service = FinancialQueryService()
            >>> response = service.get_available_fields(
            ...     market=MarketType.A_STOCK,
            ...     query_type=FinancialQueryType.A_STOCK_INDICATORS
            ... )
            >>>
            >>> if ResponseFormatter.is_success_response(response):
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
                return ResponseFormatter.validation_error(
                    field="query_type",
                    value=query_type.value,
                    allowed_values=[qt.value for qt in FinancialQueryType.get_query_types_by_market(market)],
                    query_info=query_info
                )

            # 使用字段发现服务获取字段
            available_fields = self._discover_fields(query_type)

            if not available_fields:
                return ResponseFormatter.data_not_found_error(
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

            return ResponseFormatter.success(
                data=empty_df,
                metadata=metadata,
                query_info=query_info
            )

        except Exception as e:
            self.logger.error(f"字段发现失败: {e}", exc_info=True)
            return ResponseFormatter.internal_error(
                original_error=e,
                operation=f"字段发现 ({query_type.get_display_name()})",
                query_info=query_info
            )

    def _validate_parameters(
        self,
        market: MarketType,
        query_type: FinancialQueryType,
        symbol: str,
        frequency: Frequency
    ) -> Optional[Dict[str, Any]]:
        """
        验证查询参数

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
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

    def _process_frequency(self, data: pd.DataFrame, frequency: Frequency, query_type: Optional[FinancialQueryType] = None) -> pd.DataFrame:
        """
        处理时间频率

        Args:
            data: 原始数据
            frequency: 时间频率
            query_type: 查询类型（用于识别美股财务指标）

        Returns:
            处理后的数据
        """
        # 空数据直接返回
        if data.empty:
            return data.copy()

        # 财务三表数据已经是年度数据（通过akshare的indicator="年报"或"年度"参数获取）
        # 不需要做任何频率转换，直接返回
        if query_type and query_type in [
            FinancialQueryType.A_FINANCIAL_STATEMENTS,
            FinancialQueryType.HK_FINANCIAL_STATEMENTS,
            FinancialQueryType.US_FINANCIAL_STATEMENTS
        ]:
            return data.copy()

        # 季度数据：直接返回原始数据
        if frequency == Frequency.QUARTERLY:
            return data.copy()

        # 年度数据：需要过滤或转换（仅用于财务指标数据）
        if frequency == Frequency.ANNUAL:
            # 检查是否已经是年度数据
            if self._is_already_annual_data(data):
                return data.copy()
            else:
                # 转换为年度数据
                return self._convert_to_annual_data(data, query_type)

        return data.copy()

    def _is_already_annual_data(self, data: pd.DataFrame) -> bool:
        """
        检查数据是否已经是年度数据

        通过检查日期字段的月份分布来判断：
        - A股/港股：如果大部分日期都是12月31日，则认为是年度数据
        - 美股财务三表：如果大部分日期是9月30日（财年结束），则认为是年度数据
        - 美股财务指标：通过REPORT_TYPE字段中的Q4判断

        Args:
            data: 数据DataFrame

        Returns:
            True表示已经是年度数据，False表示需要转换
        """
        if data.empty:
            return True

        # 准备数据：查找日期字段并转换为datetime类型
        date_field, data_copy = self._prepare_date_field(data)
        if date_field is None or data_copy.empty:
            return True

        # 检查是否有REPORT_TYPE字段 - 主要用于美股财务指标
        if 'REPORT_TYPE' in data_copy.columns:
            # 美股财务指标：检查Q4占比（单季报数据混合）
            q4_count = len(data_copy[data_copy['REPORT_TYPE'].str.contains('/Q4', na=False)])
            if q4_count > 0:
                return q4_count / len(data_copy) > 0.6  # 如果超过60%是Q4，认为是年度数据

        # 检查数据密度：如果平均每年只有1条记录，认为是年度数据
        # 这适用于美股财务三表（每家公司每年只有一条年报记录）
        years = data_copy[date_field].dt.year
        unique_years = years.nunique()
        if unique_years > 0:
            records_per_year = len(data_copy) / unique_years
            if records_per_year <= 1.2:  # 允许少量误差
                return True

        # A股/港股：检查12月31日占比
        dec_31_count = len(data_copy[
            (data_copy[date_field].dt.month == 12) &
            (data_copy[date_field].dt.day == 31)
        ])

        # A股/港股标准：如果超过70%是12月31日，认为是年度数据
        return dec_31_count / len(data_copy) > 0.7

    def _prepare_date_field(self, data: pd.DataFrame) -> Tuple[Optional[str], pd.DataFrame]:
        """
        准备日期字段：查找日期字段并转换为datetime类型

        这个辅助方法避免了在 _is_already_annual_data 和 _convert_to_annual_data 中重复代码

        Args:
            data: 原始数据

        Returns:
            (日期字段名, 处理后的DataFrame)
        """
        # 查找日期字段
        date_field = self._find_date_field(data)
        if date_field is None:
            return None, data

        # 确保日期字段是datetime类型
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy[date_field]):
            data_copy[date_field] = pd.to_datetime(data_copy[date_field], errors='coerce')

        # 过滤掉无效日期
        data_copy = data_copy.dropna(subset=[date_field])

        return date_field, data_copy

    def _convert_to_annual_data(self, data: pd.DataFrame, query_type: Optional[FinancialQueryType] = None) -> pd.DataFrame:
        """
        将报告期数据转换为年度数据

        过滤出财报日期为12月31日的年度报告。
        对于美股财务指标，使用财年数据处理逻辑。

        Args:
            data: 原始报告期数据
            query_type: 查询类型（用于识别美股财务指标）

        Returns:
            年度数据
        """
        if data.empty:
            return data.copy()

        # 美股财务指标特殊处理
        if query_type == FinancialQueryType.US_STOCK_INDICATORS:
            return self._process_us_fiscal_year_data(data)

        # 准备日期字段（复用辅助方法避免重复代码）
        date_field, data_copy = self._prepare_date_field(data)
        if date_field is None or data_copy.empty:
            self.logger.warning("未找到日期字段或无有效数据，返回原始数据")
            return data.copy()

        # 过滤出年度报告（12月31日，适用于A股/港股）
        annual_data = data_copy[
            (data_copy[date_field].dt.month == 12) &
            (data_copy[date_field].dt.day == 31)
        ]

        return annual_data.reset_index(drop=True)

    def _process_us_fiscal_year_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理美股财务指标财年数据，优先选择Q4数据作为年度代表

        Args:
            df: 美股财务指标原始数据

        Returns:
            处理后的年度数据
        """
        if df is None or df.empty:
            return df

        # 确保REPORT_TYPE字段存在
        if 'REPORT_TYPE' not in df.columns:
            self.logger.warning("美股财务指标数据缺少REPORT_TYPE字段，无法进行财年处理")
            return df

        # 创建财年字段，处理NaN值
        df_processed = df.copy()
        df_processed['FISCAL_YEAR'] = df_processed['REPORT_TYPE'].str.extract(r'(\d{4})')
        df_processed['FISCAL_YEAR'] = pd.to_numeric(df_processed['FISCAL_YEAR'], errors='coerce').astype('Int64')

        df_processed['QUARTER'] = df_processed['REPORT_TYPE'].str.extract(r'Q(\d)')
        df_processed['QUARTER'] = pd.to_numeric(df_processed['QUARTER'], errors='coerce').astype('Int64')

        # 过滤掉无法解析财年或季度的记录
        df_processed = df_processed.dropna(subset=['FISCAL_YEAR', 'QUARTER'])

        # 按财年和季度排序
        df_processed = df_processed.sort_values(['FISCAL_YEAR', 'QUARTER'], ascending=[False, False])

        # 为每个财年标记Q4数据
        df_processed['IS_Q4'] = df_processed['QUARTER'] == 4

        # 为每个财年选择优先级最高的数据（Q4 > Q3 > Q2 > Q1）
        df_processed['QUARTER_PRIORITY'] = 5 - df_processed['QUARTER'].fillna(5)  # Q4=1, Q3=2, Q2=3, Q1=4, 无季度=0

        # 为每个财年选择最佳记录
        df_best = df_processed.loc[df_processed.groupby('FISCAL_YEAR')['QUARTER_PRIORITY'].idxmin()]

        # 按财年降序排列
        df_best = df_best.sort_values('FISCAL_YEAR', ascending=False)

        # 保留原始REPORT_DATE格式，但更新其含义为财年结束日期
        # 将REPORT_DATE更新为STD_REPORT_DATE（财年结束日期）
        if 'STD_REPORT_DATE' in df_best.columns:
            df_best['REPORT_DATE'] = df_best['STD_REPORT_DATE']

        self.logger.info(f"美股财年数据处理完成：从 {len(df)} 条记录处理为 {len(df_best)} 条年度数据")
        return df_best

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
                FinancialQueryType.HK_STOCK_BALANCE_SHEET: self.field_discovery.discover_hk_stock_balance_sheet_fields,
                FinancialQueryType.HK_STOCK_INCOME_STATEMENT: self.field_discovery.discover_hk_stock_income_statement_fields,
                FinancialQueryType.HK_STOCK_CASH_FLOW: self.field_discovery.discover_hk_stock_cash_flow_fields,

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

    def query_financial_statements(
        self,
        query_type: FinancialQueryType,
        symbol: str,
        frequency: Frequency = Frequency.ANNUAL,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询财务三表聚合数据

        返回包含资产负债表、利润表、现金流量表的字典结构。
        所有市场（A股、港股、美股）都包含单位映射（unit_map）。

        Args:
            query_type: 财务三表聚合查询类型（A/HK/US_FINANCIAL_STATEMENTS）
            symbol: 股票代码
            frequency: 时间频率（年度/报告期）
            limit: 限制每个DataFrame返回的记录数

        Returns:
            Dict[str, Any]: 统一格式，所有市场都包含4个键
                {
                    'balance_sheet': DataFrame,
                    'income_statement': DataFrame,
                    'cash_flow': DataFrame,
                    'unit_map': Dict[str, str]  # 字段单位映射
                }

        Raises:
            ValueError: 如果query_type不是财务三表聚合查询类型

        Examples:
            >>> service = FinancialQueryService()
            >>> result = service.query_financial_statements(
            ...     query_type=FinancialQueryType.A_FINANCIAL_STATEMENTS,
            ...     symbol="SH600519",
            ...     frequency=Frequency.ANNUAL,
            ...     limit=3
            ... )
            >>> print(result.keys())  # dict_keys(['balance_sheet', 'income_statement', 'cash_flow', 'unit_map'])
        """
        # 验证是否为财务三表聚合查询类型
        aggregation_types = {
            FinancialQueryType.A_FINANCIAL_STATEMENTS: MarketType.A_STOCK,
            FinancialQueryType.HK_FINANCIAL_STATEMENTS: MarketType.HK_STOCK,
            FinancialQueryType.US_FINANCIAL_STATEMENTS: MarketType.US_STOCK,
        }

        if query_type not in aggregation_types:
            raise ValueError(
                f"查询类型 {query_type.value} 不是财务三表聚合查询类型。"
                f"支持的聚合查询类型: {[qt.value for qt in aggregation_types.keys()]}"
            )

        market = aggregation_types[query_type]

        # 根据市场类型确定三个查询器
        queryer_map = {
            MarketType.A_STOCK: {
                'balance_sheet': FinancialQueryType.A_STOCK_BALANCE_SHEET,
                'income_statement': FinancialQueryType.A_STOCK_INCOME_STATEMENT,
                'cash_flow': FinancialQueryType.A_STOCK_CASH_FLOW,
            },
            MarketType.HK_STOCK: {
                'balance_sheet': FinancialQueryType.HK_STOCK_BALANCE_SHEET,
                'income_statement': FinancialQueryType.HK_STOCK_INCOME_STATEMENT,
                'cash_flow': FinancialQueryType.HK_STOCK_CASH_FLOW,
            },
            MarketType.US_STOCK: {
                'balance_sheet': FinancialQueryType.US_STOCK_BALANCE_SHEET,
                'income_statement': FinancialQueryType.US_STOCK_INCOME_STATEMENT,
                'cash_flow': FinancialQueryType.US_STOCK_CASH_FLOW,
            }
        }

        statement_types = queryer_map[market]
        result = {}
        unit_map = {}  # 用于收集单位映射（仅A股）

        # 查询三张报表
        for statement_name, statement_query_type in statement_types.items():
            queryer = self._get_queryer(statement_query_type)
            if queryer is None:
                self.logger.warning(f"未找到查询器: {statement_query_type.value}")
                result[statement_name] = pd.DataFrame()
                continue

            # 执行查询
            query_result = queryer.query(symbol)

            # 所有市场现在都返回统一格式：{'data': DataFrame, 'unit_map': Dict}
            if isinstance(query_result, dict):
                # 新格式：包含data和unit_map（所有市场）
                raw_data = query_result.get("data", pd.DataFrame())
                statement_unit_map = query_result.get("unit_map", {})
                # 合并单位映射
                unit_map.update(statement_unit_map)
            else:
                # 兼容旧格式：直接返回DataFrame的情况
                raw_data = query_result if isinstance(query_result, pd.DataFrame) else pd.DataFrame()

            if raw_data.empty:
                result[statement_name] = pd.DataFrame()
                continue

            # 应用时间频率处理
            processed_data = self._process_frequency(raw_data, frequency, statement_query_type)

            # 应用记录数限制
            if limit is not None and len(processed_data) > limit:
                processed_data = processed_data.head(limit)

            result[statement_name] = processed_data

        # 添加单位映射到结果中（所有市场）
        if unit_map:
            result["unit_map"] = unit_map

        return result