"""
MCP (Model Context Protocol) 包

基于HTTP客户端的MCP协议适配层，为akshare-value-investment项目提供MCP协议支持。
所有数据查询都通过HTTP调用FastAPI服务实现，MCP作为协议适配层存在。

## 🏗️ 架构设计

### MCP → FastAPI 调用模式
- **MCP服务器**: 协议适配层，处理MCP请求和响应格式
- **HTTP客户端**: 通过httpx调用FastAPI REST API
- **FastAPI服务**: 核心业务服务，提供财务数据查询和缓存

### 调用流程
```
MCP客户端 → MCP服务器 → HTTP客户端 → FastAPI服务 → 业务逻辑 → SQLite缓存
```

## 🎯 核心模块

### mcp.tools
- **FinancialQueryTool**: 基于HTTP客户端的财务数据查询工具
- **FieldDiscoveryTool**: 基于HTTP客户端的字段发现工具

### mcp.schemas
- **query_schemas**: MCP查询请求Schema定义
- **response_schemas**: MCP响应Schema定义

### mcp.config
- MCP服务器配置，包含FastAPI服务地址和HTTP客户端配置

## 🚀 使用示例

```python
from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool

# 创建HTTP客户端工具实例
tool = FinancialQueryTool(api_base_url="http://localhost:8000")

# 通过HTTP调用FastAPI查询财务数据
response = tool.query_financial_data(
    market="a_stock",
    query_type="a_stock_indicators",
    symbol="600519",
    fields=["报告期", "净利润"]
)
```

## 📊 支持的操作

### 财务数据查询 (HTTP → FastAPI)
- A股: 财务指标、资产负债表、利润表、现金流量表
- 港股: 财务指标、财务三表
- 美股: 财务指标、资产负债表、利润表、现金流量表

### 字段发现 (HTTP → FastAPI)
- 查询可用字段列表
- 字段验证和相似字段建议

## 🔧 配置要求

MCP服务器依赖FastAPI服务运行：
- FastAPI服务地址: `http://localhost:8000`
- 必须先启动FastAPI服务: `poe api`
- 然后启动MCP服务器: `poe mcp`

## 📋 版本信息

- **当前版本**: 3.1.0 (HTTP客户端架构)
- **架构变更**: 从直接调用业务逻辑改为HTTP调用FastAPI
- **兼容性**: 保持MCP协议接口不变，内部实现完全重构
"""

__version__ = "3.1.0"

from .tools import FinancialQueryTool, FieldDiscoveryTool

__all__ = [
    "FinancialQueryTool",
    "FieldDiscoveryTool"
]