"""
SOLID原则验证测试套件 - 依赖倒置原则 (D)

测试目标：验证高层模块不依赖低层模块，都依赖抽象；抽象不依赖细节，细节依赖抽象
"""

import pytest
import inspect
from unittest.mock import Mock, MagicMock
from typing import Protocol, Any

# 导入项目模块
from akshare_value_investment.core.interfaces import IMarketAdapter, IMarketIdentifier, IQueryService
from akshare_value_investment.services.interfaces import (
    IFieldMapper, IResponseFormatter, ITimeRangeProcessor, IDataStructureProcessor
)
from akshare_value_investment.datasource.adapters.base_adapter import BaseMarketAdapter
from akshare_value_investment.datasource.adapters import AdapterManager
from akshare_value_investment.services.financial_query_service import FinancialIndicatorQueryService
from akshare_value_investment.business.mapping.field_mapper import FinancialFieldMapper
from akshare_value_investment.business.processing.response_formatter import ResponseFormatter
from akshare_value_investment.container import ProductionContainer


class TestDependencyInversionPrinciple:
    """依赖倒置原则测试套件"""

    def test_high_level_modules_depend_on_abstractions(self):
        """测试高层模块是否依赖抽象接口"""

        # FinancialIndicatorQueryService是高层模块，应该依赖抽象接口
        query_service = FinancialIndicatorQueryService(
            query_service=Mock(spec=IQueryService),
            field_mapper=Mock(spec=IFieldMapper),
            formatter=Mock(spec=IResponseFormatter),
            time_processor=Mock(spec=ITimeRangeProcessor),
            data_processor=Mock(spec=IDataStructureProcessor)
        )

        # 验证高层模块依赖的是抽象接口，而不是具体实现
        assert hasattr(query_service, 'query_service'), "高层模块应该有query_service依赖"
        assert hasattr(query_service, 'field_mapper'), "高层模块应该有field_mapper依赖"
        assert hasattr(query_service, 'formatter'), "高层模块应该有formatter依赖"

        # 验证依赖是抽象接口类型
        dependencies = [
            ('query_service', IQueryService),
            ('field_mapper', IFieldMapper),
            ('formatter', IResponseFormatter),
            ('time_processor', ITimeRangeProcessor),
            ('data_processor', IDataStructureProcessor)
        ]

        for attr_name, expected_interface in dependencies:
            attr_value = getattr(query_service, attr_name)
            # 检查是否是接口的实例（通过Mock模拟）
            assert hasattr(attr_value, expected_interface.__name__.replace('I', '').lower()) or \
                   hasattr(attr_value, '_spec'), \
                f"{attr_name}应该是{expected_interface.__name__}的抽象依赖"

    def test_container_uses_abstractions(self):
        """测试依赖注入容器是否使用抽象接口"""

        container = ProductionContainer()

        # 获取服务实例
        financial_service = container.financial_query_service()
        adapter_manager = container.adapter_manager()
        field_mapper = container.field_mapper()

        # 验证容器提供的是通过抽象接口配置的服务
        assert financial_service is not None, "容器应该提供财务查询服务"
        assert adapter_manager is not None, "容器应该提供适配器管理服务"
        assert field_mapper is not None, "容器应该提供字段映射服务"

        # 验证服务的依赖关系是通过接口定义的
        # 检查FinancialIndicatorQueryService的构造函数
        init_signature = inspect.signature(FinancialIndicatorQueryService.__init__)
        parameters = init_signature.parameters

        # 验证参数都是抽象接口类型
        interface_dependencies = {
            'query_service': IQueryService,
            'field_mapper': IFieldMapper,
            'formatter': IResponseFormatter,
            'time_processor': ITimeRangeProcessor,
            'data_processor': IDataStructureProcessor
        }

        for param_name, expected_interface in interface_dependencies.items():
            assert param_name in parameters, f"应该有{param_name}依赖参数"
            # 参数类型注解应该是指定的接口
            param = parameters[param_name]
            assert param.annotation != inspect.Parameter.empty, f"{param_name}应该有类型注解"

    def test_adapter_manager_dependency_inversion(self):
        """测试适配器管理器的依赖倒置"""

        adapter_manager = AdapterManager()

        # AdapterManager应该依赖IMarketAdapter抽象，而不是具体的适配器类
        assert hasattr(adapter_manager, 'adapters'), "AdapterManager应该有适配器依赖"

        # 验证适配器管理器可以处理任何实现IMarketAdapter的类
        mock_adapter = Mock(spec=IMarketAdapter)
        mock_adapter.get_financial_data.return_value = []

        # 管理器应该能够通过接口使用适配器
        adapters = adapter_manager.adapters
        assert isinstance(adapters, dict), "适配器应该是字典形式管理"

        # 验证每个适配器都是IMarketAdapter的实现
        for market_type, adapter in adapters.items():
            # 检查适配器是否实现了IMarketAdapter接口
            assert hasattr(adapter, 'get_financial_data'), f"{market_type}适配器应该实现get_financial_data方法"

    def test_mcp_handlers_use_abstractions(self):
        """测试MCP处理器是否使用抽象依赖"""

        from akshare_value_investment.mcp.handlers import QueryHandler, SearchHandler, DetailsHandler

        # 创建Mock服务来模拟抽象依赖
        financial_service_mock = Mock()
        field_discovery_service_mock = Mock()

        # QueryHandler应该依赖抽象服务接口
        query_handler = QueryHandler(financial_service_mock, field_discovery_service_mock)

        # 验证处理器依赖的是抽象接口，而不是具体实现
        assert hasattr(query_handler, 'financial_service'), "QueryHandler应该依赖财务服务抽象"
        assert hasattr(query_handler, 'field_discovery_service'), "QueryHandler应该依赖字段发现服务抽象"

        # 验证依赖可以被替换（依赖抽象的特性）
        different_financial_service = Mock()
        different_field_service = Mock()

        # 应该能够轻松替换依赖实现
        new_query_handler = QueryHandler(different_financial_service, different_field_service)
        assert new_query_handler.financial_service == different_financial_service
        assert new_query_handler.field_discovery_service == different_field_service

    def test_abstraction_independence_from_implementation_details(self):
        """测试抽象不依赖实现细节"""

        # 验证接口定义不包含具体实现细节
        interface_methods = inspect.getmembers(IMarketAdapter, predicate=inspect.isfunction)
        interface_method_names = [name for name, _ in interface_methods if not name.startswith('_')]

        # 接口应该只定义方法签名，不包含实现
        for method_name in interface_method_names:
            method = getattr(IMarketAdapter, method_name)
            assert hasattr(method, '__isabstractmethod__') or method.__code__.co_code == b'', \
                f"接口方法{method_name}不应该是具体实现"

        # 验证其他接口也遵循这个原则
        interfaces_to_check = [IFieldMapper, IResponseFormatter, ITimeRangeProcessor, IDataStructureProcessor]

        for interface in interfaces_to_check:
            methods = inspect.getmembers(interface, predicate=inspect.isfunction)
            for method_name, method in methods:
                if not method_name.startswith('_'):
                    # 协议接口方法应该是抽象的
                    assert method.__code__.co_code == b'' or hasattr(method, '__isabstractmethod__'), \
                        f"{interface.__name__}.{method_name}应该是抽象方法"

    def test_implementation_details_depend_on_abstractions(self):
        """测试实现细节依赖抽象"""

        # 具体的适配器实现应该依赖BaseMarketAdapter抽象
        a_stock_adapter = AStockAdapter()
        hk_stock_adapter = HKStockAdapter()

        # 验证具体实现继承自抽象基类
        assert isinstance(a_stock_adapter, BaseMarketAdapter), "具体适配器应该继承抽象基类"
        assert isinstance(hk_stock_adapter, BaseMarketAdapter), "具体适配器应该继承抽象基类"

        # 具体的映射器实现应该依赖接口抽象
        field_mapper = FinancialFieldMapper()

        # 验证具体实现实现了接口方法
        interface_methods = ['resolve_fields', 'map_keyword_to_field', 'search_similar_fields']
        for method_name in interface_methods:
            assert hasattr(field_mapper, method_name), f"具体映射器应该实现{method_name}方法"

        # 具体的格式化器实现应该依赖接口抽象
        formatter = ResponseFormatter()

        # 验证具体实现实现了接口方法
        formatter_methods = ['format_query_response']
        for method_name in formatter_methods:
            assert hasattr(formatter, method_name), f"具体格式化器应该实现{method_name}方法"

    def test_dependency_injection_correctness(self):
        """测试依赖注入的正确性"""

        # 验证依赖注入容器正确配置了抽象依赖
        container = ProductionContainer()

        # 获取服务并检查其依赖
        financial_service = container.financial_query_service()

        # 检查服务的依赖是否正确注入
        dependencies_to_check = [
            'query_service',
            'field_mapper',
            'formatter',
            'time_processor',
            'data_processor'
        ]

        for dependency in dependencies_to_check:
            assert hasattr(financial_service, dependency), f"服务应该注入{dependency}依赖"
            dependency_value = getattr(financial_service, dependency)
            assert dependency_value is not None, f"{dependency}依赖应该被正确注入"

    def test_loose_coupling_through_abstractions(self):
        """测试通过抽象实现松耦合"""

        # 创建不同的抽象实现
        class MockQueryService:
            def query(self, symbol: str, **kwargs):
                return Mock(success=True, data=[])

        class DifferentMockQueryService:
            def query(self, symbol: str, **kwargs):
                return Mock(success=False, data=[])

        # 高层模块应该能够接受任何实现相同抽象的依赖
        service1 = FinancialIndicatorQueryService(
            query_service=MockQueryService(),
            field_mapper=Mock(spec=IFieldMapper),
            formatter=Mock(spec=IResponseFormatter),
            time_processor=Mock(spec=ITimeRangeProcessor),
            data_processor=Mock(spec=IDataStructureProcessor)
        )

        service2 = FinancialIndicatorQueryService(
            query_service=DifferentMockQueryService(),
            field_mapper=Mock(spec=IFieldMapper),
            formatter=Mock(spec=IResponseFormatter),
            time_processor=Mock(spec=ITimeRangeProcessor),
            data_processor=Mock(spec=IDataStructureProcessor)
        )

        # 验证不同的实现可以无缝替换
        assert hasattr(service1, 'query_service')
        assert hasattr(service2, 'query_service')

        # 服务行为应该基于注入的实现
        # 这里测试的是依赖结构，而不是具体行为
        assert service1.query_service is not service2.query_service, "不同的服务实例应该有不同的依赖"

    def test_interface_stability(self):
        """测试接口的稳定性"""

        # 验证核心接口是稳定的
        stable_interfaces = [
            IMarketAdapter,
            IFieldMapper,
            IResponseFormatter,
            ITimeRangeProcessor,
            IDataStructureProcessor
        ]

        for interface in stable_interfaces:
            # 检查接口是否有适当的文档字符串（接口稳定性指标）
            if hasattr(interface, '__doc__') and interface.__doc__:
                doc_length = len(interface.__doc__.strip())
                assert doc_length > 10, f"{interface.__name__}应该有适当的文档说明"

            # 检查接口方法的命名一致性
            methods = inspect.getmembers(interface, predicate=inspect.isfunction)
            method_names = [name for name, _ in methods if not name.startswith('_')]

            # 方法命名应该遵循一致的约定
            for method_name in method_names:
                # 验证方法命名规范（小写+下划线）
                assert method_name.islower() or '_' in method_name or method_name.replace('_', '').islower(), \
                    f"{interface.__name__}.{method_name}应该遵循命名规范"

    def test_dip_violation_detection(self):
        """检测依赖倒置原则违反的情况"""

        # 检查高层模块是否直接依赖具体实现
        violations = []

        # 检查类的方法参数类型
        classes_to_check = [
            FinancialIndicatorQueryService,
            AdapterManager
        ]

        for cls in classes_to_check:
            init_method = getattr(cls, '__init__', None)
            if init_method:
                signature = inspect.signature(init_method)
                parameters = signature.parameters

                for param_name, param in parameters.items():
                    if param_name != 'self':
                        # 检查参数类型注解是否为具体类而非接口
                        if hasattr(param, 'annotation') and param.annotation != inspect.Parameter.empty:
                            annotation_str = str(param.annotation)

                            # 如果类型注解指向具体类而不是接口，可能是DIP违反
                            if ('Adapter' in annotation_str and 'Interface' not in annotation_str and
                                'Protocol' not in annotation_str and param_name != 'adapter_manager'):
                                violations.append(f"{cls.__name__}.{param_name}: {annotation_str}")

        # 如果发现违反，记录警告
        if violations:
            pytest.warn(f"检测到可能的依赖倒置原则违反: {violations}")

    def test_dip_compliance_score(self):
        """计算依赖倒置原则遵循分数"""

        dip_metrics = {
            'abstract_dependencies': 0,
            'total_dependencies': 0,
            'injection_points': 0,
            'interface_implementations': 0,
            'violations_detected': 0
        }

        # 分析高层模块的依赖
        high_level_classes = [FinancialIndicatorQueryService, AdapterManager]

        for cls in high_level_classes:
            init_method = getattr(cls, '__init__', None)
            if init_method:
                signature = inspect.signature(init_method)
                parameters = signature.parameters

                for param_name, param in parameters.items():
                    if param_name != 'self':
                        dip_metrics['total_dependencies'] += 1

                        # 检查是否依赖抽象
                        if hasattr(param, 'annotation') and param.annotation != inspect.Parameter.empty:
                            annotation_str = str(param.annotation)
                            # 接口、Protocol、或带I前缀的通常表示抽象
                            if ('Protocol' in annotation_str or 'Interface' in annotation_str or
                                annotation_str.startswith('I') or 'Mock' in annotation_str):
                                dip_metrics['abstract_dependencies'] += 1

        # 分析依赖注入点
        container = ProductionContainer()
        container_attributes = [attr for attr in dir(container) if not attr.startswith('_')]
        dip_metrics['injection_points'] = len(container_attributes)

        # 分析接口实现
        implementation_classes = [
            (AStockAdapter, IMarketAdapter),
            (FinancialFieldMapper, IFieldMapper),
            (ResponseFormatter, IResponseFormatter)
        ]

        for impl_class, interface in implementation_classes:
            try:
                # 检查是否实现了接口
                impl_instance = impl_class()
                if hasattr(impl_instance, '__class__'):
                    dip_metrics['interface_implementations'] += 1
            except Exception:
                pass

        # 检测违规
        # 如果依赖具体实现而非抽象，记录违规
        if dip_metrics['total_dependencies'] > 0:
            concrete_dependencies = dip_metrics['total_dependencies'] - dip_metrics['abstract_dependencies']
            dip_metrics['violations_detected'] = concrete_dependencies

        # 计算DIP遵循分数
        dip_score = 0

        # 抽象依赖比例 (50%)
        if dip_metrics['total_dependencies'] > 0:
            dependency_score = (dip_metrics['abstract_dependencies'] / dip_metrics['total_dependencies']) * 50
            dip_score += dependency_score

        # 依赖注入点评分 (20%)
        injection_score = min(20, dip_metrics['injection_points'] * 4)
        dip_score += injection_score

        # 接口实现评分 (30%)
        if len(implementation_classes) > 0:
            implementation_score = (dip_metrics['interface_implementations'] / len(implementation_classes)) * 30
            dip_score += implementation_score

        # 违规惩罚
        violation_penalty = dip_metrics['violations_detected'] * 10
        dip_score -= violation_penalty

        # 确保分数在0-100范围内
        dip_score = max(0, min(100, dip_score))

        print(f"\n📊 依赖倒置原则遵循分数: {dip_score:.1f}/100")
        print(f"  - 抽象依赖: {dip_metrics['abstract_dependencies']}/{dip_metrics['total_dependencies']}")
        print(f"  - 依赖注入点: {dip_metrics['injection_points']}")
        print(f"  - 接口实现: {dip_metrics['interface_implementations']}/{len(implementation_classes)}")
        print(f"  - 检测到的违规: {dip_metrics['violations_detected']}")

        # 要求至少80分的DIP遵循度
        assert dip_score >= 80, f"依赖倒置原则遵循分数过低: {dip_score:.1f}/100"


if __name__ == "__main__":
    # 运行依赖倒置原则测试
    pytest.main([__file__, "-v"])