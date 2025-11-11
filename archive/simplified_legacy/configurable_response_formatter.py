"""
可配置的响应格式化器

遵循开闭原则，支持通过配置自定义格式化行为。
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal

from .services.interfaces import IResponseFormatter
from .format_config import FormatRuleConfig, create_default_config, FieldPriority
from .models import MarketType


class ConfigurableResponseFormatter(IResponseFormatter):
    """可配置的响应格式化器"""

    def __init__(self, config: FormatRuleConfig = None):
        """
        初始化可配置格式化器

        Args:
            config: 格式化配置，如果不提供则使用默认配置
        """
        self.config = config or create_default_config()

    def update_config(self, config: FormatRuleConfig):
        """
        更新格式化配置

        Args:
            config: 新的格式化配置
        """
        self.config = config

    def format_query_response(self,
                             result: Any,
                             symbol: str,
                             mapped_fields: List[str] = None,
                             prefer_annual: bool = True,
                             include_metadata: bool = True,
                             mapping_suggestions: List[str] = None) -> str:
        """
        格式化查询响应 - 可配置版本

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
        if include_metadata and self.config.include_metadata:
            response_parts.extend(self._format_header(metadata, symbol))

        # 添加字段映射信息
        if mapping_suggestions and self.config.include_mapping_suggestions:
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

        # 使用配置化的市场类型格式化
        market = metadata.get('market')
        if market:
            header_parts.append(f"**市场**: {self._format_market_type(market)}")
        else:
            header_parts.append(f"**市场**: {symbol}")

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
        """格式化字段数据 - 可配置版本"""
        parts = []

        if not fields:
            # 使用配置的字段优先级
            priority_fields = self._get_priority_fields(indicator_data)
            parts.append(f"### 主要财务指标")
        else:
            parts.append(f"### 请求指标 ({len(fields)}个)")
            priority_fields = fields

        parts.append("")

        # 按配置的优先级排序字段
        sorted_fields = self._sort_fields_by_priority(priority_fields)

        for field in sorted_fields:
            if field in indicator_data:
                field_data = indicator_data[field]
                parts.extend(self._format_single_field(field, field_data, prefer_annual))

        return parts

    def _format_single_field(self, field_name: str, field_data: Dict[str, Any], prefer_annual: bool) -> List[str]:
        """格式化单个字段 - 可配置版本"""
        # 获取字段的格式化规则
        rule = self.config.find_rule_by_field_name(field_name)

        parts = []
        display_name = rule.display_name or field_name
        parts.append(f"**{display_name}**:")

        if prefer_annual:
            parts.extend(self._format_annual_data(field_data, rule))
        else:
            parts.extend(self._format_latest_data(field_data, rule))

        return parts

    def _format_annual_data(self, data: Dict[str, Any], rule) -> List[str]:
        """格式化年报数据 - 可配置版本"""
        annual_data = {}
        current_year = None

        # 识别年报数据
        for key, value in data.items():
            if '-12-31' in key:  # 年报数据
                year = key[:4]
                if current_year is None:
                    current_year = year
                annual_data[year] = value

        if not annual_data:
            # 如果没有年报数据，显示最新期数据
            return self._format_latest_data(data, rule)

        # 排序年份，最新的在前
        sorted_years = sorted(annual_data.keys(), reverse=True)

        formatted_parts = []
        for year in sorted_years[:5]:  # 最多显示5年
            value = annual_data[year]
            formatted_value = self._format_numeric_value(value, rule)

            # 使用配置的日期格式
            period_name = self.config.get_period_display_name(f"{year}1231", "annual")
            formatted_parts.append(f"  - {year}年: {formatted_value}")

        return formatted_parts

    def _format_latest_data(self, data: Dict[str, Any], rule) -> List[str]:
        """格式化最新期数据 - 可配置版本"""
        if not data:
            return ["  - 无数据"]

        # 按日期排序，取最新的5期
        sorted_dates = sorted(data.keys(), reverse=True)[:5]

        formatted_parts = []
        for date_str in sorted_dates:
            value = data[date_str]
            formatted_value = self._format_numeric_value(value, rule)

            # 使用配置的期间显示
            period_name = self.config.get_period_display_name(date_str)
            formatted_parts.append(f"  - {period_name}: {formatted_value}")

        return formatted_parts

    def _format_numeric_value(self, value: Any, rule) -> str:
        """
        格式化数值 - 可配置版本

        Args:
            value: 原始值
            rule: 格式化规则

        Returns:
            格式化后的字符串
        """
        if value is None:
            return "N/A"

        try:
            # 转换为Decimal进行精确计算
            decimal_value = Decimal(str(value))

            # 应用负数格式
            if decimal_value < 0:
                abs_value = abs(decimal_value)
                formatted_value = self._apply_decimal_format(abs_value, rule)
                return self.config.negative_value_format.format(value=formatted_value)
            else:
                return self._apply_decimal_format(decimal_value, rule)

        except (ValueError, TypeError):
            return str(value)

    def _apply_decimal_format(self, value: Decimal, rule) -> str:
        """应用小数位格式化"""
        # 处理大数字简化显示
        if abs(value) >= self.config.large_number_threshold:
            divided_value = value / Decimal(str(self.config.large_number_threshold))
            formatted = f"{divided_value:.{rule.decimal_places}f}"
            return f"{formatted}{self.config.large_number_unit}"
        else:
            # 应用百分比格式
            if rule.percentage:
                percentage_value = value * 100
                formatted = f"{percentage_value:.{rule.decimal_places}f}"
                return f"{formatted}%"
            else:
                formatted = f"{value:.{rule.decimal_places}f}"

                # 添加单位
                if rule.unit:
                    return f"{formatted}{rule.unit}"
                return formatted

    def _get_priority_fields(self, indicator_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """获取优先级字段 - 使用配置"""
        priority_fields = self.config.get_priority_fields()

        # 过滤出实际存在的字段
        available_fields = [field for field in priority_fields if field in indicator_data]

        # 如果没有优先级字段，返回前几个可用字段
        if not available_fields:
            return list(indicator_data.keys())[:5]

        return available_fields

    def _sort_fields_by_priority(self, fields: List[str]) -> List[str]:
        """按优先级排序字段"""
        # 获取字段的优先级权重
        priority_weights = {FieldPriority.HIGH: 1, FieldPriority.MEDIUM: 2, FieldPriority.LOW: 3}

        def get_field_priority(field_name):
            rule = self.config.find_rule_by_field_name(field_name)
            return priority_weights.get(rule.priority, 4)

        return sorted(fields, key=get_field_priority)

    def _format_market_type(self, market) -> str:
        """格式化市场类型"""
        if hasattr(market, 'value'):
            return market.value
        return str(market)

    def _get_valid_fields(self, requested_fields: List[str], indicator_data: Dict[str, Dict[str, Any]]) -> List[str]:
        """获取有效字段"""
        if not requested_fields:
            return self._get_priority_fields(indicator_data)

        return [field for field in requested_fields if field in indicator_data]

    def _extract_indicator_data(self, data: Any) -> Dict[str, Dict[str, Any]]:
        """提取指标数据"""
        if not data:
            return {}

        indicator_map = {}

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