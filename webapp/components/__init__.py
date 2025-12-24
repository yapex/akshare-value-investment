"""
Streamlit UI 组件模块

提供可复用的股票分析UI组件。
每个组件负责一个独立的分析模块，遵循统一的接口规范。
"""

from .base import AnalysisComponent

__all__ = ["AnalysisComponent"]
