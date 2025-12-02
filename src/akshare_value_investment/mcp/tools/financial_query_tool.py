"""
MCP财务查询工具

为FinancialQueryService提供MCP协议工具封装，实现字符串参数到类型枚举的转换，
以及MCP标准响应格式的适配。

## 🎯 核心功能

### 工具封装
- **统一查询工具**: 封装FinancialQueryService.query()方法
- **字段发现工具**: 封装FinancialQueryService.get_available_fields()方法
- **类型转换**: 字符串参数到枚举类型的自动转换
- **错误处理**: MCP友好的错误响应格式

### MCP兼容性
- **字符串输入**: 支持字符串形式的枚举值输入
- **参数验证**: 自动验证和转换参数类型
- **响应格式**: MCP标准的JSON响应格式
- **错误映射**: 内部错误到MCP错误类型的映射

## 📊 支持的操作

### 财务数据查询
- **A股查询**: 财务指标、资产负债表、利润表、现金流量表
- **港股查询**: 财务指标、财务三表
- **美股查询**: 财务指标、资产负债表、利润表、现金流量表

## 🔧 使用示例

### 查询财务数据
```python
tool = FinancialQueryTool()

# 查询A股财务指标
response = tool.query_financial_data(
    market="a_stock",
    query_type="a_stock_indicators",
    symbol="600519",
    fields=["报告期", "净利润", "净资产收益率"],
    frequency="annual"
)

# 响应格式
{
    "success": True,
    "data": {...},
    "metadata": {...}
}
```
"""

from typing import Dict, List, Any, Optional, Union
import logging

from ...business.financial_query_service import FinancialQueryService
from ...business.financial_types import FinancialQueryType, Frequency, MCPErrorType
from ...core.models import MarketType


