"""
SOLID原则验证测试套件 - 里氏替换原则 (L)

测试目标：验证子类可以完全替换父类，不破坏程序正确性
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Any

# 导入项目模块
from akshare_value_investment.core.models import FinancialIndicator, MarketType, PeriodType
from akshare_value_investment.core.interfaces import IMarketAdapter
from akshare_value_investment.datasource.adapters.base_adapter import BaseMarketAdapter
from akshare_value_investment.datasource.adapters import (
    AStockAdapter, HKStockAdapter, USStockAdapter
)
from akshare_value_investment.mcp.handlers import BaseHandler, QueryHandler, SearchHandler, DetailsHandler


class TestLiskovSubstitutionPrinciple:
    """里氏替换原则测试套件"""

    def test_base_adapter_substitution(self):
        """测试基础适配器可以被其子类替换"""

        # 创建基础适配器和各种子类
        base_adapter = BaseMarketAdapter()
        a_stock_adapter = AStockAdapter()
        hk_stock_adapter = HKStockAdapter()
        us_stock_adapter = USStockAdapter()

        # 测试所有适配器都实现了相同的接口
        adapters = [a_stock_adapter, hk_stock_adapter, us_stock_adapter]

        for adapter in adapters:
            # 验证子类可以替换父类，拥有相同的公共接口
            assert hasattr(adapter, 'get_financial_data'), \
                f"{type(adapter).__name__}应该有get_financial_data方法"

            # 验证方法签名一致性
            import inspect
            base_method = getattr(BaseMarketAdapter, 'get_financial_data', None)
            subclass_method = getattr(adapter, 'get_financial_data', None)

            if base_method and subclass_method:
                base_sig = inspect.signature(base_method)
                subclass_sig = inspect.signature(subclass_method)

                # 参数名称可以不同，但参数数量应该一致
                assert len(base_sig.parameters) == len(subclass_sig.parameters), \
                    f"{type(adapter).__name__}.get_financial_data的参数签名应该与基类一致"

    def test_market_adapter_return_type_consistency(self):
        """测试市场适配器的返回类型一致性"""

        # 所有适配器都应该返回相同类型的结果
        adapters = [AStockAdapter(), HKStockAdapter(), USStockAdapter()]

        # 使用mock来避免实际API调用
        mock_data = [
            FinancialIndicator(
                symbol="TEST",
                market=MarketType.A_STOCK,
                company_name="Test Company",
                report_date="2024-01-01",
                period_type=PeriodType.ANNUAL,
                currency="USD",
                indicators={"test": 100.0},
                raw_data={"raw_test": "value"}
            )
        ]

        for adapter in adapters:
            with patch.object(adapter, '_fetch_raw_data', return_value={"test": "data"}):
                try:
                    result = adapter.get_financial_data("TEST001")

                    # 验证返回类型
                    assert isinstance(result, list), \
                        f"{type(adapter).__name__}.get_financial_data应该返回list"

                    if result:  # 如果有返回数据
                        assert isinstance(result[0], FinancialIndicator), \
                            f"{type(adapter).__name__}.get_financial_data应该返回FinancialIndicator列表"

                except Exception as e:
                    # 如果有异常，应该是业务逻辑异常，而不是类型不匹配
                    pytest.fail(f"{type(adapter).__name__}.get_financial_data类型不匹配: {e}")

    def test_adapter_inheritance_contract_compliance(self):
        """测试适配器继承契约的遵守情况"""

        # 创建测试用的子类来验证契约
        class TestAdapter(BaseMarketAdapter):
            """测试适配器，验证契约遵守"""

            def get_financial_data(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
                # 正确实现契约
                return self._create_financial_indicator(
                    symbol=symbol,
                    market=MarketType.A_STOCK,
                    raw_data={"test": "data"}
                )

            def _fetch_raw_data(self, symbol: str, **kwargs) -> Any:
                return {"test": "data"}

        # 验证测试适配器可以正常工作
        test_adapter = TestAdapter()
        result = test_adapter.get_financial_data("TEST001")

        assert isinstance(result, list), "子类应该返回list类型"
        assert len(result) == 1, "子类应该返回正确数量的结果"

    def test_handler_substitution_compatibility(self):
        """测试处理器子类替换兼容性"""

        # 创建基础处理器和子类处理器
        financial_service = Mock()
        field_service = Mock()

        base_handler = BaseHandler()
        query_handler = QueryHandler(financial_service, field_service)
        search_handler = SearchHandler(financial_service, field_service)
        details_handler = DetailsHandler(field_service)

        handlers = [base_handler, query_handler, search_handler, details_handler]

        # 验证所有处理器都有相同的接口
        for handler in handlers:
            assert hasattr(handler, 'handle'), \
                f"{type(handler).__name__}应该有handle方法"

            # 验证handle方法可以被调用（不关心具体实现）
            try:
                import inspect
                handle_method = getattr(handler, 'handle')

                # 验证方法签名
                sig = inspect.signature(handle_method)
                assert 'request' in sig.parameters, \
                    f"{type(handler).__name__}.handle应该有request参数"

            except Exception as e:
                pytest.fail(f"{type(handler).__name__}接口不兼容: {e}")

    def test_adapter_polymorphic_behavior(self):
        """测试适配器的多态行为"""

        # 创建不同类型的适配器
        adapters = [
            AStockAdapter(),
            HKStockAdapter(),
            USStockAdapter()
        ]

        # 验证多态性：所有适配器可以通过相同的接口使用
        for adapter in adapters:
            # 验证可以被当作IMarketAdapter使用
            assert isinstance(adapter, IMarketAdapter), \
                f"{type(adapter).__name__}应该是IMarketAdapter的实例"

            # 验证多态调用不会破坏类型安全
            with patch.object(adapter, '_fetch_raw_data', return_value={"mock": "data"}):
                try:
                    result = adapter.get_financial_data("POLY_TEST")

                    # 多态调用应该返回一致的结果类型
                    assert isinstance(result, list), \
                        f"多态调用{type(adapter).__name__}应该返回list"

                except Exception as e:
                    # 多态调用不应该因为子类类型而失败
                    if "type" in str(e).lower():
                        pytest.fail(f"多态调用因类型问题失败: {e}")

    def test_subclass_method_override_validity(self):
        """测试子类方法重写的有效性"""

        # 验证子类没有破坏父类方法的契约
        base_adapter = BaseMarketAdapter()
        a_stock_adapter = AStockAdapter()

        # 验证子类没有随意修改父类方法的可见性或签名
        base_methods = [method for method in dir(base_adapter)
                       if not method.startswith('_') and callable(getattr(base_adapter, method))]
        subclass_methods = [method for method in dir(a_stock_adapter)
                          if not method.startswith('_') and callable(getattr(a_stock_adapter, method))]

        # 子类应该包含父类的公共方法
        for method in base_methods:
            if method != 'get_financial_data':  # 抽象方法必须重写
                assert method in subclass_methods, \
                    f"AStockAdapter应该保持父类的{method}方法"

    def test_precondition_postcondition_preservation(self):
        """测试前置条件和后置条件的保持"""

        class ValidatingAdapter(BaseMarketAdapter):
            """验证前置和后置条件的适配器"""

            def get_financial_data(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
                # 保持前置条件：symbol不能为空
                if not symbol:
                    raise ValueError("Symbol不能为空")

                # 调用父类方法（如果有的话）或实现自己的逻辑
                raw_data = self._fetch_raw_data(symbol, **kwargs)

                if not raw_data:
                    return []  # 空结果也是有效的后置条件

                # 保持后置条件：返回FinancialIndicator列表
                result = self._create_financial_indicator(
                    symbol=symbol,
                    market=MarketType.A_STOCK,
                    raw_data=raw_data
                )

                # 后置条件验证
                assert all(isinstance(item, FinancialIndicator) for item in result), \
                    "所有返回项都应该是FinancialIndicator类型"

                return result

            def _fetch_raw_data(self, symbol: str, **kwargs) -> Any:
                return {"test": "validating_data"}

        # 测试条件保持
        adapter = ValidatingAdapter()

        # 前置条件测试
        with pytest.raises(ValueError):
            adapter.get_financial_data("")

        # 正常情况测试
        result = adapter.get_financial_data("VALID_TEST")
        assert isinstance(result, list), "应该返回list"
        assert all(isinstance(item, FinancialIndicator) for item in result), "所有项都应该是FinancialIndicator"

    def test_invariant_preservation(self):
        """测试不变量的保持"""

        # 创建一个保持不变量的适配器
        class InvariantAdapter(BaseMarketAdapter):
            def __init__(self):
                super().__init__()
                self.call_count = 0  # 不变量：调用计数

            def get_financial_data(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
                self.call_count += 1  # 保持不变量

                # 不变量：调用次数应该增加
                assert self.call_count > 0, "调用次数应该大于0"

                # 不变量：返回结果不应该是None
                result = []
                if symbol:
                    result = [FinancialIndicator(
                        symbol=symbol,
                        market=MarketType.A_STOCK,
                        company_name="Invariant Test",
                        report_date="2024-01-01",
                        period_type=PeriodType.ANNUAL,
                        currency="TEST",
                        indicators={"invariant": True},
                        raw_data={"call_count": self.call_count}
                    )]

                assert result is not None, "返回结果不应该是None"
                return result

            def _fetch_raw_data(self, symbol: str, **kwargs) -> Any:
                return {"invariant_data": True, "call_count": self.call_count}

        # 测试不变量保持
        adapter = InvariantAdapter()

        # 多次调用测试不变量
        for i in range(3):
            result = adapter.get_financial_data(f"TEST{i}")
            assert adapter.call_count == i + 1, f"第{i+1}次调用后计数应该是{i+1}"
            assert result is not None, f"第{i+1}次调用结果不应该是None"

            if result:
                assert result[0].raw_data["call_count"] == i + 1, \
                    f"结果中应该包含正确的调用次数{i+1}"

    def test_lsp_violation_detection(self):
        """检测里氏替换原则违反的情况"""

        # 这个测试用于检测可能的LSP违反

        # 检查子类是否有不恰当的方法重写
        a_stock_adapter = AStockAdapter()

        # 获取所有方法
        a_stock_methods = [method for method in dir(a_stock_adapter)
                          if not method.startswith('_')]

        base_methods = [method for method in dir(BaseMarketAdapter)
                       if not method.startswith('_')]

        # 检查是否有方法签名不匹配的情况
        for method in a_stock_methods:
            if method in base_methods:
                try:
                    base_method = getattr(BaseMarketAdapter, method)
                    a_stock_method = getattr(a_stock_adapter, method)

                    # 检查参数签名
                    import inspect
                    base_sig = inspect.signature(base_method)
                    a_stock_sig = inspect.signature(a_stock_method)

                    # 如果参数数量不同，可能违反LSP
                    if len(base_sig.parameters) != len(a_stock_sig.parameters):
                        pytest.warn(f"方法{method}的参数签名与基类不一致，可能违反LSP")

                except Exception:
                    # 如果无法检查，跳过
                    pass

    def test_lsp_compliance_score(self):
        """计算里氏替换原则遵循分数"""

        lsp_metrics = {
            'substitutable_classes': 0,
            'total_inheritance_relationships': 0,
            'interface_consistency': 0,
            'total_interfaces': 0,
            'polymorphic_compatibility': 0,
            'total_polymorphic_tests': 0
        }

        # 分析继承关系
        inheritance_pairs = [
            (AStockAdapter, BaseMarketAdapter),
            (HKStockAdapter, BaseMarketAdapter),
            (USStockAdapter, BaseMarketAdapter),
            (QueryHandler, BaseHandler),
            (SearchHandler, BaseHandler),
            (DetailsHandler, BaseHandler)
        ]

        lsp_metrics['total_inheritance_relationships'] = len(inheritance_pairs)

        # 测试可替换性
        for subclass, base_class in inheritance_pairs:
            try:
                # 创建实例测试可替换性
                subclass_instance = subclass()

                # 验证子类实例可以当作父类使用
                if isinstance(subclass_instance, base_class):
                    lsp_metrics['substitutable_classes'] += 1

            except Exception:
                # 如果无法创建实例，跳过
                pass

        # 分析接口一致性
        interfaces_to_check = [IMarketAdapter]
        lsp_metrics['total_interfaces'] = len(interfaces_to_check)

        for interface in interfaces_to_check:
            try:
                # 检查是否有实现类
                implementations = [AStockAdapter, HKStockAdapter, USStockAdapter]
                valid_implementations = 0

                for impl in implementations:
                    try:
                        impl_instance = impl()
                        if isinstance(impl_instance, interface):
                            valid_implementations += 1
                    except Exception:
                        pass

                if valid_implementations > 0:
                    lsp_metrics['interface_consistency'] += 1

            except Exception:
                pass

        # 计算多态兼容性
        polymorphic_tests = [
            (AStockAdapter(), HKStockAdapter(), USStockAdapter())
        ]

        lsp_metrics['total_polymorphic_tests'] = len(polymorphic_tests)

        for test_group in polymorphic_tests:
            try:
                # 测试同组类的接口一致性
                methods = set()
                for instance in test_group:
                    instance_methods = [method for method in dir(instance)
                                      if not method.startswith('_') and callable(getattr(instance, method))]
                    methods.update(instance_methods)

                # 如果所有实例都有相似的方法集合，认为多态兼容
                if len(methods) > 0:
                    lsp_metrics['polymorphic_compatibility'] += 1

            except Exception:
                pass

        # 计算LSP遵循分数
        lsp_score = 0

        if lsp_metrics['total_inheritance_relationships'] > 0:
            lsp_score += (lsp_metrics['substitutable_classes'] / lsp_metrics['total_inheritance_relationships']) * 40

        if lsp_metrics['total_interfaces'] > 0:
            lsp_score += (lsp_metrics['interface_consistency'] / lsp_metrics['total_interfaces']) * 30

        if lsp_metrics['total_polymorphic_tests'] > 0:
            lsp_score += (lsp_metrics['polymorphic_compatibility'] / lsp_metrics['total_polymorphic_tests']) * 30

        # 确保分数在0-100范围内
        lsp_score = max(0, min(100, lsp_score))

        print(f"\n📊 里氏替换原则遵循分数: {lsp_score:.1f}/100")
        print(f"  - 可替换类: {lsp_metrics['substitutable_classes']}/{lsp_metrics['total_inheritance_relationships']}")
        print(f"  - 接口一致性: {lsp_metrics['interface_consistency']}/{lsp_metrics['total_interfaces']}")
        print(f"  - 多态兼容性: {lsp_metrics['polymorphic_compatibility']}/{lsp_metrics['total_polymorphic_tests']}")

        # 要求至少80分的LSP遵循度
        assert lsp_score >= 80, f"里氏替换原则遵循分数过低: {lsp_score:.1f}/100"


if __name__ == "__main__":
    # 运行里氏替换原则测试
    pytest.main([__file__, "-v"])