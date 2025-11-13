"""
财务指标查询引擎

提供高级的财务指标查询功能
"""

from typing import List, Dict, Optional, Tuple, Any
from .unified_field_mapper import UnifiedFieldMapper


class FinancialQueryEngine:
    """财务指标查询引擎"""

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        初始化查询引擎

        Args:
            config_paths: 配置文件路径列表
        """
        self.field_mapper = UnifiedFieldMapper(config_paths=config_paths)

    def query_financial_field(self, query: str, market_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询财务字段

        Args:
            query: 查询字符串
            market_id: 市场ID

        Returns:
            查询结果字典
        """
        # 基础映射
        best_match = self.field_mapper.map_keyword_to_field(query, market_id)

        if best_match:
            # best_match 可能是3或4个元素，兼容处理
            if len(best_match) == 4:
                field_id, similarity, field_info, market_id = best_match
            else:
                field_id, similarity, field_info = best_match
                market_id = None

            return {
                'success': True,
                'match_type': 'exact' if similarity == 1.0 else 'fuzzy',
                'similarity': similarity,
                'field_id': field_id,
                'field_name': field_info.name,
                'field_info': {
                    'name': field_info.name,
                    'keywords': field_info.keywords,
                    'priority': field_info.priority,
                    'description': field_info.description
                },
                'query': query,
                'market_id': market_id
            }
        else:
            # 获取建议
            suggestions = self.field_mapper.get_field_suggestions(query, market_id)
            similar_fields = self.field_mapper.search_similar_fields(query, market_id, 10)

            return {
                'success': False,
                'match_type': 'none',
                'query': query,
                'market_id': market_id,
                'suggestions': suggestions[:5],  # 最多5个建议
                'similar_fields': []
            }

    def search_fields(self, query: str, market_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索相关字段

        Args:
            query: 查询字符串
            market_id: 市场ID
            limit: 结果数量限制

        Returns:
            搜索结果列表
        """
        similar_fields = self.field_mapper.search_similar_fields(query, market_id, limit)

        result = []
        for item in similar_fields:
            if len(item) == 4:
                field_id, similarity, field_info, _ = item
            else:
                field_id, similarity, field_info = item

            result.append({
                'field_id': field_id,
                'field_name': field_info.name,
                'similarity': similarity,
                'priority': field_info.priority,
                'description': field_info.description,
                'keywords': field_info.keywords,
                'match_type': 'exact' if similarity == 1.0 else 'fuzzy'
            })

        return result

    def get_field_by_name(self, field_name: str, market_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据字段名获取详细信息

        Args:
            field_name: 字段名
            market_id: 市场ID

        Returns:
            字段信息字典或None
        """
        field_info = self.field_mapper.get_field_details(field_name, market_id)

        if field_info:
            return {
                'field_name': field_info.name,
                'keywords': field_info.keywords,
                'priority': field_info.priority,
                'description': field_info.description
            }
        else:
            return None

    def get_available_markets(self) -> List[str]:
        """
        获取所有可用市场

        Returns:
            市场ID列表
        """
        if not self.field_mapper.ensure_loaded():
            return []
        return self.field_mapper.config_loader.get_available_markets()

    def get_available_fields(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取可用字段列表

        Args:
            market_id: 市场ID

        Returns:
            字段信息列表
        """
        available_fields = self.field_mapper.get_available_fields(market_id)

        # 获取详细信息
        field_details = []
        for field_name in available_fields:
            field_info = self.field_mapper.get_field_details(field_name, market_id)
            if field_info:
                field_details.append({
                    'field_name': field_info.name,
                    'keywords': field_info.keywords,
                    'priority': field_info.priority,
                    'description': field_info.description
                })

        return field_details

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取配置统计信息

        Returns:
            统计信息字典
        """
        config_info = self.field_mapper.get_config_info()

        # 计算关键字统计
        total_keywords = 0
        all_keywords = self.field_mapper.get_all_keywords()
        keyword_stats = {}

        for market_id in self.get_available_markets():
            market_keywords = self.field_mapper.get_all_keywords(market_id)
            total_keywords += len(market_keywords)
            keyword_stats[market_id] = {
                'keyword_count': len(market_keywords),
                'sample_keywords': market_keywords[:10]  # 示例关键字
            }

        return {
            'config_loaded': self.field_mapper._is_loaded,
            'config_info': config_info,
            'total_keywords': len(all_keywords),
            'keyword_stats_by_market': keyword_stats,
            'query_engine_version': '1.0.0'
        }

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        验证查询字符串

        Args:
            query: 查询字符串

        Returns:
            验证结果
        """
        if not query or not query.strip():
            return {
                'valid': False,
                'error': '查询字符串不能为空'
            }

        query = query.strip()

        # 检查是否包含财务相关关键词
        financial_keywords = ['利润', '收入', '资产', '负债', '现金流', '每股', '收益', '率', '比']
        has_financial_keyword = any(keyword in query for keyword in financial_keywords)

        return {
            'valid': True,
            'query_length': len(query),
            'has_financial_keywords': has_financial_keyword,
            'suggested_markets': self.get_available_markets()
        }