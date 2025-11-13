"""
字段相似度计算器

实现多维度智能相似度算法，提高字段匹配的准确性和智能化程度
"""

import re
import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from .models import FieldInfo


@dataclass
class SimilarityConfig:
    """相似度计算配置"""
    # 权重配置
    exact_match_weight: float = 1.0        # 精确匹配权重
    contains_match_weight: float = 0.9     # 包含匹配权重
    keyword_match_weight: float = 0.8      # 关键字匹配权重
    partial_match_weight: float = 0.6      # 部分匹配权重

    # 算法参数
    min_similarity_threshold: float = 0.3  # 最小相似度阈值
    fuzzy_match_threshold: float = 0.5     # 模糊匹配阈值

    # 语言权重
    chinese_weight: float = 1.2            # 中文查询权重
    english_weight: float = 1.0            # 英文查询权重

    # 字段属性权重
    priority_weight: float = 0.1           # 字段优先级权重
    field_name_weight: float = 0.8         # 字段名权重
    keyword_weight: float = 0.7            # 关键字权重


class SimilarityMetrics:
    """相似度计算指标收集"""

    def __init__(self):
        self.calculation_count = 0
        self.match_types = {
            'exact': 0,
            'contains': 0,
            'keyword': 0,
            'partial': 0,
            'none': 0
        }
        self.language_distribution = {
            'chinese': 0,
            'english': 0,
            'mixed': 0
        }

    def record_calculation(self, match_type: str, language: str) -> None:
        """记录相似度计算"""
        self.calculation_count += 1
        if match_type in self.match_types:
            self.match_types[match_type] += 1
        if language in self.language_distribution:
            self.language_distribution[language] += 1

    def get_summary(self) -> Dict[str, Any]:
        """获取计算摘要"""
        total = max(self.calculation_count, 1)
        return {
            'total_calculations': self.calculation_count,
            'match_type_distribution': {
                k: v / total for k, v in self.match_types.items()
            },
            'language_distribution': {
                k: v / total for k, v in self.language_distribution.items()
            }
        }


