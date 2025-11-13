#!/usr/bin/env python3
"""
调试腾讯00700实际可用的字段
检查akshare数据源中腾讯的真实字段
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from akshare_value_investment.datasource.adapters import AdapterManager
from akshare_value_investment.core.models import MarketType


async def debug_tencent_available_fields():
    """调试腾讯实际可用字段"""
    print('🔍 调试腾讯控股(00700)实际可用字段')
    print('=' * 50)

    # 创建适配器管理器
    adapter_manager = AdapterManager()

    try:
        # 获取港股适配器
        hk_adapter = adapter_manager.get_adapter(MarketType.HK_STOCK)
        print(f'✅ 港股适配器获取成功: {type(hk_adapter).__name__}')

        # 查询所有可用的财务报表数据
        print()
        print('📊 查询腾讯财务报表数据...')

        # 这里我们不指定特定字段，尝试获取所有可用数据
        # 需要检查适配器的具体API
        print(f'适配器方法: {dir(hk_adapter)}')

        # 检查适配器是否有查询所有字段的方法
        if hasattr(hk_adapter, 'query_all_fields'):
            print('发现 query_all_fields 方法')
        elif hasattr(hk_adapter, 'query'):
            print('发现 query 方法')
        elif hasattr(hk_adapter, 'get_balance_sheet'):
            print('发现 get_balance_sheet 方法')
        elif hasattr(hk_adapter, 'get_financial_data'):
            print('发现 get_financial_data 方法')
        else:
            print('⚠️ 未找到合适的查询方法')

        # 尝试几个可能的查询方法
        test_methods = [
            ('query', {'symbol': '00700', 'fields': ['ALL']}),
            ('query_balance_sheet', {'symbol': '00700'}),
            ('get_balance_sheet', {'symbol': '00700'}),
            ('get_financial_data', {'symbol': '00700'}),
        ]

        for method_name, params in test_methods:
            if hasattr(hk_adapter, method_name):
                try:
                    method = getattr(hk_adapter, method_name)
                    print(f'\n🔬 尝试方法: {method_name}({params})')

                    if asyncio.iscoroutinefunction(method):
                        result = await method(**params)
                    else:
                        result = method(**params)

                    print(f'✅ 方法调用成功!')
                    print(f'结果类型: {type(result)}')

                    if isinstance(result, dict):
                        print(f'字典键: {list(result.keys())[:10]}')  # 显示前10个键
                        if 'raw_data' in result:
                            raw_data = result['raw_data']
                            print(f'原始数据键: {list(raw_data.keys())[:10]}')  # 显示前10个键

                            # 查找净资产相关字段
                            equity_fields = [k for k in raw_data.keys()
                                           if any(word in k.upper() for word in
                                                 ['EQUITY', 'ASSET', 'NET', 'BOOK', 'SHAREHOLDER'])]
                            if equity_fields:
                                print(f'🎯 找到净资产相关字段: {equity_fields}')
                                for field in equity_fields[:5]:
                                    value = raw_data[field]
                                    print(f'   - {field}: {value}')
                    elif isinstance(result, list) and result:
                        print(f'列表长度: {len(result)}')
                        print(f'列表项类型: {type(result[0])}')

                        # 检查第一项的结构
                        first_item = result[0]
                        print(f'第一项内容: {first_item}')

                        if hasattr(first_item, '__dict__'):
                            print(f'第一项属性: {list(first_item.__dict__.keys())}')
                        elif hasattr(first_item, '_asdict'):
                            try:
                                as_dict = first_item._asdict()
                                print(f'转换为字典的键: {list(as_dict.keys())}')

                                # 查找净资产相关字段
                                raw_data = as_dict.get('raw_data', {})
                                equity_fields = [k for k in raw_data.keys()
                                               if any(word in k.upper() for word in
                                                     ['EQUITY', 'ASSET', 'NET', 'BOOK', 'SHAREHOLDER', 'TOTAL'])]
                                if equity_fields:
                                    print(f'🎯 找到净资产相关字段: {equity_fields}')
                                    for field in equity_fields:
                                        value = raw_data[field]
                                        print(f'   - {field}: {value} ({type(value).__name__})')

                                    # 特别关注净资产字段
                                    if 'BPS' in raw_data:
                                        print(f'✅ 每股净资产(BPS): {raw_data["BPS"]} 港元/股')

                                    # 显示所有可用字段（按类别分组）
                                    all_fields = list(raw_data.keys())
                                    print(f'\n📋 所有可用字段 (总数: {len(all_fields)}):')

                                    # 按类别分组显示
                                    categories = {
                                        '每股指标': [f for f in all_fields if f.startswith(('PER_', 'EPS', 'BPS'))],
                                        '财务比率': [f for f in all_fields if f.endswith(('_RATIO', '_YOY', '_QOQ')) or 'ROE' in f or 'ROA' in f or 'ROIC' in f],
                                        '现金流指标': [f for f in all_fields if 'OCF' in f or 'CASH' in f],
                                        '利润指标': [f for f in all_fields if 'PROFIT' in f or 'INCOME' in f],
                                        '其他指标': [f for f in all_fields if not any(prefix in f for prefix in ['PER_', 'EPS', 'BPS', 'OCF', 'ROE', 'ROA', 'ROIC'])
                                                and not any(suffix in f for suffix in ['_RATIO', '_YOY', '_QOQ'])]
                                    }

                                    for category, fields in categories.items():
                                        if fields:
                                            print(f'\n📊 {category} ({len(fields)}个):')
                                            for i, field in enumerate(fields):
                                                print(f'   - {field}')

                                else:
                                    print('⚠️ 未找到净资产相关字段')
                            except Exception as e:
                                print(f'转换字典失败: {e}')
                        else:
                            print('⚠️ 无法检查数据结构')

                    break  # 成功找到数据，停止尝试其他方法

                except Exception as e:
                    print(f'❌ 方法 {method_name} 调用失败: {e}')
                    continue

    except Exception as e:
        print(f'❌ 调试失败: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(debug_tencent_available_fields())