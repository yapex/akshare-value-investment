"""
MCP (Model Context Protocol) 服务器模块

提供与Claude Code集成的财务数据查询接口。
采用模块化设计，每个工具有独立的处理器，遵循SOLID原则。
"""

# 导出主要组件
from .server import AkshareMCPServer
from .formatters import ResponseFormatter

__all__ = [
    'AkshareMCPServer',
    'ResponseFormatter'
]