# MCP 服务器配置指南

## 📋 概述

AKShare Value Investment MCP 服务器提供基于 MCP (Model Context Protocol) 的财务数据查询服务。该服务器通过 HTTP 调用 FastAPI 服务来获取财务数据。

## 🚀 快速开始

### 1. 基础启动

```bash
# 安装项目
poe install

# 启动 FastAPI 服务
poe api

# 在新终端启动 MCP 服务器
poe mcp
```

### 2. 环境变量配置

复制环境配置文件：
```bash
cp .env.example .env
```

修改 `.env` 文件中的配置：
```bash
# FastAPI 服务地址
AKSHARE_FASTAPI_URL=http://localhost:8000

# MCP 服务器配置
AKSHARE_MCP_HOST=localhost
AKSHARE_MCP_PORT=8080
AKSHARE_MCP_DEBUG=false
```

### 3. 命令行参数启动

```bash
# 使用默认配置
akshare-mcp-server

# 自定义端口
akshare-mcp-server --port 9000

# 自定义 FastAPI 地址
akshare-mcp-server --fastapi-url http://api.example.com:8000

# 启用调试模式
akshare-mcp-server --debug

# 组合使用
akshare-mcp-server --host 0.0.0.0 --port 8080 --fastapi-url http://localhost:8000 --debug
```

## 🔧 配置选项

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `AKSHARE_FASTAPI_URL` | `http://localhost:8000` | FastAPI 服务地址 |
| `AKSHARE_MCP_HOST` | `localhost` | MCP 服务器监听地址 |
| `AKSHARE_MCP_PORT` | `8080` | MCP 服务器监听端口 |
| `AKSHARE_MCP_DEBUG` | `false` | 调试模式开关 |

### 命令行参数

```bash
akshare-mcp-server [选项]

选项:
  --host HOST          MCP 服务器监听地址 (覆盖 AKSHARE_MCP_HOST)
  --port PORT          MCP 服务器监听端口 (覆盖 AKSHARE_MCP_PORT)
  --fastapi-url URL    FastAPI 服务地址 (覆盖 AKSHARE_FASTAPI_URL)
  --debug              启用调试模式
  --version            显示版本信息
  --help               显示帮助信息
```

## 🎯 使用方法

### 交互式模式

启动 MCP 服务器后，进入交互式模式：

```bash
🔧 请输入工具名称或命令: help
📋 可用工具:
1. query_financial_data - 查询财务数据
2. get_available_fields - 获取可用字段
3. discover_fields - 发现字段
4. validate_fields - 验证字段
5. discover_all_market_fields - 发现市场所有字段

📋 可用命令:
- help/帮助: 显示此帮助信息
- status/状态: 显示服务器状态
- quit/exit/退出: 停止服务器
```

### 工具调用示例

1. **查询财务数据**
   ```
   🔧 请输入工具名称或命令: query_financial_data
   请输入市场类型 (a_stock/hk_stock/us_stock): a_stock
   请输入查询类型: a_stock_indicators
   请输入股票代码: SH600519
   请输入时间频率 (annual/quarterly，默认 annual): annual
   请输入字段列表 (逗号分隔，可选): 报告期,净利润
   ```

2. **获取可用字段**
   ```
   🔧 请输入工具名称或命令: get_available_fields
   请输入市场类型 (a_stock/hk_stock/us_stock): a_stock
   请输入查询类型: a_stock_indicators
   ```

3. **验证字段**
   ```
   🔧 请输入工具名称或命令: validate_fields
   请输入市场类型 (a_stock/hk_stock/us_stock): a_stock
   请输入查询类型: a_stock_indicators
   请输入要验证的字段 (逗号分隔): 净利润,净资产收益率,不存在的字段
   ```

## 🔌 Poe 任务

项目提供预配置的 Poe 任务：

```bash
# 启动 MCP 服务器
poe mcp

# 启动调试模式 MCP 服务器
poe mcp-debug
```

## 🐛 调试模式

启用调试模式可以获得更详细的日志输出：

```bash
# 环境变量方式
AKSHARE_MCP_DEBUG=true akshare-mcp-server

# 命令行方式
akshare-mcp-server --debug

# Poe 任务方式
poe mcp-debug
```

## 📊 服务状态

使用 `status` 命令查看服务器状态：

```
🔧 请输入工具名称或命令: status

📊 服务器状态:
🖥️  服务器名称: akshare-value-investment-mcp
📖 版本: 1.0.0
📡 监听地址: localhost:8080
🔗 FastAPI 服务: http://localhost:8000
🐛 调试模式: 开启
```

## 🚨 错误处理

### 常见错误

1. **FastAPI 连接失败**
   ```
   ❌ 工具调用失败
   📄 错误: FastAPI服务错误 (HTTP 111): Connection refused
   ```
   解决方案：确保 FastAPI 服务正在运行 (`poe api`)

2. **无效的市场类型**
   ```
   ❌ 工具调用失败
   📄 错误: 参数验证错误: 无效的市场类型 'xxx'
   ```
   解决方案：使用有效的市场类型 (a_stock, hk_stock, us_stock)

3. **市场与查询类型不匹配**
   ```
   ❌ 工具调用失败
   📄 错误: 查询类型 hk_stock_indicators 与市场 a_stock 不匹配
   ```
   解决方案：确保查询类型与市场类型匹配

## 📁 配置文件

### `.env` 文件示例
```bash
# 基础配置
AKSHARE_FASTAPI_URL=http://localhost:8000
AKSHARE_MCP_HOST=localhost
AKSHARE_MCP_PORT=8080
AKSHARE_MCP_DEBUG=false

# 可选配置
# AKSHARE_LOG_LEVEL=INFO
# AKSHARE_DB_PATH=.cache/financial_data.db
```

### 生产环境配置示例
```bash
# 生产环境配置
AKSHARE_FASTAPI_URL=https://api.example.com:443
AKSHARE_MCP_HOST=0.0.0.0
AKSHARE_MCP_PORT=8080
AKSHARE_MCP_DEBUG=false
AKSHARE_LOG_LEVEL=WARNING
```

## 🔗 相关文档

- [FastAPI 文档](./FASTAPI_GUIDE.md)
- [系统架构文档](./SYSTEM_ARCHITECTURE_SUMMARY.md)
- [缓存系统文档](./CACHE_SYSTEM_TECHNICAL_GUIDE.md)

## 📞 支持

如果遇到问题，请检查：

1. FastAPI 服务是否正常启动
2. 网络连接是否正常
3. 配置参数是否正确
4. 日志输出中的错误信息