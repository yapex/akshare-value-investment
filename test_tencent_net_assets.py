#!/usr/bin/env python3
"""
腾讯净资产查询测试脚本
测试智能字段映射系统是否能够正确查询腾讯的净资产数据
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from akshare_value_investment.mcp_server import AkshareMCPServerV2
from akshare_value_investment.container import ProductionContainer
from akshare_value_investment.business.mapping.intelligent_field_router import IntelligentFieldRouter
from akshare_value_investment.business.mapping.query_intent_analyzer import QueryIntentAnalyzer
from akshare_value_investment.business.mapping.field_similarity_calculator import FieldSimilarityCalculator
from akshare_value_investment.business.mapping.candidate_ranker import CompositeRankingStrategy


async def test_tencent_net_assets():
    """测试腾讯净资产查询"""
    print('🔍 查询腾讯(00700)最近三年净资产数据')
    print('=' * 50)

    # 创建容器和组件
    container = ProductionContainer()

    print('📋 步骤1: 测试智能字段路由系统')
    try:
        # 创建智能路由器
        router = IntelligentFieldRouter(
            config_loader=container.config_loader(),
            similarity_calculator=FieldSimilarityCalculator(),
            ranking_strategy=CompositeRankingStrategy(),
            intent_analyzer=QueryIntentAnalyzer()
        )

        # 测试字段路由
        result = router.route_field_query('净资产', '00700', 'hk_stock')
        print(f'✅ 字段路由结果:')

        if result:
            print(f'   - 成功: {result.success}')
            print(f'   - 字段ID: {result.field_id}')
            print(f'   - 字段名: {result.field_name}')
            print(f'   - 相似度: {result.similarity:.3f}')
            print(f'   - 数据源类型: {result.source_type}')
            field_id = result.field_id
        else:
            print('❌ 字段路由失败，使用默认字段')
            field_id = 'NET_EQUITY'  # 净资产的标准字段名

    except Exception as e:
        print(f'❌ 智能路由测试失败: {e}')
        field_id = 'NET_EQUITY'

    print()
    print('📋 步骤2: 查询腾讯净资产数据')
    try:
        # 创建MCP服务器
        mcp_server = AkshareMCPServerV2(
            financial_service=container.financial_query_service(),
            field_discovery_service=container.field_discovery_service(),
            response_formatter=None
        )

        # 查询数据 - 尝试总资产字段
        query_result = await mcp_server._query_financial_indicators_async(
            symbol='00700',
            field_query='总资产',  # 先测试总资产
            start_date='2021-01-01',
            end_date='2024-12-31'
        )

        # 调试：查看映射到的字段
        print(f'📋 调试信息:')
        if hasattr(mcp_server, 'financial_service') and hasattr(mcp_server.financial_service, 'field_mapper'):
            field_mapper = mcp_server.financial_service.field_mapper
            try:
                mapped_fields, suggestions = field_mapper.resolve_fields_sync('00700', ['净资产'])
                print(f'   - 映射字段: {mapped_fields}')
                print(f'   - 建议: {suggestions}')
            except Exception as e:
                print(f'   - 映射调试失败: {e}')

        print(f'✅ 查询成功!')
        print(f'查询结果类型: {type(query_result)}')
        print(f'查询结果内容: {query_result}')

        # 显示查询结果的详细信息
        if isinstance(query_result, dict):
            print(f'📊 查询结果详情:')
            for key, value in query_result.items():
                print(f'   - {key}: {type(value)} - {value if not isinstance(value, (list, dict)) else f"包含 {len(value)} 个项目"}')

            # 检查是否有数据
            if 'data' in query_result and query_result['data']:
                data = query_result['data']
                print(f'📈 腾讯净资产数据:')
                if isinstance(data, dict):
                    for year, values in data.items():
                        print(f'   - {year}: {values}')
                elif isinstance(data, list):
                    print(f'   - 数据列表长度: {len(data)}')
                    for i, item in enumerate(data[:3]):  # 显示前3个数据项
                        print(f'   - 项目 {i+1}: {item}')
            else:
                print('⚠️  查询结果中未找到数据')

        elif hasattr(query_result, 'raw_data') and query_result.raw_data:
            raw_data = query_result.raw_data
            print(f'📊 腾讯净资产数据:')
            print(f'   - 原始数据字段数: {len(raw_data)}')

            # 查找净资产相关字段
            net_assets_fields = [k for k in raw_data.keys() if 'equity' in k.lower() or 'asset' in k.lower()]
            print(f'   - 净资产相关字段: {net_assets_fields}')

            # 尝试显示最近几年的数据
            for field in net_assets_fields[:3]:  # 只显示前3个相关字段
                print(f'   - {field}: {raw_data[field]}')

        else:
            print('⚠️  未找到数据')

        # 显示格式化结果
        if hasattr(query_result, 'formatted_data') and query_result.formatted_data:
            print(f'📈 格式化数据: {query_result.formatted_data}')

    except Exception as e:
        print(f'❌ 数据查询失败: {e}')
        import traceback
        traceback.print_exc()


async def test_intent_analysis():
    """测试查询意图分析"""
    print()
    print('📋 步骤3: 测试查询意图分析')
    try:
        analyzer = QueryIntentAnalyzer()

        queries = ['净资产', '股东权益', '总资产', '净利润']
        for query in queries:
            intent = analyzer.analyze_intent(query)
            print(f'   - "{query}" -> {intent.value}')

    except Exception as e:
        print(f'❌ 意图分析测试失败: {e}')


async def main():
    """主测试函数"""
    await test_tencent_net_assets()
    await test_intent_analysis()


if __name__ == '__main__':
    asyncio.run(main())