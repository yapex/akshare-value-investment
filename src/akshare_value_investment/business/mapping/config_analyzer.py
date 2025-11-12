"""
配置分析器

配置统计和分析功能的具体实现
遵循单一职责原则（SRP），只关注分析功能
"""

from typing import Dict, List, Any, Optional, Set
from .interfaces import IConfigAnalyzer, IConfigLoader
from .models import FieldInfo


class DefaultConfigAnalyzer:
    """默认配置分析器实现

    提供配置统计、分析和报告功能
    """

    def __init__(self, config_loader: IConfigLoader):
        """
        初始化配置分析器

        Args:
            config_loader: 配置加载器实例
        """
        self._config_loader = config_loader

    def get_metadata(self) -> Dict[str, Any]:
        """
        获取配置元数据

        Returns:
            元数据字典
        """
        if not self._config_loader.is_loaded():
            return {}

        # 基于当前实现，提供基本的元数据信息
        available_markets = self._config_loader.get_available_markets()

        total_fields = 0
        total_keywords = 0
        market_details = {}

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config:
                field_count = len(market_config.fields)
                keyword_count = sum(len(field_info.keywords) for field_info in market_config.fields.values())

                total_fields += field_count
                total_keywords += keyword_count

                market_details[market_id] = {
                    'name': market_config.name,
                    'currency': market_config.currency,
                    'field_count': field_count,
                    'keyword_count': keyword_count,
                    'avg_keywords_per_field': round(keyword_count / field_count, 2) if field_count > 0 else 0
                }

        return {
            'version': '1.0.0',
            'total_markets': len(available_markets),
            'total_fields': total_fields,
            'total_keywords': total_keywords,
            'avg_keywords_per_field': round(total_keywords / total_fields, 2) if total_fields > 0 else 0,
            'markets': market_details,
            'analysis_timestamp': self._get_timestamp()
        }

    def get_categories_info(self) -> Dict[str, Any]:
        """
        获取分类信息

        Returns:
            分类信息字典
        """
        if not self._config_loader.is_loaded():
            return {}

        # 基于字段名称和关键字推断分类
        available_markets = self._config_loader.get_available_markets()
        categories = {
            'financial_indicators': {'count': 0, 'examples': []},
            'balance_sheet': {'count': 0, 'examples': []},
            'income_statement': {'count': 0, 'examples': []},
            'cash_flow': {'count': 0, 'examples': []},
            'other': {'count': 0, 'examples': []}
        }

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if not market_config:
                continue

            for field_id, field_info in market_config.fields.items():
                category = self._categorize_field(field_id, field_info.name, field_info.keywords)
                categories[category]['count'] += 1

                # 添加示例（每个分类最多5个）
                if len(categories[category]['examples']) < 5:
                    categories[category]['examples'].append({
                        'field_id': field_id,
                        'field_name': field_info.name,
                        'market': market_id
                    })

        return categories

    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要

        Returns:
            配置摘要信息
        """
        if not self._config_loader.is_loaded():
            return {}

        available_markets = self._config_loader.get_available_markets()
        total_fields = 0
        markets_detail = {}

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config:
                field_count = len(market_config.fields)
                total_fields += field_count

                # 分析字段优先级分布
                priority_distribution = {}
                for field_info in market_config.fields.values():
                    priority = field_info.priority
                    priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

                markets_detail[market_id] = {
                    'name': market_config.name,
                    'currency': market_config.currency,
                    'fields_count': field_count,
                    'priority_distribution': priority_distribution,
                    'high_priority_fields': sum(count for priority, count in priority_distribution.items() if priority >= 8),
                    'medium_priority_fields': sum(count for priority, count in priority_distribution.items() if 4 <= priority < 8),
                    'low_priority_fields': sum(count for priority, count in priority_distribution.items() if priority < 4)
                }

        return {
            'total_markets': len(available_markets),
            'total_fields': total_fields,
            'config_files': 1,  # 默认值，实际实现中可以更准确
            'markets_detail': markets_detail,
            'health_score': self._calculate_health_score()
        }

    def analyze_field_coverage(self, market_id: str) -> Dict[str, Any]:
        """
        分析指定市场的字段覆盖情况

        Args:
            market_id: 市场ID

        Returns:
            覆盖分析结果
        """
        market_config = self._config_loader.get_market_config(market_id)
        if not market_config:
            return {'error': f'Market {market_id} not found'}

        total_fields = len(market_config.fields)

        # 分析关键字覆盖
        keywords_per_field = []
        fields_with_descriptions = 0

        for field_info in market_config.fields.values():
            keyword_count = len(field_info.keywords)
            keywords_per_field.append(keyword_count)

            if field_info.description:
                fields_with_descriptions += 1

        # 计算统计指标
        avg_keywords = sum(keywords_per_field) / total_fields if total_fields > 0 else 0
        fields_without_keywords = sum(1 for count in keywords_per_field if count == 0)
        fields_with_single_keyword = sum(1 for count in keywords_per_field if count == 1)
        fields_with_multiple_keywords = sum(1 for count in keywords_per_field if count > 1)

        return {
            'market_id': market_id,
            'market_name': market_config.name,
            'total_fields': total_fields,
            'keyword_coverage': {
                'avg_keywords_per_field': round(avg_keywords, 2),
                'fields_without_keywords': fields_without_keywords,
                'fields_with_single_keyword': fields_with_single_keyword,
                'fields_with_multiple_keywords': fields_with_multiple_keywords,
                'keyword_coverage_rate': round((total_fields - fields_without_keywords) / total_fields * 100, 2) if total_fields > 0 else 0
            },
            'description_coverage': {
                'fields_with_descriptions': fields_with_descriptions,
                'description_coverage_rate': round(fields_with_descriptions / total_fields * 100, 2) if total_fields > 0 else 0
            },
            'quality_score': self._calculate_quality_score(keywords_per_field, fields_with_descriptions, total_fields),
            'recommendations': self._generate_recommendations(fields_without_keywords, fields_with_descriptions, total_fields)
        }

    def _categorize_field(self, field_id: str, field_name: str, keywords: List[str]) -> str:
        """根据字段信息推断分类"""
        text_to_check = (field_id + " " + field_name + " " + " ".join(keywords)).lower()

        # 财务指标特征
        if any(keyword in text_to_check for keyword in ['率', 'roe', 'roa', '每股', '周转', '毛利率', '净利率', '负债率']):
            return 'financial_indicators'

        # 资产负债表特征
        elif any(keyword in text_to_check for keyword in ['资产', '负债', '权益', '股本', '资本', '公积']):
            return 'balance_sheet'

        # 利润表特征
        elif any(keyword in text_to_check for keyword in ['收入', '成本', '费用', '利润', '收益', '营收']):
            return 'income_statement'

        # 现金流量表特征
        elif any(keyword in text_to_check for keyword in ['现金流', '流量', '经营', '投资', '筹资']):
            return 'cash_flow'

        else:
            return 'other'

    def _calculate_health_score(self) -> Dict[str, float]:
        """计算配置健康分数"""
        available_markets = self._config_loader.get_available_markets()
        scores = []

        for market_id in available_markets:
            market_config = self._config_loader.get_market_config(market_id)
            if market_config and len(market_config.fields) > 0:
                # 简单的健康分数计算
                fields_with_keywords = sum(1 for f in market_config.fields.values() if len(f.keywords) > 0)
                keyword_ratio = fields_with_keywords / len(market_config.fields)
                scores.append(keyword_ratio * 100)

        if not scores:
            return {'overall': 0.0, 'per_market': {}}

        return {
            'overall': round(sum(scores) / len(scores), 2),
            'per_market': dict(zip(available_markets, [round(score, 2) for score in scores]))
        }

    def _calculate_quality_score(self, keywords_per_field: List[int], fields_with_descriptions: int, total_fields: int) -> float:
        """计算配置质量分数"""
        if total_fields == 0:
            return 0.0

        # 关键字覆盖率分数 (40%)
        fields_with_keywords = sum(1 for count in keywords_per_field if count > 0)
        keyword_score = (fields_with_keywords / total_fields) * 40

        # 平均关键字数分数 (30%)
        avg_keywords = sum(keywords_per_field) / total_fields
        avg_keywords_score = min(avg_keywords * 10, 30)  # 最多30分

        # 描述覆盖率分数 (30%)
        description_score = (fields_with_descriptions / total_fields) * 30

        return round(keyword_score + avg_keywords_score + description_score, 2)

    def _generate_recommendations(self, fields_without_keywords: int, fields_with_descriptions: int, total_fields: int) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if fields_without_keywords > 0:
            keyword_ratio = fields_without_keywords / total_fields
            if keyword_ratio > 0.3:
                recommendations.append(f"建议为{fields_without_keywords}个字段添加关键字以提高搜索覆盖率")
            elif keyword_ratio > 0.1:
                recommendations.append(f"建议为{fields_without_keywords}个字段补充关键字")

        description_ratio = fields_with_descriptions / total_fields
        if description_ratio < 0.5:
            recommendations.append("建议为更多字段添加描述信息以提高可用性")
        elif description_ratio < 0.8:
            recommendations.append("建议完善字段的描述信息")

        if not recommendations:
            recommendations.append("配置质量良好，继续保持")

        return recommendations

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()