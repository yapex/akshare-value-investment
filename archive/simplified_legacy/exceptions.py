"""
统一异常体系

定义财务服务系统的统一异常类型，支持一致的错误处理。
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"              # 低级别：不影响核心功能
    MEDIUM = "medium"        # 中等级别：影响部分功能
    HIGH = "high"            # 高级别：影响核心功能
    CRITICAL = "critical"    # 严重级别：系统无法正常工作


class ErrorCategory(Enum):
    """错误类别枚举"""
    VALIDATION = "validation"        # 验证错误
    DATA_FETCH = "data_fetch"        # 数据获取错误
    DATA_PROCESSING = "data_processing"  # 数据处理错误
    CONFIGURATION = "configuration"  # 配置错误
    NETWORK = "network"            # 网络错误
    BUSINESS_LOGIC = "business_logic"  # 业务逻辑错误
    SYSTEM = "system"              # 系统错误


class FinancialServiceException(Exception):
    """财务服务统一异常基类"""

    def __init__(self,
                 message: str,
                 error_code: Optional[str] = None,
                 category: Optional[ErrorCategory] = None,
                 severity: Optional[ErrorSeverity] = None,
                 details: Optional[Dict[str, Any]] = None,
                 cause: Optional[Exception] = None):
        """
        初始化财务服务异常

        Args:
            message: 错误消息
            error_code: 错误代码
            category: 错误类别
            severity: 错误严重程度
            details: 错误详细信息
            cause: 原始异常
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.category = category or ErrorCategory.SYSTEM
        self.severity = severity or ErrorSeverity.MEDIUM
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details
        }

    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.error_code}] {self.message}"


class ValidationError(FinancialServiceException):
    """数据验证错误"""

    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details={'field_name': field_name} if field_name else {},
            **kwargs
        )
        self.field_name = field_name


class DataFetchError(FinancialServiceException):
    """数据获取错误"""

    def __init__(self,
                 message: str,
                 symbol: Optional[str] = None,
                 source: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATA_FETCH,
            severity=ErrorSeverity.HIGH,
            details={'symbol': symbol, 'source': source} if symbol or source else {},
            **kwargs
        )
        self.symbol = symbol
        self.source = source


class DataProcessingError(FinancialServiceException):
    """数据处理错误"""

    def __init__(self,
                 message: str,
                 processing_step: Optional[str] = None,
                 data_type: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATA_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            details={'processing_step': processing_step, 'data_type': data_type},
            **kwargs
        )
        self.processing_step = processing_step
        self.data_type = data_type


class ConfigurationError(FinancialServiceException):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            details={'config_key': config_key} if config_key else {},
            **kwargs
        )
        self.config_key = config_key


class NetworkError(FinancialServiceException):
    """网络错误"""

    def __init__(self,
                 message: str,
                 url: Optional[str] = None,
                 status_code: Optional[int] = None,
                 **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            details={'url': url, 'status_code': status_code} if url or status_code else {},
            **kwargs
        )
        self.url = url
        self.status_code = status_code


class BusinessLogicError(FinancialServiceException):
    """业务逻辑错误"""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            details={'operation': operation} if operation else {},
            **kwargs
        )
        self.operation = operation


class MappingError(FinancialServiceException):
    """字段映射错误"""

    def __init__(self,
                 message: str,
                 field_name: Optional[str] = None,
                 mapping_suggestions: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATA_PROCESSING,
            severity=ErrorSeverity.LOW,
            details={
                'field_name': field_name,
                'mapping_suggestions': mapping_suggestions or []
            },
            **kwargs
        )
        self.field_name = field_name
        self.mapping_suggestions = mapping_suggestions or []


class SystemError(FinancialServiceException):
    """系统错误"""

    def __init__(self, message: str, component: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            details={'component': component} if component else {},
            **kwargs
        )
        self.component = component


# 异常工厂函数
def create_validation_error(message: str, field_name: str = None) -> ValidationError:
    """创建验证错误"""
    return ValidationError(message=message, field_name=field_name)


def create_data_fetch_error(message: str, symbol: str = None, source: str = None) -> DataFetchError:
    """创建数据获取错误"""
    return DataFetchError(message=message, symbol=symbol, source=source)


def create_network_error(message: str, url: str = None, status_code: int = None) -> NetworkError:
    """创建网络错误"""
    return NetworkError(message=message, url=url, status_code=status_code)


def create_mapping_error(message: str,
                       field_name: str = None,
                       mapping_suggestions: List[str] = None) -> MappingError:
    """创建映射错误"""
    return MappingError(
        message=message,
        field_name=field_name,
        mapping_suggestions=mapping_suggestions
    )


# 异常处理装饰器
def handle_exceptions(default_error_type=FinancialServiceException):
    """异常处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FinancialServiceException:
                # 重新抛出财务服务异常
                raise
            except Exception as e:
                # 将其他异常包装为财务服务异常
                raise default_error_type(
                    message=f"操作失败: {str(e)}",
                    cause=e
                )
        return wrapper
    return decorator


def safe_execute(func, default_value=None, error_type=FinancialServiceException):
    """安全执行函数"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if default_value is not None:
                return default_value
            raise error_type(
                message=f"安全执行失败: {str(e)}",
                cause=e
            )
    return wrapper


# 错误收集器
class ErrorCollector:
    """错误收集器，用于收集和报告错误"""

    def __init__(self):
        self.errors: List[FinancialServiceException] = []

    def add_error(self, error: FinancialServiceException):
        """添加错误"""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0

    def get_errors_by_category(self, category: ErrorCategory) -> List[FinancialServiceException]:
        """按类别获取错误"""
        return [error for error in self.errors if error.category == category]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[FinancialServiceException]:
        """按严重程度获取错误"""
        return [error for error in self.errors if error.severity == severity]

    def clear(self):
        """清空错误"""
        self.errors.clear()

    def get_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        summary = {
            'total_errors': len(self.errors),
            'by_category': {},
            'by_severity': {}
        }

        for error in self.errors:
            # 按类别统计
            category = error.category.value
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1

            # 按严重程度统计
            severity = error.severity.value
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

        return summary