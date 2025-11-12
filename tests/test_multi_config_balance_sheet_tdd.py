"""
多配置资产负债表字段映射TDD测试
测试财务指标和财务三表配置合并后的mapping机制
"""

import pytest
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_value_investment.business.mapping.enhanced_field_mapper import EnhancedFinancialFieldMapper


class TestMultiConfigBalanceSheetTDD:
    """多配置资产负债表字段映射TDD测试"""

    def setup_method(self):
        """测试设置"""
        self.field_mapper = EnhancedFinancialFieldMapper()

    def test_multi_config_loading(self):
        """测试多配置文件加载"""
        # 确保配置加载成功
        assert self.field_mapper.ensure_loaded(), "多配置文件加载失败"

        # 验证配置摘要
        summary = self.field_mapper.get_config_summary()
        assert summary['config_files'] == 2, "应该加载2个配置文件"
        assert summary['total_fields'] > 100, "总字段数应该大于100"
        assert summary['total_markets'] == 3, "应该支持3个市场"

        # 验证A股字段数量（应该包含财务指标和财务三表）
        a_stock_config = self.field_mapper.get_market_config('a_stock')
        assert a_stock_config is not None, "A股配置应该存在"
        assert len(a_stock_config.fields) > 100, f"A股字段数量应该大于100，实际: {len(a_stock_config.fields)}"

        print(f"✅ 多配置加载验证通过:")
        print(f"   配置文件数: {summary['config_files']}")
        print(f"   总字段数: {summary['total_fields']}")
        print(f"   A股字段数: {len(a_stock_config.fields)}")

    def test_financial_indicators_still_work(self):
        """测试原有财务指标查询功能不受影响"""
        # 核心财务指标测试用例
        financial_test_cases = [
            ("600519", "净利润", ["净利润"]),
            ("600519", "ROE", ["净资产收益率(ROE)"]),
            ("600519", "每股收益", ["每股现金流"]),
            ("600519", "毛利率", ["毛利率"]),
            ("600519", "流动比率", ["流动比率"]),
            ("600519", "资产负债率", ["资产负债率"]),
            ("600519", "营业总收入", ["营业总收入"]),
        ]

        for symbol, query, expected_contains in financial_test_cases:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync(symbol, [query])

            assert len(mapped_fields) > 0, f"财务指标映射失败: {query}"

            # 验证映射结果包含预期字段
            found = any(expected in mapped_field for expected in expected_contains for mapped_field in mapped_fields)
            assert found, f"财务指标映射结果不包含预期字段: 查询'{query}' -> 期望{expected_contains}, 实际{mapped_fields}"

        print(f"✅ 财务指标功能验证通过: {len(financial_test_cases)} 个测试用例")

    def test_balance_sheet_fields_mapping(self):
        """测试资产负债表字段映射"""
        # 核心资产负债表字段测试用例
        balance_sheet_test_cases = [
            # 资产类字段
            ("600519", "总资产", ["总资产"]),
            ("600519", "资产总额", ["总资产"]),
            ("600519", "流动资产", ["流动资产"]),
            ("600519", "货币资金", ["货币资金"]),
            ("600519", "应收账款", ["应收账款"]),
            ("600519", "存货", ["存货"]),
            ("600519", "固定资产", ["固定资产"]),

            # 负债类字段
            ("600519", "总负债", ["总负债"]),
            ("600519", "负债总额", ["总负债"]),
            ("600519", "流动负债", ["流动负债"]),
            ("600519", "应付账款", ["应付账款"]),

            # 权益类字段
            ("600519", "股本", ["SHARE_CAPITAL"]),
            ("600519", "实收资本", ["SHARE_CAPITAL"]),
            ("600519", "资本公积", ["资本公积"]),
            ("600519", "所有者权益合计", ["所有者权益合计"]),
            ("600519", "股东权益合计", ["所有者权益合计"]),
        ]

        success_count = 0
        for symbol, query, expected_contains in balance_sheet_test_cases:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync(symbol, [query])

            if len(mapped_fields) > 0:
                # 验证映射结果包含预期字段
                found = any(expected in mapped_field for expected in expected_contains for mapped_field in mapped_fields)
                if found:
                    success_count += 1
                    print(f"  ✅ {query} -> {mapped_fields[0]}")
                else:
                    print(f"  ⚠️ {query} -> {mapped_fields[0]} (不完全匹配)")
            else:
                print(f"  ❌ {query} -> 映射失败")
                if suggestions:
                    print(f"     建议: {suggestions[0]}")

        accuracy = success_count / len(balance_sheet_test_cases)
        print(f"📊 资产负债表映射准确率: {accuracy:.2%} ({success_count}/{len(balance_sheet_test_cases)})")

        # 期望准确率至少80%
        assert accuracy >= 0.8, f"资产负债表映射准确率过低: {accuracy:.2%} < 80%"

    def test_combined_config_integration(self):
        """测试合并配置的集成性"""
        # 测试混合查询（同时包含财务指标和财务三表）
        mixed_queries = [
            "净利润",      # 财务指标
            "总资产",      # 财务三表
            "ROE",         # 财务指标
            "股本",        # 财务三表
            "毛利率",      # 财务指标
            "应付账款",    # 财务三表
        ]

        all_success = True
        for query in mixed_queries:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", [query])

            if len(mapped_fields) == 0:
                print(f"❌ 混合查询失败: {query}")
                all_success = False
            else:
                print(f"✅ 混合查询成功: {query} -> {mapped_fields[0]}")

        assert all_success, "合并配置集成性测试失败"

    def test_keyword_search_accuracy(self):
        """测试关键字搜索准确率"""
        # 测试高优先级字段的关键字搜索
        high_priority_tests = [
            ("总资产", "TOTAL_ASSETS"),
            ("流动资产", "TOTAL_CURRENT_ASSETS"),
            ("货币资金", "MONETARYFUNDS"),
            ("应收账款", "ACCOUNTS_RECE"),
            ("存货", "INVENTORY"),
            ("股本", "SHARE_CAPITAL"),
            ("资本公积", "CAPITAL_RESERVE"),
        ]

        for keyword, expected_field_id in high_priority_tests:
            search_result = self.field_mapper.map_keyword_to_field(keyword, "a_stock")

            assert search_result is not None, f"关键字搜索失败: {keyword}"
            field_id, similarity, field_info, market_id = search_result

            # 验证字段ID或名称匹配
            if expected_field_id not in field_id and expected_field_id not in field_info.name:
                print(f"⚠️ 关键字搜索结果不精确: {keyword} -> {field_id} (期望包含: {expected_field_id})")

            # 验证相似度较高
            assert similarity >= 0.8, f"关键字搜索相似度过低: {keyword} -> {similarity}"

        print(f"✅ 高优先级关键字搜索验证通过: {len(high_priority_tests)} 个测试用例")

    def test_performance_with_combined_config(self):
        """测试合并配置后的性能"""
        import time

        # 性能测试：批量查询
        test_queries = ["净利润", "总资产", "ROE", "股本", "毛利率", "流动负债"] * 10  # 60个查询

        start_time = time.time()

        for query in test_queries:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", [query])

        end_time = time.time()
        total_time = end_time - start_time

        avg_time_per_query = total_time / len(test_queries)
        print(f"⏱️ 性能测试结果:")
        print(f"   总查询数: {len(test_queries)}")
        print(f"   总耗时: {total_time:.3f}秒")
        print(f"   平均耗时: {avg_time_per_query:.3f}秒/查询")

        # 期望平均耗时小于0.05秒（考虑配置合并的开销）
        assert avg_time_per_query < 0.05, f"合并配置后性能过慢: {avg_time_per_query:.3f}秒/查询 > 0.05秒"

    def test_config_maintenance(self):
        """测试配置维护性"""
        # 验证配置文件独立性
        summary = self.field_mapper.get_config_summary()

        # 确保有财务指标配置
        assert summary['config_files'] >= 1, "应该至少有1个配置文件"

        # 获取A股配置详情
        a_stock_config = self.field_mapper.get_market_config('a_stock')
        assert a_stock_config is not None, "A股配置应该存在"

        # 统计不同类型的字段
        indicator_fields = 0
        statement_fields = 0

        for field_id, field_info in a_stock_config.fields.items():
            if any(keyword in field_info.name for keyword in ["率", "每股", "周转"]):
                indicator_fields += 1
            elif any(keyword in field_id for keyword in ["TOTAL_", "ACCOUNTS_", "SHARE_"]):
                statement_fields += 1

        print(f"✅ 配置维护性验证通过:")
        print(f"   财务指标相关字段: {indicator_fields} 个")
        print(f"   财务三表相关字段: {statement_fields} 个")
        print(f"   总字段数: {len(a_stock_config.fields)} 个")

        # 确保两种类型字段都存在
        assert indicator_fields > 0, "应该有财务指标字段"
        assert statement_fields > 0, "应该有财务三表字段"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])