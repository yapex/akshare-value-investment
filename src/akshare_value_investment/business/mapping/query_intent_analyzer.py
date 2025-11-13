"""
查询意图分析器

基于SOLID原则的组件拆分实现
专门负责用户查询意图的分析和识别
"""

import re
import time
from typing import List, Dict, Any
from dataclasses import dataclass

from .field_router_models import QueryIntent, QueryContext


@dataclass
class IntentPatternConfig:
    """意图分析配置"""
    indicators_patterns: List[str]
    statements_patterns: List[str]
    specific_indicators: List[str]
    specific_statements: List[str]
    ambiguous_queries: List[str]
    priority_weights: Dict[str, float]


class DefaultIntentPatternConfig(IntentPatternConfig):
    """默认意图分析配置"""

    def __init__(self):
        # 英文财务指标模式
        self.indicators_patterns = [
            r'.*_RATIO$',           # 各种比率
            r'.*_RATE$',            # 各种率
            r'.*_MARGIN$',          # 各种边际率
            r'^ROE$',               # 净资产收益率
            r'^ROA$',               # 总资产收益率
            r'^PE_RATIO$',          # 市盈率
            r'^PB_RATIO$',          # 市净率
            r'^DIVIDEND_.*$',       # 股息相关
            r'^.*_PER_SHARE$',      # 每股相关
        ]

        # 英文财务三表模式
        self.statements_patterns = [
            r'^TOTAL_',             # 总计字段
            r'^NET_',               # 净额字段
            r'^GROSS_',             # 总额字段
            r'^OPERATING_',         # 营业相关
            r'^CURRENT_',           # 流动性字段
            r'^.*_ASSETS$',         # 资产类字段
            r'^.*_LIABILITIES$',    # 负债类字段
            r'^.*_REVENUE$',        # 营收类字段
            r'^.*_PROFIT$',         # 利润类字段
            r'^.*_COST$',           # 成本类字段
            r'^.*_INCOME$',         # 收入类字段
        ]

        # 中文财务指标模式（高优先级）
        self.specific_indicators = [
            '净利润率', '毛利率', '净利率', '市盈率', '市净率', '每股收益',
            'ROE', 'ROA', 'EPS', 'PE', 'PB', 'ROI'
        ]

        # 中文财务三表模式（高优先级）
        self.specific_statements = [
            '净利润', '毛利润', '营业收入', '总收入', '营业成本',
            '总资产', '总负债', '所有者权益', '股东权益'
        ]

        # 预定义模糊查询
        self.ambiguous_queries = ['收入', '利润', '收益', '成本']

        # 优先级权重
        self.priority_weights = {
            'specific_match': 3.0,
            'pattern_match': 2.0,
            'keyword_match': 1.0,
            'rate_keyword_bonus': 2.0
        }


