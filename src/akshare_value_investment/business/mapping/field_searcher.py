"""
字段搜索引擎

字段搜索和相似度匹配的具体实现
遵循单一职责原则（SRP），只关注搜索功能
"""

from typing import List, Optional, Tuple, Dict
from .interfaces import IFieldSearcher, IConfigLoader
from .models import FieldInfo


class DefaultFieldSearcher:
    """默认字段搜索引擎实现

    基于关键字和相似度进行字段搜索
    支持精确匹配、包含匹配和模糊匹配
    """

    def __init__(self, config_loader: IConfigLoader):
        """
        初始化字段搜索引擎

        Args:
            config_loader: 配置加载器实例
        """
        self._config_loader = config_loader

    def search_fields_by_keyword(
        self,
        keyword: str,
        market_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[str, float, FieldInfo, Optional[str]]]:
        """
        根据关键字搜索字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID，如果为None则搜索所有市场
            limit: 最大返回数量

        Returns:
            搜索结果列表，每个元素为 (field_id, similarity, field_info, market_id)
        """
        if not self._config_loader.is_loaded() or not keyword:
            return []

        keyword_lower = keyword.lower().strip()
        results = []

        # 确定要搜索的市场
        markets_to_search = [market_id] if market_id else self._config_loader.get_available_markets()

        for market_id_to_search in markets_to_search:
            market_config = self._config_loader.get_market_config(market_id_to_search)
            if not market_config:
                continue

            for field_id, field_info in market_config.fields.items():
                similarity = self._calculate_similarity(keyword_lower, field_info)

                if similarity > 0.3:  # 相似度阈值
                    results.append((field_id, similarity, field_info, market_id_to_search))

        # 按相似度和优先级排序
        results.sort(key=lambda x: (x[1], -x[2].priority), reverse=True)

        # 限制返回数量
        return results[:limit]

    def map_keyword_to_field(
        self,
        keyword: str,
        market_id: str
    ) -> Optional[Tuple[str, float, FieldInfo, str]]:
        """
        将关键字映射到最佳匹配字段

        Args:
            keyword: 关键字
            market_id: 市场ID

        Returns:
            (field_id, similarity, field_info, market_id) 或 None
        """
        search_results = self.search_fields_by_keyword(keyword, market_id, limit=1)

        if search_results:
            return search_results[0]

        return None

    def search_similar_fields(
        self,
        keyword: str,
        market_id: Optional[str] = None,
        max_results: int = 5
    ) -> List[Tuple[str, float, FieldInfo, str]]:
        """
        搜索相似的字段

        Args:
            keyword: 搜索关键字
            market_id: 市场ID
            max_results: 最大结果数量

        Returns:
            排序的字段列表
        """
        return self.search_fields_by_keyword(keyword, market_id, max_results)

    def _calculate_similarity(self, keyword: str, field_info: FieldInfo) -> float:
        """
        计算关键字与字段的相似度

        Args:
            keyword: 搜索关键字（已小写）
            field_info: 字段信息

        Returns:
            相似度分数 (0.0 - 1.0)
        """
        # 1. 精确匹配检查
        if field_info.matches_keyword(keyword):
            return 1.0

        # 2. 字段名匹配
        field_name_lower = field_info.name.lower()
        if keyword == field_name_lower:
            return 1.0

        # 3. 字段ID匹配
        field_id_lower = field_info.field_id.lower() if hasattr(field_info, 'field_id') else ""
        if keyword == field_id_lower:
            return 1.0

        # 4. 包含匹配
        if keyword in field_name_lower:
            return 0.9

        if field_id_lower and keyword in field_id_lower:
            return 0.8

        # 5. 关键字匹配
        for kw in field_info.keywords:
            kw_lower = kw.lower()
            if keyword == kw_lower:
                return 0.9
            if keyword in kw_lower or kw_lower in keyword:
                return 0.7

        # 6. 模糊匹配（基于编辑距离）
        name_similarity = self._fuzzy_match(keyword, field_name_lower)
        if field_id_lower:
            id_similarity = self._fuzzy_match(keyword, field_id_lower)
            max_fuzzy = max(name_similarity, id_similarity)
        else:
            max_fuzzy = name_similarity

        # 7. 关键字模糊匹配
        for kw in field_info.keywords:
            kw_fuzzy = self._fuzzy_match(keyword, kw.lower())
            max_fuzzy = max(max_fuzzy, kw_fuzzy)

        return max_fuzzy

    def _fuzzy_match(self, s1: str, s2: str) -> float:
        """
        模糊匹配算法（基于简化的Levenshtein距离）

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            相似度分数 (0.0 - 1.0)
        """
        if not s1 or not s2:
            return 0.0

        # 对于短字符串使用更简单的算法
        if len(s1) <= 3 or len(s2) <= 3:
            if s1 == s2:
                return 1.0
            if s1 in s2 or s2 in s1:
                return 0.8
            return 0.0

        # 对于较长字符串使用简化的编辑距离
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0

        # 计算编辑距离
        distance = self._edit_distance(s1, s2)
        similarity = 1.0 - (distance / max_len)

        return max(0.0, similarity * 0.6)  # 模糊匹配最高给0.6分

    def _edit_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            编辑距离
        """
        m, n = len(s1), len(s2)

        # 如果其中一个字符串为空，返回另一个的长度
        if m == 0:
            return n
        if n == 0:
            return m

        # 如果字符串太长，使用截断的算法
        max_len = 50
        if m > max_len or n > max_len:
            s1 = s1[:max_len]
            s2 = s2[:max_len]
            m, n = len(s1), len(s2)

        # 动态规划矩阵
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # 初始化第一行和第一列
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # 填充矩阵
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(
                        dp[i - 1][j] + 1,    # 删除
                        dp[i][j - 1] + 1,    # 插入
                        dp[i - 1][j - 1] + 1  # 替换
                    )

        return dp[m][n]

    def get_search_statistics(self) -> Dict[str, any]:
        """
        获取搜索引擎统计信息

        Returns:
            统计信息字典
        """
        if not self._config_loader.is_loaded():
            return {}

        available_markets = self._config_loader.get_available_markets()
        total_fields = 0
        total_keywords = 0
        fields_by_keyword_count = {}

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config:
                for field_info in market_config.fields.values():
                    total_fields += 1
                    keyword_count = len(field_info.keywords)
                    total_keywords += keyword_count

                    # 统计关键字数量分布
                    fields_by_keyword_count[keyword_count] = fields_by_keyword_count.get(keyword_count, 0) + 1

        avg_keywords_per_field = total_keywords / total_fields if total_fields > 0 else 0

        return {
            'total_fields': total_fields,
            'total_keywords': total_keywords,
            'avg_keywords_per_field': round(avg_keywords_per_field, 2),
            'fields_by_keyword_count': fields_by_keyword_count,
            'fields_without_keywords': fields_by_keyword_count.get(0, 0),
            'fields_with_single_keyword': fields_by_keyword_count.get(1, 0),
            'fields_with_multiple_keywords': sum(count for k, count in fields_by_keyword_count.items() if k > 1)
        }