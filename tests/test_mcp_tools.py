"""
MCP工具测试

测试MCP工具封装层的功能，包括财务查询工具和字段发现工具。
"""

import pytest
from unittest.mock import Mock, patch

from src.akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool
from src.akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool
from src.akshare_value_investment.business.financial_types import FinancialQueryType, Frequency
from src.akshare_value_investment.core.models import MarketType
from src.akshare_value_investment.business.mcp_response import MCPResponse


class TestFinancialQueryTool:
    """测试财务查询工具"""

    @pytest.fixture
    def mock_financial_service(self):
        """模拟财务查询服务"""
        service = Mock()
        return service

    @pytest.fixture
    def financial_tool(self, mock_financial_service):
        """财务查询工具实例"""
        return FinancialQueryTool(mock_financial_service)

    @pytest.fixture
    def sample_data(self):
        """示例数据"""
        import pandas as pd
        return {
            "status": "success",
            "data": {
                "records": [
                    {"报告期": "2023-12-31", "净利润": 100.0, "净资产收益率": "15%"},
                    {"报告期": "2022-12-31", "净利润": 80.0, "净资产收益率": "12%"}
                ],
                "columns": ["报告期", "净利润", "净资产收益率"],
                "shape": (2, 3),
                "empty": False
            },
            "metadata": {
                "record_count": 2,
                "field_count": 3,
                "market": "a_stock",
                "query_type": "A股财务指标",
                "frequency": "年度数据"
            },
            "timestamp": "2024-01-01T00:00:00"
        }

    def test_查询财务数据成功(self, financial_tool, mock_financial_service, sample_data):
        """测试查询财务数据成功"""
        # 设置模拟返回
        mock_financial_service.query.return_value = sample_data

        # 调用工具
        response = financial_tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="600519",
            fields=["报告期", "净利润"],
            frequency="annual"
        )

        # 验证调用
        mock_financial_service.query.assert_called_once_with(
            market=MarketType.A_STOCK,
            query_type=FinancialQueryType.A_STOCK_INDICATORS,
            symbol="600519",
            fields=["报告期", "净利润"],
            start_date=None,
            end_date=None,
            frequency=Frequency.ANNUAL
        )

        # 验证响应
        assert response["success"] is True
        assert "data" in response
        assert response["metadata"]["record_count"] == 2
        assert response["metadata"]["market"] == "a_stock"

    def test_查询财务数据参数错误(self, financial_tool, mock_financial_service):
        """测试查询财务数据参数错误"""
        response = financial_tool.query_financial_data(
            market="invalid_market",  # 无效市场
            query_type="a_stock_indicators",
            symbol="600519"
        )

        assert response["success"] is False
        assert "error" in response
        assert response["error"]["type"] == "invalid_fields"

    def test_获取可用字段成功(self, financial_tool, mock_financial_service):
        """测试获取可用字段成功"""
        # 设置模拟返回
        mock_response = {
            "status": "success",
            "data": {"records": [], "columns": [], "shape": (0, 0), "empty": True},
            "metadata": {
                "available_fields": ["报告期", "净利润", "净资产收益率"],
                "field_count": 3,
                "record_count": 0
            },
            "timestamp": "2024-01-01T00:00:00"
        }
        mock_financial_service.get_available_fields.return_value = mock_response

        # 调用工具
        response = financial_tool.get_available_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        # 验证调用
        mock_financial_service.get_available_fields.assert_called_once_with(
            market=MarketType.A_STOCK,
            query_type=FinancialQueryType.A_STOCK_INDICATORS
        )

        # 验证响应
        assert response["success"] is True
        assert response["available_fields"] == ["报告期", "净利润", "净资产收益率"]
        assert response["field_count"] == 3

    def test_解析市场类型(self, financial_tool):
        """测试解析市场类型"""
        assert financial_tool._parse_market("a_stock") == MarketType.A_STOCK
        assert financial_tool._parse_market("hk_stock") == MarketType.HK_STOCK
        assert financial_tool._parse_market("us_stock") == MarketType.US_STOCK

        with pytest.raises(ValueError):
            financial_tool._parse_market("invalid_market")

    def test_解析查询类型(self, financial_tool):
        """测试解析查询类型"""
        assert financial_tool._parse_query_type("a_stock_indicators") == FinancialQueryType.A_STOCK_INDICATORS
        assert financial_tool._parse_query_type("hk_stock_indicators") == FinancialQueryType.HK_STOCK_INDICATORS
        assert financial_tool._parse_query_type("us_stock_indicators") == FinancialQueryType.US_STOCK_INDICATORS

        with pytest.raises(ValueError):
            financial_tool._parse_query_type("invalid_query_type")

    def test_解析时间频率(self, financial_tool):
        """测试解析时间频率"""
        assert financial_tool._parse_frequency("annual") == Frequency.ANNUAL
        assert financial_tool._parse_frequency("quarterly") == Frequency.QUARTERLY

        with pytest.raises(ValueError):
            financial_tool._parse_frequency("invalid_frequency")

    def test_获取支持的市场和查询类型(self, financial_tool):
        """测试获取支持的市场和查询类型"""
        markets = financial_tool.get_supported_markets()
        assert "a_stock" in markets
        assert "hk_stock" in markets
        assert "us_stock" in markets

        a_stock_query_types = financial_tool.get_supported_query_types("a_stock")
        assert "a_stock_indicators" in a_stock_query_types
        assert len(a_stock_query_types) == 4  # A股有4个查询类型


