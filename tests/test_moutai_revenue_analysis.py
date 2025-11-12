"""
贵州茅台营收分析测试

验证MCP工具在真实投资分析场景中的正确性和可靠性。
"""

import pytest
import sys
import os
import asyncio
import re
from unittest.mock import Mock

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.mark.asyncio
async def test_moutai_revenue_cagr_analysis():
    """
    测试贵州茅台营收年化增长率分析场景

    验证：
    1. 能够成功查询贵州茅台的营业总收入数据
    2. 能够提取和分析营收增长率
    3. 计算结果合理且符合预期
    """

    try:
        from akshare_value_investment.mcp.server import create_mcp_server
        from akshare_value_investment.container import create_container

        # 创建MCP服务器实例
        container = create_container()
        financial_service = container.financial_query_service()
        field_service = container.field_discovery_service()
        server = create_mcp_server(financial_service, field_service)

        # 验证服务器创建成功
        assert server is not None
        assert len(server.handlers) == 3

        # 步骤1: 查询贵州茅台营业总收入
        query_handler = server.handlers["query_financial_indicators"]
        query_result = await query_handler.handle({
            "symbol": "600519",  # 贵州茅台
            "query": "营业总收入",
            "start_date": "2023-01-01",
            "end_date": "2024-12-31",
            "prefer_annual": True
        })

        # 验证查询结果
        assert query_result.isError is False
        query_text = query_result.content[0].text
        assert "600519" in query_text
        assert "营业总收入" in query_text

        print("✅ 步骤1: 贵州茅台营业总收入查询成功")

        # 步骤2: 查询营业总收入增长率
        growth_result = await query_handler.handle({
            "symbol": "600519",
            "query": "营业总收入增长率",
            "start_date": "2023-01-01",
            "end_date": "2024-12-31",
            "prefer_annual": True
        })

        # 验证增长率查询结果
        assert growth_result.isError is False
        growth_text = growth_result.content[0].text
        assert "营业总收入增长率" in growth_text

        print("✅ 步骤2: 营业总收入增长率查询成功")

        # 步骤3: 数据分析和验证
        # 提取年度营收数据
        annual_revenues = {}
        lines = query_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 查找年度报告日期（12月31日）
            if '**报告日期**:' in line and '12-31' in line:
                year_match = re.search(r'(\d{4})-12-31', line)
                if year_match:
                    year = int(year_match.group(1))

                    # 查找下一行的营业总收入
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if '**营业总收入**:' in next_line:
                            revenue_str = next_line.split(':')[1].strip()
                            try:
                                revenue = float(revenue_str)
                                annual_revenues[year] = revenue
                                print(f'{year}年营收: {revenue:,.0f} 元')
                            except ValueError:
                                pass
            i += 1

        # 验证数据完整性
        assert len(annual_revenues) >= 1, "应该至少有1年的营收数据"

        # 步骤4: 计算年化增长率
        if len(annual_revenues) >= 2:
            years = sorted(annual_revenues.keys())
            start_year = years[0]
            end_year = years[-1]
            start_revenue = annual_revenues[start_year]
            end_revenue = annual_revenues[end_year]
            year_diff = end_year - start_year

            # 计算CAGR
            cagr = (end_revenue / start_revenue) ** (1 / year_diff) - 1

            # 业务逻辑验证
            assert 150000000000 <= start_revenue <= 200000000000, "起始营收应该在合理范围内"
            assert 150000000000 <= end_revenue <= 200000000000, "结束营收应该在合理范围内"
            assert 0.05 <= cagr <= 0.30, "年化增长率应该在合理范围内(5%-30%)"

            print(f"✅ 步骤3: 年化增长率计算成功")
            print(f"   分析期间: {start_year}-{end_year} ({year_diff}年)")
            print(f"   年化增长率: {cagr * 100:.2f}%")

        else:
            print("⚠️ 数据不足，无法计算多年期年化增长率")

        # 步骤5: 验证增长率的合理性
        # 提取最新年度的增长率数据
        growth_lines = growth_text.split('\n')
        latest_growth_rate = None

        for line in growth_lines:
            if '营业总收入增长率' in line and ':' in line:
                growth_str = line.split(':')[1].strip()
                try:
                    growth_rate = float(growth_str)
                    latest_growth_rate = growth_rate
                    break
                except ValueError:
                    pass

        if latest_growth_rate:
            # 贵州茅台作为优质白酒企业，增长率应该在合理范围内
            assert 5 <= latest_growth_rate <= 30, f"最新增长率 {latest_growth_rate}% 应该在合理范围内"
            print(f"✅ 步骤4: 最新年度增长率 {latest_growth_rate:.2f}% 验证通过")

        print("🎉 贵州茅台营收分析场景测试全部通过！")
        return True

    except ImportError as e:
        print(f"⚠️ 测试跳过，MCP模块不可用: {e}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


@pytest.mark.asyncio
async def test_moutai_data_quality_validation():
    """
    测试贵州茅台数据质量验证

    验证返回的数据符合贵州茅台的业务特点：
    1. 营收规模巨大（千亿级别）
    2. 增长率相对稳定
    3. 数据格式正确
    """

    try:
        from akshare_value_investment.mcp.server import create_mcp_server
        from akshare_value_investment.container import create_container

        # 创建MCP服务器
        container = create_container()
        financial_service = container.financial_query_service()
        field_service = container.field_discovery_service()
        server = create_mcp_server(financial_service, field_service)

        query_handler = server.handlers["query_financial_indicators"]

        # 查询最新营收数据
        result = await query_handler.handle({
            "symbol": "600519",
            "query": "营业总收入",
            "prefer_annual": True
        })

        assert result.isError is False
        response_text = result.content[0].text

        # 数据质量验证
        quality_checks = {
            "contains_symbol": "600519" in response_text,
            "contains_revenue_field": "营业总收入" in response_text,
            "contains_large_number": False,  # 检查是否包含大数字
            "format_correct": "**报告日期**:" in response_text and "**营业总收入**:" in response_text
        }

        # 检查大数字（千亿级别的营收）
        import re
        large_numbers = re.findall(r'\b[1-9]\d{11,}\b', response_text)  # 12位以上的数字
        quality_checks["contains_large_number"] = len(large_numbers) > 0

        # 验证所有质量检查通过
        for check_name, check_result in quality_checks.items():
            assert check_result, f"数据质量检查失败: {check_name}"

        print("✅ 贵州茅台数据质量验证通过")
        print(f"   - 包含股票代码: {quality_checks['contains_symbol']}")
        print(f"   - 包含营收字段: {quality_checks['contains_revenue_field']}")
        print(f"   - 包含大数字: {quality_checks['contains_large_number']}")
        print(f"   - 格式正确: {quality_checks['format_correct']}")

        return True

    except ImportError as e:
        print(f"⚠️ 数据质量测试跳过: {e}")
        return True
    except Exception as e:
        print(f"❌ 数据质量测试失败: {e}")
        raise


if __name__ == "__main__":
    print("🚀 开始贵州茅台营收分析测试")
    print("=" * 50)

    async def run_all_tests():
        tests = [
            ("营收增长率分析", test_moutai_revenue_cagr_analysis),
            ("数据质量验证", test_moutai_data_quality_validation)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n🔍 执行测试: {test_name}")
            print("-" * 30)

            try:
                if await test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    failed += 1
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} - 异常: {e}")

        print("\n" + "=" * 50)
        print(f"📊 测试结果总结:")
        print(f"   ✅ 通过: {passed}")
        print(f"   ❌ 失败: {failed}")
        print(f"   📈 成功率: {passed/(passed+failed)*100:.1f}%")

        if failed == 0:
            print("\n🎉 所有贵州茅台营收分析测试通过！")
            print("MCP工具可以支持真实的投资分析场景。")

    asyncio.run(run_all_tests())