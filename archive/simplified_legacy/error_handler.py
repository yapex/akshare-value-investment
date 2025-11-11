"""
统一错误处理器

提供统一的错误处理和日志记录功能。
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict, List
from functools import wraps

from .exceptions import (
    FinancialServiceException, ErrorSeverity, ErrorCategory,
    ValidationError, DataFetchError, NetworkError
)


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self, logger_name: str = "financial_service"):
        """
        初始化错误处理器

        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {}

    def register_error_callback(self, category: ErrorCategory, callback: Callable):
        """
        注册错误回调函数

        Args:
            category: 错误类别
            callback: 回调函数
        """
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)

    def handle_exception(self,
                        exception: Exception,
                        context: Optional[Dict[str, Any]] = None) -> FinancialServiceException:
        """
        统一处理异常

        Args:
            exception: 原始异常
            context: 上下文信息

        Returns:
            包装后的财务服务异常
        """
        if isinstance(exception, FinancialServiceException):
            financial_exception = exception
        else:
            # 将一般异常包装为财务服务异常
            financial_exception = FinancialServiceException(
                message=f"未预期的错误: {str(exception)}",
                cause=exception
            )

        # 添加上下文信息
        if context:
            financial_exception.details.update(context)

        # 记录日志
        self._log_exception(financial_exception)

        # 执行错误回调
        self._execute_error_callbacks(financial_exception)

        return financial_exception

    def _log_exception(self, exception: FinancialServiceException):
        """记录异常日志"""
        # 根据严重程度选择日志级别
        if exception.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(self._format_log_message(exception))
        elif exception.severity == ErrorSeverity.HIGH:
            self.logger.error(self._format_log_message(exception))
        elif exception.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(self._format_log_message(exception))
        else:
            self.logger.info(self._format_log_message(exception))

        # 如果有原始异常，记录堆栈跟踪
        if exception.cause:
            self.logger.debug("原始异常堆栈跟踪:\n%s", traceback.format_exc())

    def _execute_error_callbacks(self, exception: FinancialServiceException):
        """执行错误回调"""
        callbacks = self.error_callbacks.get(exception.category, [])
        for callback in callbacks:
            try:
                callback(exception)
            except Exception as e:
                # 回调函数执行失败不应该影响主要错误处理
                self.logger.warning(f"错误回调执行失败: {e}")

    def _format_log_message(self, exception: FinancialServiceException) -> str:
        """格式化日志消息"""
        parts = [
            f"[{exception.error_code}]",
            f"类别: {exception.category.value}",
            f"严重程度: {exception.severity.value}",
            f"消息: {exception.message}"
        ]

        if exception.details:
            parts.append(f"详情: {exception.details}")

        return " | ".join(parts)

    def safe_execute(self,
                    func: Callable,
                    *args,
                    default_value: Any = None,
                    error_category: ErrorCategory = ErrorCategory.SYSTEM,
                    **kwargs) -> Any:
        """
        安全执行函数

        Args:
            func: 要执行的函数
            *args: 函数参数
            default_value: 出错时的默认返回值
            error_category: 错误类别
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果或默认值
        """
        try:
            return func(*args, **kwargs)
        except FinancialServiceException:
            raise
        except Exception as e:
            exception = FinancialServiceException(
                message=f"函数执行失败: {func.__name__} - {str(e)}",
                category=error_category,
                cause=e
            )
            self.handle_exception(exception)

            if default_value is not None:
                return default_value
            raise exception

    def validate_params(self, params: Dict[str, Any], rules: Dict[str, Callable]) -> None:
        """
        参数验证

        Args:
            params: 参数字典
            rules: 验证规则字典 {参数名: 验证函数}

        Raises:
            ValidationError: 参数验证失败
        """
        for param_name, validation_rule in rules.items():
            param_value = params.get(param_name)

            try:
                if not validation_rule(param_value):
                    raise ValidationError(
                        f"参数验证失败: {param_name}",
                        field_name=param_name
                    )
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(
                    f"参数验证异常: {param_name} - {str(e)}",
                    field_name=param_name
                )


# 装饰器
def error_handler(error_type: type = None, category: ErrorCategory = None):
    """
    错误处理装饰器

    Args:
        error_type: 异常类型
        category: 错误类别
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FinancialServiceException:
                raise
            except Exception as e:
                # 使用全局错误处理器
                global_error_handler = ErrorHandler()

                # 创建适当类型的异常
                if error_type:
                    exception = error_type(
                        message=f"函数 {func.__name__} 执行失败: {str(e)}",
                        cause=e
                    )
                    if category:
                        exception.category = category
                else:
                    exception = FinancialServiceException(
                        message=f"函数 {func.__name__} 执行失败: {str(e)}",
                        category=category or ErrorCategory.SYSTEM,
                        cause=e
                    )

                handled_exception = global_error_handler.handle_exception(exception)
            raise handled_exception
        return wrapper
    return decorator


def safe_execute(default_value: Any = None, log_errors: bool = True):
    """
    安全执行装饰器

    Args:
        default_value: 出错时的默认返回值
        log_errors: 是否记录错误日志
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FinancialServiceException:
                if default_value is not None:
                    return default_value
                raise
            except Exception as e:
                if log_errors:
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"函数 {func.__name__} 执行失败: {e}")

                if default_value is not None:
                    return default_value

                # 转换为系统异常
                raise FinancialServiceException(
                    message=f"函数 {func.__name__} 执行失败: {str(e)}",
                    cause=e
                )
        return wrapper
    return decorator


# 常用验证函数
def validate_not_none(value: Any) -> bool:
    """验证非空"""
    return value is not None


def validate_not_empty_string(value: Any) -> bool:
    """验证非空字符串"""
    return isinstance(value, str) and len(value.strip()) > 0


def validate_positive_number(value: Any) -> bool:
    """验证正数"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_stock_symbol(value: Any) -> bool:
    """验证股票代码格式"""
    if not isinstance(value, str):
        return False

    value = value.strip()

    # A股: 6位数字
    if value.isdigit() and len(value) == 6:
        return True

    # 港股: 5位数字
    if value.isdigit() and len(value) == 5:
        return True

    # 美股: 字母
    if value.isalpha() and len(value) <= 5:
        return True

    return False


# 全局错误处理器实例
global_error_handler = ErrorHandler()