class TestFieldDiscoveryTool:
    """测试字段发现工具"""

    @pytest.fixture
    def mock_field_service(self):
        """模拟字段发现服务"""
        service = Mock()
        return service

    @pytest.fixture
    def field_tool(self, mock_field_service):
        """字段发现工具实例"""
        return FieldDiscoveryTool(mock_field_service)

    def test_发现字段成功(self, field_tool, mock_field_service):
        """测试发现字段成功"""
        # 设置模拟返回
        mock_fields = ["报告期", "净利润", "净资产收益率", "营业收入"]
        mock_field_service.discover_a_stock_indicator_fields.return_value = mock_fields

        # 调用工具
        response = field_tool.discover_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )

        # 验证调用
        mock_field_service.discover_a_stock_indicator_fields.assert_called_once()

        # 验证响应
        assert response["success"] is True
        assert response["available_fields"] == mock_fields
        assert response["field_count"] == len(mock_fields)
        assert response["market"] == "a_stock"

    def test_发现所有市场字段成功(self, field_tool, mock_field_service):
        """测试发现所有市场字段成功"""
        # 设置模拟返回
        mock_field_service.discover_a_stock_indicator_fields.return_value = ["报告期", "净利润"]
        mock_field_service.discover_a_stock_balance_sheet_fields.return_value = ["资产总计", "负债合计"]
        mock_field_service.discover_a_stock_income_statement_fields.return_value = ["营业收入", "营业成本"]
        mock_field_service.discover_a_stock_cash_flow_fields.return_value = ["经营活动现金流"]

        # 调用工具
        response = field_tool.discover_all_market_fields(market="a_stock")

        # 验证响应
        assert response["success"] is True
        assert response["market"] == "a_stock"
        assert response["total_field_count"] == 7  # 2 + 2 + 2 + 1
        assert response["query_type_count"] == 4
        assert "all_fields" in response
        assert "a_stock_indicators" in response["all_fields"]

    def test_验证字段成功(self, field_tool, mock_field_service):
        """测试验证字段成功"""
        # 设置模拟返回
        available_fields = ["报告期", "净利润", "净资产收益率"]
        mock_field_service.discover_a_stock_indicator_fields.return_value = available_fields

        # 调用工具
        response = field_tool.validate_fields(
            market="a_stock",
            query_type="a_stock_indicators",
            fields=["报告期", "净利润", "不存在的字段"]
        )

        # 验证响应
        assert response["success"] is True
        assert "validation_result" in response
        validation = response["validation_result"]
        assert validation["valid_fields"] == ["报告期", "净利润"]
        assert validation["invalid_fields"] == ["不存在的字段"]
        assert validation["valid_field_count"] == 2
        assert validation["invalid_field_count"] == 1

    def test_字段建议功能(self, field_tool):
        """测试字段建议功能"""
        available_fields = {"净利润", "营业收入", "净资产收益率", "总资产收益率"}
        invalid_fields = ["净利", "营收", "invalid_field"]

        suggestions = field_tool._suggest_similar_fields(invalid_fields, available_fields)

        # 验证建议结果
        assert len(suggestions) == 2  # 应该为"净利"和"营收"提供建议

        # 找到"净利"的建议
        profit_suggestion = next((s for s in suggestions if s["invalid_field"] == "净利"), None)
        assert profit_suggestion is not None
        assert "净利润" in profit_suggestion["suggestions"]

        # 找到"营收"的建议
        revenue_suggestion = next((s for s in suggestions if s["invalid_field"] == "营收"), None)
        assert revenue_suggestion is not None
        assert "营业收入" in revenue_suggestion["suggestions"]

    def test_获取市场显示名称(self, field_tool):
        """测试获取市场显示名称"""
        assert field_tool._get_market_display_name(MarketType.A_STOCK) == "A股市场"
        assert field_tool._get_market_display_name(MarketType.HK_STOCK) == "港股市场"
        assert field_tool._get_market_display_name(MarketType.US_STOCK) == "美股市场"


