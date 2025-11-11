"""
概念搜索引擎
"""

import re
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict

from .models import ConceptSearchResult, MarketField
from .config_manager import ConfigManager


class ConceptSearchEngine:
    """概念搜索引擎"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.inverted_index = self._build_inverted_index()

    def _build_inverted_index(self) -> Dict[str, Set[str]]:
        """构建内存反向索引"""
        index = defaultdict(set)
        config = self.config_manager.get_config()

        for concept_id, concept_data in config.get('concepts', {}).items():
            # 索引名称
            names = [concept_data.get('name', '')] + concept_data.get('aliases', [])
            for name in names:
                for word in self._tokenize_text(name):
                    if word:
                        index[word].add(concept_id)

            # 索引关键词
            for keyword in concept_data.get('keywords', []):
                for word in self._tokenize_text(keyword):
                    if word:
                        index[word].add(concept_id)

        return index

    def _tokenize_text(self, text: str) -> List[str]:
        """文本分词"""
        if not text:
            return []

        # 简单的中文分词：按空格和常见分隔符分割，并提取单字
        text = text.strip()
        if not text:
            return []

        # 按空格和常见分隔符分割
        parts = re.split(r'[\s\-_()（）]+', text)
        tokens = []

        for part in parts:
            part = part.strip()
            if part:
                tokens.append(part.lower())
                # 如果是多字符的中文词，也添加单字
                if len(part) > 1 and '\u4e00' <= part[0] <= '\u9fff':
                    tokens.extend([char.lower() for char in part])

        return [token for token in tokens if token and len(token) > 0]

    def search_concepts(self, query: str, market: Optional[str] = None) -> List[ConceptSearchResult]:
        """概念搜索主算法"""
        query_words = self._tokenize_query(query)
        candidate_concepts = self._find_candidates(query_words)

        results = []
        for concept_id, score in candidate_concepts:
            concept_data = self.config_manager.get_concept(concept_id)
            if concept_data:
                result = self._build_search_result(
                    concept_id, concept_data, query_words, score, market
                )
                if result:
                    results.append(result)

        return sorted(results, key=lambda x: x.confidence, reverse=True)

    def _tokenize_query(self, query: str) -> List[str]:
        """查询词分词"""
        return self._tokenize_text(query)

    def _find_candidates(self, query_words: List[str]) -> List[Tuple[str, float]]:
        """通过反向索引找到候选概念"""
        candidates = {}

        for word in query_words:
            if word in self.inverted_index:
                for concept_id in self.inverted_index[word]:
                    candidates[concept_id] = candidates.get(concept_id, 0) + 1

        # 计算匹配度得分
        return [(cid, score / len(query_words)) for cid, score in candidates.items()]

    def _build_search_result(
        self,
        concept_id: str,
        concept_data: Dict[str, Any],
        query_words: List[str],
        base_score: float,
        market: Optional[str] = None
    ) -> Optional[ConceptSearchResult]:
        """构建搜索结果"""
        try:
            # 构建市场字段映射
            market_fields = self._build_market_fields(concept_data.get('market_mappings', {}))

            # 如果指定了市场，只返回该市场的字段
            if market and market in market_fields:
                market_fields = {market: market_fields[market]}
            elif not market_fields:
                return None

            # 计算置信度
            confidence = self._calculate_confidence(concept_data, query_words, base_score)

            return ConceptSearchResult(
                concept_id=concept_id,
                concept_name=concept_data.get('name', ''),
                confidence=confidence,
                description=concept_data.get('description', ''),
                available_fields=market_fields
            )

        except Exception as e:
            # 记录错误但不中断搜索
            print(f"构建搜索结果时出错 {concept_id}: {str(e)}")
            return None

    def _build_market_fields(self, market_mappings: Dict[str, Any]) -> Dict[str, List[MarketField]]:
        """构建市场字段信息"""
        market_fields = {}

        for market_type, market_data in market_mappings.items():
            fields = []
            for field_info in market_data.get('fields', []):
                field = MarketField(
                    name=field_info.get('name', ''),
                    unit=field_info.get('unit', ''),
                    priority=field_info.get('priority', 999),
                    latest_value=None  # 可以在后续查询时填充
                )
                fields.append(field)

            if fields:
                # 按优先级排序
                fields.sort(key=lambda x: x.priority)
                market_fields[market_type] = fields

        return market_fields

    def _calculate_confidence(
        self,
        concept_data: Dict[str, Any],
        query_words: List[str],
        base_score: float
    ) -> float:
        """计算置信度"""
        # 基础匹配度
        confidence = base_score

        # 名称完全匹配加分
        concept_name = concept_data.get('name', '').lower()
        query_text = ' '.join(query_words)

        if concept_name == query_text:
            confidence += 0.3
        elif concept_name in query_text or query_text in concept_name:
            confidence += 0.2

        # 别名匹配加分
        aliases = [alias.lower() for alias in concept_data.get('aliases', [])]
        for alias in aliases:
            if alias == query_text:
                confidence += 0.25
            elif alias in query_text or query_text in alias:
                confidence += 0.15

        # 关键词匹配加分
        keywords = [kw.lower() for kw in concept_data.get('keywords', [])]
        keyword_matches = sum(1 for kw in keywords if kw in query_words)
        if keyword_matches > 0:
            confidence += 0.1 * (keyword_matches / len(keywords))

        # 确保置信度在0-1范围内
        return min(1.0, max(0.0, confidence))

    def rebuild_index(self, config: Optional[Dict[str, Any]] = None) -> None:
        """重建索引"""
        if config:
            # 更新配置管理器的缓存（假设可以直接设置）
            self.config_manager._config_cache = config

        self.inverted_index = self._build_inverted_index()

    def get_all_concepts(self) -> List[str]:
        """获取所有概念ID"""
        config = self.config_manager.get_config()
        return list(config.get('concepts', {}).keys())

    def get_concept_count(self) -> int:
        """获取概念总数"""
        config = self.config_manager.get_config()
        return len(config.get('concepts', {}))