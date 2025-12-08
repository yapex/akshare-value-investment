"""
MCP服务器核心实现

提供MCP协议的服务器实现，包括工具调用、请求处理和响应管理。
"""

import json
import asyncio
import logging
import time
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
        self.financial_query_tool = FinancialQueryTool(
            api_base_url=self.config.fastapi_base_url
        )
        self.field_discovery_tool = FieldDiscoveryTool(
            api_base_url=self.config.fastapi_base_url
        )

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

    async def start(self):
        """
        启动 MCP 服务器

        提供简单的控制台交互模式，等待用户输入并处理 MCP 请求。
        """
        self.logger.info(f"MCP 服务器启动在 {self.config.host}:{self.config.port}")

        print(f"🟢 MCP 服务器已启动")
        print(f"📡 监听地址: {self.config.host}:{self.config.port}")
        print(f"🔗 FastAPI 服务: {self.config.fastapi_base_url}")
        print("💡 输入 'help' 查看可用工具")
        print("💡 输入 'quit' 或 'exit' 退出服务器")
        print("=" * 50)

        try:
            while True:
                try:
                    # 获取用户输入
                    user_input = input("\n🔧 请输入工具名称或命令: ").strip()

                    if not user_input:
                        continue

                    # 处理命令
                    if user_input.lower() in ["quit", "exit", "退出"]:
                        print("👋 正在停止 MCP 服务器...")
                        break

                    if user_input.lower() in ["help", "帮助"]:
                        self._show_help()
                        continue

                    if user_input.lower() in ["status", "状态"]:
                        self._show_status()
                        continue

                    # 处理工具调用
                    await self._handle_interactive_tool_call(user_input)

                except EOFError:
                    print("\n👋 输入结束，服务器停止")
                    break
                except KeyboardInterrupt:
                    print("\n👋 服务器已停止")
                    break

        finally:
            # 清理资源
            if hasattr(self, 'financial_query_tool') and hasattr(self.financial_query_tool, 'client'):
                self.financial_query_tool.client.close()
            if hasattr(self, 'field_discovery_tool') and hasattr(self.field_discovery_tool, 'client'):
                self.field_discovery_tool.client.close()

            self.logger.info("MCP 服务器已停止")

    def _show_help(self):
        """显示帮助信息"""
        print("\n📋 可用工具:")
        print("1. query_financial_data - 查询财务数据")
        print("2. get_available_fields - 获取可用字段")
        print("3. discover_fields - 发现字段")
        print("4. validate_fields - 验证字段")
        print("5. discover_all_market_fields - 发现市场所有字段")
        print("\n📋 可用命令:")
        print("- help/帮助: 显示此帮助信息")
        print("- status/状态: 显示服务器状态")
        print("- quit/exit/退出: 停止服务器")

    def _show_status(self):
        """显示服务器状态"""
        print(f"\n📊 服务器状态:")
        print(f"🖥️  服务器名称: {self.config.server_name}")
        print(f"📖 版本: {self.config.server_version}")
        print(f"📡 监听地址: {self.config.host}:{self.config.port}")
        print(f"🔗 FastAPI 服务: {self.config.fastapi_base_url}")
        print(f"🐛 调试模式: {'开启' if self.config.debug else '关闭'}")

    async def _handle_interactive_tool_call(self, tool_name: str):
        """处理交互式工具调用"""
        try:
            # 根据工具名称获取参数
            if tool_name == "query_financial_data":
                params = self._get_financial_query_params()
            elif tool_name == "get_available_fields":
                params = self._get_field_discovery_params()
            elif tool_name == "discover_fields":
                params = self._get_field_discovery_params()
            elif tool_name == "validate_fields":
                params = self._get_field_validation_params()
            elif tool_name == "discover_all_market_fields":
                params = {"market": input("请输入市场类型 (a_stock/hk_stock/us_stock): ").strip()}
            else:
                print(f"❌ 未知工具: {tool_name}")
                return

            # 创建请求并处理
            request = {
                "tool": tool_name,
                "parameters": params,
                "id": f"interactive_{int(time.time())}"
            }

            print(f"\n🔄 正在调用工具: {tool_name}")
            response = await self.handle_request(request)

            # 显示结果
            if response.get("success"):
                print("✅ 工具调用成功")
                result = response.get("result", {})
                if isinstance(result, dict):
                    # 格式化输出
                    for key, value in result.items():
                        if key == "available_fields" and isinstance(value, list):
                            print(f"📋 {key}: {len(value)} 个字段")
                            if value:
                                print(f"   前 5 个: {value[:5]}")
                        elif key == "field_count":
                            print(f"📊 {key}: {value}")
                        elif key == "success":
                            print(f"✅ {key}: {value}")
                        else:
                            print(f"📄 {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
                else:
                    print(f"📄 结果: {result}")
            else:
                print("❌ 工具调用失败")
                error = response.get("error", {})
                print(f"📄 错误: {error.get('message', '未知错误')}")

        except Exception as e:
            print(f"❌ 工具调用异常: {e}")

    def _get_financial_query_params(self):
        """获取财务查询参数"""
        params = {
            "market": input("请输入市场类型 (a_stock/hk_stock/us_stock): ").strip(),
            "query_type": input("请输入查询类型: ").strip(),
            "symbol": input("请输入股票代码: ").strip(),
            "frequency": input("请输入时间频率 (annual/quarterly，默认 annual): ").strip() or "annual"
        }

        # 可选参数
        fields = input("请输入字段列表 (逗号分隔，可选): ").strip()
        if fields:
            params["fields"] = [f.strip() for f in fields.split(",")]

        start_date = input("请输入开始日期 (YYYY-MM-DD，可选): ").strip()
        if start_date:
            params["start_date"] = start_date

        end_date = input("请输入结束日期 (YYYY-MM-DD，可选): ").strip()
        if end_date:
            params["end_date"] = end_date

        return params

    def _get_field_discovery_params(self):
        """获取字段发现参数"""
        return {
            "market": input("请输入市场类型 (a_stock/hk_stock/us_stock): ").strip(),
            "query_type": input("请输入查询类型: ").strip()
        }

    def _get_field_validation_params(self):
        """获取字段验证参数"""
        fields_input = input("请输入要验证的字段 (逗号分隔): ").strip()
        fields = [f.strip() for f in fields_input.split(",")] if fields_input else []

        return {
            "market": input("请输入市场类型 (a_stock/hk_stock/us_stock): ").strip(),
            "query_type": input("请输入查询类型: ").strip(),
            "fields": fields
        }


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