"""
响应格式化工具

提供API响应格式化功能，保持响应格式的一致性。
"""

def format_mcp_response(mcp_response: dict) -> dict:
    """
    格式化MCP响应为API响应

    Args:
        mcp_response: MCP服务返回的响应

    Returns:
        dict: 格式化后的API响应
    """
    # 目前直接返回MCP响应，因为格式已经符合要求
    # 后续可以根据需要进行格式转换
    return mcp_response