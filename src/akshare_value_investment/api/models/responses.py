"""
API响应模型

定义FastAPI的响应Pydantic模型，确保返回数据的一致性。
与业务服务层的响应格式保持兼容。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataInfo(BaseModel):
    """数据信息模型"""
    records: List[Dict[str, Any]] = Field(default=[], description="数据记录列表")
    columns: List[str] = Field(default=[], description="字段列表")
    shape: tuple[int, int] = Field(default=(0, 0), description="数据形状")
    empty: bool = Field(default=True, description="是否为空")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    type: str = Field(..., description="错误类型")
    code: str = Field(..., description="错误代码")
    display_name: str = Field(..., description="错误显示名称")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


class FinancialQueryResponse(BaseModel):
    """财务查询响应模型"""
    status: str = Field(..., description="响应状态")
    timestamp: str = Field(..., description="响应时间戳")
    data: DataInfo = Field(..., description="数据信息")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    query_info: Optional[Dict[str, Any]] = Field(None, description="查询信息")
    error: Optional[ErrorResponse] = Field(None, description="错误信息")


class FieldDiscoveryResponse(BaseModel):
    """字段发现响应模型"""
    status: str = Field(..., description="响应状态")
    timestamp: str = Field(..., description="响应时间戳")
    data: DataInfo = Field(..., description="数据信息（字段列表）")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    query_info: Optional[Dict[str, Any]] = Field(None, description="查询信息")
    error: Optional[ErrorResponse] = Field(None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    container: str = Field(..., description="容器状态")
    service: str = Field(..., description="服务名称")
    timestamp: Optional[str] = Field(None, description="响应时间戳")