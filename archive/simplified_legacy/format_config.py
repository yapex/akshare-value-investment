"""
响应格式化配置

定义可配置的格式化规则，支持开闭原则。
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class DateDisplayFormat(Enum):
    """日期显示格式枚举"""
    YYYYMMDD = "YYYYMMDD"          # 20241231
    YYYY_MM_DD = "YYYY-MM-DD"      # 2024-12-31
    YYYY_年_MM_月_DD_日 = "YYYY年MM月DD日"  # 2024年12月31日
    REPORT_PERIOD = "REPORT_PERIOD" # 2024年年报、2024年中报


class FieldPriority(Enum):
    """字段优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FormatRule:
    """格式化规则配置"""
    field_name: str
    priority: FieldPriority
    decimal_places: int = 2
    display_name: str = None
    unit: str = None
    percentage: bool = False
    # 格式化函数名（可选，用于特殊处理）
    formatter_name: str = None


@dataclass
class PeriodDisplayRule:
    """报告期显示规则"""
    period_type: str  # "annual", "quarterly", "semi_annual"等
    display_name: str  # 显示名称
    date_patterns: List[str]  # 匹配的日期模式


@dataclass
class FormatRuleConfig:
    """格式化规则配置集合"""
    # 默认配置
    default_decimal_places: int = 2
    default_date_format: DateDisplayFormat = DateDisplayFormat.YYYY_MM_DD
    include_metadata: bool = True
    include_mapping_suggestions: bool = True

    # 字段优先级配置
    field_rules: List[FormatRule] = None
    period_display_rules: List[PeriodDisplayRule] = None

    # 显示控制
    max_fields_to_display: int = 50
    show_empty_values: bool = False

    # 特殊处理规则
    negative_value_format: str = "({value})"  # 负数显示格式
    large_number_threshold: int = 100000000  # 大数字阈值（1亿）
    large_number_unit: str = "亿"  # 大数字单位

    def __post_init__(self):
        """初始化后处理"""
        if self.field_rules is None:
            self.field_rules = self._get_default_field_rules()

        if self.period_display_rules is None:
            self.period_display_rules = self._get_default_period_rules()

    def _get_default_field_rules(self) -> List[FormatRule]:
        """获取默认字段规则"""
        return [
            # 高优先级财务指标
            FormatRule("净资产收益率(ROE)", FieldPriority.HIGH, percentage=True),
            FormatRule("基本每股收益", FieldPriority.HIGH, decimal_places=2, unit="元"),
            FormatRule("净利润", FieldPriority.HIGH, decimal_places=0),
            FormatRule("营业总收入", FieldPriority.HIGH, decimal_places=0),
            FormatRule("毛利率", FieldPriority.HIGH, percentage=True),
            FormatRule("资产负债率", FieldPriority.HIGH, percentage=True),

            # 中等优先级指标
            FormatRule("净利润增长率", FieldPriority.MEDIUM, percentage=True),
            FormatRule("营业收入增长率", FieldPriority.MEDIUM, percentage=True),
            FormatRule("总资产", FieldPriority.MEDIUM, decimal_places=0),
            FormatRule("净资产", FieldPriority.MEDIUM, decimal_places=0),

            # 低优先级指标
            FormatRule("流动比率", FieldPriority.LOW, decimal_places=2),
            FormatRule("速动比率", FieldPriority.LOW, decimal_places=2),
            FormatRule("应收账款周转率", FieldPriority.LOW, decimal_places=2),
        ]

    def _get_default_period_rules(self) -> List[PeriodDisplayRule]:
        """获取默认报告期显示规则"""
        return [
            PeriodDisplayRule("annual", "年报", ["-12-31"]),
            PeriodDisplayRule("semi_annual", "中报", ["-06-30"]),
            PeriodDisplayRule("quarterly1", "一季报", ["-03-31"]),
            PeriodDisplayRule("quarterly2", "二季报", ["-06-30"]),
            PeriodDisplayRule("quarterly3", "三季报", ["-09-30"]),
            PeriodDisplayRule("quarterly4", "四季报", ["-12-31"]),
        ]

    def get_priority_fields(self, max_count: int = None) -> List[str]:
        """获取按优先级排序的字段列表"""
        if max_count is None:
            max_count = self.max_fields_to_display

        # 按优先级排序
        priority_order = {FieldPriority.HIGH: 1, FieldPriority.MEDIUM: 2, FieldPriority.LOW: 3}

        sorted_rules = sorted(
            self.field_rules,
            key=lambda rule: priority_order.get(rule.priority, 4)
        )

        return [rule.field_name for rule in sorted_rules[:max_count]]

    def find_rule_by_field_name(self, field_name: str) -> FormatRule:
        """根据字段名查找格式化规则"""
        for rule in self.field_rules:
            if rule.field_name == field_name:
                return rule

        # 如果没有找到规则，返回默认规则
        return FormatRule(field_name, FieldPriority.LOW)

    def get_period_display_name(self, date_str: str, period_type: str = None) -> str:
        """获取报告期显示名称"""
        if period_type:
            # 根据期间类型查找
            for rule in self.period_display_rules:
                if rule.period_type == period_type:
                    return rule.display_name

        # 根据日期模式查找
        for rule in self.period_display_rules:
            for pattern in rule.date_patterns:
                if pattern in date_str:
                    return rule.display_name

        # 默认显示格式
        if self.default_date_format == DateDisplayFormat.YYYY_MM_DD:
            return date_str[:4] + "年" + date_str[4:6] + "月" + date_str[6:8] + "日"
        elif self.default_date_format == DateDisplayFormat.YYYY年MM月DD日:
            return date_str[:4] + "年" + date_str[4:6] + "月" + date_str[6:8] + "日"
        else:
            return date_str


def create_default_config() -> FormatRuleConfig:
    """创建默认配置"""
    return FormatRuleConfig()


def create_chinese_finance_config() -> FormatRuleConfig:
    """创建中文财务格式化配置"""
    config = FormatRuleConfig(
        default_decimal_places=2,
        default_date_format=DateDisplayFormat.YYYY_年_MM_月_DD_日,
        large_number_threshold=100000000,  # 1亿
        large_number_unit="亿"
    )

    # 添加中文显示名称
    for rule in config.field_rules:
        if rule.display_name is None:
            rule.display_name = rule.field_name  # 可以进一步优化为更友好的名称

    return config


def create_international_finance_config() -> FormatRuleConfig:
    """创建国际化财务格式化配置"""
    config = FormatRuleConfig(
        default_decimal_places=2,
        default_date_format=DateDisplayFormat.YYYY_MM_DD,
        large_number_threshold=1000000,  # 1百万
        large_number_unit="M"
    )

    return config