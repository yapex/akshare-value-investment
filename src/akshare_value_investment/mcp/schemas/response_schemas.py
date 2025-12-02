"""
MCP响应Schema定义

定义各种MCP工具的响应数据结构和格式。
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"


class ErrorTypeSchema(str, Enum):
    """错误类型Schema"""
    INVALID_SYMBOL = "invalid_symbol"
    INVALID_MARKET = "invalid_market"
    INVALID_QUERY_TYPE = "invalid_query_type"
    INVALID_FIELDS = "invalid_fields"
    INVALID_DATE_RANGE = "invalid_date_range"
    INVALID_FREQUENCY = "invalid_frequency"
    DATA_NOT_FOUND = "data_not_found"
    FIELD_NOT_FOUND = "field_not_found"
    INSUFFICIENT_DATA = "insufficient_data"
    CACHE_ERROR = "cache_error"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    INTERNAL_ERROR = "internal_error"


@dataclass
class ErrorInfo:
    """错误信息结构"""
    type: ErrorTypeSchema
    display_name: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class DataInfo:
    """数据信息结构"""
    records: List[Dict[str, Any]]
    columns: List[str]
    shape: tuple
    empty: bool


@dataclass
class FinancialQueryResponse:
    """
    财务数据查询响应Schema
    """
    success: bool
    data: Optional[DataInfo] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    timestamp: Optional[str] = None
    query_info: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(
        cls,
        data_info: DataInfo,
        metadata: Dict[str, Any],
        query_info: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> "FinancialQueryResponse":
        """
        创建成功响应

        Args:
            data_info: 数据信息
            metadata: 元数据信息
            query_info: 查询信息
            timestamp: 时间戳

        Returns:
            成功响应对象
        """
        return cls(
            success=True,
            data=data_info,
            metadata=metadata,
            query_info=query_info,
            timestamp=timestamp
        )

    @classmethod
    def error_response(
        cls,
        error_info: ErrorInfo,
        query_info: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> "FinancialQueryResponse":
        """
        创建错误响应

        Args:
            error_info: 错误信息
            query_info: 查询信息
            timestamp: 时间戳

        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            error=error_info,
            query_info=query_info,
            timestamp=timestamp
        )


@dataclass
class GetAvailableFieldsResponse:
    """
    获取可用字段响应Schema
    """
    success: bool
    available_fields: List[str]
    field_count: int
    market: str
    query_type: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    timestamp: Optional[str] = None

    @classmethod
    def success_response(
        cls,
        available_fields: List[str],
        market: str,
        query_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> "GetAvailableFieldsResponse":
        """
        创建成功响应

        Args:
            available_fields: 可用字段列表
            market: 市场类型
            query_type: 查询类型
            metadata: 元数据信息
            timestamp: 时间戳

        Returns:
            成功响应对象
        """
        return cls(
            success=True,
            available_fields=available_fields,
            field_count=len(available_fields),
            market=market,
            query_type=query_type,
            metadata=metadata,
            timestamp=timestamp
        )

    @classmethod
    def error_response(
        cls,
        error_info: ErrorInfo,
        market: str,
        query_type: str,
        timestamp: Optional[str] = None
    ) -> "GetAvailableFieldsResponse":
        """
        创建错误响应

        Args:
            error_info: 错误信息
            market: 市场类型
            query_type: 查询类型
            timestamp: 时间戳

        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            available_fields=[],
            field_count=0,
            market=market,
            query_type=query_type,
            error=error_info,
            timestamp=timestamp
        )


@dataclass
class FieldValidationResult:
    """字段验证结果结构"""
    valid_fields: List[str]
    invalid_fields: List[str]
    valid_field_count: int
    invalid_field_count: int
    total_requested: int


@dataclass
class ValidateFieldsResponse:
    """
    字段验证响应Schema
    """
    success: bool
    market: str
    query_type: str
    validation_result: Optional[FieldValidationResult] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    timestamp: Optional[str] = None

    @classmethod
    def success_response(
        cls,
        validation_result: FieldValidationResult,
        market: str,
        query_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> "ValidateFieldsResponse":
        """
        创建成功响应

        Args:
            validation_result: 验证结果
            market: 市场类型
            query_type: 查询类型
            metadata: 元数据信息
            timestamp: 时间戳

        Returns:
            成功响应对象
        """
        return cls(
            success=True,
            validation_result=validation_result,
            market=market,
            query_type=query_type,
            metadata=metadata,
            timestamp=timestamp
        )

    @classmethod
    def error_response(
        cls,
        error_info: ErrorInfo,
        market: str,
        query_type: str,
        timestamp: Optional[str] = None
    ) -> "ValidateFieldsResponse":
        """
        创建错误响应

        Args:
            error_info: 错误信息
            market: 市场类型
            query_type: 查询类型
            timestamp: 时间戳

        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            market=market,
            query_type=query_type,
            error=error_info,
            timestamp=timestamp
        )


