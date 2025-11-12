"""
重构后的MCP服务器 - 轻量级适配器

只负责MCP框架交互，业务逻辑完全委托给服务层。
遵循单一职责原则，易于测试和维护。
"""

import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import List, Dict, Any

from mcp.server import Server, NotificationOptions

# 删除模块级别的日志初始化，避免重复和多余的日志信息
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

from .services import (
    FinancialIndicatorQueryService,
    FieldDiscoveryService
)


class AkshareMCPServerV2:
    """重构后的akshare财务数据MCP服务器"""

    def __init__(self,
                 financial_service: FinancialIndicatorQueryService,
                 field_discovery_service: FieldDiscoveryService,
                 response_formatter: Any = None):  # 使用Any避免循环依赖
        """
        初始化MCP服务器

        Args:
            financial_service: 财务指标查询服务
            field_discovery_service: 字段发现服务
            response_formatter: 响应格式化器（可选，遵循依赖注入原则）
        """
        self.server = Server("akshare-value-investment")
        self.financial_service = financial_service
        self.field_discovery_service = field_discovery_service
        self.logger = logging.getLogger("investment.mcp_server")

        # 使用依赖注入的格式化器，如果没有提供则使用默认实现
        if response_formatter is None:
            from .mcp.formatters import ResponseFormatter
            self.response_formatter = ResponseFormatter()
        else:
            self.response_formatter = response_formatter

        self._setup_handlers()

  
    def _setup_handlers(self):
        """设置MCP处理器 - 只做路由，不包含业务逻辑"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="query_financial_indicators",
                    description="🔍 智能查询股票财务指标，支持自然语言查询跨市场数据（A股、港股、美股）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                            },
                            "query": {
                                "type": "string",
                                "description": "财务指标查询，支持中英文自然语言，例如：'每股收益'、'ROE'、'公司赚了多少钱'、'EPS'、'毛利率'、'Revenue'"
                            },
                            "prefer_annual": {
                                "type": "boolean",
                                "description": "是否优先返回年度数据",
                                "default": True
                            },
                            "start_date": {
                                "type": "string",
                                "description": "查询开始日期，格式：YYYY-MM-DD"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "查询结束日期，格式：YYYY-MM-DD"
                            }
                        },
                        "required": ["symbol", "query"]
                    }
                ),
                Tool(
                    name="search_financial_fields",
                    description="🔎 搜索财务指标字段，了解可查询的财务指标",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "搜索关键字，例如：'利润'、'ROE'、'Revenue'、'每股'、'增长'"
                            },
                            "market": {
                                "type": "string",
                                "description": "市场类型：'a_stock'(A股)、'hk_stock'(港股)、'us_stock'(美股)、'all'(全部，默认)",
                                "default": "all"
                            }
                        },
                        "required": ["keyword"]
                    }
                ),
                Tool(
                    name="get_field_details",
                    description="📋 获取财务指标详细信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "field_name": {
                                "type": "string",
                                "description": "字段名，例如：'净利润'、'BASIC_EPS'、'ROE'、'毛利率'"
                            }
                        },
                        "required": ["field_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """处理工具调用 - 委托给相应服务"""
            try:
                if name == "query_financial_indicators":
                    return await self._handle_query_financial_indicators(arguments)
                elif name == "search_financial_fields":
                    return await self._handle_search_financial_fields(arguments)
                elif name == "get_field_details":
                    return await self._handle_get_field_details(arguments)
                else:
                    return self._format_error_response(f"未知工具: {name}")

            except Exception as e:
                return self._format_error_response(f"处理请求时发生错误: {str(e)}")

    async def _handle_query_financial_indicators(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理智能财务数据查询请求"""
        try:
            # 验证必要参数
            symbol = arguments.get("symbol", "")
            query = arguments.get("query", "")

            if not symbol:
                return self._format_error_response("股票代码不能为空")
            if not query:
                return self._format_error_response("查询内容不能为空")

            # 记录查询请求
            self.logger.info(f"查询：股票={symbol}, 内容={query}")

            # 提取参数
            prefer_annual = arguments.get("prefer_annual", True)
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")

            # 使用简化查询方法避免异步问题
            result = self._query_financial_indicators_sync(
                symbol=symbol,
                field_query=query,
                prefer_annual=prefer_annual,
                start_date=start_date,
                end_date=end_date
            )

            # 格式化响应
            if result.get("success"):
                data = result.get("data", [])
                if data:
                    self.logger.info(f"返回 [{symbol}] {len(data)} 条数据")
                    # 使用依赖注入的格式化器，遵循依赖倒置原则
                    response_text = self.response_formatter.format_query_response(
                        symbol, query, data, prefer_annual=prefer_annual
                    )
                else:
                    self.logger.warning(f"查询成功但无数据: 股票 {symbol}, 查询 {query}")
                    response_text = f"❌ 未找到匹配 '{query}' 的财务数据"
            else:
                self.logger.error(f"查询失败: {result.get('message', '未知错误')}")
                response_text = f"❌ 查询失败: {result.get('message', '未知错误')}"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)],
                isError=False
            )

        except Exception as e:
            self.logger.error(f"处理查询请求异常: {str(e)}")
            return self._format_error_response(f"查询处理失败: {str(e)}")

    async def _handle_search_financial_fields(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理财务字段搜索请求"""
        try:
            keyword = arguments.get("keyword", "")
            market = arguments.get("market", "all")

            if not keyword:
                return self._format_error_response("搜索关键字不能为空")

            # 使用智能字段映射器进行真实搜索
            from .business.mapping.field_mapper import FinancialFieldMapper

            field_mapper = FinancialFieldMapper()

            # 确定市场过滤
            market_id = None if market == "all" else market

            # 执行真实搜索
            search_results = field_mapper.search_similar_fields(keyword, market_id, max_results=10)

            if not search_results:
                response_text = f"🔍 搜索财务字段: {keyword}\n\n"
                response_text += "❌ 未找到匹配的字段\n\n"
                response_text += "💡 建议:\n"
                response_text += "- 尝试使用更通用的关键词\n"
                response_text += "- 检查市场类型是否正确\n"
                response_text += "- 尝试相关同义词"
            else:
                response_text = f"🔍 搜索财务字段: {keyword}\n\n"
                response_text += f"✅ 找到 {len(search_results)} 个相关字段:\n\n"

                for i, (field_id, similarity, field_info, market_id) in enumerate(search_results, 1):
                    market_names = {
                        'a_stock': 'A股',
                        'hk_stock': '港股',
                        'us_stock': '美股'
                    }
                    market_name = market_names.get(market_id, market_id)

                    response_text += f"**{i}. {field_info.name}**\n"
                    response_text += f"   - 字段ID: `{field_id}`\n"
                    response_text += f"   - 市场: {market_name}\n"
                    response_text += f"   - 相似度: {similarity:.2f}\n"
                    response_text += f"   - 关键词: {', '.join(field_info.keywords[:5])}"
                    if len(field_info.keywords) > 5:
                        response_text += f" 等{len(field_info.keywords)}个"
                    response_text += f"\n"
                    response_text += f"   - 描述: {field_info.description}\n\n"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)],
                isError=False
            )

        except Exception as e:
            import traceback
            error_details = f"字段搜索失败: {str(e)}\n调用栈:\n{traceback.format_exc()}"
            return self._format_error_response(error_details)

    async def _handle_get_field_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理获取字段详情请求"""
        try:
            field_name = arguments.get("field_name", "")
            if not field_name:
                return self._format_error_response("字段名不能为空")

            # 简化响应
            response_text = f"📋 字段详情: {field_name}\n\n"
            response_text += "字段类型: 财务指标\n"
            response_text += "数据来源: akshare\n"
            response_text += "更新频率: 季度\n"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)],
                isError=False
            )

        except Exception as e:
            return self._format_error_response(f"获取字段详情失败: {str(e)}")

    def _simple_query_test(self, symbol: str, field_query: str) -> Dict[str, Any]:
        """
        最简单的查询测试方法，完全绕过复杂的依赖注入

        Args:
            symbol: 股票代码
            field_query: 字段查询

        Returns:
            简单的测试结果
        """
        try:
            # 完全不调用任何服务，只返回一个简单的测试结果
            return {
                "success": True,
                "data": [{
                    "symbol": symbol,
                    "market": "test_market",
                    "report_date": "2024-12-31",
                    "period_type": "test_period",
                    "raw_data": {
                        "测试字段": "测试值",
                        "查询内容": field_query
                    },
                    "metadata": {
                        "field_query": field_query,
                        "matched_field": ["测试字段"],
                        "resolution_method": "简单测试"
                    }
                }],
                "message": f"简单测试成功 - 查询 {symbol} 的 {field_query}",
                "total_records": 1
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"简单测试失败: {str(e)}",
                "total_records": 0
            }

    def _format_error_response(self, error_message: str) -> CallToolResult:
        """格式化错误响应"""
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ 错误: {error_message}"
            )],
            isError=False
        )

    async def _handle_search_financial_fields(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理财务字段搜索请求"""
        try:
            keyword = arguments.get("keyword", "")
            if not keyword:
                return self._format_error_response("搜索关键字不能为空")

            market = arguments.get("market", "all")

            # 委托给财务查询服务的字段搜索方法
            fields = self.financial_service.search_fields(keyword, market)

            # 格式化响应
            if fields:
                response_parts = [
                    f"## 🔎 财务指标搜索结果",
                    f"**关键字**: {keyword}",
                    f"**市场**: {market}",
                    f"**找到**: {len(fields)} 个相关字段",
                    f""
                ]

                for i, field in enumerate(fields[:10], 1):  # 只显示前10个
                    response_parts.append(f"{i}. {field}")

                if len(fields) > 10:
                    response_parts.append(f"... 还有 {len(fields) - 10} 个字段")

                response_text = "\n".join(response_parts)
            else:
                response_text = f"❌ 未找到与 '{keyword}' 相关的财务指标字段"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )

        except Exception as e:
            return self._format_error_response(f"字段搜索失败: {str(e)}")

    async def _handle_get_field_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理字段详细信息请求"""
        try:
            field_name = arguments.get("field_name", "")
            if not field_name:
                return self._format_error_response("字段名不能为空")

            # 委托给财务查询服务的字段信息方法
            field_info = self.financial_service.get_field_info(field_name)

            # 格式化响应
            response_parts = [
                f"## 📋 财务指标详细信息",
                f"**字段名**: {field_name}",
                f""
            ]

            if field_info:
                keywords = field_info.get("keywords", [])
                priority = field_info.get("priority", 1)
                description = field_info.get("description", "无描述")

                response_parts.extend([
                    f"**描述**: {description}",
                    f"**优先级**: {priority}",
                    f"**关键字数量**: {len(keywords)}",
                    f"**关键字**: {', '.join(keywords[:10])}",
                    ""
                ])

                if len(keywords) > 10:
                    response_parts.append(f"... 还有 {len(keywords) - 10} 个关键字")
            else:
                response_parts.append("❌ 未找到该字段的详细信息")

            response_text = "\n".join(response_parts)

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )

        except Exception as e:
            return self._format_error_response(f"获取字段详情失败: {str(e)}")

    def _query_financial_indicators_sync(self, symbol: str, field_query: str, **kwargs) -> Dict[str, Any]:
        """
        同步财务数据查询方法，使用智能字段映射系统

        Args:
            symbol: 股票代码
            field_query: 字段查询
            **kwargs: 其他查询参数

        Returns:
            查询结果字典
        """
        try:
            # 使用同步的查询服务
            base_result = self.financial_service.query(symbol, **kwargs)

            if not hasattr(base_result, 'success') or not base_result.success:
                return {
                    "success": False,
                    "data": [],
                    "message": "无法获取基础财务数据",
                    "total_records": 0
                }

            # 使用智能字段映射系统
            from .business.mapping.field_mapper import FinancialFieldMapper

            # 初始化字段映射器
            field_mapper = FinancialFieldMapper()

            # 使用智能字段映射
            mapped_fields, suggestions = field_mapper.resolve_fields_sync(symbol, [field_query])

            if not mapped_fields:
                return {
                    "success": False,
                    "data": [],
                    "message": f"无法映射查询字段 '{field_query}'。{suggestions[0] if suggestions else ''}",
                    "total_records": 0
                }

            matched_data = []
            mapped_field = mapped_fields[0]  # 使用第一个映射的字段

            for indicator in base_result.data:
                if hasattr(indicator, 'raw_data') and indicator.raw_data:
                    # 使用智能映射的字段名进行精确匹配
                    matched_fields = {}
                    for field_name, field_value in indicator.raw_data.items():
                        # 支持字段ID和字段名的匹配
                        if (field_name == mapped_field or
                            field_name.lower() == mapped_field.lower() or
                            mapped_field.lower() in field_name.lower()):
                            matched_fields[field_name] = field_value

                    if matched_fields:
                        matched_data.append({
                            "symbol": indicator.symbol,
                            "market": indicator.market,
                            "report_date": indicator.report_date,
                            "period_type": indicator.period_type,
                            "raw_data": matched_fields,
                            "metadata": {
                                "field_query": field_query,
                                "mapped_field": mapped_field,
                                "matched_field": list(matched_fields.keys()),
                                "resolution_method": "智能字段映射",
                                "suggestions": suggestions
                            }
                        })

            return {
                "success": True,
                "data": matched_data,
                "message": f"智能映射 '{field_query}' → '{mapped_field}'，成功匹配 {len(matched_data)} 条记录",
                "total_records": len(matched_data)
            }

        except Exception as e:
            import traceback
            error_details = f"智能查询内部错误: {type(e).__name__}: {str(e)}\n"
            error_details += f"调用栈:\n{traceback.format_exc()}"
            return {
                "success": False,
                "data": [],
                "message": error_details,
                "total_records": 0
            }

    def _simple_query_test(self, symbol: str, field_query: str) -> Dict[str, Any]:
        """
        最简单的查询测试方法，完全绕过复杂的依赖注入

        Args:
            symbol: 股票代码
            field_query: 字段查询

        Returns:
            简单的测试结果
        """
        try:
            # 完全不调用任何服务，只返回一个简单的测试结果
            return {
                "success": True,
                "data": [{
                    "symbol": symbol,
                    "market": "test_market",
                    "report_date": "2024-12-31",
                    "period_type": "test_period",
                    "raw_data": {
                        "测试字段": "测试值",
                        "查询内容": field_query
                    },
                    "metadata": {
                        "field_query": field_query,
                        "matched_field": ["测试字段"],
                        "resolution_method": "简单测试"
                    }
                }],
                "message": f"简单测试成功 - 查询 {symbol} 的 {field_query}",
                "total_records": 1
            }

        except Exception as e:
            import traceback
            error_details = f"简单测试内部错误: {type(e).__name__}: {str(e)}\n"
            error_details += f"调用栈:\n{traceback.format_exc()}"
            return {
                "success": False,
                "data": [],
                "message": error_details,
                "total_records": 0
            }

    def _format_error_response(self, error_message: str) -> CallToolResult:
        """格式化错误响应"""
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ 错误: {error_message}"
            )]
        )


