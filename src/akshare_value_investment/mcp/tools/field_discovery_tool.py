"""
MCP字段发现工具

为FieldDiscoveryService提供MCP协议工具封装，专门处理字段发现相关的功能。
与FinancialQueryTool集成，提供独立的字段发现接口。

## 🎯 核心功能

### 字段发现
- **市场字段**: 查询指定市场下所有可用字段
- **查询类型字段**: 查询特定查询类型下的字段
- **字段验证**: 验证字段是否有效
- **字段建议**: 提供字段选择建议

### MCP兼容性
- **统一接口**: 标准化的字段发现接口
- **批量查询**: 支持批量查询多个市场/查询类型的字段
- **缓存友好**: 利用业务层的缓存机制

## 🔧 使用示例

```python
tool = FieldDiscoveryTool()

# 查询A股财务指标字段
response = tool.discover_fields(
    market="a_stock",
    query_type="a_stock_indicators"
)

# 批量查询所有A股字段
response = tool.discover_all_market_fields(market="a_stock")
"""

from typing import Dict, List, Any, Optional
import logging
import httpx

from ...business.financial_types import FinancialQueryType, MCPErrorType
from ...core.models import MarketType


class FieldDiscoveryTool:
    """
    MCP字段发现工具

    专门用于字段发现功能，提供独立的字段查询接口。
    """

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        初始化MCP字段发现工具

        Args:
            api_base_url: FastAPI服务的基础URL
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.client = httpx.Client(timeout=30.0)

    def discover_fields(
        self,
        market: str,
        query_type: str
    ) -> Dict[str, Any]:
        """
        查询指定市场类型和查询类型下的所有可用字段

        Args:
            market: 市场类型字符串 ("a_stock", "hk_stock", "us_stock")
            query_type: 查询类型字符串

        Returns:
            MCP标准化的响应格式，包含可用字段列表
        """
        try:
            # 发送HTTP请求到FastAPI字段发现端点
            response = self.client.get(
                f"{self.api_base_url}/api/v1/financial/fields/{market}/{query_type}"
            )

            # 检查HTTP响应状态
            if response.status_code == 200:
                api_response = response.json()

                # 转换为MCP格式
                if api_response.get("status") == "success":
                    # 从FastAPI响应提取字段信息
                    metadata = api_response.get("metadata", {})
                    available_fields = metadata.get("available_fields", [])

                    return {
                        "success": True,
                        "available_fields": available_fields,
                        "field_count": metadata.get("field_count", len(available_fields)),
                        "market": market,
                        "query_type": query_type,
                        "metadata": {
                            "display_query_type": metadata.get("query_type", query_type),
                            "market_display_name": self._get_market_display_name(self._parse_market(market))
                        }
                    }
                else:
                    # FastAPI返回错误
                    return self._create_mcp_error(
                        error_type=MCPErrorType.INTERNAL_ERROR,
                        message=f"字段发现服务返回错误: {api_response}",
                        details={
                            "market": market,
                            "query_type": query_type,
                            "api_response": api_response
                        }
                    )
            else:
                # 处理HTTP错误
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"detail": response.text}
                return self._create_mcp_error(
                    error_type=MCPErrorType.INTERNAL_ERROR,
                    message=f"FastAPI字段发现服务错误 (HTTP {response.status_code}): {error_detail.get('detail', '未知错误')}",
                    details={
                        "http_status_code": response.status_code,
                        "api_response": error_detail,
                        "market": market,
                        "query_type": query_type
                    }
                )

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
                    "operation": "字段发现",
                    "market": market,
                    "query_type": query_type
                }
            )

    def discover_all_market_fields(self, market: str) -> Dict[str, Any]:
        """
        查询指定市场下所有查询类型的字段

        Args:
            market: 市场类型字符串 ("a_stock", "hk_stock", "us_stock")

        Returns:
            MCP标准化的响应格式，包含所有查询类型的字段
        """
        try:
            market_enum = self._parse_market(market)
            query_types = FinancialQueryType.get_query_types_by_market(market_enum)

            all_fields = {}
            total_field_count = 0

            for query_type in query_types:
                try:
                    # 查询每个查询类型的字段
                    response = self.discover_fields(market, query_type.value)
                    if response.get("success"):
                        all_fields[query_type.value] = {
                            "fields": response.get("available_fields", []),
                            "field_count": response.get("field_count", 0),
                            "display_name": query_type.get_display_name()
                        }
                        total_field_count += response.get("field_count", 0)
                except Exception as e:
                    self.logger.warning(f"查询字段失败 {query_type.value}: {e}")
                    all_fields[query_type.value] = {
                        "fields": [],
                        "field_count": 0,
                        "display_name": query_type.get_display_name(),
                        "error": str(e)
                    }

            return {
                "success": True,
                "market": market,
                "all_fields": all_fields,
                "total_field_count": total_field_count,
                "query_type_count": len(query_types),
                "metadata": {
                    "market_display_name": self._get_market_display_name(market_enum),
                    "supported_query_types": [qt.value for qt in query_types]
                }
            }

        except ValueError as e:
            return self._create_mcp_error(
                error_type=MCPErrorType.INVALID_FIELDS,
                message=f"参数验证错误: {str(e)}",
                details={"market": market}
            )
        except Exception as e:
            self.logger.error(f"MCP市场字段发现失败: {e}", exc_info=True)
            return self._create_mcp_error(
                error_type=MCPErrorType.INTERNAL_ERROR,
                message=f"市场字段发现失败: {str(e)}",
                details={"operation": "市场字段发现", "market": market}
            )

    def validate_fields(
        self,
        market: str,
        query_type: str,
        fields: List[str]
    ) -> Dict[str, Any]:
        """
        验证字段是否有效

        Args:
            market: 市场类型字符串
            query_type: 查询类型字符串
            fields: 需要验证的字段列表

        Returns:
            MCP标准化的响应格式，包含字段验证结果
        """
        try:
            # 先获取所有可用字段
            discover_response = self.discover_fields(market, query_type)

            if not discover_response.get("success"):
                return discover_response

            available_fields = set(discover_response.get("available_fields", []))

            # 验证字段
            valid_fields = []
            invalid_fields = []

            for field in fields:
                if field in available_fields:
                    valid_fields.append(field)
                else:
                    invalid_fields.append(field)

            return {
                "success": True,
                "validation_result": {
                    "valid_fields": valid_fields,
                    "invalid_fields": invalid_fields,
                    "valid_field_count": len(valid_fields),
                    "invalid_field_count": len(invalid_fields),
                    "total_requested": len(fields)
                },
                "market": market,
                "query_type": query_type,
                "metadata": {
                    "all_available_fields": list(available_fields),
                    "suggestions": self._suggest_similar_fields(invalid_fields, available_fields)
                }
            }

        except Exception as e:
            self.logger.error(f"MCP字段验证失败: {e}", exc_info=True)
            return self._create_mcp_error(
                error_type=MCPErrorType.INTERNAL_ERROR,
                message=f"字段验证失败: {str(e)}",
                details={
                    "operation": "字段验证",
                    "market": market,
                    "query_type": query_type,
                    "fields": fields
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

    def _get_market_display_name(self, market: MarketType) -> str:
        """
        获取市场类型的显示名称

        Args:
            market: 市场类型枚举

        Returns:
            显示名称
        """
        display_names = {
            MarketType.A_STOCK: "A股市场",
            MarketType.HK_STOCK: "港股市场",
            MarketType.US_STOCK: "美股市场"
        }
        return display_names.get(market, market.value)

    def _suggest_similar_fields(
        self,
        invalid_fields: List[str],
        available_fields: set
    ) -> List[Dict[str, str]]:
        """
        为无效字段建议相似的可用字段

        Args:
            invalid_fields: 无效字段列表
            available_fields: 可用字段集合

        Returns:
            字段建议列表
        """
        suggestions = []

        for invalid_field in invalid_fields:
            field_suggestions = []

            # 简单的相似性匹配
            for available_field in available_fields:
                # 包含关系
                if invalid_field.lower() in available_field.lower() or available_field.lower() in invalid_field.lower():
                    field_suggestions.append(available_field)
                # 首字母匹配
                elif (invalid_field and available_field and
                      invalid_field[0].lower() == available_field[0].lower()):
                    field_suggestions.append(available_field)

            if field_suggestions:
                suggestions.append({
                    "invalid_field": invalid_field,
                    "suggestions": field_suggestions[:3]  # 最多建议3个
                })

        return suggestions

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

    def __del__(self):
        """
        析构函数，确保HTTP客户端正确关闭
        """
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception:
            # 忽略关闭时的异常
            pass