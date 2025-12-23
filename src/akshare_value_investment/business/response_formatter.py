"""
FastAPI标准化响应格式

为FastAPI Web服务提供标准化的响应格式，确保错误处理
和数据返回的一致性，便于客户端解析和使用。
"""

import pandas as pd
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .financial_types import MCPErrorType


class ResponseFormatter:
    """
    FastAPI标准化响应格式

    提供统一的成功和错误响应格式，为FastAPI客户端提供一致的接口。
    """

    @staticmethod
    def success(
        data: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建成功响应

        Args:
            data: 查询结果数据
            metadata: 数据元信息
            query_info: 查询参数信息

        Returns:
            标准化的成功响应
        """
        # 构建基础响应
        import json

        # 使用pandas的to_json方法处理DataFrame，确保日期等对象正确序列化
        if not data.empty:
            # 使用orient='records'将DataFrame转换为记录列表
            # date_format='iso'确保日期以ISO格式输出
            records_json = data.to_json(orient='records', date_format='iso', force_ascii=False)
            records = json.loads(records_json)
        else:
            records = []

        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "records": records,
                "columns": list(data.columns),
                "shape": data.shape,
                "empty": data.empty
            }
        }

        # 添加数据元信息
        if metadata is None:
            metadata = {}

        # 自动添加基本元信息
        auto_metadata = {
            "record_count": len(data),
            "field_count": len(data.columns),
            "has_date_fields": any(
                col.lower().find('date') >= 0 or col.lower().find('报告期') >= 0 or col.lower().find('时间') >= 0
                for col in data.columns
            )
        }
        metadata.update(auto_metadata)

        response["metadata"] = metadata

        # 添加查询信息
        if query_info:
            response["query_info"] = query_info

        return response

    @staticmethod
    def error(
        error_type: MCPErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            error_type: 错误类型
            message: 错误信息
            details: 错误详情
            query_info: 查询参数信息

        Returns:
            标准化的错误响应
        """
        response = {
            "status": "error",
            "error": {
                "type": error_type.value,
                "code": error_type.name,
                "display_name": error_type.get_display_name(),
                "message": message
            },
            "timestamp": datetime.now().isoformat()
        }

        if details:
            response["error"]["details"] = details

        if query_info:
            response["query_info"] = query_info

        return response

    @staticmethod
    def validation_error(
        field: str,
        value: Any,
        allowed_values: Optional[List[Any]] = None,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建验证错误响应

        Args:
            field: 验证失败的字段名
            value: 无效的值
            allowed_values: 允许的值列表
            query_info: 查询参数信息

        Returns:
            验证错误响应
        """
        details = {
            "field": field,
            "invalid_value": str(value)
        }

        if allowed_values:
            details["allowed_values"] = [str(v) for v in allowed_values]
            message = f"字段 '{field}' 的值 '{value}' 无效，允许的值为: {allowed_values}"
        else:
            message = f"字段 '{field}' 的值 '{value}' 无效"

        return ResponseFormatter.error(
            error_type=MCPErrorType.INVALID_FIELDS,
            message=message,
            details=details,
            query_info=query_info
        )

    @staticmethod
    def field_not_found_error(
        missing_fields: List[str],
        available_fields: List[str],
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建字段未找到错误响应

        Args:
            missing_fields: 未找到的字段列表
            available_fields: 可用字段列表
            query_info: 查询参数信息

        Returns:
            字段未找到错误响应
        """
        details = {
            "missing_fields": missing_fields,
            "available_fields": available_fields,
            "suggestion": "可以使用 get_available_fields() 方法获取所有可用字段"
        }

        message = f"以下字段不存在: {', '.join(missing_fields)}"

        return ResponseFormatter.error(
            error_type=MCPErrorType.FIELD_NOT_FOUND,
            message=message,
            details=details,
            query_info=query_info
        )

    @staticmethod
    def data_not_found_error(
        symbol: str,
        market: str,
        query_type: str,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建数据未找到错误响应

        Args:
            symbol: 股票代码
            market: 市场类型
            query_type: 查询类型
            query_info: 查询参数信息

        Returns:
            数据未找到错误响应
        """
        details = {
            "symbol": symbol,
            "market": market,
            "query_type": query_type
        }

        message = f"未找到股票 {symbol} 在 {market} 市场的 {query_type} 数据"

        return ResponseFormatter.error(
            error_type=MCPErrorType.DATA_NOT_FOUND,
            message=message,
            details=details,
            query_info=query_info
        )

    @staticmethod
    def api_error(
        original_error: Exception,
        api_name: str,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建API调用错误响应

        Args:
            original_error: 原始异常
            api_name: API名称
            query_info: 查询参数信息

        Returns:
            API调用错误响应
        """
        details = {
            "api_name": api_name,
            "original_error_type": type(original_error).__name__,
            "original_error_message": str(original_error)
        }

        message = f"API调用失败: {api_name}"

        return ResponseFormatter.error(
            error_type=MCPErrorType.API_ERROR,
            message=message,
            details=details,
            query_info=query_info
        )

    @staticmethod
    def internal_error(
        original_error: Exception,
        operation: str,
        query_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建内部错误响应

        Args:
            original_error: 原始异常
            operation: 操作描述
            query_info: 查询参数信息

        Returns:
            内部错误响应
        """
        details = {
            "operation": operation,
            "original_error_type": type(original_error).__name__,
            "original_error_message": str(original_error)
        }

        message = f"内部错误: {operation}"

        return ResponseFormatter.error(
            error_type=MCPErrorType.INTERNAL_ERROR,
            message=message,
            details=details,
            query_info=query_info
        )

    @staticmethod
    def is_success_response(response: Dict[str, Any]) -> bool:
        """
        检查响应是否为成功响应

        Args:
            response: 响应对象

        Returns:
            是否为成功响应
        """
        return response.get("status") == "success"

    @staticmethod
    def is_error_response(response: Dict[str, Any]) -> bool:
        """
        检查响应是否为错误响应

        Args:
            response: 响应对象

        Returns:
            是否为错误响应
        """
        return response.get("status") == "error"

    @staticmethod
    def get_error_info(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从错误响应中提取错误信息

        Args:
            response: 响应对象

        Returns:
            错误信息字典，如果不是错误响应则返回None
        """
        if ResponseFormatter.is_error_response(response):
            return response.get("error", {})
        return None

    @staticmethod
    def get_data_info(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从成功响应中提取数据信息

        Args:
            response: 响应对象

        Returns:
            数据信息字典，如果不是成功响应则返回None
        """
        if ResponseFormatter.is_success_response(response):
            return response.get("data", {})
        return None