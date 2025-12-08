"""
MCP配置模块

定义MCP服务器的配置、工具注册和运行参数。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging


@dataclass
class MCPServerConfig:
    """
    MCP服务器配置
    """
    server_name: str = "akshare-value-investment-mcp"
    server_version: str = "1.0.0"
    description: str = "AKShare价值投资分析系统 - MCP财务数据查询服务"

    # 服务器运行配置
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

    # 缓存配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存过期时间（秒）

      # FastAPI 集成配置
    fastapi_base_url: str = "http://localhost:8000"

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class MCPToolRegistry:
    """
    MCP工具注册表
    """

    def __init__(self):
        """初始化工具注册表"""
        self._tools: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def register_tool(
        self,
        name: str,
        description: str,
        tool_class,
        schema: Dict[str, Any],
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        注册MCP工具

        Args:
            name: 工具名称
            description: 工具描述
            tool_class: 工具类
            schema: 工具Schema定义
            examples: 使用示例列表
        """
        tool_info = {
            "name": name,
            "description": description,
            "class": tool_class,
            "schema": schema,
            "examples": examples or []
        }

        self._tools[name] = tool_info
        self.logger.info(f"注册MCP工具: {name}")

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具信息

        Args:
            name: 工具名称

        Returns:
            工具信息字典，不存在则返回None
        """
        return self._tools.get(name)

    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有已注册的工具

        Returns:
            所有工具的字典
        """
        return self._tools.copy()

    def list_tool_names(self) -> List[str]:
        """
        列出所有已注册的工具名称

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())


# 全局工具注册表实例
tool_registry = MCPToolRegistry()


def register_default_tools() -> None:
    """
    注册默认的MCP工具
    """
    from .tools.financial_query_tool import FinancialQueryTool
    from .tools.field_discovery_tool import FieldDiscoveryTool
    from .schemas.query_schemas import (
        FinancialQueryRequest,
        GetAvailableFieldsRequest,
        ValidateFieldsRequest,
        DiscoverAllMarketFieldsRequest
    )

    # 注册财务查询工具
    tool_registry.register_tool(
        name="query_financial_data",
        description="查询财务数据，支持A股、港股、美股市场的财务指标和财务三表数据",
        tool_class=FinancialQueryTool,
        schema={
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "enum": ["a_stock", "hk_stock", "us_stock"],
                    "description": "市场类型"
                },
                "query_type": {
                    "type": "string",
                    "enum": [
                        "a_stock_indicators", "a_stock_balance_sheet", "a_stock_income_statement", "a_stock_cash_flow",
                        "hk_stock_indicators", "hk_stock_statements",
                        "us_stock_indicators", "us_stock_balance_sheet", "us_stock_income_statement", "us_stock_cash_flow"
                    ],
                    "description": "查询类型"
                },
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "需要返回的字段列表，为空则返回所有字段"
                },
                "start_date": {
                    "type": "string",
                    "format": "date",
                    "description": "开始日期，YYYY-MM-DD格式"
                },
                "end_date": {
                    "type": "string",
                    "format": "date",
                    "description": "结束日期，YYYY-MM-DD格式"
                },
                "frequency": {
                    "type": "string",
                    "enum": ["annual", "quarterly"],
                    "default": "annual",
                    "description": "时间频率，annual为年度数据，quarterly为报告期数据"
                }
            },
            "required": ["market", "query_type", "symbol"]
        },
        examples=[
            {
                "name": "查询A股财务指标",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators",
                    "symbol": "600519",
                    "fields": ["报告期", "净利润", "净资产收益率"],
                    "frequency": "annual"
                }
            },
            {
                "name": "查询港股财务指标",
                "parameters": {
                    "market": "hk_stock",
                    "query_type": "hk_stock_indicators",
                    "symbol": "00700",
                    "frequency": "quarterly"
                }
            }
        ]
    )

    # 注册获取可用字段工具
    tool_registry.register_tool(
        name="get_available_fields",
        description="获取指定查询类型下的所有可用字段",
        tool_class=FinancialQueryTool,
        schema={
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "enum": ["a_stock", "hk_stock", "us_stock"],
                    "description": "市场类型"
                },
                "query_type": {
                    "type": "string",
                    "enum": [
                        "a_stock_indicators", "a_stock_balance_sheet", "a_stock_income_statement", "a_stock_cash_flow",
                        "hk_stock_indicators", "hk_stock_statements",
                        "us_stock_indicators", "us_stock_balance_sheet", "us_stock_income_statement", "us_stock_cash_flow"
                    ],
                    "description": "查询类型"
                }
            },
            "required": ["market", "query_type"]
        },
        examples=[
            {
                "name": "获取A股财务指标可用字段",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators"
                }
            }
        ]
    )

    # 注册字段发现工具
    tool_registry.register_tool(
        name="discover_fields",
        description="专门的字段发现工具，支持字段验证和建议",
        tool_class=FieldDiscoveryTool,
        schema={
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "enum": ["a_stock", "hk_stock", "us_stock"],
                    "description": "市场类型"
                },
                "query_type": {
                    "type": "string",
                    "enum": [
                        "a_stock_indicators", "a_stock_balance_sheet", "a_stock_income_statement", "a_stock_cash_flow",
                        "hk_stock_indicators", "hk_stock_statements",
                        "us_stock_indicators", "us_stock_balance_sheet", "us_stock_income_statement", "us_stock_cash_flow"
                    ],
                    "description": "查询类型"
                }
            },
            "required": ["market", "query_type"]
        },
        examples=[
            {
                "name": "发现A股财务指标字段",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators"
                }
            }
        ]
    )

    # 注册验证字段工具
    tool_registry.register_tool(
        name="validate_fields",
        description="验证字段是否有效，并提供相似字段建议",
        tool_class=FieldDiscoveryTool,
        schema={
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "enum": ["a_stock", "hk_stock", "us_stock"],
                    "description": "市场类型"
                },
                "query_type": {
                    "type": "string",
                    "enum": [
                        "a_stock_indicators", "a_stock_balance_sheet", "a_stock_income_statement", "a_stock_cash_flow",
                        "hk_stock_indicators", "hk_stock_statements",
                        "us_stock_indicators", "us_stock_balance_sheet", "us_stock_income_statement", "us_stock_cash_flow"
                    ],
                    "description": "查询类型"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "需要验证的字段列表"
                }
            },
            "required": ["market", "query_type", "fields"]
        },
        examples=[
            {
                "name": "验证A股财务指标字段",
                "parameters": {
                    "market": "a_stock",
                    "query_type": "a_stock_indicators",
                    "fields": ["报告期", "净利润", "不存在的字段"]
                }
            }
        ]
    )

    # 注册发现市场所有字段工具
    tool_registry.register_tool(
        name="discover_all_market_fields",
        description="发现指定市场下所有查询类型的字段",
        tool_class=FieldDiscoveryTool,
        schema={
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "enum": ["a_stock", "hk_stock", "us_stock"],
                    "description": "市场类型"
                }
            },
            "required": ["market"]
        },
        examples=[
            {
                "name": "发现A股所有字段",
                "parameters": {
                    "market": "a_stock"
                }
            }
        ]
    )


def get_server_config() -> MCPServerConfig:
    """
    获取服务器配置

    Returns:
        服务器配置对象
    """
    return MCPServerConfig()


def setup_logging(config: MCPServerConfig) -> None:
    """
    设置日志配置

    Args:
        config: 服务器配置
    """
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format
    )


# 初始化时注册默认工具
try:
    register_default_tools()
except ImportError:
    # 在某些导入环境中可能无法注册工具，这是正常的
    pass