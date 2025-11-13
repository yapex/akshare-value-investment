"""
智能字段路由器

GREEN阶段：最小实现满足TDD测试要求
实现基于查询意图、字段特征和上下文的智能字段路由算法
"""

import re
import time
from typing import Dict, List, Optional, Any, Tuple

from .field_router_models import (
    DataSourceType, QueryIntent, FieldCandidate, FieldRouteResult,
    QueryContext, RoutingMetrics
)
from .namespaced_config_loader import NamespacedMultiConfigLoader, NamespacedMarketConfig
from .models import FieldInfo
from .query_intent_analyzer import QueryIntentAnalyzer
from .field_similarity_calculator import FieldSimilarityCalculator
from .candidate_ranker import CompositeRankingStrategy


class IntelligentFieldRouter:
    """智能字段路由器

    Phase 4: 完整的智能字段路由系统
    核心功能：
    1. 查询意图分析（QueryIntentAnalyzer组件）
    2. 多维度相似度计算（FieldSimilarityCalculator组件）
    3. 智能排序策略（CompositeRankingStrategy组件）
    4. 上下文感知的路由决策
    5. 高置信度结果计算
    """

    def __init__(self, config_loader: NamespacedMultiConfigLoader,
                 intent_analyzer=None, similarity_calculator=None,
                 ranking_strategy=None, cache_manager=None):
        """
        初始化智能字段路由器

        Args:
            config_loader: 命名空间配置加载器
            intent_analyzer: 查询意图分析器（可选，默认创建）
            similarity_calculator: 相似度计算器（可选，默认创建）
            ranking_strategy: 排序策略（可选，默认创建）
            cache_manager: 缓存管理器（可选，Phase 4暂不实现）
        """
        self.config_loader = config_loader

        # 依赖注入或使用默认实现
        self._intent_analyzer = intent_analyzer or QueryIntentAnalyzer()
        self._similarity_calculator = similarity_calculator or FieldSimilarityCalculator()
        self._ranking_strategy = ranking_strategy or CompositeRankingStrategy()

        # 缓存组件（Phase 4暂不实现复杂缓存）
        self._cache_manager = cache_manager
        self._statistics_collector = None

    def route_field_query(self, query: str, symbol: str, market_id: str) -> Optional[FieldRouteResult]:
        """
        智能路由字段查询

        Args:
            query: 用户查询
            symbol: 股票代码
            market_id: 市场ID

        Returns:
            FieldRouteResult: 路由结果，如果无匹配返回None
        """
        start_time = time.time()

        # 缓存检查（Phase 4实现）
        if self._cache_manager:
            cache_key = f"{query}:{symbol}:{market_id}"
            cached_result = self._cache_manager.get_cached_result(cache_key)
            if cached_result:
                return cached_result

        try:
            # Step 1: 分析查询意图（使用专门的分析器）
            intent = self._intent_analyzer.analyze_intent(query)

            # Step 2: 获取候选字段
            candidates = self._get_candidates(query, market_id, intent)

            if not candidates:
                # 记录统计信息（Phase 4实现）
                if self._statistics_collector:
                    self._statistics_collector.record_routing({
                        'query': query,
                        'symbol': symbol,
                        'market_id': market_id,
                        'intent': intent.value,
                        'result': None,
                        'candidates_count': 0,
                        'processing_time': time.time() - start_time
                    })
                return None

            # Step 3: 创建查询上下文
            context = QueryContext(
                symbol=symbol,
                market_id=market_id,
                query=query
            )

            # Step 4: 候选字段排序（使用智能排序策略）
            ranked_candidates = self._ranking_strategy.rank_candidates(candidates, intent, context)

            if not ranked_candidates:
                # 记录统计信息（Phase 4实现）
                if self._statistics_collector:
                    self._statistics_collector.record_routing({
                        'query': query,
                        'symbol': symbol,
                        'market_id': market_id,
                        'intent': intent.value,
                        'result': None,
                        'candidates_count': len(candidates),
                        'processing_time': time.time() - start_time
                    })
                return None

            # Step 5: 创建路由结果
            best_candidate = ranked_candidates[0]
            result = self._create_route_result(best_candidate, intent, context, len(candidates))

            # 缓存结果（Phase 4实现）
            if self._cache_manager:
                cache_key = f"{query}:{symbol}:{market_id}"
                self._cache_manager.cache_result(cache_key, result)

            # 记录路由历史（Phase 4实现）
            if self._statistics_collector:
                processing_time = time.time() - start_time
                self._statistics_collector.record_routing({
                    'query': query,
                    'symbol': symbol,
                    'market_id': market_id,
                    'result_field_id': result.field_id,
                    'intent': intent.value,
                    'confidence_score': result.confidence_score,
                    'candidates_count': len(candidates),
                    'processing_time': processing_time
                })

            return result

        except Exception as e:
            # 记录错误（Phase 4实现）
            if self._statistics_collector:
                self._statistics_collector.record_routing({
                    'query': query,
                    'symbol': symbol,
                    'market_id': market_id,
                    'result': None,
                    'error_message': str(e),
                    'processing_time': time.time() - start_time
                })
            return None

    def _analyze_query_intent(self, query: str) -> QueryIntent:
        """
        分析查询意图（委托给意图分析器）

        Args:
            query: 用户查询

        Returns:
            QueryIntent: 查询意图
        """
        return self._intent_analyzer.analyze_intent(query)

    def _get_candidates(self, query: str, market_id: str, intent: QueryIntent) -> List[FieldCandidate]:
        """
        获取候选字段

        Args:
            query: 用户查询
            market_id: 市场ID
            intent: 查询意图

        Returns:
            List[FieldCandidate]: 候选字段列表
        """
        candidates = []

        # 获取市场配置
        market_config = self.config_loader.get_namespaced_config(market_id)
        if not market_config:
            return candidates

        # 遍历所有字段，计算相似度
        for field_id, field_info in market_config.fields.items():
            # 使用智能相似度计算器
            similarity = self._similarity_calculator.calculate_similarity(query, field_info)

            if similarity >= self._similarity_calculator.get_similarity_threshold():
                # 推断数据源类型
                source_type = self._infer_source_type(field_id, field_info, intent)

                candidate = FieldCandidate(
                    field_id=field_id,
                    market_id=market_id,
                    field_info=field_info,
                    source_type=source_type,
                    priority=field_info.priority,
                    similarity=similarity,
                    context={'query': query, 'intent': intent.value}
                )
                candidates.append(candidate)

        return candidates

    def _calculate_similarity(self, query: str, field_info: FieldInfo) -> float:
        """
        计算查询与字段的相似度（委托给相似度计算器）

        Args:
            query: 用户查询
            field_info: 字段信息

        Returns:
            float: 相似度得分 (0-1)
        """
        return self._similarity_calculator.calculate_similarity(query, field_info)

    def _infer_source_type(self, field_id: str, field_info: FieldInfo, intent: QueryIntent) -> DataSourceType:
        """
        推断字段数据源类型

        Args:
            field_id: 字段ID
            field_info: 字段信息
            intent: 查询意图

        Returns:
            DataSourceType: 数据源类型
        """
        # 从字段ID模式推断
        field_id_upper = field_id.upper()

        # 财务指标模式检查
        indicators_patterns = [r'.*_RATIO$', r'.*_RATE$', r'^ROE$', r'^ROA$', r'^PE_', r'^PB_']
        for pattern in indicators_patterns:
            if re.match(pattern, field_id_upper):
                return DataSourceType.FINANCIAL_INDICATORS

        # 财务三表模式检查
        statements_patterns = [r'^TOTAL_', r'^NET_', r'^GROSS_', r'^.*_ASSETS$', r'^.*_REVENUE$']
        for pattern in statements_patterns:
            if re.match(pattern, field_id_upper):
                return DataSourceType.FINANCIAL_STATEMENTS

        # 从字段名推断
        field_name_lower = field_info.name.lower()
        indicators_keywords = ['率', '比', 'roe', 'roa', 'pe', 'pb']
        statements_keywords = ['总额', '净额', '资产', '收入', '利润', '成本']

        if any(keyword in field_name_lower for keyword in indicators_keywords):
            return DataSourceType.FINANCIAL_INDICATORS
        elif any(keyword in field_name_lower for keyword in statements_keywords):
            return DataSourceType.FINANCIAL_STATEMENTS

        return DataSourceType.UNKNOWN

    def _rank_candidates(self, candidates: List[FieldCandidate],
                        intent: QueryIntent, context: QueryContext) -> List[FieldCandidate]:
        """
        对候选字段进行智能排序（委托给排序策略）

        Args:
            candidates: 候选字段列表
            intent: 查询意图
            context: 查询上下文

        Returns:
            List[FieldCandidate]: 排序后的候选字段列表
        """
        return self._ranking_strategy.rank_candidates(candidates, intent, context)

    def _create_route_result(self, candidate: FieldCandidate, intent: QueryIntent,
                           context: QueryContext, total_candidates: int) -> FieldRouteResult:
        """
        创建路由结果

        Args:
            candidate: 最佳候选字段
            intent: 查询意图
            context: 查询上下文
            total_candidates: 总候选字段数

        Returns:
            FieldRouteResult: 路由结果
        """
        # 计算置信度得分
        confidence_score = self._calculate_confidence_score(candidate, intent, total_candidates)

        # 创建路由结果
        result = FieldRouteResult(
            field_id=candidate.field_id,
            market_id=candidate.market_id,
            field_info=candidate.field_info,
            source_type=candidate.source_type,
            confidence_score=confidence_score,
            context={
                'symbol': context.symbol,
                'market_id': context.market_id,
                'query': context.query,
                'intent': intent.value
            },
            routing_metadata={
                'total_candidates': total_candidates,
                'intent': intent.value,
                'processing_time': time.time()
            }
        )

        return result

    def _calculate_confidence_score(self, candidate: FieldCandidate,
                                  intent: QueryIntent, total_candidates: int) -> float:
        """
        计算路由置信度得分

        Args:
            candidate: 候选字段
            intent: 查询意图
            total_candidates: 总候选字段数

        Returns:
            float: 置信度得分 (0-1)
        """
        base_confidence = candidate.similarity

        # 意图匹配调整
        if candidate.source_type == DataSourceType.FINANCIAL_INDICATORS and intent == QueryIntent.FINANCIAL_INDICATORS:
            base_confidence *= 1.2
        elif candidate.source_type == DataSourceType.FINANCIAL_STATEMENTS and intent == QueryIntent.FINANCIAL_STATEMENTS:
            base_confidence *= 1.2

        # 候选数量调整（候选越少，置信度越高）
        if total_candidates == 1:
            base_confidence *= 1.1
        elif total_candidates <= 3:
            base_confidence *= 1.05

        return min(base_confidence, 1.0)

    def _record_routing(self, query: str, symbol: str, market_id: str,
                       result: Optional[FieldRouteResult], candidates_count: int,
                       processing_time: float) -> None:
        """
        记录路由历史

        Args:
            query: 查询
            symbol: 股票代码
            market_id: 市场ID
            result: 路由结果
            candidates_count: 候选数量
            processing_time: 处理时间
        """
        routing_record = {
            'timestamp': time.time(),
            'query': query,
            'symbol': symbol,
            'market_id': market_id,
            'result_field_id': result.field_id if result else None,
            'confidence_score': result.confidence_score if result else 0.0,
            'candidates_count': candidates_count,
            'processing_time_ms': processing_time * 1000,
            'success': result is not None
        }

        self._routing_history.append(routing_record)

        # 限制历史记录数量
        if len(self._routing_history) > 1000:
            self._routing_history = self._routing_history[-500:]

    def _record_routing_error(self, query: str, symbol: str, market_id: str,
                             error_message: str, processing_time: float) -> None:
        """
        记录路由错误

        Args:
            query: 查询
            symbol: 股票代码
            market_id: 市场ID
            error_message: 错误信息
            processing_time: 处理时间
        """
        error_record = {
            'timestamp': time.time(),
            'query': query,
            'symbol': symbol,
            'market_id': market_id,
            'error_message': error_message,
            'processing_time_ms': processing_time * 1000,
            'success': False
        }

        self._routing_history.append(error_record)

    def get_routing_statistics(self) -> Dict[str, Any]:
        """
        获取路由统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self._routing_history:
            return {
                'total_routings': 0,
                'success_rate': 0.0,
                'avg_processing_time_ms': 0.0,
                'cache_hit_rate': 0.0
            }

        total_routings = len(self._routing_history)
        successful_routings = sum(1 for r in self._routing_history if r.get('success', False))
        success_rate = successful_routings / total_routings

        processing_times = [r.get('processing_time_ms', 0) for r in self._routing_history if 'processing_time_ms' in r]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

        return {
            'total_routings': total_routings,
            'successful_routings': successful_routings,
            'success_rate': success_rate,
            'avg_processing_time_ms': avg_processing_time,
            'cache_entries': len(self._routing_cache),
            'cache_hit_rate': len(self._routing_cache) / total_routings if total_routings > 0 else 0
        }

    def clear_cache(self) -> None:
        """清空路由缓存"""
        self._routing_cache.clear()

    def clear_history(self) -> None:
        """清空路由历史"""
        self._routing_history.clear()