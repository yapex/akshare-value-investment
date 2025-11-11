#!/usr/bin/env python3
"""
提取腾讯最近3年的ROE数据
"""

import sys
import os
from datetime import datetime, timedelta

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from akshare_value_investment.container import create_production_service

def extract_tencent_roe_data():
    """提取腾讯最近3年的ROE数据"""
    print("🔍 提取腾讯 (00700.HK) 最近3年ROE数据")
    print("=" * 60)

    # 创建查询服务
    service = create_production_service()

    # 计算查询时间范围（最近3年）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)

    print(f"📅 查询时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

    try:
        # 查询腾讯数据
        result = service.query("00700", start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))

        if not result.success:
            print(f"❌ 查询失败: {result.message}")
            return

        if not result.data:
            print("❌ 没有获取到数据")
            return

        print(f"✅ 查询成功，共获取 {len(result.data)} 条记录\n")

        # 提取ROE数据
        roe_records = []

        for i, indicator in enumerate(result.data):
            if indicator.raw_data and 'ROE_AVG' in indicator.raw_data:
                roe_value = indicator.raw_data['ROE_AVG']
                roe_records.append({
                    'report_date': indicator.report_date,
                    'period_type': indicator.period_type.value,
                    'roe_avg': roe_value,
                    'roe_yearly': indicator.raw_data.get('ROE_YEARLY', 'N/A')
                })

        if not roe_records:
            print("❌ 没有找到ROE数据")
            return

        # 按报告日期排序（最新的在前）
        roe_records.sort(key=lambda x: x['report_date'], reverse=True)

        print("📊 腾讯控股 (00700.HK) ROE数据:")
        print("-" * 60)

        for i, record in enumerate(roe_records[:10], 1):  # 显示前10条记录
            date_str = record['report_date'].strftime('%Y-%m-%d')
            period = record['period_type']
            roe_avg = record['roe_avg']
            roe_yearly = record['roe_yearly']

            print(f"{i:2d}. {date_str} [{period:>10}] | ROE_AVG: {roe_avg:>8}% | ROE_YEARLY: {roe_yearly}")

        # 提取年度数据（最近3年）
        print(f"\n🎯 最近3年年度ROE数据:")
        print("-" * 60)

        annual_records = [r for r in roe_records if r['period_type'] == 'annual']
        annual_records.sort(key=lambda x: x['report_date'], reverse=True)

        if len(annual_records) >= 3:
            for i in range(3):
                record = annual_records[i]
                year = record['report_date'].year
                roe_avg = record['roe_avg']
                roe_yearly = record['roe_yearly']
                print(f"{year}年度 | ROE_AVG: {roe_avg:>8}% | ROE_YEARLY: {roe_yearly}")
        else:
            print(f"⚠️ 年度数据不足3年，仅找到 {len(annual_records)} 年数据")
            for record in annual_records:
                year = record['report_date'].year
                roe_avg = record['roe_avg']
                roe_yearly = record['roe_yearly']
                print(f"{year}年度 | ROE_AVG: {roe_avg:>8}% | ROE_YEARLY: {roe_yearly}")

        print(f"\n💡 数据说明:")
        print(f"• ROE_AVG: 平均净资产收益率")
        print(f"• ROE_YEARLY: 年度净资产收益率")
        print(f"• 数据来源于akshare，包含季度和年度报告")

    except Exception as e:
        print(f"❌ 处理过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_tencent_roe_data()