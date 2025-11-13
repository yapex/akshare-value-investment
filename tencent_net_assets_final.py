#!/usr/bin/env python3
"""
腾讯最近三年净资产数据最终查询
展示完整的查询结果和数据格式化
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from akshare_value_investment.container import ProductionContainer


async def display_tencent_net_assets():
    """展示腾讯最近三年净资产数据"""
    print('🏆 腾讯控股(00700)最近三年净资产数据查询')
    print('=' * 60)

    # 创建容器
    container = ProductionContainer()
    financial_service = container.financial_query_service()
    field_mapper = container.field_mapper()

    print('📋 查询设置:')
    print('   - 股票代码: 00700 (腾讯控股)')
    print('   - 查询字段: 净资产 → 每股净资产 (BPS)')
    print('   - 时间范围: 2021-01-01 至 2024-12-31')
    print()

    # 步骤1: 验证字段映射
    print('📋 步骤1: 智能字段映射')
    mapped_fields, suggestions = field_mapper.resolve_fields_sync('00700', ['净资产'])
    print(f'   "净资产" → {mapped_fields[0]} (每股净资产)')
    print(f'   映射建议: {suggestions[0] if suggestions else "无"}')
    print()

    # 步骤2: 查询数据
    print('📊 步骤2: 查询净资产数据')
    try:
        result = await financial_service.query_by_field_name_simple(
            symbol='00700',
            field_query='BPS',  # 使用映射后的字段ID
            start_date='2021-01-01',
            end_date='2024-12-31'
        )

        if result and result.get('success', False):
            data = result.get('data', [])
            print(f'   ✅ 查询成功，共找到 {len(data)} 条记录')
            print()

            # 步骤3: 数据格式化和展示
            print('📈 步骤3: 腾讯最近三年净资产(每股净资产)数据')
            print('   报告日期        | 期间类型  | 净资产(BPS)  | 单位')
            print('-' * 60)

            # 按年份筛选最近三年的数据
            recent_data = []
            for record in data:
                report_date = record.get('report_date')
                if report_date and report_date.year >= 2021:
                    recent_data.append(record)

            # 按日期排序
            recent_data.sort(key=lambda x: x.get('report_date'), reverse=True)

            # 显示最近12条记录（约3年数据）
            for i, record in enumerate(recent_data[:12]):
                report_date = record.get('report_date')
                period_type = record.get('period_type', 'quarterly')
                raw_data = record.get('raw_data', {})
                bps_value = raw_data.get('BPS', 'N/A')

                period_text = '年报' if 'annual' in str(period_type).lower() else '季报'
                date_text = report_date.strftime('%Y-%m-%d') if report_date else 'N/A'

                print(f'   {date_text}    |  {period_text}    |  {bps_value:>10}  |  港元/股')

            print()
            print('📋 数据统计:')
            if recent_data:
                latest_record = recent_data[0]
                latest_value = latest_record.get('raw_data', {}).get('BPS', 0)
                print(f'   最新净资产(每股): {latest_value:.2f} 港元/股')
                print(f'   数据覆盖期间: {recent_data[-1].get("report_date").year} - {recent_data[0].get("report_date").year}')
                print(f'   总记录数: {len(recent_data)} 条')

                # 计算净资产增长情况
                annual_records = [r for r in recent_data if 'annual' in str(r.get('period_type', '')).lower()]
                if len(annual_records) >= 2:
                    latest_annual = annual_records[0].get('raw_data', {}).get('BPS', 0)
                    earliest_annual = annual_records[-1].get('raw_data', {}).get('BPS', 0)
                    if earliest_annual > 0:
                        growth_rate = ((latest_annual - earliest_annual) / earliest_annual) * 100
                        print(f'   年度增长率: {growth_rate:.2f}% (基于年报数据)')

            print()
            print('💡 说明:')
            print('   - BPS = Book Value Per Share (每股净资产/每股账面价值)')
            print('   - 数据来源: akshare 财务报表数据')
            print('   - 单位: 港元/股')
            print('   - 期间类型: 年报(12月)和季报(3/6/9月)')

        else:
            error_msg = result.get('message', '未知错误') if result else '查询失败'
            print(f'   ❌ 查询失败: {error_msg}')

    except Exception as e:
        print(f'❌ 查询异常: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(display_tencent_net_assets())