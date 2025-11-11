"""
响应格式化器

负责将查询结果格式化为用户友好的文本响应。
"""

from typing import List, Dict, Any
from ...services.interfaces import IResponseFormatter


class ResponseFormatter(IResponseFormatter):
    """响应格式化器实现"""

    def format_query_response(self,
                             result: Any,
                             symbol: str,
                             mapped_fields: List[str] = None,
                             prefer_annual: bool = True,
                             include_metadata: bool = True,
                             mapping_suggestions: List[str] = None) -> str:
        """
        格式化查询响应

        Args:
            result: 查询结果
            symbol: 股票代码
            mapped_fields: 映射后的字段
            prefer_annual: 是否优先年报
            include_metadata: 是否包含元数据
            mapping_suggestions: 映射建议列表

        Returns:
            格式化的响应文本
        """
        # 检查查询是否成功
        if not hasattr(result, 'success') or not result.success:
            return self._format_error_message(result.message if hasattr(result, 'message') else "查询失败")

        # 提取数据
        if not hasattr(result, 'data') or not result.data:
            return self._format_error_message("未找到数据")

        # 处理数据结构
        indicator_data = self._extract_indicator_data(result.data)
        metadata = self._extract_metadata(result.data)

        # 生成响应文本
        response_parts = []

        # 添加头部信息
        if include_metadata:
            response_parts.extend(self._format_header(metadata, symbol))

        # 添加字段映射信息
        if mapping_suggestions:
            response_parts.extend(self._format_mapping_suggestions(mapping_suggestions))

        # 添加字段数据
        valid_fields = self._get_valid_fields(mapped_fields, indicator_data)
        response_parts.extend(self._format_fields_data(valid_fields, indicator_data, prefer_annual))

        return "\n".join(response_parts)

    def _format_error_message(self, message: str) -> str:
        """格式化错误消息"""
        return f"❌ 查询失败: {message}"

    def _format_header(self, metadata: Dict[str, Any], symbol: str) -> List[str]:
        """格式化头部信息"""
        header_parts = []
        header_parts.append(f"## {metadata.get('company_name', symbol)} ({symbol})")
        header_parts.append("")
        header_parts.append(f"**市场**: {self._format_market_type(metadata.get('market'))}")
        header_parts.append(f"**货币**: {metadata.get('currency', 'N/A')}")
        header_parts.append(f"**可用指标数**: {metadata.get('available_fields_count', 0)}")
        header_parts.append("")
        return header_parts

    def _format_mapping_suggestions(self, suggestions: List[str]) -> List[str]:
        """格式化映射建议"""
        parts = []
        parts.append("### 🧠 智能字段映射")
        parts.append("")
        for suggestion in suggestions:
            parts.append(f"• {suggestion}")
        parts.append("")
        return parts

    def _format_fields_data(self, fields: List[str], indicator_data: Dict[str, Dict[str, Any]], prefer_annual: bool) -> List[str]:
        """格式化字段数据"""
        parts = []

        if not fields:
            parts.append("### 主要财务指标")
        else:
            parts.append(f"### 请求指标 ({len(fields)}个)")

        parts.append("")

        for field in fields:
            if field in indicator_data:
                parts.append(f"**{field}**:")
                field_data = self._format_field_data(indicator_data[field], prefer_annual)
                parts.extend(field_data)
                parts.append("")

        return parts

    def _format_field_data(self, data: Dict[str, Any], prefer_annual: bool) -> List[str]:
        """格式化单个字段的数据"""
        if not data:
            return ["  - 无数据"]

        if prefer_annual:
            # 优先显示年报数据
            return self._format_annual_data(data)
        else:
            # 显示最新期数据
            return self._format_latest_data(data)

    def _format_annual_data(self, data: Dict[str, Any]) -> List[str]:
        """格式化年报数据"""
        annual_data = {}

        for key, value in data.items():
            # 检查是否为年报数据 (YYYY-MM-DD格式中包含-12-31)
            if '-12-31' in key:
                year = key[:4]
                annual_data[year] = value

        if not annual_data:
            return ["  - 无年报数据，显示最新期数据："] + self._format_latest_data(data)[:3]

        # 按年份排序，显示最近5年
        sorted_years = sorted(annual_data.keys(), reverse=True)[:5]
        return [f"  - {year}年: {annual_data[year]}" for year in sorted_years]

    def _format_latest_data(self, data: Dict[str, Any]) -> List[str]:
        """格式化最新期数据"""
        # 过滤日期格式的数据点
        data_points = [(k, v) for k, v in data.items() if '-' in k and v is not None]
        data_points.sort(key=lambda x: x[0], reverse=True)

        if not data_points:
            return ["  - 无数据"]

        result = []
        for key, value in data_points[:5]:
            year = key[:4]
            period_name = self._get_period_name(key)
            result.append(f"  - {year}年{period_name}: {value}")

        return result

    def _get_period_name(self, date_str: str) -> str:
        """根据日期字符串获取期间名称"""
        if '-12-31' in date_str:
            return "年报"
        elif '-06-30' in date_str:
            return "中报"
        elif '-09-30' in date_str:
            return "三季报"
        elif '-03-31' in date_str:
            return "一季报"
        else:
            return "其他"

    def _format_market_type(self, market) -> str:
        """格式化市场类型"""
        if hasattr(market, 'value'):
            return market.value
        return str(market)

    def _get_valid_fields(self, requested_fields: List[str], indicator_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """获取有效字段"""
        if not requested_fields:
            # 返回默认字段
            return self._get_default_fields(indicator_data)

        # 返回请求的且存在的字段
        return [field for field in requested_fields if field in indicator_data]

    def _get_default_fields(self, indicator_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """获取默认字段"""
        # 常用财务指标优先级
        priority_fields = [
            "净资产收益率(ROE)",
            "基本每股收益",
            "净利润",
            "营业总收入",
            "毛利率",
            "资产负债率"
        ]

        # 返回可用的默认字段
        available_fields = [field for field in priority_fields if field in indicator_data]

        # 如果没有默认字段，返回前几个可用字段
        if not available_fields:
            return list(indicator_data.keys())[:5]

        return available_fields

    def _extract_indicator_data(self, data: Any) -> Dict[str, Dict[str, Any]]:
        """提取指标数据"""
        if not data:
            return {}

        indicator_map = {}

        # 处理列表数据
        if hasattr(data, '__iter__'):
            for indicator in data:
                if hasattr(indicator, 'indicators') and indicator.indicators:
                    report_date = getattr(indicator, 'report_date', None)
                    if report_date:
                        date_str = report_date.strftime('%Y-%m-%d')
                        for field_name, field_value in indicator.indicators.items():
                            if field_value is not None:
                                if field_name not in indicator_map:
                                    indicator_map[field_name] = {}
                                indicator_map[field_name][date_str] = field_value

        return indicator_map

    def _extract_metadata(self, data: Any) -> Dict[str, Any]:
        """提取元数据"""
        if not data:
            return {}

        # 获取第一条记录的基本信息
        first_record = None
        if hasattr(data, '__iter__'):
            for item in data:
                if hasattr(item, 'symbol'):
                    first_record = item
                    break

        if not first_record:
            return {}

        return {
            'company_name': getattr(first_record, 'company_name', ''),
            'symbol': getattr(first_record, 'symbol', ''),
            'market': getattr(first_record, 'market', ''),
            'currency': getattr(first_record, 'currency', ''),
            'available_fields_count': len(first_record.indicators) if hasattr(first_record, 'indicators') else 0
        }