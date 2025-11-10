#!/usr/bin/env python3
"""
美股财务指标获取原型

精简的美股财务指标获取工具，专注于提供核心财务数据分析功能。
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
    # 美股数据DATE_TYPE_CODE为'001'表示年报
    annual_df = df[df['DATE_TYPE_CODE'] == '001'].copy()

    # 按年份过滤
    if year:
        annual_df = annual_df[annual_df['REPORT_DATE'].str.contains(year, na=False)]

    # 按报告日期降序排序（最新的在前）
    annual_df = annual_df.sort_values('REPORT_DATE', ascending=False)

    return annual_df


def get_financial_indicators(symbol: str, year: Optional[str] = None) -> pd.DataFrame:
    """获取美股财务指标数据

    Args:
        symbol: 美股代码（如 TSLA, AAPL）
        year: 可选年份过滤

    Returns:
        财务指标DataFrame
    """
    try:
        # 美股接口只支持年报指标
        df = ak.stock_financial_us_analysis_indicator_em(symbol=symbol, indicator="年报")

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

    print(f"\n=== 美股财务指标摘要 ===")
    print(f"年报记录数: {len(df)} 条")
    print(f"财务指标数: {len(df.columns)} 个")

    if not df.empty:
        print(f"\n年报信息:")
        latest = df.iloc[0]
        print(f"  股票代码: {latest.get('SECURITY_CODE', 'N/A')}")
        print(f"  股票名称: {latest.get('SECURITY_NAME_ABBR', 'N/A')}")
        print(f"  报告日期: {latest.get('REPORT_DATE', 'N/A')}")
        print(f"  货币: {latest.get('CURRENCY_ABBR', 'N/A')}")

        print(f"\n关键指标（最新年报）:")

        # 显示一些关键指标（使用英文列名）
        key_indicators_map = {
            'BASIC_EPS': '基本每股收益(美元)',
            'DILUTED_EPS': '摊薄每股收益(美元)',
            'OPERATE_INCOME': '营业收入(美元)',
            'GROSS_PROFIT': '毛利(美元)',
            'PARENT_HOLDER_NETPROFIT': '股东净利润(美元)',
            'ROE_AVG': '净资产收益率(%)',
            'ROA': '总资产收益率(%)',
            'GROSS_PROFIT_RATIO': '毛利率(%)',
            'NET_PROFIT_RATIO': '净利率(%)',
            'CURRENT_RATIO': '流动比率',
            'DEBT_ASSET_RATIO': '资产负债率(%)',
            'TOTAL_ASSETS_TR': '总资产周转率',
            'EQUITY_RATIO': '净资产比率(%)'
        }

        for col_key, display_name in key_indicators_map.items():
            if col_key in df.columns and pd.notna(latest[col_key]):
                value = latest[col_key]
                if isinstance(value, (int, float)):
                    if 'RATIO' in col_key or col_key in ['ROE_AVG', 'ROA', 'GROSS_PROFIT_RATIO', 'NET_PROFIT_RATIO', 'DEBT_ASSET_RATIO', 'EQUITY_RATIO']:
                        print(f"  {display_name}: {value:.2f}%")
                    elif 'TR' in col_key:  # 周转率
                        print(f"  {display_name}: {value:.2f}")
                    else:
                        # 美股财务数据通常以千或百万为单位
                        if abs(value) >= 1e9:
                            print(f"  {display_name}: {value/1e9:.2f}B")
                        elif abs(value) >= 1e6:
                            print(f"  {display_name}: {value/1e6:.2f}M")
                        elif abs(value) >= 1e3:
                            print(f"  {display_name}: {value/1e3:.2f}K")
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
    parser = argparse.ArgumentParser(description='美股财务指标获取工具')
    parser.add_argument('symbol', help='美股代码（如 TSLA, AAPL, MSFT）')
    parser.add_argument('--year', help='指定年份（如 2023）')
    parser.add_argument('--output', help='CSV输出文件名')

    args = parser.parse_args()

    print(f"正在获取美股 {args.symbol} 的财务指标...")
    print("注：美股数据仅支持年报指标")
    if args.year:
        print(f"年份过滤: {args.year}")
    else:
        print("获取所有年度数据")

    # 获取财务指标数据
    df = get_financial_indicators(args.symbol, args.year)

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

    # 筛选年报数据
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
        filename = f"us_stock_{args.symbol}_financial_indicators.csv"
        output_path = script_dir / filename

    save_to_csv(annual_df, str(output_path))


if __name__ == "__main__":
    main()