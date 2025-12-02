"""
财务查询服务测试

测试FinancialQueryService的完整功能，包括查询路由、字段裁剪、时间频率处理、
错误处理和MCP标准化响应格式。
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from akshare_value_investment.business.financial_query_service import FinancialQueryService
from akshare_value_investment.business.financial_types import FinancialQueryType, Frequency, MCPErrorType
from akshare_value_investment.business.mcp_response import MCPResponse
from akshare_value_investment.core.models import MarketType


class TestFinancialQueryService:
    """财务查询服务测试"""

    @pytest.fixture
    def mock_container(self):
        """模拟依赖注入容器"""
        container = Mock()

        # 模拟所有查询器
        container.a_stock_indicators.return_value = Mock()
        container.a_stock_balance_sheet.return_value = Mock()
        container.a_stock_income_statement.return_value = Mock()
        container.a_stock_cash_flow.return_value = Mock()
        container.hk_stock_indicators.return_value = Mock()
        container.hk_stock_statement.return_value = Mock()
        container.us_stock_indicators.return_value = Mock()
        container.us_stock_balance_sheet.return_value = Mock()
        container.us_stock_income_statement.return_value = Mock()
        container.us_stock_cash_flow.return_value = Mock()

        return container

    @pytest.fixture
    def service(self, mock_container):
        """财务查询服务实例"""
        return FinancialQueryService(mock_container)

    class Test查询路由功能:
        """测试查询路由功能"""

        def test_A股指标查询路由正确(self, service, mock_container):
            """测试A股指标查询路由正确"""
            # 准备测试数据
            test_data = pd.DataFrame({
                '报告期': ['2023-12-31', '2022-12-31'],
                '净利润': [100.0, 80.0],
                '净资产收益率': ['15%', '12%']
            })

            mock_container.a_stock_indicators.return_value.query.return_value = test_data

            # 执行查询
            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519"
            )

            # 验证路由正确
            mock_container.a_stock_indicators.return_value.query.assert_called_once_with("600519", None, None)

            # 验证响应格式
            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["market"] == MarketType.A_STOCK.value
            assert response["metadata"]["query_type"] == "A股财务指标"
            assert response["metadata"]["record_count"] == 2
            assert response["metadata"]["field_count"] == 3

        def test_港股指标查询路由正确(self, service, mock_container):
            """测试港股指标查询路由正确"""
            test_data = pd.DataFrame({
                'date': ['2023-12-31', '2022-12-31'],
                'net_profit': [200.0, 180.0],
                'roe': ['18%', '16%']
            })

            mock_container.hk_stock_indicators.return_value.query.return_value = test_data

            response = service.query(
                market=MarketType.HK_STOCK,
                query_type=FinancialQueryType.HK_STOCK_INDICATORS,
                symbol="00700"
            )

            mock_container.hk_stock_indicators.return_value.query.assert_called_once_with("00700", None, None)
            assert MCPResponse.is_success_response(response)

        def test_美股指标查询路由正确(self, service, mock_container):
            """测试美股指标查询路由正确"""
            test_data = pd.DataFrame({
                'date': ['2023-12-31', '2022-12-31'],
                'netIncome': [50.0, 45.0],
                'returnOnEquity': ['25%', '23%']
            })

            mock_container.us_stock_indicators.return_value.query.return_value = test_data

            response = service.query(
                market=MarketType.US_STOCK,
                query_type=FinancialQueryType.US_STOCK_INDICATORS,
                symbol="AAPL"
            )

            mock_container.us_stock_indicators.return_value.query.assert_called_once_with("AAPL", None, None)
            assert MCPResponse.is_success_response(response)

        def test_无效查询类型返回错误(self, service, mock_container):
            """测试无效查询类型返回错误"""
            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.HK_STOCK_INDICATORS,  # 错误的组合
                symbol="600519"
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.INVALID_FIELDS.value

    class Test字段裁剪功能:
        """测试字段裁剪功能"""

        @pytest.fixture
        def full_data(self):
            """完整的测试数据"""
            return pd.DataFrame({
                '报告期': ['2023-12-31', '2022-12-31', '2021-12-31'],
                '净利润': [100.0, 80.0, 60.0],
                '净资产收益率': ['15%', '12%', '10%'],
                '营业收入': [200.0, 180.0, 160.0],
                '总资产': [500.0, 450.0, 400.0]
            })

        def test_不指定字段返回所有字段(self, service, mock_container, full_data):
            """测试不指定字段返回所有字段"""
            mock_container.a_stock_indicators.return_value.query.return_value = full_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                fields=None
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["field_count"] == 5
            assert set(response["data"]["columns"]) == set(full_data.columns)

        def test_指定字段严格裁剪(self, service, mock_container, full_data):
            """测试指定字段严格裁剪"""
            mock_container.a_stock_indicators.return_value.query.return_value = full_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                fields=["报告期", "净利润", "净资产收益率"]
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["field_count"] == 3
            assert set(response["data"]["columns"]) == {"报告期", "净利润", "净资产收益率"}

        def test_字段不存在返回错误(self, service, mock_container, full_data):
            """测试字段不存在返回错误"""
            mock_container.a_stock_indicators.return_value.query.return_value = full_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                fields=["报告期", "净利润", "不存在的字段"]
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.FIELD_NOT_FOUND.value
            assert "不存在的字段" in error_info["message"]

        def test_空字段列表返回空数据(self, service, mock_container, full_data):
            """测试空字段列表返回空数据"""
            mock_container.a_stock_indicators.return_value.query.return_value = full_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                fields=[]
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["record_count"] == 0

    class Test时间频率处理:
        """测试时间频率处理"""

        @pytest.fixture
        def quarterly_data(self):
            """季度报告数据"""
            return pd.DataFrame({
                '报告期': pd.to_datetime([
                    '2023-12-31', '2023-09-30', '2023-06-30', '2023-03-31',
                    '2022-12-31', '2022-09-30', '2022-06-30', '2022-03-31'
                ]),
                '净利润': [100.0, 80.0, 60.0, 40.0, 90.0, 70.0, 50.0, 30.0],
                '净资产收益率': ['15%', '12%', '10%', '8%', '14%', '11%', '9%', '7%']
            })

        def test_季度数据直接返回(self, service, mock_container, quarterly_data):
            """测试季度数据直接返回"""
            mock_container.a_stock_indicators.return_value.query.return_value = quarterly_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                frequency=Frequency.QUARTERLY
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["record_count"] == 8
            assert response["metadata"]["frequency"] == "报告期数据"

        def test_年度数据取每年最后报告(self, service, mock_container, quarterly_data):
            """测试年度数据取每年最后报告"""
            mock_container.a_stock_indicators.return_value.query.return_value = quarterly_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                frequency=Frequency.ANNUAL
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["record_count"] == 2  # 2023年和2022年
            assert response["metadata"]["frequency"] == "年度数据"
            assert response["metadata"]["original_record_count"] == 8
            assert response["metadata"]["processed_record_count"] == 2

            # 验证是每年最后一条记录（12月31日）
            data_records = response["data"]["records"]
            dates = [pd.to_datetime(record["报告期"]) for record in data_records]
            assert pd.Timestamp('2023-12-31') in dates
            assert pd.Timestamp('2022-12-31') in dates

    class Test日期范围过滤:
        """测试日期范围过滤"""

        @pytest.fixture
        def multi_year_data(self):
            """多年数据"""
            return pd.DataFrame({
                '报告期': pd.to_datetime([
                    '2023-12-31', '2023-06-30',
                    '2022-12-31', '2022-06-30',
                    '2021-12-31', '2021-06-30'
                ]),
                '净利润': [100.0, 90.0, 80.0, 70.0, 60.0, 50.0],
                '净资产收益率': ['15%', '14%', '13%', '12%', '11%', '10%']
            })

        def test_日期范围过滤正确(self, service, mock_container, multi_year_data):
            """测试日期范围过滤正确"""

            # 模拟queryer已经应用了日期过滤（因为实际的queryer会在内部处理日期过滤）
            filtered_data = multi_year_data[
                (multi_year_data['报告期'] >= pd.to_datetime("2022-01-01")) &
                (multi_year_data['报告期'] <= pd.to_datetime("2023-12-31"))
            ]
            mock_container.a_stock_indicators.return_value.query.return_value = filtered_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519",
                start_date="2022-01-01",
                end_date="2023-12-31",
                frequency=Frequency.QUARTERLY  # 避免年度聚合影响
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["record_count"] == 4  # 2022和2023年的数据

            # 验证元信息包含日期范围
            assert "date_range" in response["metadata"]
            assert response["metadata"]["date_range"]["start_date"] == "2022-01-01"
            assert response["metadata"]["date_range"]["end_date"] == "2023-12-31"

    class Test错误处理:
        """测试错误处理"""

        def test_数据为空返回数据未找到错误(self, service, mock_container):
            """测试数据为空返回数据未找到错误"""
            mock_container.a_stock_indicators.return_value.query.return_value = pd.DataFrame()

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519"
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.DATA_NOT_FOUND.value

        def test_API异常返回内部错误(self, service, mock_container):
            """测试API异常返回内部错误"""
            mock_container.a_stock_indicators.return_value.query.side_effect = Exception("API调用失败")

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519"
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.INTERNAL_ERROR.value

        def test_参数验证错误(self, service):
            """测试参数验证错误"""
            # 测试无效股票代码
            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol=""
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.INVALID_FIELDS.value

    class TestGetAvailableFields:
        """测试get_available_fields功能"""

        @patch.object(FinancialQueryService, '_discover_fields')
        def test_获取可用字段成功(self, mock_discover, service, mock_container):
            """测试获取可用字段成功"""
            mock_discover.return_value = ["报告期", "净利润", "净资产收益率", "营业收入"]

            response = service.get_available_fields(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS
            )

            assert MCPResponse.is_success_response(response)
            assert response["metadata"]["available_fields"] == ["报告期", "净利润", "净资产收益率", "营业收入"]
            assert response["metadata"]["field_count"] == 4
            assert response["metadata"]["record_count"] == 0  # 空数据，只返回字段信息

        def test_市场和查询类型不匹配返回错误(self, service):
            """测试市场和查询类型不匹配返回错误"""
            response = service.get_available_fields(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.HK_STOCK_INDICATORS  # 港股查询类型用于A股市场
            )

            assert MCPResponse.is_error_response(response)
            error_info = MCPResponse.get_error_info(response)
            assert error_info["type"] == MCPErrorType.INVALID_FIELDS.value

    class TestMCP响应格式:
        """测试MCP响应格式"""

        def test_成功响应格式标准(self, service, mock_container):
            """测试成功响应格式标准"""
            test_data = pd.DataFrame({
                '报告期': ['2023-12-31'],
                '净利润': [100.0]
            })

            mock_container.a_stock_indicators.return_value.query.return_value = test_data

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519"
            )

            # 验证响应结构
            assert "status" in response
            assert "timestamp" in response
            assert "data" in response
            assert "metadata" in response

            # 验证数据结构
            data_info = response["data"]
            assert "records" in data_info
            assert "columns" in data_info
            assert "shape" in data_info
            assert "empty" in data_info

            # 验证元信息结构
            metadata = response["metadata"]
            assert "record_count" in metadata
            assert "field_count" in metadata
            assert "has_date_fields" in metadata

        def test_错误响应格式标准(self, service, mock_container):
            """测试错误响应格式标准"""
            mock_container.a_stock_indicators.return_value.query.return_value = pd.DataFrame()

            response = service.query(
                market=MarketType.A_STOCK,
                query_type=FinancialQueryType.A_STOCK_INDICATORS,
                symbol="600519"
            )

            # 验证响应结构
            assert "status" in response
            assert "timestamp" in response
            assert "error" in response

            # 验证错误信息结构
            error_info = response["error"]
            assert "type" in error_info
            assert "code" in error_info
            assert "display_name" in error_info
            assert "message" in error_info


class TestFinancialQueryServiceIntegration:
    """财务查询服务集成测试"""

    @pytest.fixture
    def real_service(self):
        """使用真实容器的财务查询服务"""
        return FinancialQueryService()

    def test_真实容器初始化成功(self, real_service):
        """测试真实容器初始化成功"""
        assert real_service.container is not None
        assert real_service.field_discovery is not None
        assert len(real_service.queryer_mapping) == 10  # 4+2+4个查询器

    def test_查询器映射完整性(self, real_service):
        """测试查询器映射完整性"""
        for query_type in FinancialQueryType:
            assert query_type in real_service.queryer_mapping
            assert real_service.queryer_mapping[query_type] is not None

    def test_字段发现服务集成(self, real_service):
        """测试字段发现服务集成"""
        # 测试可以调用字段发现方法
        available_query_types = FinancialQueryType.get_query_types_by_market(MarketType.A_STOCK)
        assert len(available_query_types) == 4  # A股有4个查询类型