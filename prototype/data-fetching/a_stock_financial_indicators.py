#!/usr/bin/env python3
"""
财务指标获取原型
探索 akshare.stock_financial_analysis_indicator 接口的使用方法

功能：
1. 获取股票最近5年年报财务指标
2. 支持按年份过滤指定年份的年报数据
3. 导出CSV文件功能
"""

import akshare as ak
import pandas as pd
from typing import Optional
import argparse
import sys


def get_financial_indicators(symbol: str, year: Optional[str] = None) -> pd.DataFrame:
    """获取股票财务分析指标"""
    print(f"正在获取股票 {symbol} 的财务指标...")

    try:
        # 设置起始年份，默认获取最近5年数据
        current_year = pd.Timestamp.now().year
        start_year = year if year else str(current_year - 5)

        print(f"获取{year if year else f'最近5年（{start_year}年至今）'}数据")

        # 获取财务分析指标数据
        df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
        print(f"成功获取 {len(df)} 条财务指标记录")

        if df.empty:
            print("未获取到数据，请检查股票代码")
            return pd.DataFrame()

        # 转换日期列为日期类型
        df['日期'] = pd.to_datetime(df['日期'])

        # 统一的年报筛选逻辑
        df = filter_annual_reports(df, year)
        return df

    except Exception as e:
        print(f"获取财务指标失败: {e}")
        return pd.DataFrame()


def filter_annual_reports(df: pd.DataFrame, year: Optional[str] = None) -> pd.DataFrame:
    """统一的年报筛选逻辑"""
    print(f"\n筛选{'指定' if year else '最近5年'}年报数据...")

    # 筛选所有年报（12月31日）
    annual_reports = df[df['日期'].dt.strftime('%m-%d') == '12-31'].copy()

    if annual_reports.empty:
        print("未找到任何年报数据")
        return df

    # 按日期降序排序（最新的在前）
    annual_reports = annual_reports.sort_values('日期', ascending=False)

    # 如果指定了年份，进一步筛选
    if year is not None:
        year_data = annual_reports[annual_reports['日期'].dt.year == int(year)]
        if year_data.empty:
            print(f"未找到 {year} 年年报数据")
            available_dates = annual_reports['日期'].dt.strftime('%Y-%m-%d').tolist()
            if available_dates:
                print(f"可用年报日期: {', '.join(available_dates)}")
            return df
        annual_reports = year_data
        print(f"找到 {len(annual_reports)} 条 {year} 年年报记录")
    else:
        # 限制为最近5年
        if len(annual_reports) > 5:
            annual_reports = annual_reports.head(5)
            print(f"显示最近 5 年年报数据")
        else:
            print(f"找到 {len(annual_reports)} 条年报记录")

        print(f"年报日期: {annual_reports['日期'].dt.strftime('%Y-%m-%d').tolist()}")

    return annual_reports


def save_to_csv(df: pd.DataFrame, filename: str):
    """保存数据到CSV文件"""
    if not df.empty:
        # 确保文件保存在原型目录中
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)

        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到: {filepath}")
    else:
        print("数据为空，不保存文件")


def display_summary(df: pd.DataFrame, symbol: str):
    """显示数据摘要"""
    if df.empty:
        return

    print(f"\n=== 股票 {symbol} 财务指标摘要 ===")
    print(f"数据量: {len(df)} 条年报记录")
    print(f"财务指标: {len(df.columns)} 个")

    # 显示关键指标
    key_indicators = []
    for col in df.columns:
        if any(keyword in col for keyword in [
            '摊薄每股收益', '净资产收益率', '总资产净利润率',
            '销售毛利率', '资产负债率', '流动比率'
        ]):
            key_indicators.append(col)

    if key_indicators:
        print(f"\n关键指标（最新年报）:")
        for indicator in key_indicators[:6]:  # 显示前6个
            if indicator in df.columns and not pd.isna(df[indicator].iloc[0]):
                latest_value = df[indicator].iloc[0]
                print(f"  {indicator}: {latest_value}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取股票财务分析指标（年报数据）')
    parser.add_argument('symbol', help='股票代码，如 600519')
    parser.add_argument('--year', help='指定年份，如 2023（获取该年年报）', default=None)
    parser.add_argument('--output', help='输出CSV文件名', default=None)

    args = parser.parse_args()

    # 获取财务指标数据
    df = get_financial_indicators(args.symbol, args.year)

    if df.empty:
        print("未获取到有效数据")
        sys.exit(1)

    # 显示摘要
    display_summary(df, args.symbol)

    # 保存到文件
    if args.output:
        save_to_csv(df, args.output)

    # 显示详细数据
    print(f"\n=== 详细数据 ===")
    pd.set_option('display.max_columns', 8)  # 限制显示列数
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 20)
    print(df[['日期', '摊薄每股收益(元)', '净资产收益率(%)', '总资产净利润率(%)',
              '销售毛利率(%)', '资产负债率(%)', '流动比率']].round(2))


if __name__ == "__main__":
    main()