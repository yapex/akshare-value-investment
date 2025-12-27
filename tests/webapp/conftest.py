"""
Webapp 测试配置和 fixtures

提供测试共享的 fixtures：
- Mock API 响应
- 测试数据
- Streamlit 测试工具
"""

import sys
from pathlib import Path
import pandas as pd
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest

# 添加 webapp 目录到 Python 路径
webapp_path = Path(__file__).parent.parent.parent / "webapp"
sys.path.insert(0, str(webapp_path))


# ========== Mock API 响应数据 ==========

@pytest.fixture
def mock_financial_statements_response():
    """Mock 财务三表 API 响应"""
    return {
        "data": {
            "income_statement": {
                "data": [
                    {"date": "2023-12-31", "五、净利润": 1000000, "减：所得税费用": 200000, "其中：利息费用": 50000, "其中：营业收入": 2000000, "年份": 2023},
                    {"date": "2022-12-31", "五、净利润": 900000, "减：所得税费用": 180000, "其中：利息费用": 45000, "其中：营业收入": 1800000, "年份": 2022},
                ]
            },
            "balance_sheet": {
                "data": [
                    {"date": "2023-12-31", "短期借款": 100000, "长期借款": 200000, "应付债券": 50000, "一年内到期的非流动负债": 30000, "年份": 2023},
                    {"date": "2022-12-31", "短期借款": 90000, "长期借款": 180000, "应付债券": 45000, "一年内到期的非流动负债": 27000, "年份": 2022},
                ]
            },
            "cash_flow": {
                "data": [
                    {"date": "2023-12-31", "经营活动产生的现金流量净额": 1200000, "购建固定资产、无形资产和其他长期资产支付的现金": -300000, "年份": 2023},
                    {"date": "2022-12-31", "经营活动产生的现金流量净额": 1100000, "购建固定资产、无形资产和其他长期资产支付的现金": -280000, "年份": 2022},
                ]
            }
        }
    }


@pytest.fixture
def mock_api_requests(mock_financial_statements_response):
    """Mock requests.get 调用 API"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_financial_statements_response
        mock_get.return_value = mock_response
        yield mock_get


# ========== 测试数据 fixtures ==========

@pytest.fixture
def sample_income_data():
    """样本利润表数据"""
    return pd.DataFrame([
        {"年份": 2023, "五、净利润": 1000000, "减：所得税费用": 200000, "其中：利息费用": 50000, "其中：营业收入": 2000000},
        {"年份": 2022, "五、净利润": 900000, "减：所得税费用": 180000, "其中：利息费用": 45000, "其中：营业收入": 1800000},
        {"年份": 2021, "五、净利润": 800000, "减：所得税费用": 160000, "其中：利息费用": 40000, "其中：营业收入": 1600000},
    ])


@pytest.fixture
def sample_balance_data():
    """样本资产负债表数据"""
    return pd.DataFrame([
        {"年份": 2023, "短期借款": 100000, "长期借款": 200000, "应付债券": 50000, "一年内到期的非流动负债": 30000, "股东权益合计": 2000000},
        {"年份": 2022, "短期借款": 90000, "长期借款": 180000, "应付债券": 45000, "一年内到期的非流动负债": 27000, "股东权益合计": 1800000},
        {"年份": 2021, "短期借款": 80000, "长期借款": 160000, "应付债券": 40000, "一年内到期的非流动负债": 24000, "股东权益合计": 1600000},
    ])


@pytest.fixture
def sample_cashflow_data():
    """样本现金流量表数据"""
    return pd.DataFrame([
        {"年份": 2023, "经营活动产生的现金流量净额": 1200000, "购建固定资产、无形资产和其他长期资产支付的现金": -300000},
        {"年份": 2022, "经营活动产生的现金流量净额": 1100000, "购建固定资产、无形资产和其他长期资产支付的现金": -280000},
        {"年份": 2021, "经营活动产生的现金流量净额": 1000000, "购建固定资产、无形资产和其他长期资产支付的现金": -260000},
    ])


@pytest.fixture
def sample_financial_data(sample_income_data, sample_balance_data, sample_cashflow_data):
    """完整的财务数据"""
    return {
        "income_statement": sample_income_data,
        "balance_sheet": sample_balance_data,
        "cash_flow": sample_cashflow_data
    }


# ========== Streamlit 测试工具 ==========

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit 模块"""
    with patch('streamlit') as mock_st:
        # 配置常用的 Streamlit 方法
        mock_st.subheader = Mock()
        mock_st.markdown = Mock()
        mock_st.columns = Mock(return_value=[Mock(), Mock()])
        mock_st.number_input = Mock(return_value=10.0)
        mock_st.spinner = MagicMock()
        mock_st.error = Mock()
        mock_st.warning = Mock()
        mock_st.success = Mock()
        mock_st.dataframe = Mock()
        mock_st.plotly_chart = Mock()
        mock_st.metric = Mock()
        mock_st.write = Mock()

        yield mock_st


# ========== 组件测试辅助函数 ==========

@pytest.fixture
def component_test_helper():
    """组件测试辅助类"""

    class Helper:
        @staticmethod
        def create_mock_container():
            """创建 mock 的依赖注入容器"""
            container = Mock()
            container.stock_identifier = Mock(return_value=Mock())
            return container

        @staticmethod
        def assert_component_title(component, expected_title):
            """断言组件标题"""
            assert component.title == expected_title, f"组件标题应为 {expected_title}，实际为 {component.title}"

        @staticmethod
        def assert_render_signature(component):
            """断言 render 方法签名正确"""
            assert hasattr(component, 'render'), "组件必须实现 render 方法"
            import inspect
            sig = inspect.signature(component.render)
            params = list(sig.parameters.keys())
            assert params == ['symbol', 'market', 'years'], f"render 方法参数应为 [symbol, market, years]，实际为 {params}"

    return Helper()


# ========== pytest 配置 ==========

def pytest_configure(config):
    """pytest 配置"""
    # 添加自定义标记
    config.addinivalue_line("markers", "webapp: marks tests as webapp tests")
    config.addinivalue_line("markers", "component: marks tests as component tests")
    config.addinivalue_line("markers", "calculator: marks tests as calculator tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
