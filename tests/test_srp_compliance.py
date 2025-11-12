"""
SOLID原则验证测试套件 - 单一职责原则 (S)

测试目标：验证每个类只有一个变化原因，职责明确单一
"""

import pytest
import inspect
from unittest.mock import Mock
from typing import Set, List, Dict, Any

# 导入项目模块
from akshare_value_investment.core.models import FinancialIndicator, MarketType, PeriodType
from akshare_value_investment.core.interfaces import IMarketAdapter, IMarketIdentifier, IQueryService
from akshare_value_investment.services.interfaces import IFieldMapper, IResponseFormatter, ITimeRangeProcessor
from akshare_value_investment.datasource.adapters.base_adapter import BaseMarketAdapter
from akshare_value_investment.datasource.adapters import (
    AStockAdapter, HKStockAdapter, USStockAdapter, AdapterManager
)
from akshare_value_investment.mcp.handlers import BaseHandler, QueryHandler, SearchHandler, DetailsHandler
from akshare_value_investment.services.financial_query_service import FinancialIndicatorQueryService
from akshare_value_investment.business.mapping.field_mapper import FinancialFieldMapper
from akshare_value_investment.business.processing.response_formatter import ResponseFormatter


class TestSingleResponsibilityPrinciple:
    """单一职责原则测试套件"""

    def test_core_interfaces_have_single_responsibility(self):
        """测试核心接口职责单一性"""

        # IMarketAdapter 应该只负责数据访问
        adapter_methods = inspect.getmembers(IMarketAdapter, predicate=inspect.isfunction)
        adapter_method_names = [name for name, _ in adapter_methods if not name.startswith('_')]

        # 验证只包含数据访问相关方法
        expected_adapter_methods = ['get_financial_data']
        assert set(adapter_method_names) == set(expected_adapter_methods), \
            f"IMarketAdapter应该只包含数据访问方法，实际包含: {adapter_method_names}"

        # IMarketIdentifier 应该只负责市场识别
        identifier_methods = inspect.getmembers(IMarketIdentifier, predicate=inspect.isfunction)
        identifier_method_names = [name for name, _ in identifier_methods if not name.startswith('_')]

        expected_identifier_methods = ['identify']
        assert set(identifier_method_names) == set(expected_identifier_methods), \
            f"IMarketIdentifier应该只包含识别相关方法，实际包含: {identifier_method_names}"

        # IQueryService 应该只负责查询协调
        query_methods = inspect.getmembers(IQueryService, predicate=inspect.isfunction)
        query_method_names = [name for name, _ in query_methods if not name.startswith('_')]

        expected_query_methods = ['query']
        assert set(query_method_names) == set(expected_query_methods), \
            f"IQueryService应该只包含查询方法，实际包含: {query_method_names}"

    def test_adapter_classes_have_single_responsibility(self):
        """测试适配器类职责单一性"""

        # AStockAdapter 应该只负责A股数据访问
        a_stock_adapter = AStockAdapter()

        # 检查方法是否都围绕数据访问职责
        public_methods = [method for method in dir(a_stock_adapter)
                         if not method.startswith('_') and callable(getattr(a_stock_adapter, method))]

        # 应该只包含数据访问相关方法
        expected_methods = ['get_financial_data']
        actual_methods = [method for method in public_methods if method in expected_methods]

        assert len(actual_methods) >= 1, "AStockAdapter应该实现数据访问方法"

        # 验证不应该包含的方法（违反单一职责的方法）
        forbidden_methods = ['query', 'validate', 'format', 'search', 'resolve']
        for method in forbidden_methods:
            assert method not in public_methods, \
                f"AStockAdapter不应该包含{method}方法，这违反了单一职责原则"

    def test_mcp_handlers_have_single_responsibility(self):
        """测试MCP处理器职责单一性"""

        # QueryHandler 应该只负责查询处理
        query_handler = QueryHandler(Mock(), Mock())

        # 检查方法是否都围绕查询处理职责
        query_methods = [method for method in dir(query_handler)
                        if not method.startswith('_') and callable(getattr(query_handler, method))]

        # 验证包含查询相关方法
        assert hasattr(query_handler, 'handle'), "QueryHandler应该有handle方法"
        assert 'query' in str(type(query_handler)).lower(), "QueryHandler应该专注于查询"

        # SearchHandler 应该只负责搜索处理
        search_handler = SearchHandler(Mock(), Mock())
        assert hasattr(search_handler, 'handle'), "SearchHandler应该有handle方法"
        assert 'search' in str(type(search_handler)).lower(), "SearchHandler应该专注于搜索"

        # DetailsHandler 应该只负责详情处理
        details_handler = DetailsHandler(Mock(), Mock())
        assert hasattr(details_handler, 'handle'), "DetailsHandler应该有handle方法"
        assert 'details' in str(type(details_handler)).lower(), "DetailsHandler应该专注于详情"

    def test_base_adapter_follows_srp(self):
        """测试基础适配器是否遵循单一职责原则"""

        # BaseMarketAdapter 应该只负责通用数据处理逻辑
        base_methods = inspect.getmembers(BaseMarketAdapter, predicate=inspect.isfunction)
        base_method_names = [name for name, _ in base_methods if not name.startswith('_')]

        # 验证方法都是数据处理相关
        data_processing_methods = [
            '_filter_by_date_range',    # 日期过滤
            '_parse_report_date',       # 日期解析
            '_create_financial_indicator'  # 指标创建
        ]

        for method in data_processing_methods:
            assert method in base_method_names, \
                f"BaseMarketAdapter应该包含{method}方法"

        # 验证不包含业务逻辑方法
        business_logic_methods = ['query', 'validate_symbol', 'identify_market']
        for method in business_logic_methods:
            assert method not in base_method_names, \
                f"BaseMarketAdapter不应该包含业务逻辑方法{method}"

    def test_adapter_manager_srp_violation(self):
        """检测适配器管理器是否存在单一职责违反"""

        adapter_manager = AdapterManager()

        # 检查是否有过多职责
        public_methods = [method for method in dir(adapter_manager)
                         if not method.startswith('_') and callable(getattr(adapter_manager, method))]

        # 适配器管理器应该只负责适配器管理
        core_methods = ['query', 'get_adapter']
        actual_core_methods = [method for method in public_methods if method in core_methods]

        assert len(actual_core_methods) >= 1, "AdapterManager应该包含核心管理方法"

        # 如果方法过多，可能存在职责过重问题
        if len(public_methods) > 5:
            pytest.warn(f"AdapterManager可能有过多职责，包含{len(public_methods)}个公共方法: {public_methods}")

    def test_financial_query_service_srp_analysis(self):
        """分析财务查询服务的单一职责情况"""

        # 这是一个已知的SRP违反案例，用于测试检测能力
        service = FinancialIndicatorQueryService(
            query_service=Mock(),
            field_mapper=Mock(),
            formatter=Mock(),
            time_processor=Mock(),
            data_processor=Mock()
        )

        # 检查方法数量和职责范围
        public_methods = [method for method in dir(service)
                         if not method.startswith('_') and callable(getattr(service, method))]

        # 识别不同职责的方法
        query_related_methods = [m for m in public_methods if 'query' in m.lower()]
        field_related_methods = [m for m in public_methods if 'field' in m.lower() or 'map' in m.lower()]
        validation_methods = [m for m in public_methods if 'validate' in m.lower()]

        # 记录职责分析结果
        responsibility_analysis = {
            'total_methods': len(public_methods),
            'query_methods': len(query_related_methods),
            'field_methods': len(field_related_methods),
            'validation_methods': len(validation_methods),
            'method_list': public_methods
        }

        # 如果类承担了太多不同类型的职责，标记为潜在的SRP违反
        responsibility_count = sum([
            len(query_related_methods) > 0,
            len(field_related_methods) > 0,
            len(validation_methods) > 0
        ])

        if responsibility_count > 2:
            pytest.warn(f"FinancialIndicatorQueryService可能违反SRP原则，承担了{responsibility_count}种不同职责: {responsibility_analysis}")

    def test_field_mapper_srp_analysis(self):
        """分析字段映射器的单一职责情况"""

        field_mapper = FinancialFieldMapper()

        # 检查方法职责分类
        public_methods = [method for method in dir(field_mapper)
                         if not method.startswith('_') and callable(getattr(field_mapper, method))]

        # 识别不同职责
        mapping_methods = [m for m in public_methods if 'map' in m.lower()]
        search_methods = [m for m in public_methods if 'search' in m.lower() or 'similar' in m.lower()]
        validation_methods = [m for m in public_methods if 'validate' in m.lower() or 'check' in m.lower()]
        retrieval_methods = [m for m in public_methods if 'get' in m.lower() or 'available' in m.lower()]

        # 职责分析
        responsibilities = {
            'mapping': len(mapping_methods),
            'searching': len(search_methods),
            'validation': len(validation_methods),
            'retrieval': len(retrieval_methods)
        }

        active_responsibilities = sum(1 for count in responsibilities.values() if count > 0)

        # 如果承担了超过3种不同职责，可能违反SRP
        if active_responsibilities > 3:
            pytest.warn(f"FinancialFieldMapper可能违反SRP原则，承担了{active_responsibilities}种职责: {responsibilities}")

    def test_response_formatter_srp_compliance(self):
        """测试响应格式化器是否遵循单一职责原则"""

        formatter = ResponseFormatter()

        # 响应格式化器应该只负责格式化相关职责
        public_methods = [method for method in dir(formatter)
                         if not method.startswith('_') and callable(getattr(formatter, method))]

        # 验证方法都是格式化相关
        formatting_methods = [m for m in public_methods if 'format' in m.lower() or 'extract' in m.lower()]

        assert len(formatting_methods) >= 1, "ResponseFormatter应该包含格式化方法"

        # 验证不包含其他职责的方法
        forbidden_responsibilities = ['query', 'validate', 'search', 'process']
        for method in public_methods:
            for forbidden in forbidden_responsibilities:
                if forbidden in method.lower() and forbidden not in ['format', 'extract']:
                    pytest.warn(f"ResponseFormatter可能包含非格式化职责方法: {method}")

    def test_srp_compliance_report(self):
        """生成单一职责原则遵循情况报告"""

        srp_analysis = {
            'compliant_classes': [],
            'potentially_violating_classes': [],
            'recommendations': []
        }

        # 分析各个类的SRP遵循情况
        classes_to_analyze = [
            ('AStockAdapter', AStockAdapter()),
            ('HKStockAdapter', HKStockAdapter()),
            ('USStockAdapter', USStockAdapter()),
            ('QueryHandler', QueryHandler(Mock(), Mock())),
            ('SearchHandler', SearchHandler(Mock(), Mock())),
            ('ResponseFormatter', ResponseFormatter()),
        ]

        for class_name, instance in classes_to_analyze:
            public_methods = [method for method in dir(instance)
                             if not method.startswith('_') and callable(getattr(instance, method))]

            # 简单的SRP评估：方法数量和相关性
            method_count = len(public_methods)

            if method_count <= 5:
                srp_analysis['compliant_classes'].append({
                    'class': class_name,
                    'method_count': method_count,
                    'methods': public_methods
                })
            else:
                srp_analysis['potentially_violating_classes'].append({
                    'class': class_name,
                    'method_count': method_count,
                    'methods': public_methods[:5],  # 只显示前5个方法
                    'warning': f'方法过多({method_count}个)，可能违反单一职责原则'
                })

        # 生成改进建议
        if srp_analysis['potentially_violating_classes']:
            srp_analysis['recommendations'].append(
                "考虑将职责过重的类拆分为多个专门类"
            )
            srp_analysis['recommendations'].append(
                "为每个类定义明确的单一职责边界"
            )

        # 输出分析报告（实际项目中可以写入日志或文件）
        print(f"\n📋 单一职责原则分析报告:")
        print(f"✅ 符合SRP的类: {len(srp_analysis['compliant_classes'])}")
        print(f"⚠️  可能违反SRP的类: {len(srp_analysis['potentially_violating_classes'])}")

        # 验证至少有一半的类符合SRP
        total_classes = len(srp_analysis['compliant_classes']) + len(srp_analysis['potentially_violating_classes'])
        if total_classes > 0:
            compliance_rate = len(srp_analysis['compliant_classes']) / total_classes
            assert compliance_rate >= 0.6, \
                f"SRP遵循率过低，只有{compliance_rate:.1%}的类符合单一职责原则"


if __name__ == "__main__":
    # 运行单一职责原则测试
    pytest.main([__file__, "-v"])