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
            self.logger.info(f"执行查询: {market.value} {query_type.value} {symbol}")
            raw_data = queryer.query(symbol, start_date, end_date)

            if raw_data.empty:
                return MCPResponse.data_not_found_error(
                    symbol=symbol,
                    market=market.value,
                    query_type=query_type.get_display_name(),
                    query_info=query_info
                )

            # 4. 时间频率处理
            processed_data = self._process_frequency(raw_data, frequency, query_type)

            # 5. 字段裁剪（增强错误处理）
            try:
                final_data = self._apply_field_filter(processed_data, fields)
            except ValueError as e:
                if "请求的字段不存在" in str(e) or "字段不存在" in str(e):
                    # 提取缺失字段和可用字段信息
                    import re
                    
                    # 尝试从详细错误信息中提取字段
                    missing_fields = []
                    available_fields = list(processed_data.columns)
                    
                    # 提取缺失字段（多种格式支持）
                    missing_match = re.search(r'请求的字段不存在: \[(.*?)\]', str(e))
                    if missing_match:
                        missing_fields_str = missing_match.group(1)
                        missing_fields = [field.strip().strip("'\"") for field in missing_fields_str.split(',')]
                    else:
                        # 备用提取方式
                        lines = str(e).split('\n')
                        for line in lines:
                            if '请求的字段不存在' in line:
                                field_match = re.search(r'\[(.*?)\]', line)
                                if field_match:
                                    missing_fields = [f.strip().strip("'\"") for f in field_match.group(1).split(',')]
                                    break

                    # 构建增强的错误响应
                    return MCPResponse.field_not_found_error(
                        missing_fields=missing_fields,
                        available_fields=available_fields,
                        query_info=query_info
                    )
                else:
                    # 其他ValueError异常
                    self.logger.error(f"字段处理异常: {e}", exc_info=True)
                    raise

            # 6. 构建成功响应
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

            self.logger.info(f"查询成功: {len(final_data)} 条记录, {len(final_data.columns)} 个字段")
            
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

    def _process_frequency(self, data: pd.DataFrame, frequency: Frequency, query_type: Optional[FinancialQueryType] = None) -> pd.DataFrame:
        """
        处理时间频率

        Args:
            data: 原始数据
            frequency: 时间频率
            query_type: 查询类型（用于特殊处理美股数据）

        Returns:
            处理后的数据
        """
        if frequency == Frequency.QUARTERLY:
            # 报告期数据，直接返回
            return data.copy()

        if frequency == Frequency.ANNUAL:
            # 美股财务三表硬编码使用年报数据，直接返回
            us_financial_statements = [
                FinancialQueryType.US_STOCK_BALANCE_SHEET,
                FinancialQueryType.US_STOCK_INCOME_STATEMENT,
                FinancialQueryType.US_STOCK_CASH_FLOW
            ]
            if query_type in us_financial_statements:
                return data.copy()

            # 检查是否已经是年度数据
            if self._is_already_annual_data(data):
                # 已经是年度数据，直接返回
                return data.copy()
            else:
                # 需要转换为年度数据
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

        # 查找日期字段
        date_field = self._find_date_field(data)
        if date_field is None:
            # 找不到日期字段，无法判断，假设已经是年度数据
            return True

        # 确保日期字段是datetime类型
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy[date_field]):
            data_copy[date_field] = pd.to_datetime(data_copy[date_field], errors='coerce')

        # 过滤掉无效日期
        data_copy = data_copy.dropna(subset=[date_field])

        if data_copy.empty:
            return True

        # 检查是否有REPORT_TYPE字段 - 主要用于美股财务指标
        if 'REPORT_TYPE' in data_copy.columns:
            # 美股财务指标：检查Q4占比（单季报数据混合）
            q4_count = len(data_copy[data_copy['REPORT_TYPE'].str.contains('/Q4', na=False)])
            if q4_count > 0:
                return q4_count / len(data_copy) > 0.6  # 如果超过60%是Q4，认为是年度数据

        # A股/港股：检查12月31日占比
        dec_31_count = len(data_copy[
            (data_copy[date_field].dt.month == 12) &
            (data_copy[date_field].dt.day == 31)
        ])

        # A股/港股标准：如果超过70%是12月31日，认为是年度数据
        return dec_31_count / len(data_copy) > 0.7

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

        # 查找日期字段
        date_field = self._find_date_field(data)
        if date_field is None:
            # 找不到日期字段，无法转换为年度数据
            self.logger.warning("未找到日期字段，无法转换为年度数据")
            return data.copy()

        # 确保日期字段是datetime类型
        data_copy = data.copy()
        if not pd.api.types.is_datetime64_any_dtype(data_copy[date_field]):
            data_copy[date_field] = pd.to_datetime(data_copy[date_field], errors='coerce')

        # 过滤掉无效日期
        data_copy = data_copy.dropna(subset=[date_field])

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

    def _apply_field_filter(self, data: pd.DataFrame, fields: Optional[List[str]]) -> pd.DataFrame:
        """
        应用字段过滤器

        严格的字段裁剪：如果请求的字段不存在，抛出详细的错误信息而不是忽略

        Args:
            data: 原始数据
            fields: 需要保留的字段列表

        Returns:
            过滤后的数据

        Raises:
            ValueError: 当请求的字段不存在时，包含详细的错误信息和可用字段建议
        """
        if fields is None:
            # 未指定字段，返回所有字段
            self.logger.debug(f"未指定字段，返回所有 {len(data.columns)} 个字段")
            return data.copy()

        if not fields:
            # 空字段列表，返回空DataFrame（保留结构）
            self.logger.debug("字段列表为空，返回空DataFrame")
            return data.iloc[:0].copy()

        # 检查字段是否存在
        missing_fields = [field for field in fields if field not in data.columns]
        
        if missing_fields:
            # 构建详细的错误信息
            available_fields = list(data.columns)
            
            # 提供字段相似性建议
            similar_fields = []
            for missing_field in missing_fields:
                # 使用简单的字符串相似性查找相似字段
                suggestions = []
                missing_lower = missing_field.lower()
                
                for available_field in available_fields:
                    available_lower = available_field.lower()
                    # 检查包含关系
                    if missing_lower in available_lower or available_lower in missing_lower:
                        suggestions.append(available_field)
                    # 检查编辑距离相近的字段
                    elif self._calculate_similarity(missing_lower, available_lower) > 0.7:
                        suggestions.append(available_field)
                
                similar_fields.extend(suggestions[:3])  # 最多建议3个相似字段
            
            error_msg = (
                f"请求的字段不存在: {missing_fields}\n"
                f"当前数据表可用字段 ({len(available_fields)}个): {available_fields[:10]}{'...' if len(available_fields) > 10 else ''}\n"
                f"相似字段建议: {list(set(similar_fields))[:5] if similar_fields else '无相似字段'}"
            )
            
            self.logger.warning(f"字段过滤失败: {error_msg}")
            raise ValueError(error_msg)

        # 过滤字段
        available_fields = [field for field in fields if field in data.columns]
        self.logger.debug(f"字段过滤成功，从 {len(data.columns)} 个字段中选择了 {len(available_fields)} 个字段")
        
        return data[available_fields].copy()

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度（简单的字符匹配算法）

        Args:
            str1: 字符串1
            str2: 字符串2

        Returns:
            相似度分数 (0-1之间)
        """
        if not str1 or not str2:
            return 0.0
        
        # 计算共同的字符比例
        common_chars = set(str1) & set(str2)
        total_chars = set(str1) | set(str2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)

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
    ) -> Dict[str, pd.DataFrame]:
        """
        查询财务三表聚合数据

        返回包含资产负债表、利润表、现金流量表的字典结构。

        Args:
            query_type: 财务三表聚合查询类型（A/HK/US_FINANCIAL_STATEMENTS）
            symbol: 股票代码
            frequency: 时间频率（年度/报告期）
            limit: 限制每个DataFrame返回的记录数

        Returns:
            字典结构：{'balance_sheet': DataFrame, 'income_statement': DataFrame, 'cash_flow': DataFrame}

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
            >>> print(result.keys())  # dict_keys(['balance_sheet', 'income_statement', 'cash_flow'])
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

        # 查询三张报表
        for statement_name, statement_query_type in statement_types.items():
            queryer = self._get_queryer(statement_query_type)
            if queryer is None:
                self.logger.warning(f"未找到查询器: {statement_query_type.value}")
                result[statement_name] = pd.DataFrame()
                continue

            # 执行查询
            raw_data = queryer.query(symbol)

            if raw_data.empty:
                result[statement_name] = pd.DataFrame()
                continue

            # 应用时间频率处理
            processed_data = self._process_frequency(raw_data, frequency, statement_query_type)

            # 应用记录数限制
            if limit is not None and len(processed_data) > limit:
                processed_data = processed_data.head(limit)

            result[statement_name] = processed_data

        return result