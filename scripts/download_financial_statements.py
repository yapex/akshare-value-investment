#!/usr/bin/env python3
"""
重新下载港股和美股财务三表样本数据
使用indicator="年报"获取纯年报数据
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import akshare as ak
import pandas as pd
from datetime import datetime

def download_hk_financial_statements():
    """下载港股财务三表数据"""
    print("📊 下载港股财务三表数据...")

    # 测试股票
    symbols = ["00700"]  # 腾讯、阿里巴巴

    for symbol in symbols:
        print(f"\n🔍 下载 {symbol} 的财务数据...")

        try:
            # 资产负债表
            print(f"  📋 资产负债表...")
            balance_df = ak.stock_financial_hk_report_em(stock=symbol, symbol="资产负债表", indicator="年度")
            if not balance_df.empty:
                filename = f"tests/sample_data/hk_{symbol}_balance_sheet_{datetime.now().strftime('%Y%m%d')}.csv"
                balance_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(balance_df)} 条记录)")

            # 损益表
            print(f"  📈 损益表...")
            income_df = ak.stock_financial_hk_report_em(stock=symbol, symbol="利润表", indicator="年度")
            if not income_df.empty:
                filename = f"tests/sample_data/hk_{symbol}_income_statement_{datetime.now().strftime('%Y%m%d')}.csv"
                income_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(income_df)} 条记录)")

            # 现金流量表
            print(f"  💰 现金流量表...")
            cashflow_df = ak.stock_financial_hk_report_em(stock=symbol, symbol="现金流量表", indicator="年度")
            if not cashflow_df.empty:
                filename = f"tests/sample_data/hk_{symbol}_cash_flow_{datetime.now().strftime('%Y%m%d')}.csv"
                cashflow_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(cashflow_df)} 条记录)")

        except Exception as e:
            print(f"    ❌ 下载失败: {e}")

def download_us_financial_statements():
    """下载美股财务三表数据"""
    print("\n📈 下载美股财务三表数据...")

    # 测试股票
    symbols = ["AAPL"]  # 苹果、微软

    for symbol in symbols:
        print(f"\n🔍 下载 {symbol} 的财务数据...")

        try:
            # 资产负债表
            print(f"  📋 资产负债表...")
            balance_df = ak.stock_financial_us_report_em(stock=symbol, symbol="资产负债表", indicator="年报")
            if not balance_df.empty:
                filename = f"tests/sample_data/us_{symbol}_balance_sheet_{datetime.now().strftime('%Y%m%d')}.csv"
                balance_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(balance_df)} 条记录)")

            # 损益表
            print(f"  📈 损益表...")
            income_df = ak.stock_financial_us_report_em(stock=symbol, symbol="综合损益表", indicator="年报")
            if not income_df.empty:
                filename = f"tests/sample_data/us_{symbol}_income_statement_{datetime.now().strftime('%Y%m%d')}.csv"
                income_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(income_df)} 条记录)")

            # 现金流量表
            print(f"  💰 现金流量表...")
            cashflow_df = ak.stock_financial_us_report_em(stock=symbol, symbol="现金流量表", indicator="年报")
            if not cashflow_df.empty:
                filename = f"tests/sample_data/us_{symbol}_cash_flow_{datetime.now().strftime('%Y%m%d')}.csv"
                cashflow_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"    ✅ 已保存: {filename} ({len(cashflow_df)} 条记录)")

        except Exception as e:
            print(f"    ❌ 下载失败: {e}")

def clean_old_files():
    """删除旧的样本数据文件"""
    print("\n🗑️  清理旧的样本数据文件...")

    old_files = [
        "hk_stock_statements_sample.csv",
        "us_stock_statements_sample.csv"
    ]

    for filename in old_files:
        file_path = f"tests/sample_data/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  🗑️  已删除: {file_path}")
        else:
            print(f"  ⚠️  文件不存在: {file_path}")

def main():
    """主函数"""
    print("🚀 开始重新下载港股和美股财务三表样本数据...")
    print(f"📅 下载时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 确保目录存在
    os.makedirs("tests/sample_data", exist_ok=True)

    # 清理旧文件
    clean_old_files()

    # 下载数据
    download_hk_financial_statements()
    download_us_financial_statements()

    print("\n✅ 下载完成!")

if __name__ == "__main__":
    main()