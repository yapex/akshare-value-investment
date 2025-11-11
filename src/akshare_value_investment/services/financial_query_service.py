"""
财务查询服务

核心业务逻辑，协调各种服务完成财务指标查询功能。
"""

from typing import List, Optional, Any, Tuple, Dict
from .interfaces import (
    IQueryService,
    IResponseFormatter,
    ITimeRangeProcessor,
    IDataStructureProcessor
)
from ..business.mapping.field_mapper import IFieldMapper


class FinancialQueryService:
    """财务查询服务 - 纯业务逻辑"""

    def __init__(self,
                 query_service: IQueryService,
                 field_mapper: IFieldMapper,
                 formatter: IResponseFormatter,
                 time_processor: ITimeRangeProcessor,
                 data_processor: IDataStructureProcessor):
        """
        初始化财务查询服务

        Args:
            query_service: 查询服务
            field_mapper: 字段映射服务
            formatter: 响应格式化服务
            time_processor: 时间范围处理器
            data_processor: 数据结构处理器
        """
        self.query_service = query_service
        self.field_mapper = field_mapper
        self.formatter = formatter
        self.time_processor = time_processor
        self.data_processor = data_processor

    async def query_indicators(self,
                             symbol: str,
                             fields: List[str] = None,
                             prefer_annual: bool = True,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             include_metadata: bool = True,
                             default_years: int = 5) -> str:
        """
        查询财务指标

        Args:
            symbol: 股票代码
            fields: 请求的字段列表
            prefer_annual: 是否优先年报
            start_date: 开始日期
            end_date: 结束日期
            include_metadata: 是否包含元数据
            default_years: 默认查询年数

        Returns:
            格式化的查询响应
        """
        # 1. 参数验证和处理
        validated_params = self._validate_and_process_params(
            symbol, fields, prefer_annual, start_date, end_date, include_metadata, default_years
        )

        # 2. 字段映射
        if validated_params['fields']:
            mapped_fields, mapping_suggestions = await self.field_mapper.resolve_fields(
                validated_params['symbol'],
                validated_params['fields']
            )
        else:
            mapped_fields, mapping_suggestions = [], []

        # 3. 执行查询
        result = self.query_service.query(
            validated_params['symbol'],
            start_date=validated_params['start_date'],
            end_date=validated_params['end_date']
        )

        # 4. 格式化响应
        return self.formatter.format_query_response(
            result=result,
            symbol=validated_params['symbol'],
            mapped_fields=mapped_fields,
            prefer_annual=validated_params['prefer_annual'],
            include_metadata=validated_params['include_metadata'],
            mapping_suggestions=mapping_suggestions
        )

    def _validate_and_process_params(self,
                                    symbol: str,
                                    fields: List[str],
                                    prefer_annual: bool,
                                    start_date: Optional[str],
                                    end_date: Optional[str],
                                    include_metadata: bool,
                                    default_years: int) -> dict:
        """
        验证和处理参数

        Args:
            symbol: 股票代码
            fields: 字段列表
            prefer_annual: 优先年报
            start_date: 开始日期
            end_date: 结束日期
            include_metadata: 包含元数据
            default_years: 默认年数

        Returns:
            处理后的参数字典
        """
        if not symbol or not symbol.strip():
            raise ValueError("股票代码不能为空")

        # 处理时间范围
        processed_start_date, processed_end_date = self.time_processor.process_time_range(
            start_date, end_date, default_years
        )

        return {
            'symbol': symbol.strip(),
            'fields': fields or [],
            'prefer_annual': prefer_annual,
            'start_date': processed_start_date,
            'end_date': processed_end_date,
            'include_metadata': include_metadata
        }

    def query(self, symbol: str, **kwargs) -> Any:
        """
        同步查询方法 - 向后兼容接口

        Args:
            symbol: 股票代码
            **kwargs: 其他查询参数

        Returns:
            查询结果（与内部query_service接口兼容）
        """
        # 直接调用内部query_service的query方法
        return self.query_service.query(symbol, **kwargs)

    async def query_by_field_name(self, symbol: str, field_query: str, **kwargs) -> Any:
        """
        通过字段名或关键字查询单只股票的财务指标

        Args:
            symbol: 股票代码
            field_query: 字段查询，可以是字段名或自然语言描述
            **kwargs: 其他查询参数（如日期范围等）

        Returns:
            查询结果，包含匹配的字段数据
        """
        try:
            # 1. 先获取所有财务数据
            base_result = self.query(symbol, **kwargs)
            if not hasattr(base_result, 'success') or not base_result.success:
                return {
                    "success": False,
                    "data": [],
                    "message": "无法获取基础财务数据",
                    "total_records": 0
                }

            # 2. 提取所有可用字段
            available_fields = set()
            for indicator in base_result.data:
                if hasattr(indicator, 'raw_data') and indicator.raw_data:
                    available_fields.update(indicator.raw_data.keys())

            # 3. 使用新的字段映射器解析字段
            mapped_fields, suggestions = await self.field_mapper.resolve_fields(symbol, [field_query])

            matched_field = mapped_fields[0] if mapped_fields else None
            explanation = f"字段映射匹配: '{field_query}' -> '{matched_field}'" if matched_field else "未找到匹配字段"

            if not matched_field:
                # 提供建议
                suggestion_text = ", ".join(suggestions[:3])

                return {
                    "success": False,
                    "data": [],
                    "message": f"未找到匹配字段: '{field_query}'。建议尝试: {suggestion_text}",
                    "total_records": 0
                }

            # 4. 提取匹配字段的数据
            filtered_data = []
            for indicator in base_result.data:
                if (hasattr(indicator, 'raw_data') and
                    indicator.raw_data and
                    matched_field in indicator.raw_data):

                    # 创建新的指标数据，只包含请求的字段
                    filtered_indicator = {
                        "symbol": indicator.symbol,
                        "market": indicator.market,
                        "report_date": indicator.report_date,
                        "period_type": indicator.period_type,
                        "raw_data": {matched_field: indicator.raw_data[matched_field]},
                        "metadata": {
                            **(getattr(indicator, 'metadata', {}) or {}),
                            "field_query": field_query,
                            "matched_field": matched_field,
                            "resolution_method": explanation
                        }
                    }
                    filtered_data.append(filtered_indicator)

            # 5. 返回查询结果
            return {
                "success": True,
                "data": filtered_data,
                "message": f"成功匹配字段: {matched_field} ({explanation})",
                "total_records": len(filtered_data)
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"字段查询失败: {str(e)}",
                "total_records": 0
            }

    async def query_by_field_name_simple(self, symbol: str, field_query: str, **kwargs) -> Any:
        """
        简化版字段查询，避免复杂的异步调用

        Args:
            symbol: 股票代码
            field_query: 字段查询
            **kwargs: 其他查询参数

        Returns:
            查询结果
        """
        try:
            # 直接获取基础数据，不进行复杂的字段映射
            base_result = self.query(symbol, **kwargs)
            if not hasattr(base_result, 'success') or not base_result.success:
                return {
                    "success": False,
                    "data": [],
                    "message": "无法获取基础财务数据",
                    "total_records": 0
                }

            # 简单的字段匹配逻辑
            matched_data = []
            for indicator in base_result.data:
                if hasattr(indicator, 'raw_data') and indicator.raw_data:
                    # 查找包含关键字的字段
                    matched_fields = {}
                    for field_name, field_value in indicator.raw_data.items():
                        if (field_query.lower() in field_name.lower() or
                            any(keyword in field_name.lower() for keyword in field_query.lower().split())):
                            matched_fields[field_name] = field_value

                    if matched_fields:
                        matched_data.append({
                            "symbol": indicator.symbol,
                            "market": indicator.market,
                            "report_date": indicator.report_date,
                            "period_type": indicator.period_type,
                            "raw_data": matched_fields,
                            "metadata": {
                                "field_query": field_query,
                                "matched_field": list(matched_fields.keys()),
                                "resolution_method": "关键字匹配"
                            }
                        })

            return {
                "success": True,
                "data": matched_data,
                "message": f"成功匹配 {len(matched_data)} 条记录",
                "total_records": len(matched_data)
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"简化查询失败: {str(e)}",
                "total_records": 0
            }

    def get_field_info(self, field_name: str) -> Dict[str, Any]:
        """
        获取字段的详细信息

        Args:
            field_name: 字段名

        Returns:
            字段信息字典
        """
        field_info = self.field_mapper.get_field_details(field_name)
        if field_info:
            return {
                'name': field_info.name,
                'keywords': field_info.keywords,
                'priority': field_info.priority,
                'description': field_info.description
            }
        return {}

    def search_fields(self, keyword: str, market: Optional[Any] = None) -> List[str]:
        """
        通过关键字搜索字段

        Args:
            keyword: 搜索关键字
            market: 市场类型（可选）

        Returns:
            匹配的字段列表
        """
        # 从新的字段映射器搜索
        market_id = None
        if market:
            # 将MarketType枚举转换为market_id字符串
            if hasattr(market, 'value'):
                market_id = market.value

        similar_fields = self.field_mapper.search_similar_fields(keyword, market_id, max_results=20)

        return [field_info.name for _, _, field_info, _ in similar_fields]