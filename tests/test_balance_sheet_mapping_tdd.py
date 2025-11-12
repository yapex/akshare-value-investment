"""
资产负债表字段映射TDD测试
重点验证mapping机制，抽样测试代表性字段
"""

import pytest
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_value_investment.business.mapping.field_mapper import FinancialFieldMapper


class TestBalanceSheetMappingTDD:
    """资产负债表字段映射TDD测试"""

    def setup_method(self):
        """测试设置"""
        self.field_mapper = FinancialFieldMapper()

    def test_core_balance_sheet_fields_mapping(self):
        """测试核心资产负债表字段映射"""
        # 核心字段测试用例：每个字段测试多个关键字
        core_test_cases = [
            # 总资产相关
            ("600519", "总资产", ["TOTAL_ASSETS"]),
            ("600519", "资产总额", ["TOTAL_ASSETS"]),
            ("600519", "公司总资产", ["TOTAL_ASSETS"]),

            # 流动资产相关
            ("600519", "流动资产", ["TOTAL_CURRENT_ASSETS"]),
            ("600519", "流动资产合计", ["TOTAL_CURRENT_ASSETS"]),

            # 货币资金相关
            ("600519", "货币资金", ["MONETARYFUNDS"]),
            ("600519", "现金", ["MONETARYFUNDS"]),

            # 应收账款相关
            ("600519", "应收账款", ["ACCOUNTS_RECE"]),
            ("600519", "应收", ["ACCOUNTS_RECE"]),

            # 存货相关
            ("600519", "存货", ["INVENTORY"]),
            ("600519", "库存", ["INVENTORY"]),

            # 固定资产相关
            ("600519", "固定资产", ["FIXED_ASSET"]),
            ("600519", "固定资产净值", ["FIXED_ASSET"]),

            # 总负债相关
            ("600519", "总负债", ["TOTAL_LIABILITIES"]),
            ("600519", "负债总额", ["TOTAL_LIABILITIES"]),
            ("600519", "公司总负债", ["TOTAL_LIABILITIES"]),

            # 流动负债相关
            ("600519", "流动负债", ["TOTAL_CURRENT_LIAB"]),
            ("600519", "流动负债合计", ["TOTAL_CURRENT_LIAB"]),

            # 应付账款相关
            ("600519", "应付账款", ["ACCOUNTS_PAYABLE"]),
            ("600519", "应付款项", ["ACCOUNTS_PAYABLE"]),

            # 所有者权益相关
            ("600519", "所有者权益合计", ["TOTAL_EQUITY"]),
            ("600519", "股东权益合计", ["TOTAL_EQUITY"]),
            ("600519", "权益总计", ["TOTAL_EQUITY"]),

            # 股本相关
            ("600519", "股本", ["SHARE_CAPITAL"]),
            ("600519", "实收资本", ["SHARE_CAPITAL"]),

            # 资本公积相关
            ("600519", "资本公积", ["CAPITAL_RESERVE"]),
            ("600519", "资本储备", ["CAPITAL_RESERVE"]),

            # 未分配利润相关
            ("600519", "未分配利润", ["UNASSIGN_RPOFIT"]),
            ("600519", "留存收益", ["UNASSIGN_RPOFIT"]),

            # 归属于母公司所有者权益相关
            ("600519", "归属于母公司所有者权益", ["TOTAL_PARENT_EQUITY"]),
            ("600519", "归母权益", ["TOTAL_PARENT_EQUITY"]),
        ]

        for symbol, query, expected_contains in core_test_cases:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync(symbol, [query])

            assert len(mapped_fields) > 0, f"核心字段映射失败: {query}"

            # 验证映射结果包含预期字段
            found = any(expected in mapped_field for expected in expected_contains for mapped_field in mapped_fields)
            assert found, f"映射结果不包含预期字段: 查询'{query}' -> 期望{expected_contains}, 实际{mapped_fields}"

    def test_general_balance_sheet_fields_mapping(self):
        """测试一般资产负债表字段映射"""
        # 一般字段测试用例：基础关键字映射
        general_test_cases = [
            ("600519", "SECURITY_CODE", ["SECURITY_CODE"]),
            ("600519", "REPORT_DATE", ["REPORT_DATE"]),
            ("600519", "REPORT_TYPE", ["REPORT_TYPE"]),
            ("600519", "CURRENCY", ["CURRENCY"]),
            ("600519", "CIP", ["CIP"]),  # 在建工程
            ("600519", "GOODWILL", ["GOODWILL"]),  # 商誉
            ("600519", "INTANGIBLE_ASSET", ["INTANGIBLE_ASSET"]),  # 无形资产
        ]

        for symbol, query, expected_contains in general_test_cases:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync(symbol, [query])

            assert len(mapped_fields) > 0, f"一般字段映射失败: {query}"

            # 验证映射结果包含预期字段
            found = any(expected in mapped_field for expected in expected_contains for mapped_field in mapped_fields)
            assert found, f"映射结果不包含预期字段: 查询'{query}' -> 期望{expected_contains}, 实际{mapped_fields}"

    def test_balance_sheet_field_mapping_accuracy(self):
        """测试资产负债表字段映射准确率"""
        # 选择一组代表性字段进行准确率测试
        test_queries = [
            "总资产", "流动资产", "固定资产", "货币资金", "应收账款", "存货",
            "总负债", "流动负债", "应付账款", "短期借款", "长期借款",
            "所有者权益合计", "股本", "资本公积", "未分配利润", "归属于母公司所有者权益"
        ]

        success_count = 0
        total_count = len(test_queries)

        for query in test_queries:
            mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", [query])

            if len(mapped_fields) > 0:
                success_count += 1
                print(f"✅ 映射成功: {query} -> {mapped_fields[0]}")
            else:
                print(f"❌ 映射失败: {query}")

        accuracy = success_count / total_count
        print(f"\n📊 映射准确率: {accuracy:.2%} ({success_count}/{total_count})")

        # 期望准确率至少90%
        assert accuracy >= 0.9, f"映射准确率过低: {accuracy:.2%} < 90%"

    def test_balance_sheet_keyword_variations(self):
        """测试资产负债表字段关键字变体"""
        # 测试同一字段的多种查询方式
        keyword_variation_cases = [
            ("总资产", ["总资产", "资产总额", "公司总资产", "所有资产", "资产规模"]),
            ("货币资金", ["货币资金", "现金", "货币", "现金及现金等价物"]),
            ("存货", ["存货", "库存", "库存商品", "存货合计"]),
            ("应收账款", ["应收账款", "应收", "应收款项"]),
            ("应付账款", ["应付账款", "应付款项", "应付"]),
        ]

        for target_field, variations in keyword_variation_cases:
            print(f"\n🔍 测试字段: {target_field}")
            success_variations = 0

            for variation in variations:
                mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", [variation])

                if len(mapped_fields) > 0:
                    success_variations += 1
                    print(f"  ✅ {variation} -> {mapped_fields[0]}")
                else:
                    print(f"  ❌ {variation} -> 映射失败")

            variation_rate = success_variations / len(variations)
            print(f"  📊 变体命中率: {variation_rate:.2%} ({success_variations}/{len(variations)})")

            # 至少应该有一个变体能成功映射
            assert success_variations >= 1, f"字段 {target_field} 的所有变体都映射失败"

    def test_balance_sheet_configuration_integrity(self):
        """测试资产负债表配置完整性"""
        # 确保配置加载成功
        assert self.field_mapper.ensure_loaded(), "字段映射器配置加载失败"

        # 验证A股市场配置
        available_markets = self.field_mapper.config_loader.get_available_markets()
        assert "a_stock" in available_markets, "缺少A股市场配置"

        # 验证A股字段数量（原有195个 + 新增319个 = 514个）
        a_stock_config = self.field_mapper.config_loader.get_market_config('a_stock')
        assert a_stock_config is not None, "A股市场配置为空"
        assert len(a_stock_config.fields) >= 500, f"A股字段数量不足: {len(a_stock_config.fields)} < 500"

        print(f"✅ 配置完整性验证通过:")
        print(f"   可用市场: {available_markets}")
        print(f"   A股字段数量: {len(a_stock_config.fields)}")

    def test_balance_sheet_mapping_mechanism_performance(self):
        """测试资产负债表映射机制性能"""
        import time

        # 性能测试：批量查询
        test_queries = ["总资产", "流动资产", "应收账款", "存货", "应付账款"] * 10  # 50个查询

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

        # 期望平均耗时小于0.1秒
        assert avg_time_per_query < 0.1, f"映射性能过慢: {avg_time_per_query:.3f}秒/查询 > 0.1秒"

    def test_balance_sheet_edge_cases(self):
        """测试资产负债表边界情况"""
        # 测试空查询
        mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", [])
        assert mapped_fields == []
        assert suggestions == []

        # 测试不存在的字段
        mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", ["不存在的字段"])
        assert len(mapped_fields) == 0
        assert len(suggestions) > 0  # 应该有建议

        # 测试未知股票代码（但字段映射仍应工作）
        mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("UNKNOWN999", ["总资产"])
        # 即使股票代码未知，也应该尝试字段映射

        # 测试混合查询（有成功的，有失败的）
        mapped_fields, suggestions = self.field_mapper.resolve_fields_sync("600519", ["总资产", "不存在的字段"])
        assert len(mapped_fields) >= 1  # 至少总资产应该成功
        assert len(suggestions) >= 1  # 应该有失败建议


if __name__ == '__main__':
    pytest.main([__file__, '-v'])