class FinancialQueryTool:
    """
    MCP财务查询工具

    为MCP协议提供财务数据查询的工具封装，支持字符串参数输入和
    MCP标准响应格式输出。
    """

    def __init__(self, service: Optional[FinancialQueryService] = None):
        """
        初始化MCP财务查询工具

        Args:
            service: 财务查询服务实例，如果为None则创建默认实例
        """
        self.service = service or FinancialQueryService()
        self.logger = logging.getLogger(__name__)

    def query_financial_data(
        self,
        market: str,
        query_type: str,
        symbol: str,
        fields: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = "annual"
    ) -> Dict[str, Any]:
        """
        MCP财务数据查询工具

        将MCP字符串参数转换为FinancialQueryService所需的枚举类型，
        并调用查询服务，最后转换为MCP标准响应格式。

        Args:
            market: 市场类型字符串 ("a_stock", "hk_stock", "us_stock")
            query_type: 查询类型字符串 (如 "a_stock_indicators", "hk_stock_indicators")
            symbol: 股票代码字符串
            fields: 需要返回的字段列表，None表示返回所有字段
            start_date: 开始日期字符串，YYYY-MM-DD格式
            end_date: 结束日期字符串，YYYY-MM-DD格式
            frequency: 时间频率字符串 ("annual", "quarterly")

        Returns:
            MCP标准化的响应格式

        Examples:
            >>> tool = FinancialQueryTool()
            >>>
            >>> # 查询A股财务指标
            >>> response = tool.query_financial_data(
            ...     market="a_stock",
            ...     query_type="a_stock_indicators",
            ...     symbol="600519",
            ...     fields=["报告期", "净利润"]
            ... )
            >>>
            >>> # 查询港股年度数据
            >>> response = tool.query_financial_data(
            ...     market="hk_stock",
            ...     query_type="hk_stock_indicators",
            ...     symbol="00700",
            ...     frequency="annual"
            ... )
        """
        try:
            # 参数类型转换
            market_enum = self._parse_market(market)
            query_type_enum = self._parse_query_type(query_type)
            frequency_enum = self._parse_frequency(frequency)

            # 调用财务查询服务
            response = self.service.query(
                market=market_enum,
                query_type=query_type_enum,
                symbol=symbol,
                fields=fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency_enum
            )

            # 转换为MCP标准格式
            return self._convert_to_mcp_response(response)

        except ValueError as e:
            return self._create_mcp_error(
                error_type=MCPErrorType.INVALID_FIELDS,
                message=f"参数验证错误: {str(e)}",
                details={
                    "market": market,
                    "query_type": query_type,
                    "symbol": symbol,
                    "frequency": frequency
                }
            )
        except Exception as e:
            self.logger.error(f"MCP财务查询失败: {e}", exc_info=True)
            return self._create_mcp_error(
                error_type=MCPErrorType.INTERNAL_ERROR,
                message=f"查询执行失败: {str(e)}",
                details={
                    "operation": "财务数据查询",
                    "market": market,
                    "query_type": query_type
                }
            )

    def get_available_fields(
        self,
        market: str,
        query_type: str
    ) -> Dict[str, Any]:
        """
        MCP可用字段查询工具

        查询指定市场类型和查询类型下的所有可用字段。

        Args:
            market: 市场类型字符串 ("a_stock", "hk_stock", "us_stock")
            query_type: 查询类型字符串 (如 "a_stock_indicators", "hk_stock_indicators")

        Returns:
            MCP标准化的响应格式，包含可用字段列表

        Examples:
            >>> tool = FinancialQueryTool()
            >>>
            >>> # 获取A股财务指标可用字段
            >>> response = tool.get_available_fields(
            ...     market="a_stock",
            ...     query_type="a_stock_indicators"
            ... )
            >>>
            >>> fields = response.get("available_fields", [])
            >>> print(f"可用字段: {fields}")
        """
        try:
            # 参数类型转换
            market_enum = self._parse_market(market)
            query_type_enum = self._parse_query_type(query_type)

            # 调用财务查询服务
            response = self.service.get_available_fields(
                market=market_enum,
                query_type=query_type_enum
            )

            # 转换为MCP标准格式
            mcp_response = self._convert_to_mcp_response(response)

            # 提取字段信息到顶层，方便MCP客户端访问
            if mcp_response.get("success") and "metadata" in mcp_response:
                mcp_response["available_fields"] = mcp_response["metadata"].get("available_fields", [])
                mcp_response["field_count"] = mcp_response["metadata"].get("field_count", 0)

            return mcp_response

        except ValueError as e:
            return self._create_mcp_error(
                error_type=MCPErrorType.INVALID_FIELDS,
                message=f"参数验证错误: {str(e)}",
                details={
                    "market": market,
                    "query_type": query_type
                }
            )
        except Exception as e:
            self.logger.error(f"MCP字段发现失败: {e}", exc_info=True)
            return self._create_mcp_error(
                error_type=MCPErrorType.INTERNAL_ERROR,
                message=f"字段发现失败: {str(e)}",
                details={
                    "operation": "可用字段查询",
                    "market": market,
                    "query_type": query_type
                }
            )

    def _parse_market(self, market: str) -> MarketType:
        """
        解析市场类型字符串

        Args:
            market: 市场类型字符串

        Returns:
            MarketType枚举值

        Raises:
            ValueError: 当市场类型无效时
        """
        market_mapping = {
            "a_stock": MarketType.A_STOCK,
            "hk_stock": MarketType.HK_STOCK,
            "us_stock": MarketType.US_STOCK
        }

        if market not in market_mapping:
            valid_values = list(market_mapping.keys())
            raise ValueError(f"无效的市场类型 '{market}'，支持的值为: {valid_values}")

        return market_mapping[market]

    def _parse_query_type(self, query_type: str) -> FinancialQueryType:
        """
        解析查询类型字符串

        Args:
            query_type: 查询类型字符串

        Returns:
            FinancialQueryType枚举值

        Raises:
            ValueError: 当查询类型无效时
        """
        try:
            return FinancialQueryType(query_type)
        except ValueError:
            valid_values = [qt.value for qt in FinancialQueryType]
            raise ValueError(f"无效的查询类型 '{query_type}'，支持的值为: {valid_values}")

    def _parse_frequency(self, frequency: str) -> Frequency:
        """
        解析时间频率字符串

        Args:
            frequency: 时间频率字符串

        Returns:
            Frequency枚举值

        Raises:
            ValueError: 当时间频率无效时
        """
        try:
            return Frequency(frequency)
        except ValueError:
            valid_values = [freq.value for freq in Frequency]
            raise ValueError(f"无效的时间频率 '{frequency}'，支持的值为: {valid_values}")

    def _convert_to_mcp_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        将FinancialQueryService响应转换为MCP标准格式

        Args:
            response: FinancialQueryService的响应

        Returns:
            MCP标准响应格式
        """
        # 检查是否为成功响应
        if response.get("status") == "success":
            return {
                "success": True,
                "data": response.get("data", {}),
                "metadata": response.get("metadata", {}),
                "timestamp": response.get("timestamp"),
                "query_info": response.get("query_info", {})
            }
        else:
            # 错误响应转换
            error_info = response.get("error", {})
            return {
                "success": False,
                "error": {
                    "type": error_info.get("type"),
                    "display_name": error_info.get("display_name"),
                    "message": error_info.get("message"),
                    "details": error_info.get("details", {})
                },
                "timestamp": response.get("timestamp"),
                "query_info": response.get("query_info", {})
            }

    def _create_mcp_error(
        self,
        error_type: MCPErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建MCP标准错误响应

        Args:
            error_type: 错误类型
            message: 错误消息
            details: 错误详情

        Returns:
            MCP错误响应格式
        """
        return {
            "success": False,
            "error": {
                "type": error_type.value,
                "display_name": error_type.get_display_name(),
                "message": message,
                "details": details or {}
            }
        }

    def get_supported_markets(self) -> List[str]:
        """
        获取支持的市场类型列表

        Returns:
            支持的市场类型字符串列表
        """
        return ["a_stock", "hk_stock", "us_stock"]

    def get_supported_query_types(self, market: str) -> List[str]:
        """
        获取指定市场支持的查询类型列表

        Args:
            market: 市场类型字符串

        Returns:
            支持的查询类型字符串列表
        """
        try:
            market_enum = self._parse_market(market)
            query_types = FinancialQueryType.get_query_types_by_market(market_enum)
            return [qt.value for qt in query_types]
        except ValueError:
            return []

    def get_supported_frequencies(self) -> List[str]:
        """
        获取支持的时间频率列表

        Returns:
            支持的时间频率字符串列表
        """
        return [freq.value for freq in Frequency]