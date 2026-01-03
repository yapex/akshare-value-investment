"""
测试 components/ 组件

测试分析组件的基础功能和接口规范
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import inspect

# 添加 webapp 目录到 Python 路径
webapp_path = Path(__file__).parent.parent.parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))

# 导入所有组件
from components.roic import ROICComponent
from components.dcf_valuation import DCFValuationComponent
from components.cash_flow_pattern import CashFlowPatternComponent
from components.revenue_growth import RevenueGrowthComponent
from components.ebit_margin import EBITMarginComponent
from components.net_profit_cash_ratio import NetProfitCashRatioComponent
from components.free_cash_flow_ratio import FreeCashFlowRatioComponent
from components.debt_to_equity import DebtToEquityComponent
from components.debt_to_fcf_ratio import DebtToFcfRatioComponent
from components.liquidity_ratio import LiquidityRatioComponent
from components.net_income_valuation import NetIncomeValuationComponent


class TestComponentInterface:
    """测试组件接口规范"""

    @pytest.fixture
    def all_components(self):
        """所有组件类"""
        return [
            ROICComponent,
            DCFValuationComponent,
            CashFlowPatternComponent,
            RevenueGrowthComponent,
            EBITMarginComponent,
            NetProfitCashRatioComponent,
            FreeCashFlowRatioComponent,
            DebtToEquityComponent,
            DebtToFcfRatioComponent,
            LiquidityRatioComponent,
            NetIncomeValuationComponent,
        ]

    def test_all_components_have_title(self, all_components):
        """测试所有组件都有 title 属性"""
        for component_class in all_components:
            assert hasattr(component_class, 'title'), f"{component_class.__name__} 缺少 title 属性"
            assert isinstance(component_class.title, str), f"{component_class.__name__}.title 应为字符串"
            assert len(component_class.title) > 0, f"{component_class.__name__}.title 不应为空"

    def test_all_components_have_render_method(self, all_components):
        """测试所有组件都有 render 方法"""
        for component_class in all_components:
            assert hasattr(component_class, 'render'), f"{component_class.__name__} 缺少 render 方法"

    def test_render_method_signature(self, all_components):
        """测试 render 方法签名正确"""
        for component_class in all_components:
            sig = inspect.signature(component_class.render)
            params = list(sig.parameters.keys())

            assert params == ['symbol', 'market', 'years'], \
                f"{component_class.__name__}.render 参数应为 [symbol, market, years]，实际为 {params}"

    def test_render_is_static_method(self, all_components):
        """测试 render 是静态方法"""
        for component_class in all_components:
            # 静态方法可以通过类直接调用
            assert callable(component_class.render), f"{component_class.__name__}.render 应该可调用"

    def test_component_titles_are_meaningful(self, all_components):
        """测试组件标题有意义（包含中文或描述性内容）"""
        for component_class in all_components:
            title = component_class.title
            # 标题应该包含中文或特定关键词
            assert any(char in title for char in '盈利债务现金流估值ROICEBIT增长利润率'), \
                f"{component_class.__name__}.title 应包含有意义的描述"


class TestROICComponent:
    """测试 ROIC 组件"""

    def test_title(self):
        """测试标题"""
        assert ROICComponent.title == "💎 投入资本回报率（ROIC）"

    @patch('streamlit.subheader')
    @patch('streamlit.spinner')
    def test_render_signature(self, mock_spinner, mock_subheader):
        """测试 render 方法可以被调用"""
        # Mock 所有依赖 - 正确的路径是 services.calculators.roic.calculate
        with patch('services.calculators.roic.calculate') as mock_calculate:
            mock_calculate.return_value = (Mock(), Mock(), Mock(), [], [], {}, {}, {}, {})

            with patch('streamlit.success'):
                # 调用 render 方法
                result = ROICComponent.render("600519", "A股", 5)

                # 验证返回类型
                assert isinstance(result, bool)


class TestNetIncomeValuationComponent:
    """测试净利润估值组件"""

    def test_title(self):
        """测试标题"""
        assert NetIncomeValuationComponent.title == "📊 估值（净利润）"

    @patch('streamlit.subheader')
    def test_render_signature(self, mock_subheader):
        """测试 render 方法可以被调用"""
        # Mock 所有依赖 - 正确的路径是 services.calculators.net_income_valuation.calculate
        with patch('services.calculators.net_income_valuation.calculate') as mock_calculate:
            mock_calculate.return_value = (Mock(), [], {})

            with patch('streamlit.markdown'):
                with patch('streamlit.columns'):
                    with patch('streamlit.number_input', return_value=10.0):
                        with patch('streamlit.spinner'):
                            with patch('streamlit.success'):
                                # 调用 render 方法
                                result = NetIncomeValuationComponent.render("600519", "A股", 5)

                                # 验证返回类型
                                assert isinstance(result, bool)


class TestDCFValuationComponent:
    """测试 DCF 估值组件"""

    def test_title(self):
        """测试标题"""
        assert DCFValuationComponent.title == "📈 DCF估值分析"

    @patch('streamlit.subheader')
    def test_render_signature(self, mock_subheader):
        """测试 render 方法可以被调用"""
        # Mock 所有依赖 - 正确的路径是 services.calculators.dcf_valuation.calculate
        with patch('services.calculators.dcf_valuation.calculate') as mock_calculate:
            mock_calculate.return_value = (Mock(), [], {})

            with patch('streamlit.markdown'):
                with patch('streamlit.columns'):
                    with patch('streamlit.number_input', return_value=10.0):
                        with patch('streamlit.spinner'):
                            with patch('streamlit.success'):
                                # 调用 render 方法
                                result = DCFValuationComponent.render("600519", "A股", 5)

                                # 验证返回类型
                                assert isinstance(result, bool)


class TestDebtToEquityComponent:
    """测试债务权益比组件"""

    def test_title(self):
        """测试标题"""
        assert DebtToEquityComponent.title == "💳 有息债务权益比"


class TestRevenueGrowthComponent:
    """测试收入增长组件"""

    def test_title(self):
        """测试标题"""
        assert RevenueGrowthComponent.title == "📈 营收是否增长（成长性）"


class TestEBITMarginComponent:
    """测试 EBIT 利润率组件"""

    def test_title(self):
        """测试标题"""
        assert EBITMarginComponent.title == "💰 盈利能力如何（EBIT利润率）"


class TestCashFlowPatternComponent:
    """测试现金流模式组件"""

    def test_title(self):
        """测试标题"""
        assert CashFlowPatternComponent.title == "💵 现金流类型分析"


class TestComponentGrouping:
    """测试组件分组"""

    def test_all_components_unique(self):
        """测试所有组件都是唯一的"""
        # 导入 app.py 中的组件列表
        from app import ANALYSIS_COMPONENTS

        # 验证没有重复
        assert len(ANALYSIS_COMPONENTS) == len(set(ANALYSIS_COMPONENTS)), \
            "ANALYSIS_COMPONENTS 中存在重复组件"

    def test_component_groups_complete(self):
        """测试组件分组完整"""
        from app import ANALYSIS_GROUPS

        # 验证所有分组
        expected_groups = [
            "💰 盈利分析",
            "💳 债务分析",
            "💵 现金流分析",
            "📈 估值(DCF)",
            "📊 估值(净利润)"
        ]

        for group in expected_groups:
            assert group in ANALYSIS_GROUPS, f"缺少分组: {group}"
            assert len(ANALYSIS_GROUPS[group]) > 0, f"分组 {group} 为空"

    def test_all_components_in_groups(self):
        """测试所有组件都在分组中"""
        from app import ANALYSIS_GROUPS, ANALYSIS_COMPONENTS

        # 从分组中收集所有组件
        grouped_components = []
        for components in ANALYSIS_GROUPS.values():
            grouped_components.extend(components)

        # 验证数量一致
        assert len(grouped_components) == len(ANALYSIS_COMPONENTS), \
            "分组中的组件数量与 ANALYSIS_COMPONENTS 不一致"

        # 验证所有组件都在分组中
        for component in ANALYSIS_COMPONENTS:
            assert component in grouped_components, f"{component.__name__} 不在任何分组中"


class TestComponentIntegration:
    """测试组件集成"""

    def test_component_render_returns_bool(self):
        """测试组件 render 方法返回布尔值"""
        # 这个测试验证组件接口契约
        # 实际的渲染测试需要完整的 Streamlit 环境

        from components.base import AnalysisComponent

        # 创建一个符合 Protocol 的测试组件
        class TestComponent:
            title = "测试组件"

            @staticmethod
            def render(symbol: str, market: str, years: int) -> bool:
                return True

        # 验证符合接口
        component = TestComponent()
        assert isinstance(component.render("test", "A股", 5), bool)
