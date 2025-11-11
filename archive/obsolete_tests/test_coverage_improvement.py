#!/usr/bin/env python3
"""
测试字段覆盖改进效果
"""

import asyncio
from src.akshare_value_investment.services.yaml_field_mapper import YAMLFieldMapper
from src.akshare_value_investment import create_production_service

async def test_coverage_improvement():
    """测试覆盖改进效果"""

    print('🔍 扩展后的字段覆盖测试')
    print('=' * 60)

    mapper = YAMLFieldMapper()
    service = create_production_service()

    # 测试新增概念的映射
    test_concepts = [
        'ROA', '速动比率', '应收账款周转率', '每股现金流', '增长率'
    ]

    symbol = '605499'

    print(f'📊 测试股票: {symbol}')
    print(f'🧠 可用概念数: {len(mapper.get_available_concepts())}')
    print()

    for concept in test_concepts:
        try:
            mapped_fields, suggestions = await mapper.resolve_fields(symbol, [concept])
            print(f'✅ "{concept}" -> {mapped_fields[0] if mapped_fields else "未找到"}')
        except Exception as e:
            print(f'❌ "{concept}" -> 错误: {e}')

    # 获取实际覆盖率
    print()
    print('📈 计算实际覆盖率...')

    result = service.query(symbol)
    if result.success and result.data:
        all_fields = set()
        for indicator in result.data:
            if hasattr(indicator, 'indicators') and indicator.indicators:
                all_fields.update(indicator.indicators.keys())

        # 获取YAML覆盖的字段
        covered_fields = set()
        concepts = mapper.get_available_concepts()

        for concept_id in concepts:
            concept_info = mapper.get_concept_info(concept_id)
            if concept_info:
                market_mappings = concept_info.get('market_mappings', {})
                market_config = market_mappings.get('a_stock', {})
                market_field_configs = market_config.get('fields', [])

                for field_config in market_field_configs:
                    field_name = field_config.get('name', '')
                    covered_fields.add(field_name)

        actual_coverage = len(covered_fields.intersection(all_fields))
        coverage_rate = actual_coverage / len(all_fields) * 100

        print(f'📋 A股总字段数: {len(all_fields)}')
        print(f'✅ YAML覆盖字段数: {actual_coverage}')
        print(f'📈 覆盖率: {coverage_rate:.1f}%')
        print()
        print(f'🎯 覆盖改进: 从5.7%提升到{coverage_rate:.1f}%')
        improvement = coverage_rate - 5.7
        print(f'🚀 提升: +{improvement:.1f}个百分点')

        # 显示覆盖的详细字段
        print()
        print('📝 已覆盖的A股字段:')
        for field in sorted(covered_fields.intersection(all_fields)):
            print(f'   • {field}')

if __name__ == "__main__":
    asyncio.run(test_coverage_improvement())