"""
API路由模块

定义FastAPI路由端点，将HTTP请求转换为business服务调用。
"""

# from .financial import router as financial_router  # 后续实现
from .field_discovery import router as field_discovery_router

__all__ = ["field_discovery_router"]  # 暂时只导出字段发现路由
