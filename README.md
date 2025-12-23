# AKShare价值投资分析系统 - FastAPI Web服务

> 基于akshare的跨市场财务数据查询Web API服务

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![akshare](https://img.shields.io/badge/akshare-1.0.0+-green.svg)](https://www.akshare.xyz/)

## 项目概述

基于 FastAPI 的现代化财务数据查询Web API服务，提供A股、港股、美股的财务指标和财务三表数据查询能力，支持GET和POST双模式访问。

**核心特性**：
- 🌐 RESTful API：财务查询端点，支持浏览器URL访问
- ⚡ 异步处理：FastAPI异步高性能处理
- 📖 自动文档：OpenAPI/Swagger自动生成
- 🎯 类型安全：Pydantic模型验证和序列化
- 💾 智能缓存：SQLite缓存系统，API调用减少70%+

## 快速开始

### 启动API服务

```bash
poe api
# 或
PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000
```

### 健康检查

```bash
curl http://localhost:8000/health
```

### 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API端点

### 核心查询端点

| HTTP方法 | 端点 | 功能 |
|---------|------|------|
| GET/POST | `/api/v1/financial/indicators` | 财务指标查询 |
| GET/POST | `/api/v1/financial/statements` | 财务三表聚合查询 |
| GET | `/api/v1/financial/fields/{market}/{query_type}` | 字段发现 |
| GET | `/health` | 健康检查 |

## API使用

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**响应**：
```json
{
  "status": "healthy",
  "container": "configured",
  "services": {
    "a_stock_indicators": "available",
    "hk_stock_indicators": "available",
    "us_stock_indicators": "available",
    "financial_query_service": "available",
    "field_discovery_service": "available"
  }
}
```

### 2. 财务指标查询

**GET方法（浏览器URL）**：
```bash
# A股
curl "http://localhost:8000/api/v1/financial/indicators?symbol=SH600519&market=a_stock&frequency=annual"

# 港股
curl "http://localhost:8000/api/v1/financial/indicators?symbol=00700&market=hk_stock&frequency=quarterly"

# 美股
curl "http://localhost:8000/api/v1/financial/indicators?symbol=AAPL&market=us_stock&frequency=annual"
```

**POST方法（支持字段过滤）**：
```bash
curl -X POST "http://localhost:8000/api/v1/financial/indicators" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "a_stock",
    "query_type": "a_stock_indicators",
    "symbol": "SH600519",
    "fields": ["报告期", "净利润", "净资产收益率"],
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "frequency": "annual"
  }'
```

**响应格式**：
```json
{
  "status": "success",
  "data": {
    "records": [{"报告期": "2023-12-31", "净利润": 747.34}],
    "columns": ["报告期", "净利润"],
    "shape": [1, 2],
    "empty": false
  },
  "metadata": {
    "query_type": "A股财务指标",
    "frequency": "年度数据",
    "record_count": 1
  },
  "query_info": {
    "market": "a_stock",
    "symbol": "SH600519",
    "frequency": "annual"
  }
}
```

### 3. 财务三表查询

**GET方法**：
```bash
# A股财务三表（最近3年）
curl "http://localhost:8000/api/v1/financial/statements?symbol=SH600519&query_type=a_financial_statements&frequency=annual&limit=3"

# 港股财务三表
curl "http://localhost:8000/api/v1/financial/statements?symbol=00700&query_type=hk_financial_statements&frequency=annual"

# 美股财务三表
curl "http://localhost:8000/api/v1/financial/statements?symbol=AAPL&query_type=us_financial_statements&frequency=annual"
```

**POST方法**：
```bash
curl -X POST "http://localhost:8000/api/v1/financial/statements" \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "a_financial_statements",
    "symbol": "SH600519",
    "frequency": "annual",
    "limit": 3
  }'
```

**响应格式**：
```json
{
  "status": "success",
  "data": {
    "balance_sheet": {
      "columns": ["报告期", "资产总计", "负债合计"],
      "data": [{"报告期": "2023-12-31", "资产总计": 1234.56}],
      "record_count": 1
    },
    "income_statement": {...},
    "cash_flow": {...}
  },
  "metadata": {
    "symbol": "SH600519",
    "query_type": "A股财务三表",
    "frequency": "年度数据",
    "record_counts": {
      "balance_sheet": 1,
      "income_statement": 1,
      "cash_flow": 1
    },
    "limit": 3
  }
}
```

### 4. 字段发现查询

```bash
# A股财务指标字段
curl http://localhost:8000/api/v1/financial/fields/a_stock/a_stock_indicators

# A股财务三表字段
curl http://localhost:8000/api/v1/financial/fields/a_stock/a_financial_statements

# 港股财务指标字段
curl http://localhost:8000/api/v1/financial/fields/hk_stock/hk_stock_indicators

# 美股财务三表字段
curl http://localhost:8000/api/v1/financial/fields/us_stock/us_financial_statements
```

## 参数说明

### 通用参数

| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `symbol` | string | 股票代码 | SH600519, 00700, AAPL |
| `market` | string | 市场类型 | a_stock, hk_stock, us_stock |
| `frequency` | string | 数据频率 | annual（年度）, quarterly（报告期） |
| `query_type` | string | 查询类型 | 见下方查询类型列表 |
| `limit` | int | 限制返回记录数（可选） | >=1 |

### 查询类型

**财务指标**：
- `a_stock_indicators` - A股财务指标
- `hk_stock_indicators` - 港股财务指标
- `us_stock_indicators` - 美股财务指标

**财务三表**：
- `a_financial_statements` - A股财务三表
- `hk_financial_statements` - 港股财务三表
- `us_financial_statements` - 美股财务三表

## 数据范围

### A股市场
- **财务指标**: 25+核心财务指标
- **资产负债表**: 75+字段
- **利润表**: 46+字段
- **现金流量表**: 72+字段

### 港股市场
- **财务指标**: 核心财务指标
- **财务三表**: 完整财务报表数据（窄表→宽表转换）

### 美股市场
- **财务指标**: 核心财务指标
- **财务三表**: 完整财务报表数据（窄表→宽表转换）

## 错误处理

| 状态码 | 说明 |
|--------|------|
| 200 | 查询成功 |
| 400 | 业务错误（市场与查询类型不匹配） |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

**错误响应格式**：
```json
{
  "detail": {
    "error": {
      "type": "invalid_query_type",
      "message": "查询类型与市场不匹配"
    }
  }
}
```

## 系统架构

```
src/akshare_value_investment/
├── api/                    # FastAPI Web API
│   ├── main.py            # 应用入口
│   ├── routes/            # API路由
│   │   ├── financial.py   # 财务查询端点
│   │   └── field_discovery.py # 字段发现端点
│   ├── models/            # Pydantic模型
│   └── dependencies.py    # 依赖注入配置
├── business/              # 业务服务层
│   ├── financial_query_service.py # 查询服务
│   └── field_discovery_service.py # 字段发现服务
├── datasource/queryers/   # 数据查询器
└── container.py           # 依赖注入容器
```

## 运行测试

```bash
# 运行所有测试
uv run pytest tests/

# 运行API测试
uv run pytest tests/api/
```

**测试统计**：259个测试，100%通过率

## 版本历史

### v3.0.0 (2025-12-23) - FastAPI Web服务版
- ✅ FastAPI集成：完整的RESTful API服务
- ✅ GET/POST双模式：支持浏览器URL和POST JSON
- ✅ 自动API文档：Swagger UI和ReDoc自动生成
- ✅ 健康检查端点：服务状态监控
- ✅ 类型安全：Pydantic模型验证

---

**当前版本**: v3.0.0 (FastAPI Web服务版)
**技术栈**: Python 3.13, FastAPI, Pydantic, akshare, dependency-injector, SQLite
**最后更新**: 2025-12-23