@dataclass
class DiscoverAllMarketFieldsResponse:
    """
    发现市场所有字段响应Schema
    """
    success: bool
    market: str
    all_fields: Dict[str, Dict[str, Any]]
    total_field_count: int
    query_type_count: int
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    timestamp: Optional[str] = None

    @classmethod
    def success_response(
        cls,
        market: str,
        all_fields: Dict[str, Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> "DiscoverAllMarketFieldsResponse":
        """
        创建成功响应

        Args:
            market: 市场类型
            all_fields: 所有字段信息
            metadata: 元数据信息
            timestamp: 时间戳

        Returns:
            成功响应对象
        """
        total_field_count = sum(
            fields.get("field_count", 0) for fields in all_fields.values()
        )
        query_type_count = len(all_fields)

        return cls(
            success=True,
            market=market,
            all_fields=all_fields,
            total_field_count=total_field_count,
            query_type_count=query_type_count,
            metadata=metadata,
            timestamp=timestamp
        )

    @classmethod
    def error_response(
        cls,
        error_info: ErrorInfo,
        market: str,
        timestamp: Optional[str] = None
    ) -> "DiscoverAllMarketFieldsResponse":
        """
        创建错误响应

        Args:
            error_info: 错误信息
            market: 市场类型
            timestamp: 时间戳

        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            market=market,
            all_fields={},
            total_field_count=0,
            query_type_count=0,
            error=error_info,
            timestamp=timestamp
        )


# 工具函数：转换为字典格式
def financial_query_response_to_dict(response: FinancialQueryResponse) -> Dict[str, Any]:
    """
    将财务查询响应转换为字典格式

    Args:
        response: 响应对象

    Returns:
        字典格式的响应
    """
    result = {
        "success": response.success,
        "timestamp": response.timestamp
    }

    if response.success:
        if response.data:
            result["data"] = {
                "records": response.data.records,
                "columns": response.data.columns,
                "shape": response.data.shape,
                "empty": response.data.empty
            }
        if response.metadata:
            result["metadata"] = response.metadata
        if response.query_info:
            result["query_info"] = response.query_info
    else:
        if response.error:
            result["error"] = {
                "type": response.error.type.value,
                "display_name": response.error.display_name,
                "message": response.error.message,
                "details": response.error.details or {}
            }
        if response.query_info:
            result["query_info"] = response.query_info

    return result


def get_available_fields_response_to_dict(response: GetAvailableFieldsResponse) -> Dict[str, Any]:
    """
    将获取可用字段响应转换为字典格式

    Args:
        response: 响应对象

    Returns:
        字典格式的响应
    """
    result = {
        "success": response.success,
        "available_fields": response.available_fields,
        "field_count": response.field_count,
        "market": response.market,
        "query_type": response.query_type,
        "timestamp": response.timestamp
    }

    if response.metadata:
        result["metadata"] = response.metadata
    if not response.success and response.error:
        result["error"] = {
            "type": response.error.type.value,
            "display_name": response.error.display_name,
            "message": response.error.message,
            "details": response.error.details or {}
        }

    return result


def validate_fields_response_to_dict(response: ValidateFieldsResponse) -> Dict[str, Any]:
    """
    将字段验证响应转换为字典格式

    Args:
        response: 响应对象

    Returns:
        字典格式的响应
    """
    result = {
        "success": response.success,
        "market": response.market,
        "query_type": response.query_type,
        "timestamp": response.timestamp
    }

    if response.success and response.validation_result:
        result["validation_result"] = {
            "valid_fields": response.validation_result.valid_fields,
            "invalid_fields": response.validation_result.invalid_fields,
            "valid_field_count": response.validation_result.valid_field_count,
            "invalid_field_count": response.validation_result.invalid_field_count,
            "total_requested": response.validation_result.total_requested
        }

    if response.metadata:
        result["metadata"] = response.metadata
    if not response.success and response.error:
        result["error"] = {
            "type": response.error.type.value,
            "display_name": response.error.display_name,
            "message": response.error.message,
            "details": response.error.details or {}
        }

    return result


def discover_all_market_fields_response_to_dict(response: DiscoverAllMarketFieldsResponse) -> Dict[str, Any]:
    """
    将发现市场所有字段响应转换为字典格式

    Args:
        response: 响应对象

    Returns:
        字典格式的响应
    """
    result = {
        "success": response.success,
        "market": response.market,
        "all_fields": response.all_fields,
        "total_field_count": response.total_field_count,
        "query_type_count": response.query_type_count,
        "timestamp": response.timestamp
    }

    if response.metadata:
        result["metadata"] = response.metadata
    if not response.success and response.error:
        result["error"] = {
            "type": response.error.type.value,
            "display_name": response.error.display_name,
            "message": response.error.message,
            "details": response.error.details or {}
        }

    return result