class TestMCPIntegration:
    """测试MCP集成"""

    @pytest.fixture
    def mock_services(self):
        """模拟服务"""
        financial_service = Mock()
        field_service = Mock()
        return financial_service, field_service

    @pytest.fixture
    def tools(self, mock_services):
        """工具实例"""
        financial_tool = FinancialQueryTool(mock_services[0])
        field_tool = FieldDiscoveryTool(mock_services[1])
        return financial_tool, field_tool

    def test_完整查询流程(self, tools, mock_services):
        """测试完整查询流程"""
        financial_tool, field_tool = tools
        financial_service, field_service = mock_services

        # 1. 先获取可用字段
        field_service.discover_a_stock_indicator_fields.return_value = [
            "报告期", "净利润", "净资产收益率", "营业收入"
        ]
        fields_response = field_tool.discover_fields(
            market="a_stock",
            query_type="a_stock_indicators"
        )
        assert fields_response["success"] is True

        # 2. 查询财务数据
        sample_response = {
            "status": "success",
            "data": {
                "records": [{"报告期": "2023-12-31", "净利润": 100.0}],
                "columns": ["报告期", "净利润"],
                "shape": (1, 2),
                "empty": False
            },
            "metadata": {
                "record_count": 1,
                "field_count": 2,
                "market": "a_stock",
                "query_type": "A股财务指标"
            },
            "timestamp": "2024-01-01T00:00:00"
        }
        financial_service.query.return_value = sample_response

        query_response = financial_tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="600519",
            fields=["报告期", "净利润"]
        )

        assert query_response["success"] is True
        assert query_response["data"]["records"][0]["净利润"] == 100.0

    def test_错误处理和恢复(self, tools, mock_services):
        """测试错误处理和恢复"""
        financial_tool, field_tool = tools
        financial_service, field_service = mock_services

        # 模拟服务异常
        financial_service.query.side_effect = Exception("数据库连接失败")

        response = financial_tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="600519"
        )

        assert response["success"] is False
        assert "error" in response
        assert "查询执行失败" in response["error"]["message"]

    def test_参数验证和错误消息(self, financial_tool):
        """测试参数验证和错误消息"""
        # 测试无效市场类型
        response = financial_tool.query_financial_data(
            market="invalid_market",
            query_type="a_stock_indicators",
            symbol="600519"
        )
        assert response["success"] is False
        assert "无效的市场类型" in response["error"]["message"]

        # 测试无效查询类型
        response = financial_tool.query_financial_data(
            market="a_stock",
            query_type="invalid_query_type",
            symbol="600519"
        )
        assert response["success"] is False
        assert "无效的查询类型" in response["error"]["message"]

        # 测试无效频率
        response = financial_tool.query_financial_data(
            market="a_stock",
            query_type="a_stock_indicators",
            symbol="600519",
            frequency="invalid_frequency"
        )
        assert response["success"] is False
        assert "无效的时间频率" in response["error"]["message"]