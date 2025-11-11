#!/usr/bin/env python3
"""
测试未被财务概念覆盖的指标的查询行为

验证当用户查询未被YAML概念覆盖的指标时，系统的降级机制和用户体验
"""

import asyncio
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from akshare_value_investment.services.yaml_field_mapper import YAMLFieldMapper
from akshare_value_investment import create_production_service


async def test_uncovered_field_behavior():
    """测试未覆盖字段的行为"""

    print("=" * 80)
    print("🔍 未覆盖字段查询行为测试")
    print("=" * 80)

    yaml_mapper = YAMLFieldMapper()
    service = create_production_service()
    symbol = "605499"

    # 1. 获取所有实际字段
    print("📋 获取A股实际字段...")
    result = service.query(symbol)

    if not result.success or not result.data:
        print("❌ 无法获取基础数据")
        return

    # 收集所有字段
    all_fields = set()
    for indicator in result.data:
        if hasattr(indicator, 'indicators') and indicator.indicators:
            all_fields.update(indicator.indicators.keys())

    # 获取已覆盖的字段
    covered_fields = set()
    concepts = yaml_mapper.get_available_concepts()

    for concept_id in concepts:
        concept_info = yaml_mapper.get_concept_info(concept_id)
        if concept_info:
            market_mappings = concept_info.get('market_mappings', {})
            market_config = market_mappings.get('a_stock', {})
            market_field_configs = market_config.get('fields', [])

            for field_config in market_field_configs:
                field_name = field_config.get('name', '')
                covered_fields.add(field_name)

    # 找出未覆盖的字段
    uncovered_fields = all_fields - covered_fields

    print(f"📊 A股总字段数: {len(all_fields)}")
    print(f"✅ 已覆盖字段数: {len(covered_fields)}")
    print(f"❌ 未覆盖字段数: {len(uncovered_fields)}")
    print(f"📈 覆盖率: {len(covered_fields)/len(all_fields)*100:.1f}%")

    # 2. 测试一些未覆盖字段的查询行为
    print("\n🧪 测试未覆盖字段的查询行为:")
    print("-" * 60)

    # 选择一些代表性的未覆盖字段
    test_fields = list(uncovered_fields)[:8]

    for i, field in enumerate(test_fields, 1):
        print(f"\n{i}. 测试字段: '{field}'")

        try:
            # 测试YAML映射
            mapped_fields, suggestions = await yaml_mapper.resolve_fields(symbol, [field])

            print(f"   🗺️  映射结果: {mapped_fields if mapped_fields else '空'}")
            print(f"   💡 映射建议: {suggestions[0] if suggestions else '无'}")

            # 分析降级机制
            if not mapped_fields:
                print(f"   🔍 分析: 映射失败 - 未找到匹配的财务概念")

                # 检查是否有其他降级机制
                direct_match = yaml_mapper._direct_field_match(field)
                print(f"   🔍 直接匹配: {direct_match if direct_match else '无'}")

                if not direct_match:
                    print(f"   ❌ 结果: 完全失败 - 没有任何降级机制")
                else:
                    print(f"   ✅ 结果: 降级成功 - 通过直接匹配")
            else:
                print(f"   ✅ 结果: 映射成功")

        except Exception as e:
            print(f"   ❌ 查询异常: {str(e)}")

    # 3. 测试模糊查询行为
    print(f"\n🧪 测试模糊查询和降级行为:")
    print("-" * 60)

    fuzzy_test_cases = [
        ("营业总收入", "存在字段"),
        ("息前税后总资产报酬率_平均", "存在字段"),
        ("每股净资产_最新股数", "存在字段"),
        ("产权比率", "存在字段"),
        ("成本费用率", "存在字段"),
        ("完全不存在的字段XYZ", "不存在字段"),
        ("未知指标", "模糊查询"),
        ("", "空查询"),
        ("123", "纯数字")
    ]

    for query, description in fuzzy_test_cases:
        print(f"\n🔍 模糊查询: '{query}' ({description})")

        try:
            mapped_fields, suggestions = await yaml_mapper.resolve_fields(symbol, [query])

            print(f"   🗺️  映射结果: {mapped_fields}")
            print(f"   💡 建议数量: {len(suggestions)}")

            if suggestions:
                print(f"   💡 第一个建议: {suggestions[0]}")

            # 分析降级行为
            exists_in_data = query in all_fields
            print(f"   📋 数据中存在: {'✅' if exists_in_data else '❌'}")

            if exists_in_data and not mapped_fields:
                print(f"   ⚠️  问题: 字段存在但未映射 - 需要改进映射逻辑")
            elif not exists_in_data and not mapped_fields:
                print(f"   ✅ 正常: 字段不存在且未映射")
            elif mapped_fields:
                print(f"   ✅ 正常: 成功映射")

        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")

    # 4. 测试实际查询结果
    print(f"\n🧪 测试实际查询的降级行为:")
    print("-" * 60)

    # 测试一些可能失败但有趣的查询
    test_queries = [
        "营业总收入",           # 存在但未覆盖
        "息前税后总资产报酬率", # 存在但未覆盖
        "每股净资产",          # 模糊查询
        "不存在的指标",        # 不存在
    ]

    for query in test_queries:
        print(f"\n🔍 实际查询测试: '{query}'")

        try:
            # 直接使用query_indicators测试
            result = await service.query_indicators(
                symbol=symbol,
                fields=[query],
                prefer_annual=True,
                start_date="2023-01-01",
                end_date="2024-12-31",
                include_metadata=True
            )

            print(f"   📊 查询结果长度: {len(result)} 字符")

            # 分析结果内容
            if "未找到匹配字段" in result:
                print(f"   ❌ 结果: 映射失败，查询返回空结果")
            elif "### 请求指标" in result:
                print(f"   ✅ 结果: 查询成功，包含指标数据")
                # 提取指标名称
                lines = result.split('\n')
                for line in lines:
                    if line.startswith('**') and ':' in line:
                        indicator_name = line.split(':')[0].replace('**', '')
                        print(f"   📈 包含指标: {indicator_name}")
                        break
            else:
                print(f"   ⚠️  结果: 查询结果格式异常")

        except Exception as e:
            print(f"   ❌ 查询异常: {str(e)}")

    # 5. 总结分析
    print(f"\n📊 降级机制分析总结:")
    print("=" * 60)

    print(f"✅ 当前系统的降级机制:")
    print(f"   1. YAML概念映射 - 主要机制")
    print(f"   2. 直接字段匹配 - 备用机制")
    print(f"   3. 模糊搜索 - 部分支持")

    print(f"\n❌ 发现的问题:")
    print(f"   1. 75%的A股字段未覆盖")
    print(f"   2. 缺少智能降级机制")
    print(f"   3. 用户体验需要改进")

    print(f"\n💡 改进建议:")
    print(f"   1. 实现字段名模糊匹配")
    print(f"   2. 添加查询建议功能")
    print(f"   3. 改进错误提示信息")
    print(f"   4. 扩展YAML概念覆盖")


if __name__ == "__main__":
    asyncio.run(test_uncovered_field_behavior())