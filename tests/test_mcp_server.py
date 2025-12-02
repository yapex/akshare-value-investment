"""
MCP服务器集成测试

测试MCP服务器的请求处理、工具路由和响应格式。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.akshare_value_investment.mcp.server import MCPServer, create_server
from src.akshare_value_investment.mcp.config import MCPServerConfig, tool_registry


class TestMCPServer:
    """测试MCP服务器"""

    @pytest.fixture
    def server_config(self):
        """服务器配置"""
        return MCPServerConfig(
            server_name="test-server",
            server_version="1.0.0-test",
            debug=True
        )

    @pytest.fixture
    def server(self, server_config):
        """MCP服务器实例"""
        return MCPServer(server_config)

    @pytest.mark.asyncio
    async def test_处理获取工具信息请求(self, server):
        """测试处理获取工具信息请求"""
        request = {
            "tool": "get_tools_info",
            "parameters": {},
            "id": "test-001"
        }

        response = await server.handle_request(request)

        assert response["success"] is True
        assert "result" in response
        assert response["result"]["server_info"]["name"] == "test-server"
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0

    @pytest.mark.asyncio
    async def test_处理获取可用字段请求(self, server):
        """测试处理获取可用字段请求"""
        request = {
            "tool": "get_available_fields",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            },
            "id": "test-002"
        }

        with patch.object(server.financial_query_tool, 'get_available_fields') as mock_method:
            # 设置模拟返回
            mock_method.return_value = {
                "success": True,
                "available_fields": ["报告期", "净利润", "净资产收益率"],
                "field_count": 3,
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            }

            response = await server.handle_request(request)

            assert response["success"] is True
            assert "result" in response
            assert response["result"]["success"] is True
            mock_method.assert_called_once_with(market="a_stock", query_type="a_stock_indicators")

    @pytest.mark.asyncio
    async def test_处理财务数据查询请求(self, server):
        """测试处理财务数据查询请求"""
        request = {
            "tool": "query_financial_data",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "symbol": "600519",
                "fields": ["报告期", "净利润"],
                "frequency": "annual"
            },
            "id": "test-003"
        }

        with patch.object(server.financial_query_tool, 'query_financial_data') as mock_method:
            # 设置模拟返回
            mock_method.return_value = {
                "success": True,
                "data": {
                    "records": [{"报告期": "2023-12-31", "净利润": 100.0}],
                    "columns": ["报告期", "净利润"],
                    "shape": (1, 2),
                    "empty": False
                },
                "metadata": {
                    "record_count": 1,
                    "field_count": 2,
                    "market": "a_stock"
                }
            }

            response = await server.handle_request(request)

            assert response["success"] is True
            assert "result" in response
            mock_method.assert_called_once_with(
                market="a_stock",
                query_type="a_stock_indicators",
                symbol="600519",
                fields=["报告期", "净利润"],
                frequency="annual",
                start_date=None,
                end_date=None
            )

    @pytest.mark.asyncio
    async def test_处理字段发现请求(self, server):
        """测试处理字段发现请求"""
        request = {
            "tool": "discover_fields",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            },
            "id": "test-004"
        }

        with patch.object(server.field_discovery_tool, 'discover_fields') as mock_method:
            # 设置模拟返回
            mock_method.return_value = {
                "success": True,
                "available_fields": ["报告期", "净利润", "净资产收益率"],
                "field_count": 3,
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            }

            response = await server.handle_request(request)

            assert response["success"] is True
            assert "result" in response
            mock_method.assert_called_once_with(market="a_stock", query_type="a_stock_indicators")

    @pytest.mark.asyncio
    async def test_处理字段验证请求(self, server):
        """测试处理字段验证请求"""
        request = {
            "tool": "validate_fields",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "fields": ["报告期", "净利润", "不存在的字段"]
            },
            "id": "test-005"
        }

        with patch.object(server.field_discovery_tool, 'validate_fields') as mock_method:
            # 设置模拟返回
            mock_method.return_value = {
                "success": True,
                "validation_result": {
                    "valid_fields": ["报告期", "净利润"],
                    "invalid_fields": ["不存在的字段"],
                    "valid_field_count": 2,
                    "invalid_field_count": 1,
                    "total_requested": 3
                },
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            }

            response = await server.handle_request(request)

            assert response["success"] is True
            assert "result" in response
            mock_method.assert_called_once_with(
                market="a_stock",
                query_type="a_stock_indicators",
                fields=["报告期", "净利润", "不存在的字段"]
            )

    @pytest.mark.asyncio
    async def test_处理发现市场所有字段请求(self, server):
        """测试处理发现市场所有字段请求"""
        request = {
            "tool": "discover_all_market_fields",
            "parameters": {
                "market": "a_stock"
            },
            "id": "test-006"
        }

        with patch.object(server.field_discovery_tool, 'discover_all_market_fields') as mock_method:
            # 设置模拟返回
            mock_method.return_value = {
                "success": True,
                "market": "a_stock",
                "all_fields": {
                    "a_stock_indicators": {
                        "fields": ["报告期", "净利润"],
                        "field_count": 2,
                        "display_name": "A股财务指标"
                    },
                    "a_stock_balance_sheet": {
                        "fields": ["资产总计", "负债合计"],
                        "field_count": 2,
                        "display_name": "A股资产负债表"
                    }
                },
                "total_field_count": 4,
                "query_type_count": 2
            }

            response = await server.handle_request(request)

            assert response["success"] is True
            assert "result" in response
            mock_method.assert_called_once_with(market="a_stock")

    @pytest.mark.asyncio
    async def test_处理无效工具请求(self, server):
        """测试处理无效工具请求"""
        request = {
            "tool": "non_existent_tool",
            "parameters": {},
            "id": "test-007"
        }

        response = await server.handle_request(request)

        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "tool_not_found"

    @pytest.mark.asyncio
    async def test_处理无效请求格式(self, server):
        """测试处理无效请求格式"""
        # 缺少tool字段
        request = {
            "parameters": {},
            "id": "test-008"
        }

        response = await server.handle_request(request)

        assert response["success"] is False
        assert "error" in response
        assert response["error"]["code"] == "invalid_request"

    @pytest.mark.asyncio
    async def test_处理工具异常(self, server):
        """测试处理工具异常"""
        request = {
            "tool": "query_financial_data",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "symbol": "600519"
            },
            "id": "test-009"
        }

        with patch.object(server.financial_query_tool, 'query_financial_data') as mock_method:
            # 设置抛出异常
            mock_method.side_effect = Exception("模拟工具异常")

            response = await server.handle_request(request)

            assert response["success"] is False
            assert "error" in response
            assert response["error"]["code"] == "query_error"

    def test_验证请求格式(self, server):
        """测试验证请求格式"""
        # 有效请求
        valid_request = {
            "tool": "test_tool",
            "parameters": {}
        }
        assert server._validate_request(valid_request) is True

        # 无效请求 - 缺少tool
        invalid_request1 = {
            "parameters": {}
        }
        assert server._validate_request(invalid_request1) is False

        # 无效请求 - tool不是字符串
        invalid_request2 = {
            "tool": 123,
            "parameters": {}
        }
        assert server._validate_request(invalid_request2) is False

        # 无效请求 - parameters不是字典
        invalid_request3 = {
            "tool": "test_tool",
            "parameters": "not a dict"
        }
        assert server._validate_request(invalid_request3) is False

    def test_创建错误响应(self, server):
        """测试创建错误响应"""
        error_response = server._create_error_response(
            error_code="test_error",
            error_message="测试错误消息",
            request_id="test-010"
        )

        assert error_response["success"] is False
        assert error_response["error"]["code"] == "test_error"
        assert error_response["error"]["message"] == "测试错误消息"
        assert error_response["id"] == "test-010"
        assert "timestamp" in error_response
        assert "server_info" in error_response

    def test_获取工具信息(self, server):
        """测试获取工具信息"""
        tools_info = server.get_tools_info()

        assert "server_info" in tools_info
        assert "tools" in tools_info
        assert "total_tools" in tools_info

        server_info = tools_info["server_info"]
        assert server_info["name"] == "test-server"
        assert server_info["version"] == "1.0.0-test"

        tools = tools_info["tools"]
        assert len(tools) > 0
        assert "query_financial_data" in tools
        assert "get_available_fields" in tools

    def test_获取支持的市场和查询类型(self, server):
        """测试获取支持的市场和查询类型"""
        markets = server.get_supported_markets()
        assert "a_stock" in markets
        assert "hk_stock" in markets
        assert "us_stock" in markets

        a_stock_query_types = server.get_supported_query_types("a_stock")
        assert "a_stock_indicators" in a_stock_query_types
        assert len(a_stock_query_types) == 4

        hk_stock_query_types = server.get_supported_query_types("hk_stock")
        assert "hk_stock_indicators" in hk_stock_query_types
        assert len(hk_stock_query_types) == 2

        us_stock_query_types = server.get_supported_query_types("us_stock")
        assert "us_stock_indicators" in us_stock_query_types
        assert len(us_stock_query_types) == 4

        invalid_query_types = server.get_supported_query_types("invalid_market")
        assert len(invalid_query_types) == 0


class TestMCPConfig:
    """测试MCP配置"""

    def test_工具注册(self):
        """测试工具注册"""
        all_tools = tool_registry.get_all_tools()
        assert len(all_tools) > 0

        # 检查是否注册了预期的工具
        expected_tools = [
            "query_financial_data",
            "get_available_fields",
            "discover_fields",
            "validate_fields",
            "discover_all_market_fields"
        ]

        for tool_name in expected_tools:
            assert tool_name in all_tools
            tool_info = tool_registry.get_tool_info(tool_name)
            assert tool_info is not None
            assert "name" in tool_info
            assert "description" in tool_info
            assert "schema" in tool_info

    def test_创建服务器(self):
        """测试创建服务器"""
        # 使用默认配置创建
        server1 = create_server()
        assert server1.config.server_name == "akshare-value-investment-mcp"

        # 使用自定义配置创建
        custom_config = MCPServerConfig(
            server_name="custom-server",
            debug=True
        )
        server2 = create_server(custom_config)
        assert server2.config.server_name == "custom-server"
        assert server2.config.debug is True

    def test_服务器单例(self):
        """测试服务器单例"""
        from src.akshare_value_investment.mcp.server import get_server

        server1 = get_server()
        server2 = get_server()

        # 应该是同一个实例
        assert server1 is server2


class TestMCPIntegration:
    """MCP集成测试"""

    @pytest.mark.asyncio
    async def test_完整的查询流程(self):
        """测试完整的查询流程"""
        server = MCPServer()

        # 1. 获取可用字段
        fields_request = {
            "tool": "get_available_fields",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            }
        }

        with patch.object(server.financial_query_tool, 'get_available_fields') as mock_fields:
            mock_fields.return_value = {
                "success": True,
                "available_fields": ["报告期", "净利润", "净资产收益率"],
                "field_count": 3,
                "market": "a_stock",
                "query_type": "a_stock_indicators"
            }

            fields_response = await server.handle_request(fields_request)
            assert fields_response["success"] is True

        # 2. 使用字段进行查询
        query_request = {
            "tool": "query_financial_data",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "symbol": "600519",
                "fields": ["报告期", "净利润"]
            }
        }

        with patch.object(server.financial_query_tool, 'query_financial_data') as mock_query:
            mock_query.return_value = {
                "success": True,
                "data": {
                    "records": [{"报告期": "2023-12-31", "净利润": 100.0}],
                    "columns": ["报告期", "净利润"],
                    "shape": (1, 2),
                    "empty": False
                },
                "metadata": {
                    "record_count": 1,
                    "field_count": 2,
                    "market": "a_stock"
                }
            }

            query_response = await server.handle_request(query_request)
            assert query_response["success"] is True
            assert query_response["result"]["data"]["records"][0]["净利润"] == 100.0

    @pytest.mark.asyncio
    async def test_错误恢复和重试(self):
        """测试错误恢复和重试"""
        server = MCPServer()

        request = {
            "tool": "query_financial_data",
            "parameters": {
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "symbol": "600519"
            }
        }

        with patch.object(server.financial_query_tool, 'query_financial_data') as mock_method:
            # 第一次调用失败
            mock_method.side_effect = [
                Exception("网络错误"),
                {
                    "success": True,
                    "data": {"records": [], "columns": [], "shape": (0, 0), "empty": True},
                    "metadata": {"record_count": 0, "field_count": 0}
                }
            ]

            # 第一次请求应该失败
            response1 = await server.handle_request(request)
            assert response1["success"] is False
            assert response1["error"]["code"] == "query_error"

            # 第二次请求应该成功（模拟重试）
            response2 = await server.handle_request(request)
            assert response2["success"] is True