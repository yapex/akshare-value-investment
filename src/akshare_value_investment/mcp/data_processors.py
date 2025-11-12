"""
MCP数据处理器

专门处理数据分类、过滤和业务逻辑，遵循单一职责原则。
"""

from typing import List, Dict, Any, Tuple, Protocol
from dataclasses import dataclass


@dataclass
class DataProcessingResult:
    """数据处理结果"""
    annual_records: List[Dict[str, Any]]
    quarterly_records: List[Dict[str, Any]]
    total_records: int
    has_annual_data: bool


class IQueryDataProcessor(Protocol):
    """查询数据处理器接口"""

    def classify_records(self, data: List[Dict[str, Any]]) -> DataProcessingResult:
        """
        分类记录数据

        Args:
            data: 原始数据记录

        Returns:
            分类后的处理结果
        """
        ...

    def get_recommended_records(self,
                                data: List[Dict[str, Any]],
                                prefer_annual: bool = True) -> List[Dict[str, Any]]:
        """
        获取推荐的显示记录

        Args:
            data: 原始数据记录
            prefer_annual: 是否优先年报

        Returns:
            推荐的记录列表
        """
        ...


class IFieldMatcher(Protocol):
    """字段匹配器接口"""

    def find_relevant_fields(self,
                            query: str,
                            raw_data: Dict[str, Any],
                            max_fields: int = 5) -> Dict[str, Any]:
        """
        查找与查询相关的字段

        Args:
            query: 查询内容
            raw_data: 原始字段数据
            max_fields: 最大字段数量

        Returns:
            相关的字段映射
        """
        ...


class QueryDataProcessor:
    """查询数据处理器实现"""

    def classify_records(self, data: List[Dict[str, Any]]) -> DataProcessingResult:
        """
        分类年报和季报记录

        Args:
            data: 原始数据记录

        Returns:
            分类后的处理结果
        """
        annual_records = []
        quarterly_records = []

        for record in data:
            # 支持多种日期格式
            report_date = record.get('report_date', '')

            # 检查是否有 period_type 字段
            period_type = record.get('period_type')
            if period_type:
                # 如果有明确的期间类型，直接使用
                if hasattr(period_type, 'value'):
                    # 枚举类型
                    if period_type.value == 'annual':
                        annual_records.append(record)
                    else:
                        quarterly_records.append(record)
                elif isinstance(period_type, str):
                    # 字符串类型
                    if 'annual' in period_type.lower():
                        annual_records.append(record)
                    else:
                        quarterly_records.append(record)
                else:
                    # 其他情况，按日期判断
                    quarterly_records.append(record)
            else:
                # 没有 period_type，按日期格式判断
                if isinstance(report_date, str):
                    # 字符串日期，检查格式
                    if '12-31' in report_date or report_date.endswith('1231'):
                        annual_records.append(record)
                    else:
                        quarterly_records.append(record)
                elif hasattr(report_date, 'month'):
                    # datetime 对象，检查月份
                    if report_date.month == 12 and report_date.day == 31:
                        annual_records.append(record)
                    else:
                        quarterly_records.append(record)
                else:
                    # 其他情况，默认为季报
                    quarterly_records.append(record)

        return DataProcessingResult(
            annual_records=annual_records,
            quarterly_records=quarterly_records,
            total_records=len(data),
            has_annual_data=len(annual_records) > 0
        )

    def get_recommended_records(self,
                                data: List[Dict[str, Any]],
                                prefer_annual: bool = True) -> List[Dict[str, Any]]:
        """
        获取推荐的显示记录

        Args:
            data: 原始数据记录
            prefer_annual: 是否优先年报

        Returns:
            推荐的记录列表
        """
        result = self.classify_records(data)

        if prefer_annual and result.has_annual_data:
            return result.annual_records
        elif result.has_annual_data:
            return result.annual_records
        else:
            return result.quarterly_records


class FieldMatcher:
    """字段匹配器实现"""

    def find_relevant_fields(self,
                            query: str,
                            raw_data: Dict[str, Any],
                            max_fields: int = 5) -> Dict[str, Any]:
        """
        查找与查询相关的字段

        Args:
            query: 查询内容
            raw_data: 原始字段数据
            max_fields: 最大字段数量

        Returns:
            相关的字段映射
        """
        if not raw_data:
            return {}

        matched_fields = {}
        query_lower = query.lower()

        # 1. 精确匹配
        for field, value in raw_data.items():
            if query_lower in field.lower():
                matched_fields[field] = value

        # 2. 如果精确匹配不足，添加其他字段
        if len(matched_fields) < max_fields:
            other_fields = {k: v for k, v in raw_data.items() if k not in matched_fields}
            additional_needed = max_fields - len(matched_fields)

            for field, value in list(other_fields.items())[:additional_needed]:
                matched_fields[field] = value

        return matched_fields


class SmartQueryDataProcessor:
    """智能查询数据处理器 - 组合多个处理器"""

    def __init__(self,
                 data_processor: IQueryDataProcessor = None,
                 field_matcher: IFieldMatcher = None):
        """
        初始化智能数据处理器

        Args:
            data_processor: 数据处理器
            field_matcher: 字段匹配器
        """
        self.data_processor = data_processor or QueryDataProcessor()
        self.field_matcher = field_matcher or FieldMatcher()

    def get_optimized_records(self,
                             data: List[Dict[str, Any]],
                             query: str,
                             prefer_annual: bool = True) -> List[Dict[str, Any]]:
        """
        获取优化后的记录列表

        Args:
            data: 原始数据
            query: 查询内容
            prefer_annual: 是否优先年报

        Returns:
            优化后的记录列表
        """
        # 获取推荐的记录
        records = self.data_processor.get_recommended_records(data, prefer_annual)

        # 为每条记录添加相关字段信息
        for record in records:
            if record.get('raw_data'):
                matched_fields = self.field_matcher.find_relevant_fields(
                    query, record['raw_data'], max_fields=5
                )
                record['_matched_fields'] = matched_fields

        return records