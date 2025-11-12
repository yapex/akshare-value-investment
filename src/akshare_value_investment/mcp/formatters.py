"""
MCP响应格式化器

统一处理所有MCP工具的响应格式化，确保输出一致性和可读性。
"""

from typing import List, Dict, Any


class ResponseFormatter:
    """MCP响应格式化器"""

    def format_query_response(self,
                            symbol: str,
                            query: str,
                            data: List[Dict[str, Any]],
                            message: str = None) -> str:
        """
        格式化财务指标查询响应

        Args:
            symbol: 股票代码
            query: 查询内容
            data: 查询结果数据
            message: 消息

        Returns:
            格式化的响应文本
        """
        if not data:
            return f"❌ 未找到匹配 '{query}' 的财务数据"

        response_parts = [
            f"## 📊 {symbol} 财务数据查询结果",
            f"",
            f"**查询**: {query}",
            f"**记录数**: {len(data)} 条",
            f""
        ]

        for record in data[:5]:  # 只显示前5条
            response_parts.append(f"**报告日期**: {record.get('report_date', 'N/A')}")

            if record.get('raw_data'):
                for field, value in list(record['raw_data'].items())[:3]:  # 只显示前3个字段
                    response_parts.append(f"**{field}**: {value}")
            response_parts.append("")

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