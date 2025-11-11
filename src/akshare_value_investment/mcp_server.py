"""
akshare-value-investment MCP服务器

提供简单的MCP接口，让Claude Code能够查询财务指标数据。
"""

__version__ = "0.1.0"

import asyncio
from functools import lru_cache
from typing import Any, Dict, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

# 导入现有的财务指标查询服务
from akshare_value_investment import create_production_service
from akshare_value_investment.field_concepts import (
    ConceptSearchEngine,
    ConfigManager,
)
from pathlib import Path


class AkshareMCPServer:
    """akshare财务数据MCP服务器"""

    def __init__(self):
        self.server = Server("akshare-value-investment")
        self.query_service = create_production_service()
        # 初始化概念搜索引擎
        self._init_concept_search()
        self._setup_handlers()

    def _init_concept_search(self):
        """初始化概念搜索引擎"""
        try:
            # 获取概念配置文件路径
            config_path = Path(__file__).parent / "field_concepts" / "financial_concepts.yaml"
            config_manager = ConfigManager(str(config_path))
            self.concept_search_engine = ConceptSearchEngine(config_manager)
        except Exception as e:
            self.concept_search_engine = None

    def _setup_handlers(self):
        """设置MCP处理器"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="query_financial_indicators",
                    description="智能查询股票财务指标数据，支持自然语言字段映射和A股、港股、美股。自动识别'ROE'、'每股收益'等自然语言查询并映射到正确字段",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                            },
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "需要返回的字段名列表，支持自然语言如：['ROE', '每股收益', '净利润']。系统会自动映射到正确的字段名。如果不指定，返回关键字段"
                            },
                            "include_metadata": {
                                "type": "boolean",
                                "description": "是否包含元数据（公司名、报告日期等），默认true",
                                "default": True
                            },
                            "prefer_annual": {
                                "type": "boolean",
                                "description": "是否优先返回年度数据（默认true），适合财务分析场景。设置为false则返回最新期数据",
                                "default": True
                            },
                            "start_date": {
                                "type": "string",
                                "description": "查询开始日期，格式：YYYY-MM-DD。如果不指定，使用默认时间范围（最近3年）",
                                "default": ""
                            },
                            "end_date": {
                                "type": "string",
                                "description": "查询结束日期，格式：YYYY-MM-DD。如果不指定，使用当前日期",
                                "default": ""
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="discover_available_fields",
                    description="查询指定股票的所有可用财务指标字段名（带缓存优化，仅返回字段名信息）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                            },
                            "keyword_filter": {
                                "type": "string",
                                "description": "可选的关键词过滤，如'收益率'、'净资产'、'扣非'等",
                                "default": ""
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "最大返回结果数，默认20个",
                                "default": 20
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="suggest_field_names",
                    description="根据描述智能推荐可能的字段名",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                            },
                            "description": {
                                "type": "string",
                                "description": "用户描述，如'扣非净资产收益率'、'每股收益'、'净利润'等"
                            }
                        },
                        "required": ["symbol", "description"]
                    }
                ),
                Tool(
                    name="map_financial_fields",
                    description="智能映射财务字段，将自然语言或可能的字段名映射到正确字段。支持批量验证和学习字段映射关系",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）。用于获取对应市场的可用字段"
                            },
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "需要映射的字段列表，支持自然语言如：['ROE', '每股收益', '净利润']"
                            }
                        },
                        "required": ["symbol", "fields"]
                    }
                ),
                Tool(
                    name="search_financial_concepts",
                    description="通过自然语言搜索财务概念，返回对应市场的字段名映射。例如：搜索'每股收益'可以找到A股的'摊薄每股收益(元)'和港股的'BASIC_EPS'",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "自然语言查询，如：'每股收益'、'ROE'、'毛利率'、'资产负债率'"
                            },
                            "market": {
                                "type": "string",
                                "description": "指定市场类型：'a_stock'（A股）、'hk_stock'（港股）、'us_stock'（美股）。如果不指定，返回所有市场",
                                "enum": ["a_stock", "hk_stock", "us_stock"]
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="reload_concepts_config",
                    description="重载概念配置文件，用于更新概念映射配置",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """处理工具调用"""
            if name == "query_financial_indicators":
                return await self._query_financial_indicators(arguments)
            elif name == "discover_available_fields":
                return await self._discover_available_fields(arguments)
            elif name == "suggest_field_names":
                return await self._suggest_field_names(arguments)
            elif name == "map_financial_fields":
                return await self._map_financial_fields(arguments)
            elif name == "search_financial_concepts":
                return await self._search_financial_concepts(arguments)
            elif name == "reload_concepts_config":
                return await self._reload_concepts_config(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"未知工具: {name}")]
                )

    def _get_default_fields(self, market_type: str) -> List[str]:
        """获取默认关键字段"""
        if market_type == "A_STOCK":
            return ["摊薄每股收益(元)", "净资产收益率(%)", "销售毛利率(%)", "资产负债率(%)", "净利润"]
        elif market_type == "HK_STOCK":
            return ["BASIC_EPS", "ROE_YEARLY", "GROSS_PROFIT_RATIO", "DEBT_ASSET_RATIO", "HOLDER_PROFIT"]
        elif market_type == "US_STOCK":
            return ["BASIC_EPS", "ROE_AVG", "GROSS_PROFIT_RATIO", "DEBT_ASSET_RATIO", "PARENT_HOLDER_NETPROFIT"]
        else:
            return []

    def _format_hk_us_value(self, value: Any, field: str, market_type: str) -> str:
        """格式化港股和美股的数值显示"""
        if value is None:
            return "数据不可用"

        try:
            # 转换为数值类型
            if isinstance(value, str):
                value = float(value) if value.replace('.', '', 1).isdigit() else value

            if isinstance(value, (int, float)):
                if field.endswith('_PROFIT') or field.endswith('_INCOME') or 'EPS' in field or 'BPS' in field:
                    # 利润类数据转换为亿单位
                    if field.endswith('_PROFIT') or field.endswith('_INCOME'):
                        return f"{value/100000000:.2f}亿{'港元' if market_type == 'hk_stock' else '美元'}"
                    else:
                        # 每股收益类数据
                        return f"{value:.2f}{'港元' if market_type == 'hk_stock' else '美元'}"
                elif field.endswith('_RATIO') or field == 'ROE_YEARLY' or field == 'ROE_AVG' or field == 'ROA':
                    # 百分比数据
                    return f"{value:.2f}%"
                else:
                    # 其他数值
                    return f"{value:.4f}"
            else:
                return str(value)
        except (ValueError, TypeError):
            return str(value)

    async def _query_financial_indicators(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询财务指标（支持智能字段映射）"""
        try:
            symbol = arguments.get("symbol", "")
            requested_fields = arguments.get("fields", [])
            include_metadata = arguments.get("include_metadata", True)
            prefer_annual = arguments.get("prefer_annual", True)
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")

            if not symbol:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="请提供股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                    )]
                )

            # 处理时间范围参数
            from datetime import datetime, timedelta

            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            if not start_date:
                # 默认查询最近5年的数据
                start_date_obj = datetime.now() - timedelta(days=5*365)
                start_date = start_date_obj.strftime('%Y-%m-%d')

            # 智能字段映射和验证
            final_fields, mapping_suggestions = await self._resolve_fields(symbol, requested_fields)

            # 调用现有的查询服务，传递时间范围参数
            result = self.query_service.query(symbol, start_date=start_date, end_date=end_date)

            if result.success and result.data:
                # 获取市场类型和第一条记录用于元数据
                if result.data:
                    company_name = result.data[0].company_name
                    market_type = result.data[0].market.value
                    currency = result.data[0].currency

                # 根据市场类型构建不同的数据结构
                indicator_map = {}

                if market_type == "a_stock":
                    # A股数据：新的结构，每个indicator代表一个报告期的所有财务数据
                    for indicator in result.data:
                        if indicator.indicators:
                            # 使用indicators字典中的所有指标
                            for field_name, field_value in indicator.indicators.items():
                                if field_name not in indicator_map:
                                    indicator_map[field_name] = {}
                                # 添加时间序列数据点
                                report_date = indicator.report_date.strftime('%Y-%m-%d')
                                indicator_map[field_name][report_date] = field_value

                elif market_type in ["hk_stock", "us_stock"]:
                    # 港股和美股数据：构建时间序列数据
                    indicator_map = {}

                    # 收集所有记录的时间序列数据
                    for indicator in result.data:
                        if indicator.raw_data:
                            report_date = indicator.report_date.strftime('%Y-%m-%d')

                            for field, value in indicator.raw_data.items():
                                if field not in ['REPORT_DATE', 'FISCAL_YEAR', 'CURRENCY', 'ORG_CODE', 'SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR']:
                                    if field not in indicator_map:
                                        indicator_map[field] = {}
                                    # 添加时间序列数据点
                                    indicator_map[field][report_date] = value

                if not indicator_map:
                    return CallToolResult(
                        content=[TextContent(type="text", text="未找到指标数据")]
                    )

                all_indicator_names = list(indicator_map.keys())

                # 确定要返回的字段
                if final_fields:
                    # 使用智能映射后的字段
                    valid_fields = [field for field in final_fields if field in all_indicator_names]
                    missing_fields = [field for field in final_fields if field not in all_indicator_names]

                    if not valid_fields:
                        return CallToolResult(
                            content=[TextContent(
                                type="text",
                                text=f"智能映射的指标都不存在。可用指标: {', '.join(all_indicator_names[:20])}..."
                            )]
                        )
                else:
                    # 使用默认关键字段
                    valid_fields = self._get_default_fields(market_type)
                    missing_fields = []

                # 构建响应
                response_parts = []

                # 添加元数据
                if include_metadata:
                    response_parts.append(f"## {company_name} ({symbol})")
                    response_parts.append("")
                    response_parts.append(f"**市场**: {market_type}")
                    response_parts.append(f"**货币**: {currency}")
                    response_parts.append(f"**可用指标数**: {len(all_indicator_names)}")
                    response_parts.append("")

                    # 显示字段映射信息（智能查询时）
                    if requested_fields and mapping_suggestions:
                        response_parts.append("### 🧠 智能字段映射")
                        response_parts.append("")
                        for suggestion in mapping_suggestions:
                            response_parts.append(f"• {suggestion}")
                        response_parts.append("")

                # 添加字段信息
                if requested_fields:
                    response_parts.append(f"### 请求指标 ({len(valid_fields)}/{len(requested_fields)})")
                else:
                    response_parts.append("### 主要财务指标")

                response_parts.append("")

                # 显示请求的指标数据
                for field in valid_fields:
                    if field in indicator_map:
                        indicator_data = indicator_map[field]

                        response_parts.append(f"**{field}**:")

                        if market_type == "a_stock":
                            # A股数据处理
                            if prefer_annual:
                                # 优先返回年度数据模式（适合财务分析）
                                annual_data = {}
                                for key, value in indicator_data.items():
                                    # 检查是否为年报日期（YYYY-MM-DD格式，MM-DD为12-31）
                                    if '-12-31' in key:  # 年报数据
                                        year = key[:4]
                                        annual_data[year] = value

                                if annual_data:
                                    # 按年份排序，显示最近几年的年报数据（默认5年）
                                    sorted_years = sorted(annual_data.keys(), reverse=True)[:5]
                                    for year in sorted_years:
                                        response_parts.append(f"  - {year}年: {annual_data[year]}")
                                else:
                                    # 如果没有年报数据，显示最新的几个数据点
                                    response_parts.append("  - 无年报数据，显示最新期数据：")
                                    data_points = [(k, v) for k, v in indicator_data.items()
                                                 if '-' in k]  # 过滤日期格式数据
                                    data_points.sort(key=lambda x: x[0], reverse=True)

                                    for key, value in data_points[:5]:
                                        if '-12-31' in key:
                                            period_name = "年报"
                                        elif '-06-30' in key:
                                            period_name = "中报"
                                        elif '-09-30' in key:
                                            period_name = "三季报"
                                        elif '-03-31' in key:
                                            period_name = "一季报"
                                        else:
                                            period_name = "其他"
                                        year = key[:4]

                                        response_parts.append(f"  - {year}年{period_name}: {value}")
                            else:
                                # 返回最新期数据模式
                                data_points = [(k, v) for k, v in indicator_data.items()
                                             if '-' in k]  # 过滤日期格式数据
                                data_points.sort(key=lambda x: x[0], reverse=True)

                                for key, value in data_points[:3]:
                                    year = key[:4]
                                    period = key[4:6]
                                    if period == '1231':
                                        period_name = "年报"
                                    elif period == '0630':
                                        period_name = "中报"
                                    elif period == '0930':
                                        period_name = "三季报"
                                    elif period == '0331':
                                        period_name = "一季报"
                                    else:
                                        period_name = f"第{period}期"

                                    response_parts.append(f"  - {year}年{period_name}: {value}")

                        elif market_type in ["hk_stock", "us_stock"]:
                            # 港股和美股数据处理：时间序列显示
                            if isinstance(indicator_data, dict):
                                # 按日期排序，显示最近的几个数据点
                                sorted_dates = sorted(indicator_data.keys(), reverse=True)

                                # 根据 prefer_annual 参数决定显示策略
                                if prefer_annual:
                                    # 优先显示年度数据（适合财务分析）
                                    annual_data = {}
                                    for date_str in sorted_dates:
                                        if date_str.endswith('-12-31'):  # 年报数据
                                            year = date_str[:4]
                                            annual_data[year] = indicator_data[date_str]

                                    if annual_data:
                                        # 按年份排序，显示最近几年的年报数据
                                        sorted_years = sorted(annual_data.keys(), reverse=True)[:3]
                                        for year in sorted_years:
                                            value = annual_data[year]
                                            formatted_value = self._format_hk_us_value(value, field, market_type)
                                            response_parts.append(f"  - {year}年: {formatted_value}")
                                    else:
                                        # 如果没有年报数据，显示最新的数据点
                                        for date_str in sorted_dates[:3]:
                                            value = indicator_data[date_str]
                                            formatted_value = self._format_hk_us_value(value, field, market_type)
                                            response_parts.append(f"  - {date_str}: {formatted_value}")
                                else:
                                    # 显示最新期数据
                                    for date_str in sorted_dates[:5]:  # 显示最新5个数据点
                                        value = indicator_data[date_str]
                                        formatted_value = self._format_hk_us_value(value, field, market_type)
                                        response_parts.append(f"  - {date_str}: {formatted_value}")
                            else:
                                # 兼容旧版本单一值显示
                                formatted_value = self._format_hk_us_value(indicator_data, field, market_type)
                                response_parts.append(f"  - {formatted_value}")

                        response_parts.append("")

                # 显示缺失的字段提醒
                if missing_fields:
                    response_parts.append("⚠️ **以下指标不存在**:")
                    for field in missing_fields:
                        response_parts.append(f"- {field}")
                    response_parts.append("")

                # 显示可用指标提示
                if not requested_fields:
                    response_parts.append(f"💡 **可用指标总数**: {len(all_indicator_names)}")
                    response_parts.append(f"💡 **示例指标**: {', '.join(all_indicator_names[:10])}...")
                    response_parts.append("")
                    response_parts.append("💡 *使用 `fields` 参数指定需要的指标，如：")
                    response_parts.append('`query_financial_indicators(symbol="600036", fields=["净资产收益率(ROE)", "基本每股收益"])`')
                    response_parts.append("")
                    response_parts.append("💡 *数据类型控制参数：")
                    response_parts.append('  - `prefer_annual=true` (默认): 优先返回年度数据，适合财务分析')
                    response_parts.append('  - `prefer_annual=false`: 返回最新期数据，包含季度报告')
                    response_parts.append("")
                    response_parts.append("💡 *时间范围控制参数：")
                    response_parts.append('  - `start_date="YYYY-MM-DD"`: 查询开始日期（可选，默认3年前）')
                    response_parts.append('  - `end_date="YYYY-MM-DD"`: 查询结束日期（可选，默认当前日期）')
                    response_parts.append("")
                    response_parts.append("💡 *示例：查询最新期数据（含季报）")
                    response_parts.append('`query_financial_indicators(symbol="600036", prefer_annual=false)`')
                    response_parts.append("")
                    response_parts.append("💡 *示例：查询最近5年数据")
                    response_parts.append('`query_financial_indicators(symbol="00700", start_date="2020-01-01")`')
                    response_parts.append("")
                    response_parts.append("💡 *使用 `discover_available_fields` 查看所有可用指标")

                response = "\n".join(response_parts)

                return CallToolResult(
                    content=[TextContent(type="text", text=response)]
                )
            else:
                error_msg = result.message if result.message else "未找到数据"
                return CallToolResult(
                    content=[TextContent(type="text", text=f"查询失败: {error_msg}")]
                )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"查询过程中发生错误: {str(e)}")]
            )

    async def _resolve_fields(self, symbol: str, requested_fields: List[str]) -> List[str]:
        """
        智能字段映射和验证

        Args:
            symbol: 股票代码
            requested_fields: 用户请求的字段列表

        Returns:
            映射后的正确字段列表
        """
        if not requested_fields:
            return []

        # 获取股票的所有可用字段和市场类型
        available_fields = self._get_all_fields_for_symbol(symbol)
        market_type = self._get_market_type(symbol)

        if not available_fields:
            return requested_fields

        # 智能字段映射
        mapped_fields = []
        mapping_suggestions = []

        for field in requested_fields:
            # 1. 直接匹配
            if field in available_fields:
                mapped_fields.append(field)
                continue

            # 2. 使用概念搜索引擎
            if self.concept_search_engine:
                mapped_field = await self._map_using_concept_search(field, available_fields, market_type)
                if mapped_field:
                    mapped_fields.append(mapped_field)
                    mapping_suggestions.append(f"'{field}' → '{mapped_field}'")
                    continue

            # 3. 模糊匹配
            fuzzy_match = await self._fuzzy_match_field(field, available_fields)
            if fuzzy_match:
                mapped_fields.append(fuzzy_match)
                mapping_suggestions.append(f"'{field}' → '{fuzzy_match}'")
                continue

            # 4. 保留原字段（可能会失败，但让用户知道尝试过）
            mapped_fields.append(field)

        return mapped_fields, mapping_suggestions

    def _get_market_type(self, symbol: str) -> str:
        """获取股票市场类型"""
        try:
            # 使用市场识别器获取市场类型
            market, _ = self.query_service.market_identifier.identify(symbol)
            return market.value.lower()  # 转换为小写，如 hk_stock
        except Exception:
            # 默认根据股票代码推断
            if symbol.isdigit() and len(symbol) == 6:
                return 'a_stock'
            elif symbol.isdigit() and len(symbol) == 5:
                return 'hk_stock'
            elif symbol.replace('.', '').isalpha():
                return 'us_stock'
            else:
                return 'hk_stock'  # 默认港股

    async def _are_fields_likely_correct(self, symbol: str, fields: List[str]) -> bool:
        """快速检查字段是否可能正确"""
        # 如果字段包含常见的关键词，可能是正确的
        common_patterns = [
            'ROE', 'EPS', 'BPS', 'ROA', 'RATIO', 'PROFIT', 'INCOME',
            '每股收益', '净资产收益率', '毛利率', '净利润', '营业收入'
        ]

        correct_looking_count = sum(1 for field in fields
                                  if any(pattern in field.upper() for pattern in common_patterns))

        return correct_looking_count / len(fields) >= 0.7  # 70%的字段看起来正确

    async def _map_using_concept_search(self, field: str, available_fields: List[str], market_type: str = None) -> str:
        """使用概念搜索引擎进行字段映射"""
        if not self.concept_search_engine:
            return None

        try:
            # 首先尝试指定市场搜索
            if market_type:
                results = self.concept_search_engine.search_concepts(field, market_type)
            else:
                results = self.concept_search_engine.search_concepts(field)

            if results:
                # 获取最佳匹配结果
                best_result = results[0]

                # 如果指定了市场，优先使用该市场的字段
                if market_type and market_type in best_result.available_fields:
                    fields_list = best_result.available_fields[market_type]
                    if fields_list:
                        # 返回优先级最高的字段
                        mapped_field = max(fields_list, key=lambda x: x.priority).name
                        # 验证该字段是否在可用字段中
                        if mapped_field in available_fields:
                            return mapped_field

                # 如果没有指定市场或指定市场没有找到，尝试所有市场
                for market_key, fields_list in best_result.available_fields.items():
                    if fields_list:
                        # 返回优先级最高的字段
                        mapped_field = max(fields_list, key=lambda x: x.priority).name
                        # 验证该字段是否在可用字段中
                        if mapped_field in available_fields:
                            return mapped_field

        except Exception as e:
            pass

        return None

    async def _fuzzy_match_field(self, field: str, available_fields: List[str]) -> str:
        """智能字段匹配"""
        field_upper = field.upper()
        field_lower = field.lower()

        # 1. 直接映射规则表
        direct_mappings = {
            # ROE相关
            'ROE': 'ROE_AVG',
            '净资产收益率': 'ROE_AVG',
            '股本回报率': 'ROE_AVG',
            '股东权益回报率': 'ROE_AVG',

            # EPS相关
            'EPS': 'BASIC_EPS',
            '每股收益': 'BASIC_EPS',
            '基本每股收益': 'BASIC_EPS',
            '摊薄每股收益': 'DILUTED_EPS',
            '每股收益TTM': 'EPS_TTM',

            # 利润相关
            '净利润': 'HOLDER_PROFIT',
            '毛利润': 'GROSS_PROFIT',
            '营业利润': 'OPERATE_INCOME',

            # 比率相关
            '毛利率': 'GROSS_PROFIT_RATIO',
            '净利率': 'NET_PROFIT_RATIO',
            '资产负债率': 'DEBT_ASSET_RATIO',
            '流动比率': 'CURRENT_RATIO',

            # ROA相关
            'ROA': 'ROA',
            '资产收益率': 'ROA',

            # BPS相关
            'BPS': 'BPS',
            '每股净资产': 'BPS',
        }

        # 2. 检查直接映射
        if field_upper in direct_mappings:
            mapped_field = direct_mappings[field_upper]
            if mapped_field in available_fields:
                return mapped_field

        if field in direct_mappings:
            mapped_field = direct_mappings[field]
            if mapped_field in available_fields:
                return mapped_field

        # 3. 模糊匹配
        for available_field in available_fields:
            available_upper = available_field.upper()
            available_lower = available_field.lower()

            # 检查是否有共同的词根
            if field_upper in available_upper or available_upper in field_upper:
                return available_field

            # 检查关键词相似性
            field_words = set(field_lower.replace('_', ' ').split())
            available_words = set(available_lower.replace('_', ' ').split())

            # 如果有共同词汇且相似度较高
            common_words = field_words & available_words
            if common_words and len(common_words) >= min(len(field_words), len(available_words)) * 0.5:
                return available_field

        # 4. 模式匹配
        for available_field in available_fields:
            # 检查缩写匹配
            if field_upper == available_field.upper():
                return available_field

            # 检查中英文对应关系
            if any(char in available_field for char in field_upper):
                similarity = self._calculate_similarity(field_lower, available_lower)
                if similarity > 0.6:  # 相似度阈值
                    return available_field

        return None

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        # 简单的相似度计算
        common_chars = set(str1) & set(str2)
        total_chars = set(str1) | set(str2)

        if not total_chars:
            return 0.0

        return len(common_chars) / len(total_chars)

    def _get_all_fields_for_symbol(self, symbol: str) -> List[str]:
        """获取股票的所有可用字段"""
        try:
            # 基础查询，获取所有记录
            result = self.query_service.query(symbol)

            if result.success and result.data:
                fields = set()

                # 收集所有原始字段
                for indicator in result.data:
                    if indicator.raw_data:
                        fields.update(indicator.raw_data.keys())

                # 过滤掉元数据字段
                exclude_fields = {
                    'REPORT_DATE', 'FISCAL_YEAR', 'CURRENCY', 'ORG_CODE',
                    'SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR',
                    '报告期', '指标', '选项'
                }

                return [field for field in fields if field not in exclude_fields]

            return []
        except Exception:
            return []

    @lru_cache(maxsize=128)
    def _get_stock_fields_minimal(self, symbol: str) -> List[str]:
        """获取股票的所有字段名（最小数据查询，带LRU缓存）"""
        try:
            # 基础查询，获取第一条记录即可
            result = self.query_service.query(symbol)

            if result.success and result.data:
                fields = set()
                # 遍历所有记录，收集所有指标名称
                for indicator in result.data:
                    if indicator.raw_data and '指标' in indicator.raw_data:
                        fields.add(indicator.raw_data['指标'])

                return sorted(list(fields))
            return []
        except Exception:
            return []

    async def _discover_available_fields(self, arguments: Dict[str, Any]) -> CallToolResult:
        """查询可用字段（使用缓存优化）"""
        try:
            symbol = arguments.get("symbol", "")
            keyword_filter = arguments.get("keyword_filter", "").lower()
            max_results = arguments.get("max_results", 20)

            if not symbol:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="请提供股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                    )]
                )

            # 使用缓存获取字段列表
            all_fields = self._get_stock_fields_minimal(symbol)

            if not all_fields:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"未找到股票 {symbol} 的字段数据")]
                )

            # 关键词过滤
            if keyword_filter:
                filtered_fields = [
                    field for field in all_fields
                    if keyword_filter in field.lower()
                ]
            else:
                filtered_fields = all_fields

            # 限制结果数量
            filtered_fields = filtered_fields[:max_results]

            # 构建响应
            response_parts = [
                f"## {symbol} 可用财务指标字段",
                "",
                f"**总字段数**: {len(all_fields)}",
                f"**筛选结果**: {len(filtered_fields)} 个字段",
                ""
            ]

            if keyword_filter:
                response_parts.append(f"**筛选关键词**: '{keyword_filter}'")
                response_parts.append("")

            response_parts.append("### 字段列表")
            response_parts.append("")

            for i, field in enumerate(filtered_fields, 1):
                response_parts.append(f"{i:2d}. **{field}**")

            if len(filtered_fields) == 0 and keyword_filter:
                response_parts.append(f"未找到包含 '{keyword_filter}' 的字段。")
                response_parts.append("")
                response_parts.append("💡 **建议**:")
                response_parts.append("- 尝试使用不同的关键词，如：'收益率'、'每股收益'、'利润'")
                response_parts.append("- 不使用关键词查看所有字段")

            return CallToolResult(
                content=[TextContent(type="text", text="\n".join(response_parts))]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"查询字段时发生错误: {str(e)}")]
            )

    async def _suggest_field_names(self, arguments: Dict[str, Any]) -> CallToolResult:
        """返回所有字段，让大语言模型自己选择合适的字段"""
        try:
            symbol = arguments.get("symbol", "")
            description = arguments.get("description", "")

            if not symbol or not description:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="请提供股票代码和字段描述"
                    )]
                )

            # 获取所有字段
            all_fields = self._get_stock_fields_minimal(symbol)

            if not all_fields:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"未找到股票 {symbol} 的字段数据")]
                )

            # 构建响应 - 简单返回所有字段，让LLM自己判断
            response_parts = [
                f"## {symbol} 所有可用字段",
                "",
                f"**用户查询**: '{description}'",
                f"**总字段数**: {len(all_fields)}",
                "",
                "### 完整字段列表",
                "",
                "请根据您的查询需求，从以下字段中选择最合适的：",
                ""
            ]

            for i, field in enumerate(all_fields, 1):
                response_parts.append(f"{i:2d}. **{field}**")

            response_parts.extend([
                "",
                "### 使用建议",
                "",
                "请选择上述列表中最符合您需求的字段名，然后使用以下格式查询：",
                f"`query_financial_indicators(symbol='{symbol}', fields=['您选择的字段名'])`",
                "",
                "💡 **提示**: 您也可以使用 `discover_available_fields` 并提供关键词来筛选相关字段"
            ])

            return CallToolResult(
                content=[TextContent(type="text", text="\n".join(response_parts))]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"获取字段时发生错误: {str(e)}")]
            )

    async def _map_financial_fields(self, arguments: Dict[str, Any]) -> CallToolResult:
        """智能映射财务字段"""
        try:
            symbol = arguments.get("symbol", "")
            requested_fields = arguments.get("fields", [])

            if not symbol:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="请提供股票代码，例如：600036（A股）、00700（港股）、AAPL（美股）"
                    )]
                )

            if not requested_fields:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="请提供需要映射的字段列表，例如：['ROE', '每股收益', '净利润']"
                    )]
                )

            # 执行智能字段映射
            mapped_fields, mapping_suggestions = await self._resolve_fields(symbol, requested_fields)

            # 获取市场信息
            market_type = self._get_market_type(symbol)
            available_fields = self._get_all_fields_for_symbol(symbol)

            # 构建响应
            response_parts = [
                f"## 字段映射结果 - {symbol}",
                "",
                f"**市场类型**: {market_type}",
                f"**可用字段总数**: {len(available_fields)}",
                ""
            ]

            # 显示映射结果
            response_parts.append("### 🎯 映射结果")
            response_parts.append("")

            for i, (original, mapped) in enumerate(zip(requested_fields, mapped_fields), 1):
                is_valid = mapped in available_fields
                status = "✅" if is_valid else "❌"

                response_parts.append(f"{i}. **{original}** → **{mapped}** {status}")

                if original != mapped:
                    response_parts.append(f"   *映射方式: 智能映射*")

                if not is_valid:
                    response_parts.append(f"   *⚠️ 字段不存在，查询时会失败*")

            response_parts.append("")

            # 显示映射统计
            valid_count = sum(1 for field in mapped_fields if field in available_fields)
            response_parts.append("### 📊 映射统计")
            response_parts.append("")
            response_parts.append(f"• 总字段数: {len(requested_fields)}")
            response_parts.append(f"• 成功映射: {valid_count}")
            response_parts.append(f"• 映射成功率: {valid_count/len(requested_fields)*100:.1f}%")
            response_parts.append("")

            # 使用建议
            if valid_count == len(requested_fields):
                response_parts.append("✅ **所有字段映射成功，可以直接查询**")
                response_parts.append("")
                response_parts.append("💡 使用示例:")
                response_parts.append(f"`query_financial_indicators(symbol='{symbol}', fields={mapped_fields})`")
            elif valid_count > 0:
                response_parts.append("⚠️ **部分字段映射成功**")
                response_parts.append("")
                response_parts.append("建议:")
                response_parts.append("• 使用成功映射的字段进行查询")
                response_parts.append("• 使用 `discover_available_fields` 查看完整字段列表")
                response_parts.append("• 使用 `search_financial_concepts` 搜索相关概念")
            else:
                response_parts.append("❌ **所有字段映射失败**")
                response_parts.append("")
                response_parts.append("建议:")
                response_parts.append("• 使用 `discover_available_fields` 查看所有可用字段")
                response_parts.append("• 使用 `search_financial_concepts` 搜索相关财务概念")

            return CallToolResult(
                content=[TextContent(type="text", text="\n".join(response_parts))]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"字段映射时发生错误: {str(e)}")]
            )

    async def _search_financial_concepts(self, arguments: Dict[str, Any]) -> CallToolResult:
        """搜索财务概念"""
        try:
            if not self.concept_search_engine:
                return CallToolResult(
                    content=[TextContent(type="text", text="概念搜索引擎未初始化")]
                )

            query = arguments.get("query", "").strip()
            market = arguments.get("market")

            if not query:
                return CallToolResult(
                    content=[TextContent(type="text", text="请提供查询关键词，如：'每股收益'、'ROE'")]
                )

            # 执行搜索
            results = self.concept_search_engine.search_concepts(query, market)

            if not results:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"没有找到与'{query}'相关的财务概念")]
                )

            # 格式化结果
            response_text = f"🔍 搜索 '{query}' 的结果：\n\n"

            for i, result in enumerate(results, 1):
                response_text += f"📊 结果 {i}: {result.concept_name} ({result.concept_id})\n"
                response_text += f"   置信度: {result.confidence:.2f}\n"
                response_text += f"   描述: {result.description}\n"

                response_text += "   可用字段:\n"
                for market_key, fields in result.available_fields.items():
                    market_name = {
                        'a_stock': 'A股',
                        'hk_stock': '港股',
                        'us_stock': '美股'
                    }.get(market_key, market_key)

                    response_text += f"     {market_name}:\n"
                    for field in fields:
                        response_text += f"       • {field.name} ({field.unit}) [优先级: {field.priority}]\n"
                response_text += "\n"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"搜索概念时发生错误: {str(e)}")]
            )

    async def _reload_concepts_config(self, arguments: Dict[str, Any]) -> CallToolResult:
        """重载概念配置"""
        try:
            if not self.concept_search_engine:
                return CallToolResult(
                    content=[TextContent(type="text", text="概念搜索引擎未初始化")]
                )

            # 重新初始化概念搜索引擎
            self._init_concept_search()

            if self.concept_search_engine:
                concept_count = self.concept_search_engine.get_concept_count()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"✅ 概念配置重载成功，当前包含 {concept_count} 个概念"
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="❌ 概念配置重载失败")]
                )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"重载配置时发生错误: {str(e)}")]
            )


async def main():
    """启动MCP服务器"""
    mcp_server = AkshareMCPServer()

    # 使用stdio传输协议
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="akshare-value-investment",
                server_version="0.1.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())