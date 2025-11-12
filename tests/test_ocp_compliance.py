"""
SOLID原则验证测试套件 - 开闭原则 (O)

测试目标：验证系统对扩展开放，对修改封闭
"""

import pytest
import inspect
from unittest.mock import Mock, patch
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# 导入项目模块
from akshare_value_investment.core.models import FinancialIndicator, MarketType, PeriodType
from akshare_value_investment.core.interfaces import IMarketAdapter
from akshare_value_investment.datasource.adapters.base_adapter import BaseMarketAdapter
from akshare_value_investment.datasource.adapters import (
    AStockAdapter, HKStockAdapter, USStockAdapter, AdapterManager
)
from akshare_value_investment.container import ProductionContainer
from akshare_value_investment.mcp.handlers import BaseHandler


class TestOpenClosedPrinciple:
    """开闭原则测试套件"""

    def test_adapter_interface_extensibility(self):
        """测试适配器接口的可扩展性"""

        # 验证IMarketAdapter接口是抽象的，可以扩展
        assert hasattr(IMarketAdapter, 'get_financial_data'), "IMarketAdapter应该定义可扩展的方法"

        # 创建一个新的市场适配器来验证扩展性
        class TestMarketAdapter(BaseMarketAdapter):
            """新的测试市场适配器，演示开闭原则"""

            def get_financial_data(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
                """实现IMarketAdapter接口，展示扩展能力"""
                return [
                    FinancialIndicator(
                        symbol=symbol,
                        market=MarketType.A_STOCK,  # 用于测试
                        company_name="Test Company",
                        report_date="2024-01-01",
                        period_type=PeriodType.ANNUAL,
                        currency="TEST",
                        indicators={"test_field": 100.0},
                        raw_data={"test_raw_field": "test_value"}
                    )
                ]

            def _fetch_raw_data(self, symbol: str, **kwargs) -> Any:
                """实现基类的抽象方法"""
                return [{"test": "data"}]

        # 验证新适配器可以正常工作
        test_adapter = TestMarketAdapter()
        result = test_adapter.get_financial_data("TEST001")

        assert len(result) > 0, "新适配器应该能够正常工作"
        assert result[0].symbol == "TEST001", "新适配器应该正确处理symbol"

    def test_base_adapter_inheritance_correctness(self):
        """测试基础适配器的继承正确性"""

        # 验证BaseMarketAdapter是抽象基类，支持扩展
        assert hasattr(BaseMarketAdapter, '__abstractmethods__'), "BaseMarketAdapter应该是抽象基类"

        # 验证继承层次结构
        assert issubclass(AStockAdapter, BaseMarketAdapter), "AStockAdapter应该继承BaseMarketAdapter"
        assert issubclass(HKStockAdapter, BaseMarketAdapter), "HKStockAdapter应该继承BaseMarketAdapter"
        assert issubclass(USStockAdapter, BaseMarketAdapter), "USStockAdapter应该继承BaseMarketAdapter"

        # 验证每个子类都实现了必要的方法
        for adapter_class in [AStockAdapter, HKStockAdapter, USStockAdapter]:
            adapter = adapter_class()
            assert hasattr(adapter, 'get_financial_data'), f"{adapter_class.__name__}应该实现get_financial_data方法"
            assert hasattr(adapter, '_fetch_raw_data'), f"{adapter_class.__name__}应该实现_fetch_raw_data方法"

    def test_handler_extensibility(self):
        """测试处理器的可扩展性"""

        # 验证BaseHandler支持扩展
        assert hasattr(BaseHandler, '__abstractmethods__'), "BaseHandler应该支持扩展"

        # 创建新的处理器来演示开闭原则
        class TestHandler(BaseHandler):
            """新的测试处理器"""

            def __init__(self, test_service=None):
                super().__init__()
                self.test_service = test_service or Mock()

            async def handle(self, request: Dict[str, Any]):
                """实现BaseHandler的抽象方法"""
                return Mock(
                    isError=False,
                    content=[Mock(text="Test response")]
                )

        # 验证新处理器可以正常工作
        test_handler = TestHandler()
        assert hasattr(test_handler, 'handle'), "新处理器应该实现handle方法"

    def test_adapter_manager_extension_mechanism(self):
        """测试适配器管理器的扩展机制"""

        # 当前AdapterManager的扩展性测试
        adapter_manager = AdapterManager()

        # 验证当前支持的适配器
        current_adapters = adapter_manager.adapters
        assert len(current_adapters) >= 3, "AdapterManager应该支持至少3种市场"

        # 测试添加新适配器需要修改现有代码（这是一个OCP违反点）
        # 这个测试用于检测需要改进的地方
        try:
            # 尝试获取不存在的市场类型
            new_market_adapter = adapter_manager.get_adapter(MarketType.A_STOCK)
            assert new_market_adapter is not None, "应该能获取存在的适配器"
        except AttributeError:
            pytest.warn("AdapterManager可能需要改进以支持动态适配器注册")

    def test_dependency_container_extensibility(self):
        """测试依赖注入容器的可扩展性"""

        # 验证容器支持添加新的依赖
        container = ProductionContainer()

        # 验证现有服务可以获取
        financial_service = container.financial_query_service()
        assert financial_service is not None, "容器应该提供财务查询服务"

        # 测试容器结构是否支持扩展
        container_attributes = [attr for attr in dir(container) if not attr.startswith('_')]

        # 容器应该有足够的服务支持
        expected_services = [
            'financial_query_service',
            'field_mapper',
            'adapter_manager'
        ]

        for service in expected_services:
            if hasattr(container, service):
                service_instance = getattr(container, service)
                assert service_instance is not None, f"容器应该提供{service}服务"

    def test_interface_separation_for_extension(self):
        """测试接口分离是否支持扩展"""

        # 验证接口设计支持实现扩展
        from akshare_value_investment.services.interfaces import IFieldMapper, IResponseFormatter

        # 创建新的字段映射器实现
        class TestFieldMapper:
            """测试字段映射器实现"""

            async def resolve_fields(self, symbol: str, fields: List[str]) -> tuple:
                return fields, []

            def map_keyword_to_field(self, keyword: str, market_id: str = None):
                return keyword, 1.0, None

            def search_similar_fields(self, keyword: str, market_id: str = None, max_results: int = 5):
                return []

            def get_available_fields(self, market_id: str = None):
                return []

            def get_field_details(self, field_name: str):
                return None

        # 验证新实现可以正常使用
        test_mapper = TestFieldMapper()
        assert hasattr(test_mapper, 'resolve_fields'), "新实现应该支持接口方法"

        # 测试新实现的扩展性
        result_fields, suggestions = test_mapper.resolve_fields("TEST001", ["field1", "field2"])
        assert isinstance(result_fields, list), "新实现应该返回正确的数据类型"

    def test_extensibility_without_modification(self):
        """测试在不修改现有代码的情况下进行扩展"""

        # 这个测试演示如何在不修改现有代码的情况下添加新功能

        # 1. 创建新的市场类型（枚举扩展）
        class ExtendedMarketType(MarketType):
            """扩展的市场类型"""
            CRYPTOCURRENCY = "crypto"  # 新增加密货币市场

        # 2. 创建对应的适配器
        class CryptoAdapter(BaseMarketAdapter):
            """加密货币市场适配器"""

            def get_financial_data(self, symbol: str, **kwargs) -> List[FinancialIndicator]:
                return [
                    FinancialIndicator(
                        symbol=symbol,
                        market=MarketType.A_STOCK,  # 使用现有类型进行测试
                        company_name="Crypto Asset",
                        report_date="2024-01-01",
                        period_type=PeriodType.ANNUAL,
                        currency="USD",
                        indicators={"market_cap": 1000000.0},
                        raw_data={"price": 50000.0}
                    )
                ]

            def _fetch_raw_data(self, symbol: str, **kwargs) -> Any:
                return [{"crypto_data": "test"}]

        # 3. 验证新适配器可以独立工作，不需要修改现有代码
        crypto_adapter = CryptoAdapter()
        crypto_data = crypto_adapter.get_financial_data("BTC")

        assert len(crypto_data) > 0, "新适配器应该能正常工作"
        assert crypto_data[0].symbol == "BTC", "新适配器应该正确处理symbol"

    def test_closed_for_modification_validation(self):
        """验证现有代码对修改的封闭性"""

        # 验证基类的抽象方法不会被随意修改
        base_adapter_methods = inspect.getmembers(BaseMarketAdapter, predicate=inspect.isfunction)
        abstract_methods = [name for name, _ in base_adapter_methods if name.startswith('_fetch_raw_data')]

        # 关键的抽象方法不应该被随意修改
        assert '_fetch_raw_data' in [method for method, _ in base_adapter_methods], \
            "BaseMarketAdapter应该保持抽象方法的稳定性"

        # 验证接口的稳定性
        interface_methods = inspect.getmembers(IMarketAdapter, predicate=inspect.isfunction)
        interface_method_names = [name for name, _ in interface_methods if not name.startswith('_')]

        # 核心接口方法应该保持稳定
        expected_stable_methods = ['get_financial_data']
        for method in expected_stable_methods:
            assert method in interface_method_names, f"关键接口方法{method}应该保持稳定"

    def test_ocp_violation_detection(self):
        """检测开闭原则违反的情况"""

        # 这个测试用于检测可能违反开闭原则的代码模式

        # 检查AdapterManager是否存在硬编码的适配器列表
        adapter_manager = AdapterManager()
        adapters_dict = adapter_manager.adapters

        # 如果适配器是硬编码的，可能违反OCP
        if isinstance(adapters_dict, dict) and len(adapters_dict) > 0:
            # 这是一个潜在的OCP违反点，但为了向后兼容可能是必要的
            pytest.warn("AdapterManager使用硬编码适配器列表，可能违反开闭原则。建议使用动态注册机制。")

        # 检查是否有使用大量if-else来处理不同类型的情况
        # 这通常表明需要使用多态来改进
        financial_service_source = inspect.getsource(FinancialIndicatorQueryService)
        conditional_patterns = ['if market', 'elif market', 'switch', 'case market']

        for pattern in conditional_patterns:
            if pattern.lower() in financial_service_source.lower():
                pytest.warn(f"在FinancialIndicatorQueryService中发现条件分支模式'{pattern}'，可能违反开闭原则")

    def test_ocp_compliance_score(self):
        """计算开闭原则遵循分数"""

        ocp_metrics = {
            'extensible_interfaces': 0,
            'total_interfaces': 0,
            'extensible_classes': 0,
            'total_classes': 0,
            'extension_mechanisms': 0,
            'hardcoded_elements': 0
        }

        # 分析接口的可扩展性
        interfaces_to_check = [IMarketAdapter]
        for interface in interfaces_to_check:
            ocp_metrics['total_interfaces'] += 1
            if hasattr(interface, '__abstractmethods__'):
                ocp_metrics['extensible_interfaces'] += 1

        # 分析类的可扩展性
        classes_to_check = [BaseMarketAdapter, BaseHandler]
        for cls in classes_to_check:
            ocp_metrics['total_classes'] += 1
            if hasattr(cls, '__abstractmethods__') or inspect.isabstract(cls):
                ocp_metrics['extensible_classes'] += 1

        # 分析扩展机制
        if hasattr(ProductionContainer, 'providers'):
            ocp_metrics['extension_mechanisms'] += 1

        # 分析硬编码元素
        adapter_manager = AdapterManager()
        if hasattr(adapter_manager, 'adapters') and isinstance(adapter_manager.adapters, dict):
            ocp_metrics['hardcoded_elements'] += 1

        # 计算遵循分数
        extensibility_score = 0
        if ocp_metrics['total_interfaces'] > 0:
            extensibility_score += (ocp_metrics['extensible_interfaces'] / ocp_metrics['total_interfaces']) * 40

        if ocp_metrics['total_classes'] > 0:
            extensibility_score += (ocp_metrics['extensible_classes'] / ocp_metrics['total_classes']) * 30

        if ocp_metrics['extension_mechanisms'] > 0:
            extensibility_score += 20

        # 硬编码元素降低分数
        extensibility_score -= (ocp_metrics['hardcoded_elements'] * 10)

        # 确保分数在0-100范围内
        extensibility_score = max(0, min(100, extensibility_score))

        print(f"\n📊 开闭原则遵循分数: {extensibility_score:.1f}/100")
        print(f"  - 可扩展接口: {ocp_metrics['extensible_interfaces']}/{ocp_metrics['total_interfaces']}")
        print(f"  - 可扩展类: {ocp_metrics['extensible_classes']}/{ocp_metrics['total_classes']}")
        print(f"  - 扩展机制: {ocp_metrics['extension_mechanisms']}")
        print(f"  - 硬编码元素: {ocp_metrics['hardcoded_elements']}")

        # 要求至少70分的开闭原则遵循度
        assert extensibility_score >= 70, f"开闭原则遵循分数过低: {extensibility_score:.1f}/100"


if __name__ == "__main__":
    # 运行开闭原则测试
    pytest.main([__file__, "-v"])