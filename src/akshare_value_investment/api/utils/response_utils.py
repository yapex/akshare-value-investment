"""
响应格式化工具

提供API响应格式化功能，保持响应格式的一致性。
"""


def format_service_response(service_response: dict) -> dict:
    """
    格式化服务响应为API响应

    Args:
        service_response: 服务层返回的响应

    Returns:
        dict: 格式化后的API响应
    """
    # 目前直接返回服务响应，因为格式已经符合要求
    # 后续可以根据需要进行格式转换
    return service_response