class QueryIntentAnalyzer:
    """查询意图分析器

    职责单一：专门负责分析用户查询意图
    可扩展：支持自定义模式和配置
    可测试：独立组件，易于单元测试
    """

    def __init__(self, config: IntentPatternConfig = None):
        """
        初始化查询意图分析器

        Args:
            config: 意图分析配置，如果为None则使用默认配置
        """
        self._config = config or DefaultIntentPatternConfig()
        self._analysis_history: List[Dict[str, Any]] = []

    def analyze_intent(self, query: str) -> QueryIntent:
        """
        分析查询意图

        Args:
            query: 用户查询

        Returns:
            QueryIntent: 查询意图
        """
        # 记录分析历史
        analysis_start_time = time.time()

        # 执行意图分析
        result = self._perform_intent_analysis(query)

        # 记录分析历史
        self._record_analysis(query, result, time.time() - analysis_start_time)

        return result

    def _perform_intent_analysis(self, query: str) -> QueryIntent:
        """
        执行实际的意图分析

        Args:
            query: 用户查询

        Returns:
            QueryIntent: 查询意图
        """
        query_lower = query.lower()

        # 1. 检查是否为预定义的模糊查询
        if self._is_ambiguous_query(query):
            return QueryIntent.AMBIGUOUS

        # 2. 检查具体财务指标模式（高优先级）
        indicators_score = self._check_specific_indicators(query)
        if indicators_score > 0:
            return QueryIntent.FINANCIAL_INDICATORS

        # 3. 检查具体财务三表模式（高优先级）
        statements_score = self._check_specific_statements(query)
        if statements_score > 0:
            return QueryIntent.FINANCIAL_STATEMENTS

        # 4. 模式匹配分析
        pattern_indicators_score = self._calculate_pattern_score(
            query_lower, self._config.indicators_patterns
        )
        pattern_statements_score = self._calculate_pattern_score(
            query_lower, self._config.statements_patterns
        )

        # 5. 中文关键字分析
        chinese_scores = self._calculate_chinese_scores(query)

        # 6. 综合评分
        total_indicators_score = pattern_indicators_score + chinese_scores['indicators']
        total_statements_score = pattern_statements_score + chinese_scores['statements']

        # 7. 意图决策
        return self._make_intent_decision(
            total_indicators_score,
            total_statements_score,
            query
        )

    def _is_ambiguous_query(self, query: str) -> bool:
        """检查是否为模糊查询"""
        return (query in self._config.ambiguous_queries and
                len(query) <= 2 and
                not any(pattern in query for pattern in self._config.specific_indicators + self._config.specific_statements))

    def _check_specific_indicators(self, query: str) -> float:
        """检查具体财务指标模式"""
        for pattern in self._config.specific_indicators:
            if pattern in query:
                return self._config.priority_weights['specific_match']
        return 0.0

    def _check_specific_statements(self, query: str) -> float:
        """检查具体财务三表模式"""
        for pattern in self._config.specific_statements:
            if pattern in query:
                return self._config.priority_weights['specific_match']
        return 0.0

    def _calculate_pattern_score(self, query: str, patterns: List[str]) -> float:
        """计算模式匹配得分"""
        score = 0.0
        for pattern in patterns:
            matches = len(re.findall(pattern, query, re.IGNORECASE))
            if matches > 0:
                score += matches * self._config.priority_weights['pattern_match']
        return score

    def _calculate_chinese_scores(self, query: str) -> Dict[str, float]:
        """计算中文关键字得分"""
        indicators_keywords = ['率', '比', '比率', '收益率', '周转率', '利润率', '毛利率', '净利率', '每股收益']
        statements_keywords = ['总额', '净额', '资产', '负债', '收入', '利润', '成本', '营业收入', '总收入']

        indicators_score = 0.0
        statements_score = 0.0

        # 检查财务指标关键字
        for keyword in indicators_keywords:
            if keyword in query:
                weight = 2.0 if keyword in ['净利润率', '毛利率', '每股收益'] else 1.0
                indicators_score += weight

        # 检查财务三表关键字
        for keyword in statements_keywords:
            if keyword in query:
                weight = 2.0 if keyword in ['净利润', '毛利润', '营业收入', '总收入'] else 1.0
                statements_score += weight

        return {
            'indicators': indicators_score,
            'statements': statements_score
        }

    def _make_intent_decision(self, indicators_score: float,
                            statements_score: float, query: str) -> QueryIntent:
        """
        基于得分做出意图决策

        Args:
            indicators_score: 财务指标得分
            statements_score: 财务三表得分
            query: 原始查询

        Returns:
            QueryIntent: 查询意图
        """
        if indicators_score > statements_score and indicators_score > 0:
            return QueryIntent.FINANCIAL_INDICATORS
        elif statements_score > indicators_score and statements_score > 0:
            return QueryIntent.FINANCIAL_STATEMENTS
        elif indicators_score == statements_score and indicators_score > 0:
            # 平局情况下的决策逻辑
            if '率' in query or 'ratio' in query.lower() or 'rate' in query.lower():
                return QueryIntent.FINANCIAL_INDICATORS
            elif len(query) <= 2 and query in self._config.ambiguous_queries:
                return QueryIntent.AMBIGUOUS
            else:
                return QueryIntent.FINANCIAL_STATEMENTS
        else:
            return QueryIntent.AMBIGUOUS

    def _record_analysis(self, query: str, result: QueryIntent,
                         processing_time: float) -> None:
        """记录分析历史"""
        analysis_record = {
            'timestamp': time.time(),
            'query': query,
            'result_intent': result.value,
            'processing_time_ms': processing_time * 1000,
            'config_type': 'default'
        }

        self._analysis_history.append(analysis_record)

        # 限制历史记录数量
        if len(self._analysis_history) > 1000:
            self._analysis_history = self._analysis_history[-500:]

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """获取分析统计信息"""
        if not self._analysis_history:
            return {
                'total_analyses': 0,
                'intent_distribution': {},
                'avg_processing_time_ms': 0.0
            }

        total_analyses = len(self._analysis_history)

        # 意图分布统计
        intent_counts = {}
        for record in self._analysis_history:
            intent = record['result_intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # 平均处理时间
        processing_times = [record['processing_time_ms'] for record in self._analysis_history]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

        return {
            'total_analyses': total_analyses,
            'intent_distribution': intent_counts,
            'avg_processing_time_ms': avg_processing_time,
            'recent_queries': [record['query'] for record in self._analysis_history[-10:]]
        }

    def update_config(self, config: IntentPatternConfig) -> None:
        """更新分析配置"""
        self._config = config

    def add_custom_pattern(self, intent_type: QueryIntent,
                          pattern: str, priority: float = 1.0) -> None:
        """
        添加自定义模式

        Args:
            intent_type: 意图类型
            pattern: 正则表达式模式
            priority: 优先级权重
        """
        if intent_type == QueryIntent.FINANCIAL_INDICATORS:
            self._config.indicators_patterns.append(pattern)
        elif intent_type == QueryIntent.FINANCIAL_STATEMENTS:
            self._config.statements_patterns.append(pattern)

    def clear_history(self) -> None:
        """清空分析历史"""
        self._analysis_history.clear()

    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            'indicators_patterns': self._config.indicators_patterns,
            'statements_patterns': self._config.statements_patterns,
            'specific_indicators': self._config.specific_indicators,
            'specific_statements': self._config.specific_statements,
            'ambiguous_queries': self._config.ambiguous_queries,
            'priority_weights': self._config.priority_weights
        }