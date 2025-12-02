"""
MCP服务器核心实现

提供MCP协议的服务器实现，包括工具调用、请求处理和响应管理。
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .config import MCPServerConfig, tool_registry, setup_logging
from .tools import FinancialQueryTool, FieldDiscoveryTool


class MCPServer:
    """
    MCP服务器核心类

    实现MCP协议的服务器端，处理工具调用和响应管理。
    """

    def __init__(self, config: Optional[MCPServerConfig] = None):
        """
        初始化MCP服务器

        Args:
            config: 服务器配置，如果为None则使用默认配置
        """
        self.config = config or MCPServerConfig()
        self.logger = logging.getLogger(__name__)

        # 初始化工具实例
        self._init_tools()

        # 设置日志
        setup_logging(self.config)

        self.logger.info(f"MCP服务器初始化完成: {self.config.server_name} v{self.config.server_version}")

    def _init_tools(self) -> None:
        """初始化工具实例"""
        self.financial_query_tool = FinancialQueryTool()
        self.field_discovery_tool = FieldDiscoveryTool()

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: MCP请求数据

        Returns:
            MCP响应数据
        """
        try:
            # 验证请求格式
            if not self._validate_request(request):
                return self._create_error_response(
                    "invalid_request",
                    "请求格式无效",
                    request_id=request.get("id")
                )

            tool_name = request.get("tool")
            parameters = request.get("parameters", {})
            request_id = request.get("id")

            self.logger.info(f"处理MCP请求: {tool_name}, 参数: {parameters}")

            # 路由到对应的工具
            response = await self._route_to_tool(tool_name, parameters)

            # 添加请求ID和元信息
            response["id"] = request_id
            response["timestamp"] = datetime.now().isoformat()
            response["server_info"] = {
                "name": self.config.server_name,
                "version": self.config.server_version
            }

            return response

        except Exception as e:
            self.logger.error(f"处理MCP请求失败: {e}", exc_info=True)
            return self._create_error_response(
                "internal_error",
                f"服务器内部错误: {str(e)}",
                request_id=request.get("id")
            )

    async def _route_to_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        路由请求到对应的工具

        Args:
            tool_name: 工具名称
            parameters: 工具参数

        Returns:
            工具执行结果
        """
        # 首先检查内置方法
        if tool_name == "get_tools_info":
            return {"success": True, "result": self.get_tools_info()}

        # 获取工具信息
        tool_info = tool_registry.get_tool_info(tool_name)
        if not tool_info:
            return self._create_error_response(
                "tool_not_found",
                f"未找到工具: {tool_name}"
            )

        # 根据工具名称调用对应的方法
        if tool_name == "query_financial_data":
            return await self._handle_query_financial_data(parameters)
        elif tool_name == "get_available_fields":
            return await self._handle_get_available_fields(parameters)
        elif tool_name == "discover_fields":
            return await self._handle_discover_fields(parameters)
        elif tool_name == "validate_fields":
            return await self._handle_validate_fields(parameters)
        elif tool_name == "discover_all_market_fields":
            return await self._handle_discover_all_market_fields(parameters)
        else:
            return self._create_error_response(
                "unsupported_tool",
                f"不支持的工具: {tool_name}"
            )

    async def _handle_query_financial_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理财务数据查询请求"""
        try:
            result = self.financial_query_tool.query_financial_data(
                market=parameters.get("market"),
                query_type=parameters.get("query_type"),
                symbol=parameters.get("symbol"),
                fields=parameters.get("fields"),
                start_date=parameters.get("start_date"),
                end_date=parameters.get("end_date"),
                frequency=parameters.get("frequency", "annual")
            )
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"财务数据查询失败: {e}", exc_info=True)
            return self._create_error_response("query_error", f"财务数据查询失败: {str(e)}")

    async def _handle_get_available_fields(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取可用字段请求"""
        try:
            result = self.financial_query_tool.get_available_fields(
                market=parameters.get("market"),
                query_type=parameters.get("query_type")
            )
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"获取可用字段失败: {e}", exc_info=True)
            return self._create_error_response("query_error", f"获取可用字段失败: {str(e)}")

    async def _handle_discover_fields(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理字段发现请求"""
        try:
            result = self.field_discovery_tool.discover_fields(
                market=parameters.get("market"),
                query_type=parameters.get("query_type")
            )
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"字段发现失败: {e}", exc_info=True)
            return self._create_error_response("query_error", f"字段发现失败: {str(e)}")

    async def _handle_validate_fields(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理字段验证请求"""
        try:
            result = self.field_discovery_tool.validate_fields(
                market=parameters.get("market"),
                query_type=parameters.get("query_type"),
                fields=parameters.get("fields", [])
            )
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"字段验证失败: {e}", exc_info=True)
            return self._create_error_response("query_error", f"字段验证失败: {str(e)}")

    async def _handle_discover_all_market_fields(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理发现市场所有字段请求"""
        try:
            result = self.field_discovery_tool.discover_all_market_fields(
                market=parameters.get("market")
            )
            return {"success": True, "result": result}
        except Exception as e:
            self.logger.error(f"发现市场所有字段失败: {e}", exc_info=True)
            return self._create_error_response("query_error", f"发现市场所有字段失败: {str(e)}")

    def _validate_request(self, request: Dict[str, Any]) -> bool:
        """
        验证请求格式

        Args:
            request: 请求数据

        Returns:
            是否有效
        """
        if not isinstance(request, dict):
            return False

        if "tool" not in request:
            return False

        if not isinstance(request["tool"], str):
            return False

        if "parameters" in request and not isinstance(request["parameters"], dict):
            return False

        return True

    def _create_error_response(
        self,
        error_code: str,
        error_message: str,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            error_code: 错误代码
            error_message: 错误消息
            request_id: 请求ID

        Returns:
            错误响应数据
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message
            },
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "name": self.config.server_name,
                "version": self.config.server_version
            }
        }

        if request_id:
            response["id"] = request_id

        return response

    def get_tools_info(self) -> Dict[str, Any]:
        """
        获取所有已注册工具的信息

        Returns:
            工具信息字典
        """
        tools_info = {}

        for tool_name, tool_info in tool_registry.get_all_tools().items():
            tools_info[tool_name] = {
                "name": tool_info["name"],
                "description": tool_info["description"],
                "schema": tool_info["schema"],
                "examples": tool_info["examples"]
            }

        return {
            "server_info": {
                "name": self.config.server_name,
                "version": self.config.server_version,
                "description": self.config.description
            },
            "tools": tools_info,
            "total_tools": len(tools_info)
        }

    def get_supported_markets(self) -> List[str]:
        """
        获取支持的市场类型

        Returns:
            支持的市场类型列表
        """
        return ["a_stock", "hk_stock", "us_stock"]

    def get_supported_query_types(self, market: str) -> List[str]:
        """
        获取指定市场支持的查询类型

        Args:
            market: 市场类型

        Returns:
            支持的查询类型列表
        """
        if market == "a_stock":
            return [
                "a_stock_indicators",
                "a_stock_balance_sheet",
                "a_stock_income_statement",
                "a_stock_cash_flow"
            ]
        elif market == "hk_stock":
            return [
                "hk_stock_indicators",
                "hk_stock_statements"
            ]
        elif market == "us_stock":
            return [
                "us_stock_indicators",
                "us_stock_balance_sheet",
                "us_stock_income_statement",
                "us_stock_cash_flow"
            ]
        return []


# 便捷函数
def create_server(config: Optional[MCPServerConfig] = None) -> MCPServer:
    """
    创建MCP服务器实例

    Args:
        config: 服务器配置

    Returns:
        MCP服务器实例
    """
    return MCPServer(config)


# 服务器实例（单例模式）
_server_instance: Optional[MCPServer] = None


def get_server() -> MCPServer:
    """
    获取全局服务器实例

    Returns:
        MCP服务器实例
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPServer()
    return _server_instance