"""
MCP响应格式化器

只负责格式化输出，遵循单一职责原则。
业务逻辑委托给专门的数据处理器。
"""

from typing import List, Dict, Any
from .interfaces import IMCPResponseFormatter
from .data_processors import SmartQueryDataProcessor


class ResponseFormatter(IMCPResponseFormatter):
    """MCP响应格式化器 - 只负责格式化"""

    def __init__(self, data_processor: SmartQueryDataProcessor = None):
        """
        初始化格式化器

        Args:
            data_processor: 数据处理器（可选）
        """
        self.data_processor = data_processor or SmartQueryDataProcessor()

    def format_query_response(self,
                            symbol: str,
                            query: str,
                            data: List[Dict[str, Any]],
                            message: str = None,
                            prefer_annual: bool = True) -> str:
        """
        格式化财务指标查询响应

        Args:
            symbol: 股票代码
            query: 查询内容
            data: 查询结果数据
            message: 消息
            prefer_annual: 是否优先年报数据

        Returns:
            格式化的响应文本
        """
        if not data:
            return f"❌ 未找到匹配 '{query}' 的财务数据"

        # 委托给数据处理器进行业务逻辑处理
        processed_records = self.data_processor.get_optimized_records(
            data, query, prefer_annual=prefer_annual
        )

        # 格式化器只负责输出格式化
        return self._format_records(symbol, query, processed_records, data)

    def _format_records(self,
                       symbol: str,
                       query: str,
                       records: List[Dict[str, Any]],
                       original_data: List[Dict[str, Any]]) -> str:
        """
        格式化记录为Markdown文本

        Args:
            symbol: 股票代码
            query: 查询内容
            records: 处理后的记录
            original_data: 原始数据

        Returns:
            格式化的Markdown文本
        """
        response_parts = [
            f"## 📊 {symbol} 财务数据查询结果",
            f"",
            f"**查询**: {query}",
            f"**记录数**: {len(original_data)} 条",
            f""
        ]

        for record in records:
            response_parts.append(f"**报告日期**: {record.get('report_date', 'N/A')}")

            # 显示处理器预先匹配的字段
            if '_matched_fields' in record:
                for field, value in record['_matched_fields'].items():
                    response_parts.append(f"**{field}**: {value}")
            elif record.get('raw_data'):
                # 兼容性处理：如果没有预先匹配的字段
                raw_data = record['raw_data']
                # 简单显示前几个字段
                for field, value in list(raw_data.items())[:3]:
                    response_parts.append(f"**{field}**: {value}")
            response_parts.append("")

        # 添加记录数量提示
        if len(records) < len(original_data):
            response_parts.append(f"*注：共{len(original_data)}条记录，显示{len(records)}条相关记录*")

        return "\n".join(response_parts)

    def format_search_response(self,
                             keyword: str,
                             market: str,
                             fields: List[str]) -> str:
        """
        格式化字段搜索响应

        Args:
            keyword: 搜索关键字
            market: 市场类型
            fields: 搜索结果字段

        Returns:
            格式化的响应文本
        """
        if not fields:
            return f"❌ 未找到与 '{keyword}' 相关的财务指标字段"

        response_parts = [
            f"## 🔎 财务指标搜索结果",
            f"**关键字**: {keyword}",
            f"**市场**: {market}",
            f"**找到**: {len(fields)} 个相关字段",
            f""
        ]

        for i, field in enumerate(fields[:10], 1):  # 只显示前10个
            response_parts.append(f"{i}. {field}")

        if len(fields) > 10:
            response_parts.append(f"... 还有 {len(fields) - 10} 个字段")

        return "\n".join(response_parts)

    def format_field_details_response(self,
                                    field_name: str,
                                    field_info: Dict[str, Any]) -> str:
        """
        格式化字段详情响应

        Args:
            field_name: 字段名
            field_info: 字段信息

        Returns:
            格式化的响应文本
        """
        response_parts = [
            f"## 📋 财务指标详细信息",
            f"**字段名**: {field_name}",
            f""
        ]

        if field_info:
            keywords = field_info.get("keywords", [])
            priority = field_info.get("priority", 1)
            description = field_info.get("description", "无描述")

            response_parts.extend([
                f"**描述**: {description}",
                f"**优先级**: {priority}",
                f"**关键字数量**: {len(keywords)}",
                f"**关键字**: {', '.join(keywords[:10])}",
                ""
            ])

            if len(keywords) > 10:
                response_parts.append(f"... 还有 {len(keywords) - 10} 个关键字")
        else:
            response_parts.append("❌ 未找到该字段的详细信息")

        return "\n".join(response_parts)

    def format_simple_message(self, message: str) -> str:
        """
        格式化简单消息

        Args:
            message: 消息内容

        Returns:
            格式化的消息
        """
        return f"ℹ️ {message}"