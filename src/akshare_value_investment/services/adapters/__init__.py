"""
服务适配器模块

提供新旧架构之间的适配器，确保向后兼容性。
"""

from .query_service_adapter import QueryServiceAdapter

__all__ = [
    'QueryServiceAdapter'
]