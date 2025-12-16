# MCP架构指南

## 📋 概述

本文档详细说明了 akshare-value-investment 项目中 MCP (Model Context Protocol) 服务器的架构设计和实现方式。

## 🏗️ 当前架构 (v3.1.0)

### 架构模式：HTTP客户端适配层

MCP 服务器已从直接业务逻辑调用架构重构为基于 HTTP 客户端的适配层架构：

```
┌─────────────┐    HTTP     ┌──────────────┐    业务逻辑    ┌─────────────┐
│ MCP客户端   │ ────────► │ MCP服务器    │ ──────────► │ FastAPI服务 │
│ (Claude等) │           │ (协议适配层) │             │ (核心服务)  │
└─────────────┘           └──────────────┘             └─────────────┘
        │                           │                           │
        │ MCP协议                   │ HTTP REST API              │ 数据库查询
        │                           │                           │ 和缓存
        ▼                           ▼                           ▼
   标准化JSON请求           httpx HTTP客户端              SQLite缓存
   标准化JSON响应         格式转换和错误处理              业务逻辑处理
```

## 🎯 核心组件

### 1. MCP服务器 (协议适配层)

**位置**: `src/akshare_value_investment/mcp/server.py`

**职责**:
- 处理 MCP 协议请求和响应
- 路由工具调用到对应的 HTTP 客户端工具
- 维护 MCP 协议的标准化接口

**特点**:
- 不直接访问数据库或业务逻辑
- 通过 HTTP 调用 FastAPI 服务
- 保持 MCP 协议接口的兼容性

### 2. HTTP客户端工具

**位置**: `src/akshare_value_investment/mcp/tools/`

**主要工具**:
- `FinancialQueryTool`: 财务数据查询 HTTP 客户端
- `FieldDiscoveryTool`: 字段发现 HTTP 客户端

**实现方式**:
```python
class FinancialQueryTool:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def query_financial_data(self, ...):
        response = self.client.post(
            f"{self.api_base_url}/api/v1/financial/query",
            json=request_data
        )
        return self._convert_to_mcp_response(response.json())
```

### 3. FastAPI服务 (核心业务层)

**位置**: `src/akshare_value_investment/api/`

**职责**:
- 核心财务数据查询逻辑
- SQLite 智能缓存管理
- 数据验证和格式化
- 错误处理和日志记录

**优势**:
- 独立的 REST API 服务
- 支持多种客户端 (MCP、Web应用、第三方集成)
- 统一的缓存和业务逻辑

## 🔄 调用流程详解

### 完整的数据查询流程

1. **MCP客户端请求**
   ```json
   {
     "tool": "query_financial_data",
     "parameters": {
       "market": "a_stock",
       "query_type": "a_stock_indicators",
       "symbol": "600519"
     }
   }
   ```

2. **MCP服务器处理**
   - 验证 MCP 请求格式
   - 路由到 `FinancialQueryTool`
   - 转换参数格式

3. **HTTP客户端调用**
   ```python
   response = client.post(
       "http://localhost:8000/api/v1/financial/query",
       json={
         "market": "a_stock",
         "query_type": "a_stock_indicators",
         "symbol": "600519"
       }
   )
   ```

4. **FastAPI服务处理**
   - 参数验证和类型转换
   - 缓存查询 (SQLite)
   - 数据获取 (akshare)
   - 缓存更新
   - 响应格式化

5. **响应返回**
   - FastAPI → HTTP响应 → MCP格式转换 → MCP客户端

## ⚙️ 配置管理

### MCP服务器配置

**文件**: `src/akshare_value_investment/mcp/config.py`

```python
@dataclass
class MCPServerConfig:
    # FastAPI服务配置 (核心数据源)
    fastapi_base_url: str = "http://localhost:8000"
    fastapi_timeout: int = 30
    fastapi_retry_attempts: int = 3

    # HTTP客户端配置
    http_client_config: dict = None
```

### 环境变量支持

```bash
# FastAPI服务地址
export FASTAPI_BASE_URL="http://localhost:8000"

# MCP服务器调试模式
export MCP_DEBUG="true"
```

## 🚀 部署和运行

### 启动顺序

1. **启动FastAPI服务** (核心服务)
   ```bash
   poe api
   # 或者
   uvicorn akshare_value_investment.api.main:create_app --reload
   ```

2. **启动MCP服务器** (协议适配层)
   ```bash
   poe mcp
   # 或者
   akshare-mcp-server
   ```

### 验证服务状态

```bash
# 检查FastAPI服务
curl -s http://localhost:8000/health

# 检查MCP服务器
akshare-mcp-server --info
```

## 📊 架构优势

### 1. 服务分离
- **MCP**: 专注协议适配和标准化
- **FastAPI**: 专注业务逻辑和数据处理
- **Web应用**: 专注用户界面和交互

### 2. 可扩展性
- FastAPI可以独立扩展和优化
- 支持多种客户端协议 (MCP、REST、GraphQL)
- 便于微服务架构演进

### 3. 维护性
- 清晰的服务边界
- 独立的版本管理
- 简化的测试策略

### 4. 性能优化
- FastAPI异步处理能力
- 统一的SQLite缓存策略
- HTTP连接池管理

## 🔧 故障排查

### 常见问题和解决方案

#### 1. MCP服务器无法启动
**原因**: FastAPI服务未运行
**解决**: 先启动FastAPI服务 `poe api`

#### 2. HTTP连接超时
**原因**: FastAPI服务响应慢或网络问题
**解决**: 检查FastAPI服务状态，调整超时配置

#### 3. 数据查询失败
**原因**: MCP和FastAPI版本不匹配
**解决**: 确保使用相同版本的服务

### 调试模式

```bash
# 启动MCP调试模式
poe mcp-debug

# 查看详细日志
export MCP_DEBUG=true
akshare-mcp-server
```

## 📈 未来演进

### 可能的架构改进

1. **服务发现**: 动态FastAPI服务发现
2. **负载均衡**: 多个FastAPI实例支持
3. **缓存层**: Redis分布式缓存
4. **监控告警**: 服务健康状态监控

### 兼容性保证

- 保持MCP协议接口稳定
- 向后兼容的API版本管理
- 渐进式架构演进

---

**文档版本**: v3.1.0
**最后更新**: 2025-12-16
**架构版本**: HTTP客户端适配层