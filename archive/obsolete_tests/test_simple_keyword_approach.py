#!/usr/bin/env python3
"""
验证简化关键字方案的可行性

对比当前复杂方案与简单关键字标识方案的效果
"""

import sys
import os
from collections import defaultdict
import math

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from akshare_value_investment import create_production_service


def calculate_tfidf_score(query: str, keywords: list) -> float:
    """计算TF-IDF相似度得分"""
    query_terms = set(query.lower().replace(' ', '').split())
    keyword_terms = set()

    for keyword in keywords:
        keyword_terms.update(keyword.lower().replace(' ', '').split())

    # 计算交集比例（简化版TF-IDF）
    intersection = query_terms.intersection(keyword_terms)
    if not intersection:
        return 0.0

    # 简化评分：交集大小 / 查询词大小
    score = len(intersection) / len(query_terms)
    return score


def test_simple_keyword_approach():
    """测试简化关键字方案"""

    print("=" * 80)
    print("🎯 简化关键字方案可行性验证")
    print("=" * 80)

    # 获取实际字段
    service = create_production_service()
    symbol = "605499"

    result = service.query(symbol)
    if not result.success or not result.data:
        print("❌ 无法获取基础数据")
        return

    # 收集所有字段
    all_fields = []
    for indicator in result.data:
        if hasattr(indicator, 'indicators') and indicator.indicators:
            all_fields.extend(list(indicator.indicators.keys()))

    print(f"📋 A股总字段数: {len(all_fields)}")

    # 模拟关键字字典（简化版）
    field_keywords = {
        # 盈利能力
        "扣除非经常性损益后的净利润(元)": ["扣非", "净利润", "非经常", "扣除非经常"],
        "营业总收入": ["营业", "总收入", "收入", "营收"],
        "净利润": ["净利润", "利润", "盈利", "净利"],
        "基本每股收益": ["每股", "收益", "每股收益", "EPS"],

        # 营运能力
        "存货周转率": ["存货", "周转", "存货周转", "周转率"],
        "应收账款周转率": ["应收", "账款", "周转", "应收账款"],
        "总资产周转率": ["总资产", "周转", "资产周转"],

        # 偿债能力
        "资产负债率": ["负债", "资产", "资产负债", "负债率"],
        "流动比率": ["流动", "比率", "流动比率"],
        "速动比率": ["速动", "比率", "速动比率"],

        # 成长性
        "归属母公司净利润增长率": ["增长率", "同比", "增长", "净利润增长"],
        "营业总收入增长率": ["增长率", "同比", "增长", "收入增长"],

        # 现金流
        "每股现金流": ["每股", "现金流", "每股现金流"],
        "经营性现金净流量": ["经营", "现金流", "经营现金流"],

        # 资产相关
        "每股净资产": ["每股", "净资产", "每股净资产", "股东权益"],
        "总资产": ["总资产", "资产", "资产总额"],
    }

    # 测试查询用例
    test_queries = [
        "扣非净利润",           # 应该匹配：扣除非经常性损益后的净利润(元)
        "营业收入",             # 应该匹配：营业总收入
        "存货周转",             # 应该匹配：存货周转率
        "每股收益",             # 应该匹配：基本每股收益
        "负债率",               # 应该匹配：资产负债率
        "增长率",               # 应该匹配：增长率相关字段
        "现金流",               # 应该匹配：现金流相关字段
        "每股净资产",           # 应该匹配：每股净资产
    ]

    print(f"\n🧪 关键字匹配测试 ({len(test_queries)}个查询):")
    print("-" * 60)

    success_count = 0
    for query in test_queries:
        print(f"\n🔍 查询: '{query}'")

        best_match = None
        best_score = 0
        best_field = None

        # 计算与每个字段的匹配得分
        for field in all_fields:
            if field in field_keywords:
                score = calculate_tfidf_score(query, field_keywords[field])
                if score > best_score:
                    best_score = score
                    best_match = field

        if best_match:
            print(f"   ✅ 匹配成功: '{best_match}' (得分: {best_score:.3f})")
            print(f"   🏷️  关键字: {field_keywords[best_match]}")
            success_count += 1
        else:
            print(f"   ❌ 未找到匹配")

    success_rate = success_count / len(test_queries) * 100
    print(f"\n📊 关键字方案统计:")
    print(f"   🎯 查询成功率: {success_rate:.1f}% ({success_count}/{len(test_queries)})")

    # 对比复杂度
    print(f"\n🔍 复杂度对比:")
    print("-" * 60)

    print(f"📋 简化关键字方案:")
    print(f"   • 配置文件: 字段名 → [关键字列表]")
    print(f"   • 匹配算法: TF-IDF相似度计算")
    print(f"   • 扩展性: 轻松添加关键字")
    print(f"   • 维护成本: 低")
    print(f"   • 用户理解: 简单直观")

    print(f"\n📋 当前复杂方案:")
    print(f"   • 配置文件: 概念定义 + 多市场映射")
    print(f"   • 匹配算法: 4层降级机制")
    print(f"   • 扩展性: 需要添加完整概念")
    print(f"   • 维护成本: 高")
    print(f"   • 用户理解: 需要懂财务概念")

    # 评估实用性
    print(f"\n💡 实用性评估:")
    print("-" * 60)

    if success_rate >= 70:
        print(f"   ✅ 高可行性 - 成功率{success_rate:.1f}%足够实用")
        print(f"   📈 建议采用简化方案，并完善关键字覆盖")
    elif success_rate >= 50:
        print(f"   ⚠️  中等可行性 - 成功率{success_rate:.1f%，需要完善关键字")
        print(f"   📈 建议先完善关键字，再考虑方案切换")
    else:
        print(f"   ❌ 低可行性 - 成功率仅{success_rate:.1f%，关键字需要大幅完善")
        print(f"   📈 建议先优化关键字匹配算法")

    # 关键字覆盖分析
    print(f"\n📊 关键字覆盖分析:")
    print("-" * 60)

    covered_fields = len(field_keywords)
    total_fields = len(all_fields)
    coverage_rate = covered_fields / total_fields * 100

    print(f"   📋 总字段数: {total_fields}")
    print(f"   ✅ 已标注字段数: {covered_fields}")
    print(f"   📈 标注覆盖率: {coverage_rate:.1f}%")

    if coverage_rate < 30:
        print(f"   ⚠️  需要大幅增加关键字标注")
        print(f"   💡 建议: 完整标注所有字段的关键字")

    return success_rate >= 70


if __name__ == "__main__":
    is_feasible = test_simple_keyword_approach()

    print(f"\n" + "=" * 80)
    if is_feasible:
        print("🎉 结论: 简化关键字方案可行！建议采用您的方案。")
    else:
        print("🔧 结论: 简化方案需要进一步优化。")
    print("=" * 80)