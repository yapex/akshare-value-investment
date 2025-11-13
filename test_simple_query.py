#!/usr/bin/env python3
"""
简单的腾讯净资产查询测试
直接使用容器进行测试，避免MCP服务器的复杂性
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from akshare_value_investment.container import ProductionContainer


async def test_simple_tencent_query():
    """简单测试腾讯查询"""
    print('🔍 简单测试腾讯(00700)财务数据查询')
    print('=' * 50)

    # 创建容器
    container = ProductionContainer()

    print('📋 步骤1: 测试字段映射器')
    try:
        field_mapper = container.field_mapper()

        # 测试不同字段的映射
        test_fields = ['净资产', '总资产', '净利润', '每股收益']
        for field in test_fields:
            try:
                mapped_fields, suggestions = field_mapper.resolve_fields_sync('00700', [field])
                print(f'   - "{field}" -> {mapped_fields}')
                if suggestions:
                    print(f'     建议: {suggestions[:2]}')  # 只显示前2个建议
            except Exception as e:
                print(f'   - "{field}" -> 错误: {e}')

    except Exception as e:
        print(f'❌ 字段映射器测试失败: {e}')
        return

    print()
    print('📋 步骤2: 测试直接财务查询')
    try:
        financial_service = container.financial_query_service()

        # 使用已知存在的字段进行测试
        test_queries = [
            ('00700', 'NET_PROFIT'),  # 净利润
            ('00700', 'BASIC_EPS'),  # 每股收益
            ('00700', 'BPS'),        # 每股净资产
        ]

        for symbol, field in test_queries:
            try:
                result = await financial_service.query_by_field_name_simple(
                    symbol=symbol,
                    field_query=field,
                    start_date='2021-01-01',
                    end_date='2024-12-31'
                )

                print(f'   - {symbol} {field}:')
                if result and isinstance(result, dict):
                    success = result.get('success', False)
                    if success:
                        data = result.get('data', [])
                        print(f'     ✅ 查询成功，数据条数: {len(data)}')
                        if data:
                            print(f'     示例数据: {data[0]}')
                    else:
                        message = result.get('message', '未知错误')
                        print(f'     ❌ 查询失败: {message}')
                else:
                    print(f'     ❌ 结果格式错误: {type(result)}')

            except Exception as e:
                print(f'   - {symbol} {field}: ❌ 异常 - {e}')

    except Exception as e:
        print(f'❌ 财务查询测试失败: {e}')


if __name__ == '__main__':
    asyncio.run(test_simple_tencent_query())