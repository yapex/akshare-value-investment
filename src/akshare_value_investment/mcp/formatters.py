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

        # 优化显示逻辑：优先显示年报数据，最多显示10条记录
        annual_records = []
        quarterly_records = []

        # 分类年报和季报数据
        for record in data:
            report_date = record.get('report_date', '')
            if '12-31' in report_date:  # 年报
                annual_records.append(record)
            else:  # 季报
                quarterly_records.append(record)

        # 优先显示年报数据
        records_to_show = annual_records[:10]  # 最多10条年报
        if len(records_to_show) < 10:  # 如果年报不足10条，补充季报
            remaining = 10 - len(records_to_show)
            records_to_show.extend(quarterly_records[:remaining])

        for record in records_to_show:
            response_parts.append(f"**报告日期**: {record.get('report_date', 'N/A')}")

            if record.get('raw_data'):
                # 显示所有匹配查询的字段，最多显示5个关键字段
                matched_fields = {}
                raw_data = record['raw_data']

                # 优先显示完全匹配查询的字段
                query_lower = query.lower()
                for field, value in raw_data.items():
                    if query_lower in field.lower():
                        matched_fields[field] = value

                # 如果匹配字段不足5个，添加其他字段
                other_fields = {k: v for k, v in raw_data.items() if k not in matched_fields}
                for field, value in list(other_fields.items())[:5 - len(matched_fields)]:
                    matched_fields[field] = value

                for field, value in matched_fields.items():
                    response_parts.append(f"**{field}**: {value}")
            response_parts.append("")

        # 如果总数据超过显示数量，添加提示
        total_records = len(data)
        shown_records = len(records_to_show)
        if total_records > shown_records:
            response_parts.append(f"*注：共{total_records}条记录，显示前{shown_records}条*")

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