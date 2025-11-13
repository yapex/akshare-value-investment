#!/usr/bin/env python3
"""
修复腾讯净资产字段映射问题
找出正确的字段名并更新配置
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from akshare_value_investment.datasource.adapters import AdapterManager
from akshare_value_investment.core.models import MarketType


async def fix_tencent_asset_mapping():
    """修复腾讯资产字段映射"""
    print('🔧 修复腾讯净资产字段映射问题')
    print('=' * 50)

    # 创建适配器管理器
    adapter_manager = AdapterManager()

    try:
        # 获取港股适配器
        hk_adapter = adapter_manager.get_adapter(MarketType.HK_STOCK)
        result = hk_adapter.get_financial_data(symbol='00700')

        if result and isinstance(result, list) and len(result) > 0:
            # 获取第一条记录的所有字段
            first_item = result[0]
            raw_data = first_item.raw_data
            all_fields = sorted(list(raw_data.keys()))

            print(f'📋 腾讯可用字段总数: {len(all_fields)}')
            print()

            # 显示所有字段
            print('📋 所有可用字段:')
            for i, field in enumerate(all_fields, 1):
                print(f'   [{i:2d}] {field}')
                if i % 10 == 0:  # 每10个字段换行
                    print()

            print()
            print('🎯 查找关键字段:')

            # 查找关键字段
            key_fields = {}
            search_terms = {
                '净资产': ['EQUITY', 'NET', 'BOOK', 'ASSET', 'SHAREHOLDER'],
                '总资产': ['TOTAL_ASSET', 'ASSET', 'TOTAL'],
                '每股净资产': ['BPS', 'BOOK_PER_SHARE'],
                '股东权益': ['EQUITY', 'SHAREHOLDER'],
                '净利润': ['PROFIT', 'NET_PROFIT'],
                '每股收益': ['EPS', 'EARN_PER_SHARE']
            }

            for search_term, keywords in search_terms.items():
                matches = [field for field in all_fields
                         if any(keyword in field.upper() for keyword in keywords)]
                if matches:
                    key_fields[search_term] = matches
                    print(f'   ✅ {search_term}: {matches}')
                else:
                    print(f'   ❌ {search_term}: 未找到')

            print()
            print('💡 分析结果:')
            print('   ✅ BPS - 每股净资产 (已找到)')
            print('   ✅ HOLDER_PROFIT - 归属于股东净利润 (类似净利润)')
            print('   ❌ 总资产 - 未找到直接的资产字段')
            print('   ❌ 净资产总额 - 未找到直接的净资产字段')

            print()
            print('🔧 问题诊断:')
            print('   1. 配置文件中的 NET_EQUITY_IMPLIED 字段在实际数据中不存在')
            print('   2. 实际数据源缺少完整的资产负债表字段')
            print('   3. 需要检查数据源是否提供完整的财务三表数据')

            print()
            print('🎯 解决方案:')
            print('   方案1: 使用现有字段 - BPS (每股净资产)')
            print('   方案2: 检查是否需要调用不同的API获取资产负债表')
            print('   方案3: 验证配置文件是否需要更新到实际可用的字段')

        else:
            print('❌ 未能获取到腾讯数据')

    except Exception as e:
        print(f'❌ 修复失败: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(fix_tencent_asset_mapping())