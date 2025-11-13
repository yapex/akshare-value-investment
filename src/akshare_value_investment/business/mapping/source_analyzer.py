"""
字段来源类型分析器

实现ISourceAnalyzer接口，专门负责推断字段的来源类型（财务指标 vs 财务三表）
"""

import re
from typing import Dict, Any, List

from .namespaced_interfaces import ISourceAnalyzer


class FieldSourceAnalyzer(ISourceAnalyzer):
    """字段来源类型分析器"""

    def __init__(self):
        # 财务指标识别模式
        self.indicators_patterns = [
            r'.*_RATIO$',           # 各种比率
            r'.*_RATE$',            # 各种率
            r'.*_MARGIN$',          # 各种边际率
            r'.*_TURNOVER$',        # 各种周转率
            r'^ROE$',               # 净资产收益率
            r'^ROA$',               # 总资产收益率
            r'^PE_RATIO$',          # 市盈率
            r'^PB_RATIO$',          # 市净率
            r'^DIVIDEND_.*$',       # 股息相关
            r'^EARNING_.*_RATIO$',  # 收益率相关
            r'^.*_PER_SHARE$',      # 每股相关
        ]

        # 财务三表识别模式
        self.statements_patterns = [
            r'^TOTAL_',             # 总计字段
            r'^NET_',               # 净额字段
            r'^GROSS_',             # 总额字段
            r'^OPERATING_',         # 营业相关
            r'^CURRENT_',           # 流动性字段
            r'^NON_CURRENT_',       # 非流动性字段
            r'^CASH_.*_FLOW$',      # 现金流量
            r'^.*_ASSETS$',         # 资产类字段
            r'^.*_LIABILITIES$',    # 负债类字段
            r'^.*_EQUITY$',         # 权益类字段
            r'^.*_EXPENSES$',       # 费用类字段
            r'^.*_INCOME$',         # 收入类字段
            r'^.*_REVENUE$',        # 营收类字段
            r'^.*_PROFIT$',         # 利润类字段
            r'^.*_COST$',           # 成本类字段
        ]

    def infer_source_type(self, field_id: str, context: Dict[str, Any]) -> str:
        """
        推断字段来源类型

        Args:
            field_id: 字段ID
            context: 上下文信息（包含配置文件路径、市场信息等）

        Returns:
            str: 来源类型 ('financial_indicators', 'financial_statements', 'unknown')
        """
        # 策略1: 从配置文件路径推断
        if 'config_path' in context:
            config_path = str(context['config_path']).lower()
            if 'financial_indicators' in config_path:
                return 'financial_indicators'
            elif 'financial_statements' in config_path:
                return 'financial_statements'

        # 策略2: 从字段ID模式推断
        if self._matches_pattern(field_id, self.indicators_patterns):
            return 'financial_indicators'
        elif self._matches_pattern(field_id, self.statements_patterns):
            return 'financial_statements'

        # 策略3: 从市场配置上下文推断
        if 'market_config' in context:
            market_config = context['market_config']
            source_type = self._infer_from_market_config(field_id, market_config)
            if source_type != 'unknown':
                return source_type

        # 策略4: 从字段名推断（如果可用）
        if 'field_name' in context:
            field_name = context['field_name']
            source_type = self._infer_from_field_name(field_name)
            if source_type != 'unknown':
                return source_type

        # 默认返回unknown
        return 'unknown'

    def _matches_pattern(self, field_id: str, patterns: List[str]) -> bool:
        """检查字段ID是否匹配给定的模式列表"""
        field_id_upper = field_id.upper()
        for pattern in patterns:
            if re.match(pattern, field_id_upper):
                return True
        return False

    def _infer_from_market_config(self, field_id: str, market_config: Dict[str, Any]) -> str:
        """从市场配置推断字段来源类型"""
        # 这里可以根据市场的特定规则进行推断
        # 例如，某些市场可能有特定的字段命名约定

        # 检查是否在财务指标字段列表中
        if 'indicators_fields' in market_config and field_id in market_config['indicators_fields']:
            return 'financial_indicators'

        # 检查是否在财务三表字段列表中
        if 'statements_fields' in market_config and field_id in market_config['statements_fields']:
            return 'financial_statements'

        return 'unknown'

    def _infer_from_field_name(self, field_name: str) -> str:
        """从字段名推断来源类型"""
        field_name_lower = field_name.lower()

        # 财务指标关键词
        indicators_keywords = [
            '率', '比', '比率', '收益率', '周转率', '毛利率',
            'roe', 'roa', 'pe', 'pb', 'eps', 'dividend'
        ]

        # 财务三表关键词
        statements_keywords = [
            '总额', '净额', '资产', '负债', '权益', '收入',
            '成本', '费用', '利润', '现金流', '存货',
            'assets', 'liabilities', 'equity', 'revenue', 'profit'
        ]

        if any(keyword in field_name_lower for keyword in indicators_keywords):
            return 'financial_indicators'
        elif any(keyword in field_name_lower for keyword in statements_keywords):
            return 'financial_statements'

        return 'unknown'

    def get_confidence_score(self, field_id: str, context: Dict[str, Any]) -> float:
        """
        获取推断的置信度得分

        Args:
            field_id: 字段ID
            context: 上下文信息

        Returns:
            float: 置信度得分 (0-1)
        """
        # 从文件路径推断的置信度最高
        if 'config_path' in context:
            config_path = str(context['config_path']).lower()
            if 'financial_indicators' in config_path or 'financial_statements' in config_path:
                return 0.9

        # 从字段ID模式推断的置信度较高
        if self._matches_pattern(field_id, self.indicators_patterns):
            return 0.8
        elif self._matches_pattern(field_id, self.statements_patterns):
            return 0.8

        # 从其他方式推断的置信度较低
        return 0.5

    def add_custom_pattern(self, source_type: str, pattern: str) -> None:
        """
        添加自定义模式

        Args:
            source_type: 来源类型
            pattern: 正则表达式模式
        """
        if source_type == 'financial_indicators':
            self.indicators_patterns.append(pattern)
        elif source_type == 'financial_statements':
            self.statements_patterns.append(pattern)

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """获取模式统计信息"""
        return {
            'indicators_patterns_count': len(self.indicators_patterns),
            'statements_patterns_count': len(self.statements_patterns),
            'indicators_patterns': self.indicators_patterns.copy(),
            'statements_patterns': self.statements_patterns.copy()
        }