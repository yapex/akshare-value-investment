# AKShare价值投资分析系统 - MCP服务器

基于Model Context Protocol (MCP) 的财务数据查询服务器，为AI助手提供标准化的财务数据访问接口。

## 🎯 功能特性

### 支持的市场和查询类型

**A股市场 (4个查询类型)**
- 财务指标 (`a_stock_indicators`)
- 资产负债表 (`a_stock_balance_sheet`)
- 利润表 (`a_stock_income_statement`)
- 现金流量表 (`a_stock_cash_flow`)

**港股市场 (2个查询类型)**
- 财务指标 (`hk_stock_indicators`)
- 财务三表 (`hk_stock_statements`)

**美股市场 (4个查询类型)**
- 财务指标 (`us_stock_indicators`)
- 资产负债表 (`us_stock_balance_sheet`)
- 利润表 (`us_stock_income_statement`)
- 现金流量表 (`us_stock_cash_flow`)

### 核心功能

- **严格字段过滤**: 按需返回指定字段，减少数据传输
- **时间频率处理**: 支持年度数据和报告期数据
- **智能股票代码格式化**: 自动适配AKShare API格式要求
- **字段发现**: 提供可用字段查询和字段验证功能
- **MCP标准化响应**: 统一的错误处理和响应格式

## 🚀 快速开始

### 1. 启动MCP服务器

```bash
# 使用uv启动
uv run python -m src.akshare_value_investment.mcp.server

# 或者启动交互模式
uv run python -m src.akshare_value_investment.mcp.server --info
```

### 2. 配置MCP客户端

在 `.mcp.json` 中已配置好：

```json
{
  "mcpServers": {
    "akshare-value-investment": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "src.akshare_value_investment.mcp.server"
      ],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### 3. 使用MCP工具

#### 查询财务数据

```json
{
  "tool": "query_financial_data",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators",
    "symbol": "600519",
    "fields": ["报告期", "净利润", "净资产收益率"],
    "frequency": "annual"
  }
}
```

#### 获取可用字段

```json
{
  "tool": "get_available_fields",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators"
  }
}
```

#### 验证字段

```json
{
  "tool": "validate_fields",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators",
    "fields": ["报告期", "净利润", "不存在的字段"]
  }
}
```

## 📊 可用工具

### 1. query_financial_data
查询财务数据，支持严格字段过滤和时间频率处理。

**参数:**
- `market` (required): 市场类型 - "a_stock", "hk_stock", "us_stock"
- `query_type` (required): 查询类型
- `symbol` (required): 股票代码
- `fields` (optional): 字段列表
- `start_date` (optional): 开始日期 (YYYY-MM-DD)
- `end_date` (optional): 结束日期 (YYYY-MM-DD)
- `frequency` (optional): 时间频率 - "annual", "quarterly"

### 2. get_available_fields
获取指定查询类型下的所有可用字段。

**参数:**
- `market` (required): 市场类型
- `query_type` (required): 查询类型

### 3. discover_fields
专门的字段发现工具，支持字段验证和建议。

**参数:**
- `market` (required): 市场类型
- `query_type` (required): 查询类型

### 4. validate_fields
验证字段是否有效，并提供相似字段建议。

**参数:**
- `market` (required): 市场类型
- `query_type` (required): 查询类型
- `fields` (required): 需要验证的字段列表

### 5. discover_all_market_fields
发现指定市场下所有查询类型的字段。

**参数:**
- `market` (required): 市场类型

## 🔧 开发和测试

### 启动交互模式

```bash
uv run python -m src.akshare_value_investment.mcp.server --info
```

### 运行测试

```bash
uv run python -m src.akshare_value_investment.mcp.server --test
```

### 调试模式

```bash
uv run python -m src.akshare_value_investment.mcp.server --debug
```

## 📖 响应格式

### 成功响应
```json
{
  "success": true,
  "result": {
    "success": true,
    "data": {
      "records": [...],
      "columns": [...],
      "shape": [n, m],
      "empty": false
    },
    "metadata": {
      "record_count": n,
      "field_count": m,
      "market": "a_stock",
      "query_type": "A股财务指标"
    }
  },
  "timestamp": "2024-01-01T00:00:00",
  "server_info": {
    "name": "akshare-value-investment-mcp",
    "version": "1.0.0"
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "field_not_found",
    "message": "字段不存在: [不存在的字段]",
    "type": "field_not_found",
    "display_name": "字段未找到"
  },
  "timestamp": "2024-01-01T00:00:00",
  "server_info": {
    "name": "akshare-value-investment-mcp",
    "version": "1.0.0"
  }
}
```

## 🏗️ 架构设计

```
mcp/
├── __init__.py                 # MCP包入口
├── __main__.py                # 命令行启动入口
├── README.md                  # MCP文档
├── server.py                  # MCP服务器核心
├── config.py                  # 配置和工具注册
├── tools/                     # MCP工具实现
│   ├── __init__.py
│   ├── financial_query_tool.py    # 财务查询工具
│   └── field_discovery_tool.py    # 字段发现工具
└── schemas/                   # Schema定义
    ├── __init__.py
    ├── query_schemas.py           # 请求Schema
    └── response_schemas.py        # 响应Schema
```

## 🔗 相关模块

- `business/financial_query_service.py`: 核心财务查询服务
- `business/field_discovery_service.py`: 字段发现服务
- `core/stock_identifier.py`: 智能股票代码识别器
- `cache/`: SQLite智能缓存系统

## 📝 更新日志

### v1.0.0
- ✅ 完整的MCP服务器实现
- ✅ 5个核心MCP工具
- ✅ 标准化的Schema定义
- ✅ 交互式测试模式
- ✅ 完整的错误处理机制