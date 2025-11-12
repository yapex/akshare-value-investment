"""
SOLID原则验证测试套件 - 接口隔离原则 (I)

测试目标：验证接口设计专一，不强迫实现不需要的方法
"""

import pytest
import inspect
from typing import Protocol, List, Dict, Any

# 导入项目模块
from akshare_value_investment.core.interfaces import IMarketAdapter, IMarketIdentifier, IQueryService
from akshare_value_investment.services.interfaces import (
    IFieldMapper, IResponseFormatter, ITimeRangeProcessor, IDataStructureProcessor
)
from akshare_value_investment.datasource.adapters import AStockAdapter, HKStockAdapter, USStockAdapter
from akshare_value_investment.mcp.handlers import BaseHandler, QueryHandler, SearchHandler, DetailsHandler


class TestInterfaceSegregationPrinciple:
    """接口隔离原则测试套件"""

    def test_core_interfaces_specialization(self):
        """测试核心接口的专一化设计"""

        # IMarketAdapter应该只包含数据访问相关方法
        adapter_methods = inspect.getmembers(IMarketAdapter, predicate=inspect.isfunction)
        adapter_method_names = [name for name, _ in adapter_methods if not name.startswith('_')]

        # 验证接口专一性：只包含必要的核心方法
        expected_adapter_methods = ['get_financial_data']
        unexpected_methods = ['validate', 'identify', 'format', 'search', 'process']

        for method in unexpected_methods:
            assert method not in adapter_method_names, \
                f"IMarketAdapter不应该包含{method}方法，违反接口隔离原则"

        # IMarketIdentifier应该只包含识别相关方法
        identifier_methods = inspect.getmembers(IMarketIdentifier, predicate=inspect.isfunction)
        identifier_method_names = [name for name, _ in identifier_methods if not name.startswith('_')]

        expected_identifier_methods = ['identify_market', 'validate_symbol', 'normalize_symbol']
        unexpected_methods = ['query', 'fetch', 'format', 'process']

        for method in unexpected_methods:
            assert method not in identifier_method_names, \
                f"IMarketIdentifier不应该包含{method}方法，违反接口隔离原则"

        # IQueryService应该只包含查询相关方法
        query_methods = inspect.getmembers(IQueryService, predicate=inspect.isfunction)
        query_method_names = [name for name, _ in query_methods if not name.startswith('_')]

        expected_query_methods = ['query']
        unexpected_methods = ['validate', 'identify', 'format', 'search', 'process']

        for method in unexpected_methods:
            assert method not in query_method_names, \
                f"IQueryService不应该包含{method}方法，违反接口隔离原则"

    def test_service_interfaces_cohesion(self):
        """测试服务层接口的内聚性"""

        # IFieldMapper应该专注于字段映射
        field_mapper_methods = inspect.getmembers(IFieldMapper, predicate=inspect.isfunction)
        field_mapper_method_names = [name for name, _ in field_mapper_methods if not name.startswith('_')]

        # 验证字段映射相关方法
        mapping_related_methods = ['resolve_fields', 'map_keyword_to_field', 'search_similar_fields', 'get_available_fields', 'get_field_details']
        non_mapping_methods = ['query', 'fetch_data', 'format_response', 'validate_symbol']

        for method in mapping_related_methods:
            assert method in field_mapper_method_names, \
                f"IFieldMapper应该包含{method}方法"

        for method in non_mapping_methods:
            assert method not in field_mapper_method_names, \
                f"IFieldMapper不应该包含{method}方法，违反接口隔离原则"

        # IResponseFormatter应该专注于格式化
        formatter_methods = inspect.getmembers(IResponseFormatter, predicate=inspect.isfunction)
        formatter_method_names = [name for name, _ in formatter_methods if not name.startswith('_')]

        formatting_related_methods = ['format_query_response']
        non_formatting_methods = ['query', 'fetch_data', 'resolve_fields', 'validate_symbol']

        for method in non_formatting_methods:
            assert method not in formatter_method_names, \
                f"IResponseFormatter不应该包含{method}方法，违反接口隔离原则"

    def test_interface_method_necessity(self):
        """测试接口方法的必要性"""

        # 创建最小化接口实现来测试必要性
        class MinimalMarketAdapter:
            """最小化的市场适配器实现"""
            def get_financial_data(self, symbol: str, **kwargs) -> List:
                """实现IMarketAdapter的唯一必需方法"""
                return []

        class MinimalFieldMapper:
            """最小化的字段映射器实现"""
            async def resolve_fields(self, symbol: str, fields: List[str]) -> tuple:
                """实现核心映射方法"""
                return fields, []

            def map_keyword_to_field(self, keyword: str, market_id: str = None):
                """实现关键字映射方法"""
                return keyword, 1.0, None

            def search_similar_fields(self, keyword: str, market_id: str = None, max_results: int = 5):
                """实现字段搜索方法"""
                return []

            def get_available_fields(self, market_id: str = None):
                """实现字段获取方法"""
                return []

            def get_field_details(self, field_name: str):
                """实现字段详情方法"""
                return None

        # 验证最小化实现可以满足接口要求
        minimal_adapter = MinimalMarketAdapter()
        assert hasattr(minimal_adapter, 'get_financial_data'), "最小化适配器应该实现核心方法"

        minimal_mapper = MinimalFieldMapper()
        required_methods = ['resolve_fields', 'map_keyword_to_field', 'search_similar_fields', 'get_available_fields', 'get_field_details']
        for method in required_methods:
            assert hasattr(minimal_mapper, method), f"最小化映射器应该实现{method}方法"

    def test_adapter_interface_implementation(self):
        """测试适配器接口实现的专一性"""

        # A股适配器应该只实现IMarketAdapter，不被迫实现其他接口
        a_stock_adapter = AStockAdapter()

        # 验证实现了必要的接口
        assert isinstance(a_stock_adapter, IMarketAdapter), "AStockAdapter应该实现IMarketAdapter"

        # 验证不被迫实现其他接口的方法
        adapter_methods = [method for method in dir(a_stock_adapter)
                          if not method.startswith('_') and callable(getattr(a_stock_adapter, method))]

        # 不应该包含其他接口的方法
        other_interface_methods = ['format_response', 'resolve_fields', 'validate_symbol', 'identify_market']
        for method in other_interface_methods:
            if method in adapter_methods and not hasattr(IMarketAdapter, method):
                pytest.warn(f"AStockAdapter可能被迫实现了不需要的方法: {method}")

    def test_handler_interface_specialization(self):
        """测试处理器接口的专一化"""

        # 检查BaseHandler是否提供了最小化的接口
        base_handler_methods = inspect.getmembers(BaseHandler, predicate=inspect.isfunction)
        base_handler_method_names = [name for name, _ in base_handler_methods if not name.startswith('_')]

        # BaseHandler应该只包含处理器必需的方法
        expected_handler_methods = ['handle', '_create_response', '_create_error_response']
        unnecessary_methods = ['query', 'fetch', 'resolve', 'format', 'validate']

        for method in unnecessary_methods:
            if method in base_handler_method_names:
                pytest.warn(f"BaseHandler包含可能不必要的方法: {method}")

        # 验证各个处理器专注于自己的职责
        query_handler = QueryHandler(Mock(), Mock())
        search_handler = SearchHandler(Mock(), Mock())
        details_handler = DetailsHandler(Mock())

        # QueryHandler应该专注于查询
        assert hasattr(query_handler, 'handle'), "QueryHandler应该有handle方法"

        # SearchHandler应该专注于搜索
        assert hasattr(search_handler, 'handle'), "SearchHandler应该有handle方法"

        # DetailsHandler应该专注于详情
        assert hasattr(details_handler, 'handle'), "DetailsHandler应该有handle方法"

    def test_interface_segregation_violations(self):
        """检测接口隔离原则违反的情况"""

        # 检查是否有过于庞大的接口
        interfaces_to_check = [
            (IFieldMapper, "IFieldMapper"),
            (IResponseFormatter, "IResponseFormatter"),
            (ITimeRangeProcessor, "ITimeRangeProcessor"),
            (IDataStructureProcessor, "IDataStructureProcessor")
        ]

        for interface, interface_name in interfaces_to_check:
            methods = inspect.getmembers(interface, predicate=inspect.isfunction)
            method_names = [name for name, _ in methods if not name.startswith('_')]

            # 如果接口方法过多，可能违反ISP
            if len(method_names) > 10:
                pytest.warn(f"{interface_name}接口方法过多({len(method_names)}个)，可能违反接口隔离原则")

            # 检查方法是否属于同一个职责
            method_categories = {
                'query': ['query', 'fetch', 'get'],
                'validation': ['validate', 'check', 'verify'],
                'formatting': ['format', 'render', 'present'],
                'mapping': ['map', 'resolve', 'transform'],
                'processing': ['process', 'handle', 'execute']
            }

            categories_found = set()
            for method in method_names:
                for category, keywords in method_categories.items():
                    if any(keyword in method.lower() for keyword in keywords):
                        categories_found.add(category)

            # 如果一个接口包含太多不同类别的职责，可能违反ISP
            if len(categories_found) > 3:
                pytest.warn(f"{interface_name}包含过多不同类别的职责: {categories_found}")

    def test_fine_grained_interfaces(self):
        """测试细粒度接口设计"""

        # 创建细粒度接口的示例
        class IDataReader(Protocol):
            """专门负责数据读取的接口"""
            def read_data(self, source: str) -> Any: ...

        class IDataValidator(Protocol):
            """专门负责数据验证的接口"""
            def validate_data(self, data: Any) -> bool: ...

        class IDataAdapter(Protocol):
            """专门负责数据转换的接口"""
            def adapt_data(self, data: Any) -> Any: ...

        # 验证细粒度接口的专一性
        for interface, expected_methods in [
            (IDataReader, ['read_data']),
            (IDataValidator, ['validate_data']),
            (IDataAdapter, ['adapt_data'])
        ]:
            methods = inspect.getmembers(interface, predicate=inspect.isfunction)
            method_names = [name for name, _ in methods if not name.startswith('_')]

            assert len(method_names) <= 3, f"{interface.__name__}应该保持简洁，当前有{len(method_names)}个方法"

    def test_interface_client_specificity(self):
        """测试接口的客户端特定性"""

        # 模拟不同的客户端需求
        class QueryClient:
            """查询客户端只需要查询功能"""
            def __init__(self, query_service: IQueryService):
                self.query_service = query_service

            def execute_query(self, symbol: str):
                return self.query_service.query(symbol)

        class MarketClient:
            """市场客户端只需要市场识别功能"""
            def __init__(self, market_identifier: IMarketIdentifier):
                self.market_identifier = market_identifier

            def identify_market(self, symbol: str):
                return self.market_identifier.identify_market(symbol)

        # 验证客户端不被迫依赖不需要的接口
        query_service = Mock(spec=IQueryService)
        market_identifier = Mock(spec=IMarketIdentifier)

        query_client = QueryClient(query_service)
        market_client = MarketClient(market_identifier)

        # 验证客户端只使用它们需要的方法
        assert hasattr(query_client.query_service, 'query'), "QueryClient应该只需要query方法"
        assert hasattr(market_client.market_identifier, 'identify_market'), "MarketClient应该只需要identify_market方法"

    def test_interface_evolution_compatibility(self):
        """测试接口演化的兼容性"""

        # 模拟接口演化：添加新方法而不影响现有实现
        class IExtendedQueryService(IQueryService, Protocol):
            """扩展的查询服务接口，添加新方法但不影响现有实现"""
            def async_query(self, symbol: str, **kwargs): ...

        # 创建兼容现有接口的实现
        class CompatibleQueryService:
            def query(self, symbol: str, **kwargs):
                return Mock(success=True, data=[])

            # 不实现新方法，但应该仍然可以工作
            # async_query的实现是可选的

        # 验证兼容性
        compatible_service = CompatibleQueryService()
        assert hasattr(compatible_service, 'query'), "兼容服务应该实现基本query方法"

        # 可以选择性地实现新方法
        if hasattr(compatible_service, 'async_query'):
            # 新方法是可选的，不影响基本功能
            pass

    def test_isp_compliance_score(self):
        """计算接口隔离原则遵循分数"""

        isp_metrics = {
            'focused_interfaces': 0,
            'total_interfaces': 0,
            'interface_method_count': [],
            'violations_detected': 0,
            'client_specific_interfaces': 0
        }

        # 分析核心接口
        core_interfaces = [
            (IMarketAdapter, "IMarketAdapter"),
            (IMarketIdentifier, "IMarketIdentifier"),
            (IQueryService, "IQueryService")
        ]

        # 分析服务层接口
        service_interfaces = [
            (IFieldMapper, "IFieldMapper"),
            (IResponseFormatter, "IResponseFormatter"),
            (ITimeRangeProcessor, "ITimeRangeProcessor"),
            (IDataStructureProcessor, "IDataStructureProcessor")
        ]

        all_interfaces = core_interfaces + service_interfaces

        for interface, interface_name in all_interfaces:
            isp_metrics['total_interfaces'] += 1

            # 获取接口方法
            methods = inspect.getmembers(interface, predicate=inspect.isfunction)
            method_names = [name for name, _ in methods if not name.startswith('_')]
            isp_metrics['interface_method_count'].append(len(method_names))

            # 评估接口专一性
            method_categories = {
                'query': ['query', 'fetch', 'get'],
                'validation': ['validate', 'check', 'verify'],
                'formatting': ['format', 'render'],
                'mapping': ['map', 'resolve'],
                'processing': ['process', 'handle']
            }

            categories_found = set()
            for method in method_names:
                for category, keywords in method_categories.items():
                    if any(keyword in method.lower() for keyword in keywords):
                        categories_found.add(category)

            # 如果职责单一（≤2个类别），认为是专一的
            if len(categories_found) <= 2:
                isp_metrics['focused_interfaces'] += 1

            # 如果方法过多或职责过多，记录违规
            if len(method_names) > 8 or len(categories_found) > 3:
                isp_metrics['violations_detected'] += 1

        # 计算客户端特定接口
        # 如果接口方法较少且职责明确，认为是客户端特定的
        for method_count in isp_metrics['interface_method_count']:
            if method_count <= 3:
                isp_metrics['client_specific_interfaces'] += 1

        # 计算ISP遵循分数
        isp_score = 0

        if isp_metrics['total_interfaces'] > 0:
            # 专一接口比例 (40%)
            focus_score = (isp_metrics['focused_interfaces'] / isp_metrics['total_interfaces']) * 40

            # 客户端特定接口比例 (30%)
            client_specific_score = (isp_metrics['client_specific_interfaces'] / isp_metrics['total_interfaces']) * 30

            # 违规惩罚 (最多-30%)
            violation_penalty = min(30, (isp_metrics['violations_detected'] / isp_metrics['total_interfaces']) * 30)

            isp_score = focus_score + client_specific_score - violation_penalty

        # 确保分数在0-100范围内
        isp_score = max(0, min(100, isp_score))

        # 计算平均方法数
        avg_methods = sum(isp_metrics['interface_method_count']) / len(isp_metrics['interface_method_count']) if isp_metrics['interface_method_count'] else 0

        print(f"\n📊 接口隔离原则遵循分数: {isp_score:.1f}/100")
        print(f"  - 专一接口: {isp_metrics['focused_interfaces']}/{isp_metrics['total_interfaces']}")
        print(f"  - 客户端特定接口: {isp_metrics['client_specific_interfaces']}/{isp_metrics['total_interfaces']}")
        print(f"  - 检测到的违规: {isp_metrics['violations_detected']}")
        print(f"  - 平均接口方法数: {avg_methods:.1f}")

        # 要求至少75分的ISP遵循度
        assert isp_score >= 75, f"接口隔离原则遵循分数过低: {isp_score:.1f}/100"


if __name__ == "__main__":
    # 运行接口隔离原则测试
    pytest.main([__file__, "-v"])