def create_mcp_server_v2() -> AkshareMCPServerV2:
    """
    创建MCP服务器实例 - 简化方式避免依赖注入问题

    Returns:
        配置好的MCP服务器实例
    """
    try:
        # 使用依赖注入容器创建服务
        from .container import create_container
        container = create_container()
        financial_service = container.financial_query_service()
        field_discovery_service = container.field_discovery_service()

        # 创建MCP服务器
        return AkshareMCPServerV2(
            financial_service=financial_service,
            field_discovery_service=field_discovery_service
        )
    except Exception as e:
        print(f"MCP服务器创建失败: {e}")
        import traceback
        traceback.print_exc()
        # 创建一个最小化的服务器作为后备
        return AkshareMCPServerV2(
            financial_service=None,
            field_discovery_service=None
        )


# 向后兼容的主入口
def create_mcp_server() -> AkshareMCPServerV2:
    """向后兼容的创建函数"""
    return create_mcp_server_v2()


async def main():
    """启动重构后的MCP服务器"""
    # 创建重构后的MCP服务器实例
    mcp_server = create_mcp_server_v2()

    # 使用stdio传输协议
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="akshare-value-investment",
                server_version="0.2.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    import sys
    import os

    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 调试信息
    sys.stderr.write(f"🔧 MCP服务器启动中...\n")
    sys.stderr.write(f"📁 当前目录: {current_dir}\n")
    sys.stderr.write(f"📁 项目根目录: {project_root}\n")
    sys.stderr.write(f"🐍 Python路径已添加\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.stderr.write("🛑 MCP服务器已停止\n")
    except Exception as e:
        sys.stderr.write(f"❌ MCP服务器启动失败: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)