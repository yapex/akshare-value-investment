#!/usr/bin/env python3
"""
基于真实数据的字段映射表

基于data-fetching原型中真实的财务数据分析结果
建立的跨市场字段映射关系。
"""

from typing import Optional
from data_models import MappingInfo, MarketType

# 基于真实数据分析的核心映射表
CORE_MAPPINGS = [
    # Level 1: 核心指标 - 100%覆盖
    MappingInfo(
        unified_field="basic_eps",
        description="基本每股收益",
        a_stock_field="摊薄每股收益(元)",
        hk_stock_field="BASIC_EPS",
        us_stock_field="BASIC_EPS",
        coverage_level=1
    ),
    MappingInfo(
        unified_field="roe",
        description="净资产收益率",
        a_stock_field="净资产收益率(%)",
        hk_stock_field="ROE_YEARLY",
        us_stock_field="ROE_AVG",
        coverage_level=1
    ),
    MappingInfo(
        unified_field="gross_margin",
        description="毛利率",
        a_stock_field="销售毛利率(%)",
        hk_stock_field="GROSS_PROFIT_RATIO",
        us_stock_field="GROSS_PROFIT_RATIO",
        coverage_level=1
    ),
    MappingInfo(
        unified_field="debt_ratio",
        description="资产负债率",
        a_stock_field="资产负债率(%)",
        hk_stock_field="DEBT_ASSET_RATIO",
        us_stock_field="DEBT_ASSET_RATIO",
        coverage_level=1
    ),
    MappingInfo(
        unified_field="current_ratio",
        description="流动比率",
        a_stock_field="流动比率",
        hk_stock_field="CURRENT_RATIO",
        us_stock_field="CURRENT_RATIO",
        coverage_level=1
    ),

    # Level 2: 部分覆盖指标
    MappingInfo(
        unified_field="revenue",
        description="营业收入",
        a_stock_field=None,  # A股数据中未找到对应字段
        hk_stock_field="OPERATE_INCOME",
        us_stock_field="OPERATE_INCOME",
        coverage_level=2
    ),
    MappingInfo(
        unified_field="net_profit",
        description="净利润",
        a_stock_field="净利润",  # 在A股数据中找到
        hk_stock_field="HOLDER_PROFIT",
        us_stock_field="PARENT_HOLDER_NETPROFIT",
        coverage_level=2
    ),
    MappingInfo(
        unified_field="roa",
        description="总资产收益率",
        a_stock_field="总资产净利润率(%)",
        hk_stock_field="ROA",
        us_stock_field="ROA",
        coverage_level=2
    ),
    MappingInfo(
        unified_field="total_equity",
        description="每股净资产",
        a_stock_field="每股净资产",
        hk_stock_field="BPS",
        us_stock_field=None,  # 美股数据中未找到对应字段
        coverage_level=2
    ),
    MappingInfo(
        unified_field="diluted_eps",
        description="稀释每股收益",
        a_stock_field="基本每股收益(元)",
        hk_stock_field="DILUTED_EPS",
        us_stock_field="DILUTED_EPS",
        coverage_level=2
    ),
]

def get_mapping_by_field(unified_field: str) -> MappingInfo:
    """根据统一字段名获取映射信息"""
    for mapping in CORE_MAPPINGS:
        if mapping.unified_field == unified_field:
            return mapping
    return None

def get_available_fields(market: MarketType) -> list[str]:
    """获取指定市场可用的统一字段列表"""
    available = []
    for mapping in CORE_MAPPINGS:
        if market in mapping.available_markets:
            available.append(mapping.unified_field)
    return available

def get_market_field_name(unified_field: str, market: MarketType) -> Optional[str]:
    """获取统一字段在指定市场的实际字段名"""
    mapping = get_mapping_by_field(unified_field)
    if not mapping:
        return None

    if market == MarketType.A_STOCK:
        return mapping.a_stock_field
    elif market == MarketType.HK_STOCK:
        return mapping.hk_stock_field
    elif market == MarketType.US_STOCK:
        return mapping.us_stock_field

    return None


class DefaultFieldMapper:
    """默认字段映射器 - 实现FieldMapper协议"""

    def get_market_field(self, unified_field: str, market: MarketType) -> Optional[str]:
        """获取指定市场字段名"""
        return get_market_field_name(unified_field, market)

    def get_available_markets(self, unified_field: str) -> list[MarketType]:
        """获取字段可用市场列表"""
        mapping = get_mapping_by_field(unified_field)
        return mapping.available_markets if mapping else []


def print_coverage_report():
    """打印覆盖度报告"""
    print("🔍 跨市场财务指标覆盖度报告")
    print("=" * 60)

    # 统计各市场覆盖情况
    market_stats = {
        MarketType.A_STOCK: 0,
        MarketType.HK_STOCK: 0,
        MarketType.US_STOCK: 0
    }

    for mapping in CORE_MAPPINGS:
        print(f"\n📊 {mapping.description} ({mapping.unified_field})")
        print(f"  A股: {'✅' if mapping.a_stock_field else '❌'} {mapping.a_stock_field or '未找到'}")
        print(f"  港股: {'✅' if mapping.hk_stock_field else '❌'} {mapping.hk_stock_field or '未找到'}")
        print(f"  美股: {'✅' if mapping.us_stock_field else '❌'} {mapping.us_stock_field or '未找到'}")

        for market in MarketType:
            if market in mapping.available_markets:
                market_stats[market] += 1

    print(f"\n📈 覆盖度统计:")
    print(f"A股覆盖指标: {market_stats[MarketType.A_STOCK]}/{len(CORE_MAPPINGS)}")
    print(f"港股覆盖指标: {market_stats[MarketType.HK_STOCK]}/{len(CORE_MAPPINGS)}")
    print(f"美股覆盖指标: {market_stats[MarketType.US_STOCK]}/{len(CORE_MAPPINGS)}")

    total_possible = len(CORE_MAPPINGS) * 3
    total_covered = sum(market_stats.values())
    overall_coverage = (total_covered / total_possible) * 100

    print(f"整体覆盖度: {overall_coverage:.1f}%")

if __name__ == "__main__":
    print_coverage_report()