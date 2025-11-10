#!/usr/bin/env python3
"""
港股财务指标获取原型

精简的港股财务指标获取工具，专注于提供核心财务数据分析功能。
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import akshare as ak
import pandas as pd


def filter_annual_reports(df: pd.DataFrame, year: Optional[str] = None) -> pd.DataFrame:
    """筛选年报数据，支持年份过滤

    Args:
        df: 原始数据DataFrame
        year: 可选年份过滤

    Returns:
        筛选后的年报数据
    """
    # 筛选年报数据（港股年报通常在12月31日）
    # 港股数据使用REPORT_DATE列，且DATE_TYPE_CODE为'001'表示年报
    annual_df = df[df['DATE_TYPE_CODE'] == '001'].copy()

    # 按年份过滤（使用FISCAL_YEAR字段的年份部分）
    if year:
        annual_df = annual_df[annual_df['REPORT_DATE'].str.contains(year, na=False)]

    # 按报告日期降序排序（最新的在前）
    annual_df = annual_df.sort_values('REPORT_DATE', ascending=False)

    return annual_df


def get_financial_indicators(symbol: str, indicator: str = "年度", year: Optional[str] = None) -> pd.DataFrame:
    """获取港股财务指标数据

    Args:
        symbol: 港股代码（如 00700）
        indicator: 指标类型（年度/半年/季度）
        year: 可选年份过滤

    Returns:
        财务指标DataFrame
    """
    try:
        # 获取港股财务指标数据
        df = ak.stock_financial_hk_analysis_indicator_em(symbol=symbol, indicator=indicator)

        if df.empty:
            print(f"⚠️  未找到股票 {symbol} 的财务指标数据")
            return df

        print(f"✅ 成功获取 {len(df)} 条记录")
        return df

    except Exception as e:
        print(f"❌ 获取数据时出错: {e}")
        return pd.DataFrame()


def format_summary(df: pd.DataFrame) -> None:
    """格式化输出数据摘要

    Args:
        df: 过滤后的年报DataFrame
    """
    if df.empty:
        print("❌ 未找到年报数据")
        return

    print(f"\n=== 港股财务指标摘要 ===")
    print(f"年报记录数: {len(df)} 条")
    print(f"财务指标数: {len(df.columns)} 个")

    if not df.empty:
        print(f"\n年报信息:")
        latest = df.iloc[0]
        print(f"  股票代码: {latest.get('SECURITY_CODE', 'N/A')}")
        print(f"  股票名称: {latest.get('SECURITY_NAME_ABBR', 'N/A')}")
        print(f"  财年: {latest.get('FISCAL_YEAR', 'N/A')}")
        print(f"  报告日期: {latest.get('REPORT_DATE', 'N/A')}")
        print(f"  货币: {latest.get('CURRENCY', 'N/A')}")

        print(f"\n关键指标（最新年报）:")

        # 显示一些关键指标（使用英文列名）
        key_indicators_map = {
            'BASIC_EPS': '基本每股收益(港元)',
            'DILUTED_EPS': '摊薄每股收益(港元)',
            'BPS': '每股净资产(港元)',
            'ROE_YEARLY': '净资产收益率(%)',
            'ROA': '总资产收益率(%)',
            'GROSS_PROFIT': '毛利(港元)',
            'HOLDER_PROFIT': '股东应占溢利(港元)',
            'DEBT_ASSET_RATIO': '资产负债率(%)',
            'CURRENT_RATIO': '流动比率'
        }

        for col_key, display_name in key_indicators_map.items():
            if col_key in df.columns and pd.notna(latest[col_key]):
                value = latest[col_key]
                if isinstance(value, (int, float)):
                    if 'RATIO' in col_key or col_key in ['ROE_YEARLY', 'ROA']:
                        print(f"  {display_name}: {value:.2f}%")
                    else:
                        print(f"  {display_name}: {value:,.2f}")
                else:
                    print(f"  {display_name}: {value}")


def save_to_csv(df: pd.DataFrame, filename: str) -> None:
    """保存数据到CSV文件

    Args:
        df: 要保存的DataFrame
        filename: 文件名
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='港股财务指标获取工具')
    parser.add_argument('symbol', help='港股代码（如 00700）')
    parser.add_argument('--indicator', choices=['年度', '半年', '季度'],
                       default='年度', help='指标类型（默认：年度）')
    parser.add_argument('--year', help='指定年份（如 2023）')
    parser.add_argument('--output', help='CSV输出文件名')

    args = parser.parse_args()

    print(f"正在获取港股 {args.symbol} 的财务指标...")
    print(f"指标类型: {args.indicator}")
    if args.year:
        print(f"年份过滤: {args.year}")
    else:
        print("获取所有年度数据")

    # 获取财务指标数据
    df = get_financial_indicators(args.symbol, args.indicator, args.year)

    if df.empty:
        print("❌ 未获取到数据")
        return

    print(f"\n原始数据包含 {len(df)} 条记录")
    print(f"财务指标: {len(df.columns)} 个")

    # 显示所有列名
    if not df.empty:
        print(f"\n可用指标:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")

    # 筛选年报数据（只有年度指标才筛选年报）
    annual_df = df
    if args.indicator == '年度':
        print(f"\n筛选年报数据...")
        annual_df = filter_annual_reports(df, args.year)
        print(f"找到 {len(annual_df)} 条年报记录")

    # 格式化输出摘要
    format_summary(annual_df)

    # 保存到CSV文件
    if args.output:
        output_path = Path(args.output)
    else:
        # 生成默认文件名
        script_dir = Path(__file__).parent
        filename = f"hk_stock_{args.symbol}_financial_indicators.csv"
        output_path = script_dir / filename

    save_to_csv(annual_df, str(output_path))


if __name__ == "__main__":
    main()