class FieldSimilarityCalculator:
    """智能字段相似度计算器

    实现多维度相似度计算算法：
    1. 精确匹配：查询与字段名/关键字完全相同
    2. 包含匹配：查询包含在字段名/关键字中，或反之
    3. 关键字匹配：查询与关键字的部分匹配
    4. 模糊匹配：基于编辑距离的相似度计算
    5. 语义匹配：基于财务领域专业词汇的智能匹配
    """

    def __init__(self, config: SimilarityConfig = None):
        """
        初始化相似度计算器

        Args:
            config: 相似度计算配置，如果为None则使用默认配置
        """
        self._config = config or SimilarityConfig()
        self._metrics = SimilarityMetrics()

        # 财务领域同义词映射
        self._financial_synonyms = {
            # 利润相关
            '净利润': ['净利', '纯利', '净收益', '税后利润'],
            '毛利润': ['毛利', '毛收益', '营业毛利'],
            '营业收入': ['营收', '收入', '营业额', '销售收入'],
            '营业成本': ['成本', '营业成本', '销货成本'],

            # 指标相关
            'ROE': ['净资产收益率', '股东权益回报率', '权益回报率'],
            'ROA': ['总资产收益率', '资产收益率'],
            '毛利率': ['销售毛利率', '毛利润率'],
            '净利率': ['销售净利率', '净利润率'],
            '市盈率': ['PE', '本益比', 'P/E'],
            '市净率': ['PB', '市价净值比', 'P/B'],
            '每股收益': ['EPS', '每股盈余'],

            # 资产相关
            '总资产': ['资产总计', '资产总额'],
            '净资产': ['股东权益', '所有者权益', '净资产'],
            '流动资产': ['流动资产合计'],
            '总负债': ['负债总计', '负债总额'],
        }

        # 缩写词映射
        self._abbreviation_mapping = {
            'ROE': ['Return on Equity', '净资产收益率'],
            'ROA': ['Return on Assets', '总资产收益率'],
            'PE': ['Price to Earnings', '市盈率'],
            'PB': ['Price to Book', '市净率'],
            'EPS': ['Earnings Per Share', '每股收益'],
            'ROI': ['Return on Investment', '投资回报率'],
            'EBITDA': ['Earnings Before Interest', '税息折旧及摊销前利润'],
        }

    def calculate_similarity(self, query: str, field_info: FieldInfo) -> float:
        """
        计算查询与字段信息的相似度

        Args:
            query: 用户查询
            field_info: 字段信息

        Returns:
            float: 相似度得分 (0-1)
        """
        if not query or not field_info:
            return 0.0

        query_lower = query.strip().lower()

        # 检测查询语言
        language = self._detect_language(query)
        language_weight = self._config.chinese_weight if language == 'chinese' else self._config.english_weight

        # 1. 字段名相似度计算
        name_similarity = self._calculate_text_similarity(
            query_lower, field_info.name.lower()
        )

        # 2. 关键字相似度计算
        keyword_similarity = self._calculate_keyword_similarity(
            query_lower, field_info.keywords
        )

        # 3. 同义词匹配
        synonym_similarity = self._calculate_synonym_similarity(
            query_lower, field_info
        )

        # 4. 缩写词匹配
        abbreviation_similarity = self._calculate_abbreviation_similarity(
            query_lower, field_info
        )

        # 5. 综合相似度计算
        final_similarity = (
            name_similarity * self._config.field_name_weight +
            keyword_similarity * self._config.keyword_weight +
            synonym_similarity * 0.5 +     # 同义词权重适中
            abbreviation_similarity * 0.7   # 缩写词权重较高
        )

        # 6. 应用语言权重
        final_similarity *= language_weight

        # 7. 应用字段优先级权重
        priority_bonus = (field_info.priority / 5.0) * self._config.priority_weight
        final_similarity += priority_bonus

        # 8. 确保结果在0-1范围内
        final_similarity = max(0.0, min(1.0, final_similarity))

        # 记录计算指标
        match_type = self._determine_match_type(final_similarity, name_similarity, keyword_similarity)
        self._metrics.record_calculation(match_type, language)

        return final_similarity

    def _detect_language(self, text: str) -> str:
        """
        检测文本主要语言

        Args:
            text: 输入文本

        Returns:
            str: 语言类型 ('chinese', 'english', 'mixed')
        """
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))

        total_chars = len(text.replace(' ', ''))

        if total_chars == 0:
            return 'english'

        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars

        if chinese_ratio > 0.7:
            return 'chinese'
        elif english_ratio > 0.7:
            return 'english'
        else:
            return 'mixed'

    def _calculate_text_similarity(self, query: str, text: str) -> float:
        """
        计算两个文本之间的相似度

        Args:
            query: 查询文本
            text: 目标文本

        Returns:
            float: 相似度得分 (0-1)
        """
        if not query or not text:
            return 0.0

        # 精确匹配
        if query == text:
            return self._config.exact_match_weight

        # 包含匹配
        if query in text:
            return self._config.contains_match_weight * (len(query) / len(text))
        if text in query:
            return self._config.contains_match_weight * (len(text) / len(query))

        # 模糊匹配 - 基于字符重叠度
        similarity = self._calculate_fuzzy_similarity(query, text)
        if similarity >= self._config.fuzzy_match_threshold:
            return self._config.partial_match_weight * similarity

        return 0.0

    def _calculate_keyword_similarity(self, query: str, keywords: List[str]) -> float:
        """
        计算查询与关键字列表的相似度

        Args:
            query: 查询文本
            keywords: 关键字列表

        Returns:
            float: 相似度得分 (0-1)
        """
        if not keywords:
            return 0.0

        max_similarity = 0.0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            similarity = self._calculate_text_similarity(query, keyword_lower)
            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_synonym_similarity(self, query: str, field_info: FieldInfo) -> float:
        """
        计算基于同义词的相似度

        Args:
            query: 查询文本
            field_info: 字段信息

        Returns:
            float: 同义词相似度得分 (0-1)
        """
        query_original = query.strip()

        # 检查查询是否是财务同义词
        for standard_term, synonyms in self._financial_synonyms.items():
            if query_original in synonyms:
                # 如果查询是同义词，检查标准词是否与字段匹配
                standard_similarity = self._calculate_text_similarity(
                    standard_term.lower(), field_info.name.lower()
                )
                if standard_similarity > 0:
                    return standard_similarity * 0.9  # 同义词匹配略降权重

        return 0.0

    def _calculate_abbreviation_similarity(self, query: str, field_info: FieldInfo) -> float:
        """
        计算基于缩写词的相似度

        Args:
            query: 查询文本
            field_info: 字段信息

        Returns:
            float: 缩写词相似度得分 (0-1)
        """
        query_upper = query.strip().upper()

        # 检查查询是否是缩写词
        for abbreviation, full_forms in self._abbreviation_mapping.items():
            if query_upper == abbreviation.upper():
                # 如果查询是缩写，检查完整形式是否与字段匹配
                for full_form in full_forms:
                    similarity = self._calculate_text_similarity(
                        full_form.lower(), field_info.name.lower()
                    )
                    if similarity > 0:
                        return similarity * 0.8  # 缩写匹配略降权重

        # 检查字段是否包含缩写词
        field_name_upper = field_info.name.upper()
        for abbreviation, full_forms in self._abbreviation_mapping.items():
            if abbreviation in field_name_upper:
                # 检查查询是否与完整形式匹配
                for full_form in full_forms:
                    similarity = self._calculate_text_similarity(
                        query, full_form.lower()
                    )
                    if similarity > 0:
                        return similarity * 0.8

        return 0.0

    def _calculate_fuzzy_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的模糊相似度（基于字符重叠）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            float: 模糊相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0

        # 计算字符重叠度
        chars1 = set(text1)
        chars2 = set(text2)

        intersection = chars1.intersection(chars2)
        union = chars1.union(chars2)

        if not union:
            return 0.0

        jaccard_similarity = len(intersection) / len(union)

        # 考虑长度相似性
        length_similarity = 1.0 - abs(len(text1) - len(text2)) / max(len(text1), len(text2))

        # 综合相似度
        return jaccard_similarity * 0.7 + length_similarity * 0.3

    def _determine_match_type(self, final_similarity: float,
                            name_similarity: float,
                            keyword_similarity: float) -> str:
        """
        确定匹配类型

        Args:
            final_similarity: 最终相似度
            name_similarity: 字段名相似度
            keyword_similarity: 关键字相似度

        Returns:
            str: 匹配类型
        """
        if final_similarity >= self._config.exact_match_weight:
            return 'exact'
        elif final_similarity >= self._config.contains_match_weight:
            return 'contains'
        elif final_similarity >= self._config.keyword_match_weight:
            return 'keyword'
        elif final_similarity >= self._config.partial_match_weight:
            return 'partial'
        else:
            return 'none'

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取相似度计算指标

        Returns:
            Dict[str, Any]: 计算指标
        """
        return self._metrics.get_summary()

    def add_financial_synonym(self, standard_term: str, synonyms: List[str]) -> None:
        """
        添加财务同义词映射

        Args:
            standard_term: 标准术语
            synonyms: 同义词列表
        """
        self._financial_synonyms[standard_term] = synonyms

    def add_abbreviation(self, abbreviation: str, full_forms: List[str]) -> None:
        """
        添加缩写词映射

        Args:
            abbreviation: 缩写词
            full_forms: 完整形式列表
        """
        self._abbreviation_mapping[abbreviation] = full_forms

    def update_config(self, config: SimilarityConfig) -> None:
        """
        更新相似度计算配置

        Args:
            config: 新的配置
        """
        self._config = config

    def clear_metrics(self) -> None:
        """清空指标统计"""
        self._metrics = SimilarityMetrics()

    def get_similarity_threshold(self) -> float:
        """获取相似度阈值"""
        return self._config.min_similarity_threshold

    def should_accept_field(self, query: str, field_info: FieldInfo) -> bool:
        """
        判断是否应该接受该字段作为候选

        Args:
            query: 查询文本
            field_info: 字段信息

        Returns:
            bool: 是否接受
        """
        similarity = self.calculate_similarity(query, field_info)
        return similarity >= self._config.min_similarity_threshold

    def batch_calculate_similarity(self, query: str,
                                 field_list: List[FieldInfo]) -> List[Tuple[FieldInfo, float]]:
        """
        批量计算相似度

        Args:
            query: 查询文本
            field_list: 字段信息列表

        Returns:
            List[Tuple[FieldInfo, float]]: 字段和相似度的元组列表
        """
        results = []
        for field_info in field_list:
            similarity = self.calculate_similarity(query, field_info)
            if similarity >= self._config.min_similarity_threshold:
                results.append((field_info, similarity))

        # 按相似度降序排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results