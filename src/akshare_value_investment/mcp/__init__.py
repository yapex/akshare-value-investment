"""
MCP (Model Context Protocol) 包

为akshare-value-investment项目提供MCP协议支持，包含财务数据查询、
字段发现等功能的MCP工具封装。

## 🎯 核心模块

### mcp.tools
- **FinancialQueryTool**: 财务数据查询工具封装
- **FieldDiscoveryTool**: 字段发现工具封装

### mcp.schemas
- **query_schemas**: 查询请求Schema定义
- **response_schemas**: 响应Schema定义

### mcp.config
- MCP服务器配置和工具注册

## 🚀 使用示例

```python
from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool

# 创建工具实例
tool = FinancialQueryTool()

# 查询财务数据
response = tool.query_financial_data(
    market="a_stock",
    query_type="a_stock_indicators",
    symbol="600519",
    fields=["报告期", "净利润"]
)
```

## 📊 支持的操作

### 财务数据查询
- A股: 财务指标、资产负债表、利润表、现金流量表
- 港股: 财务指标、财务三表
- 美股: 财务指标、资产负债表、利润表、现金流量表

### 字段发现
- 查询可用字段列表
- 字段验证和提示
"""

__version__ = "1.0.0"

from .tools import FinancialQueryTool, FieldDiscoveryTool

__all__ = [
    "FinancialQueryTool",
    "FieldDiscoveryTool"
]