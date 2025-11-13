"""
候选字段排序策略

实现多维度智能排序算法，综合考虑相似度、优先级、上下文等因素
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .field_router_models import FieldCandidate, QueryIntent, QueryContext, DataSourceType


class RankingFactor(Enum):
    """排序因子类型"""
    SIMILARITY = "similarity"
    PRIORITY = "priority"
    RELEVANCE = "relevance"
    CONTEXT = "context"
    CONFIDENCE = "confidence"


@dataclass
class RankingWeight:
    """排序权重配置"""
    factor: RankingFactor
    weight: float
    enabled: bool = True


@dataclass
class RankingConfig:
    """排序配置"""
    # 基础权重配置
    weights: List[RankingWeight]

    # 上下文权重
    context_weight: float = 0.2
    market_preference_weight: float = 0.1

    # 数据源类型偏好
    source_type_preferences: Dict[DataSourceType, float] = None

    # 动态权重调整
    enable_dynamic_weighting: bool = True
    confidence_threshold: float = 0.7

    def __post_init__(self):
        """初始化后处理"""
        if self.source_type_preferences is None:
            self.source_type_preferences = {
                DataSourceType.FINANCIAL_INDICATORS: 1.1,
                DataSourceType.FINANCIAL_STATEMENTS: 1.0,
                DataSourceType.UNKNOWN: 0.8
            }


class RankingMetrics:
    """排序指标收集"""

    def __init__(self):
        self.total_rankings = 0
        self.factor_contributions = {factor: [] for factor in RankingFactor}
        self.source_type_distribution = {}
        self.confidence_distribution = []

    def record_ranking(self, final_scores: List[float],
                      factor_scores: Dict[RankingFactor, List[float]],
                      source_types: List[DataSourceType]) -> None:
        """记录排序过程"""
        self.total_rankings += 1

        # 记录因子贡献
        for factor, scores in factor_scores.items():
            if scores:
                avg_contribution = sum(scores) / len(scores)
                self.factor_contributions[factor].append(avg_contribution)

        # 记录数据源类型分布
        for source_type in source_types:
            self.source_type_distribution[source_type] = \
                self.source_type_distribution.get(source_type, 0) + 1

        # 记录置信度分布
        if final_scores:
            avg_confidence = sum(final_scores) / len(final_scores)
            self.confidence_distribution.append(avg_confidence)

    def get_summary(self) -> Dict[str, Any]:
        """获取排序指标摘要"""
        factor_avg_contributions = {}
        for factor, contributions in self.factor_contributions.items():
            if contributions:
                factor_avg_contributions[factor.value] = sum(contributions) / len(contributions)

        return {
            'total_rankings': self.total_rankings,
            'factor_contributions': factor_avg_contributions,
            'source_type_distribution': {
                st.value: count for st, count in self.source_type_distribution.items()
            },
            'average_confidence': (
                sum(self.confidence_distribution) / len(self.confidence_distribution)
                if self.confidence_distribution else 0.0
            )
        }


class CompositeRankingStrategy:
    """复合排序策略

    实现多维度智能排序算法：
    1. 相似度权重：基于查询与字段的相似度
    2. 优先级权重：基于字段的配置优先级
    3. 相关性权重：基于查询意图与字段类型的匹配度
    4. 上下文权重：基于股票代码、市场等上下文信息
    5. 动态权重：根据置信度动态调整权重
    """

    def __init__(self, config: RankingConfig = None):
        """
        初始化排序策略

        Args:
            config: 排序配置，如果为None则使用默认配置
        """
        self._config = config or self._create_default_config()
        self._metrics = RankingMetrics()

    def rank_candidates(self, candidates: List[FieldCandidate],
                       intent: QueryIntent,
                       context: QueryContext) -> List[FieldCandidate]:
        """
        对候选字段进行排序

        Args:
            candidates: 候选字段列表
            intent: 查询意图
            context: 查询上下文

        Returns:
            List[FieldCandidate]: 排序后的候选字段列表
        """
        if not candidates:
            return []

        # 计算每个候选字段的综合得分
        scored_candidates = []
        factor_scores = {factor: [] for factor in RankingFactor}

        for candidate in candidates:
            score, candidate_factor_scores = self._calculate_composite_score(
                candidate, intent, context
            )

            # 更新候选字段的相似度为综合得分
            candidate.similarity = score

            scored_candidates.append((score, candidate))

            # 收集因子得分用于指标统计
            for factor, factor_score in candidate_factor_scores.items():
                factor_scores[factor].append(factor_score)

        # 按得分降序排序
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        ranked_candidates = [candidate for _, candidate in scored_candidates]

        # 记录排序指标
        final_scores = [score for score, _ in scored_candidates]
        source_types = [candidate.source_type for candidate in ranked_candidates]
        self._metrics.record_ranking(final_scores, factor_scores, source_types)

        return ranked_candidates

    def _calculate_composite_score(self, candidate: FieldCandidate,
                                 intent: QueryIntent,
                                 context: QueryContext) -> tuple[float, Dict[RankingFactor, float]]:
        """
        计算候选字段的综合得分

        Args:
            candidate: 候选字段
            intent: 查询意图
            context: 查询上下文

        Returns:
            tuple[float, Dict[RankingFactor, float]]: (综合得分, 各因子得分)
        """
        factor_scores = {}

        # 1. 相似度因子
        similarity_score = self._calculate_similarity_score(candidate)
        factor_scores[RankingFactor.SIMILARITY] = similarity_score

        # 2. 优先级因子
        priority_score = self._calculate_priority_score(candidate)
        factor_scores[RankingFactor.PRIORITY] = priority_score

        # 3. 相关性因子
        relevance_score = self._calculate_relevance_score(candidate, intent)
        factor_scores[RankingFactor.RELEVANCE] = relevance_score

        # 4. 上下文因子
        context_score = self._calculate_context_score(candidate, context)
        factor_scores[RankingFactor.CONTEXT] = context_score

        # 5. 置信度因子
        confidence_score = self._calculate_confidence_score(candidate, intent, context)
        factor_scores[RankingFactor.CONFIDENCE] = confidence_score

        # 计算加权综合得分
        composite_score = 0.0
        total_weight = 0.0

        for weight_config in self._config.weights:
            if weight_config.enabled:
                factor_score = factor_scores.get(weight_config.factor, 0.0)
                composite_score += factor_score * weight_config.weight
                total_weight += weight_config.weight

        # 标准化得分
        if total_weight > 0:
            composite_score /= total_weight

        return composite_score, factor_scores

    def _calculate_similarity_score(self, candidate: FieldCandidate) -> float:
        """
        计算相似度得分

        Args:
            candidate: 候选字段

        Returns:
            float: 相似度得分 (0-1)
        """
        return candidate.similarity

    def _calculate_priority_score(self, candidate: FieldCandidate) -> float:
        """
        计算优先级得分

        Args:
            candidate: 候选字段

        Returns:
            float: 优先级得分 (0-1)
        """
        # 将优先级(1-5)转换为0-1得分
        return candidate.priority / 5.0

    def _calculate_relevance_score(self, candidate: FieldCandidate,
                                 intent: QueryIntent) -> float:
        """
        计算相关性得分

        Args:
            candidate: 候选字段
            intent: 查询意图

        Returns:
            float: 相关性得分 (0-1)
        """
        # 数据源类型与查询意图的匹配度
        intent_source_mapping = {
            QueryIntent.FINANCIAL_INDICATORS: {
                DataSourceType.FINANCIAL_INDICATORS: 1.0,
                DataSourceType.FINANCIAL_STATEMENTS: 0.6,
                DataSourceType.UNKNOWN: 0.3
            },
            QueryIntent.FINANCIAL_STATEMENTS: {
                DataSourceType.FINANCIAL_STATEMENTS: 1.0,
                DataSourceType.FINANCIAL_INDICATORS: 0.4,
                DataSourceType.UNKNOWN: 0.3
            },
            QueryIntent.AMBIGUOUS: {
                DataSourceType.FINANCIAL_INDICATORS: 0.7,
                DataSourceType.FINANCIAL_STATEMENTS: 0.7,
                DataSourceType.UNKNOWN: 0.5
            }
        }

        base_score = intent_source_mapping.get(intent, {}).get(
            candidate.source_type, 0.5
        )

        # 应用数据源类型偏好
        preference_multiplier = self._config.source_type_preferences.get(
            candidate.source_type, 1.0
        )

        return base_score * preference_multiplier

    def _calculate_context_score(self, candidate: FieldCandidate,
                               context: QueryContext) -> float:
        """
        计算上下文得分

        Args:
            candidate: 候选字段
            context: 查询上下文

        Returns:
            float: 上下文得分 (0-1)
        """
        score = 0.5  # 基础分数

        # 市场偏好
        if hasattr(context, 'market_id'):
            if candidate.market_id == context.market_id:
                score += 0.2

        # 股票特定的字段偏好（可以基于历史数据学习）
        if hasattr(context, 'symbol'):
            symbol = context.symbol.lower()
            field_id = candidate.field_id.lower()

            # 某些股票代码对特定字段类型有偏好
            if symbol in ['600519', '000858']:  # 贵州茅台、五粮液
                if any(keyword in field_id for keyword in ['profit', 'margin', 'ratio']):
                    score += 0.1
            elif symbol in ['000001', '601398']:  # 平安银行、工商银行
                if any(keyword in field_id for keyword in ['asset', 'loan', 'deposit']):
                    score += 0.1

        return min(1.0, score)

    def _calculate_confidence_score(self, candidate: FieldCandidate,
                                  intent: QueryIntent,
                                  context: QueryContext) -> float:
        """
        计算置信度得分

        Args:
            candidate: 候选字段
            intent: 查询意图
            context: 查询上下文

        Returns:
            float: 置信度得分 (0-1)
        """
        # 基于相似度和相关性的置信度
        base_confidence = candidate.similarity

        # 如果查询明确（非模糊），提高置信度
        if intent != QueryIntent.AMBIGUOUS:
            base_confidence *= 1.2

        # 如果字段具有高优先级，提高置信度
        if candidate.priority >= 4:
            base_confidence *= 1.1

        # 应用置信度阈值调整
        if base_confidence >= self._config.confidence_threshold:
            return min(1.0, base_confidence)
        else:
            return base_confidence * 0.9

    def _create_default_config(self) -> RankingConfig:
        """
        创建默认排序配置

        Returns:
            RankingConfig: 默认配置
        """
        return RankingConfig(
            weights=[
                RankingWeight(RankingFactor.SIMILARITY, 0.4),
                RankingWeight(RankingFactor.PRIORITY, 0.2),
                RankingWeight(RankingFactor.RELEVANCE, 0.3),
                RankingWeight(RankingFactor.CONTEXT, 0.1),
                RankingWeight(RankingFactor.CONFIDENCE, 0.0),  # 置信度作为调整因子
            ]
        )

    def update_config(self, config: RankingConfig) -> None:
        """
        更新排序配置

        Args:
            config: 新的配置
        """
        self._config = config

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取排序指标

        Returns:
            Dict[str, Any]: 排序指标
        """
        return self._metrics.get_summary()

    def clear_metrics(self) -> None:
        """清空指标统计"""
        self._metrics = RankingMetrics()

    def add_custom_weight(self, factor: RankingFactor, weight: float) -> None:
        """
        添加自定义权重

        Args:
            factor: 排序因子
            weight: 权重值
        """
        # 检查是否已存在该因子
        for weight_config in self._config.weights:
            if weight_config.factor == factor:
                weight_config.weight = weight
                weight_config.enabled = True
                return

        # 添加新的权重配置
        self._config.weights.append(RankingWeight(factor, weight))

    def enable_dynamic_weighting(self, enabled: bool) -> None:
        """
        启用/禁用动态权重调整

        Args:
            enabled: 是否启用动态权重
        """
        self._config.enable_dynamic_weighting = enabled

    def set_confidence_threshold(self, threshold: float) -> None:
        """
        设置置信度阈值

        Args:
            threshold: 置信度阈值 (0-1)
        """
        self._config.confidence_threshold = max(0.0, min(1.0, threshold))