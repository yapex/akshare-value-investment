# AKShare价值投资分析系统

> 跨市场股票财务分析工具 - 支持A股、港股、美股

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![akshare](https://img.shields.io/badge/akshare-1.0.0+-green.svg)](https://www.akshare.xyz/)

## 1分钟上手

### 启动Web应用

```bash
# 1. 启动后端API服务
poe api

# 2. 启动前端Web应用
poe streamlit
```

访问 **http://localhost:8501**,输入股票代码即可开始分析!

**支持格式**：
- A股: `600519` 或 `SH600519` (茅台)
- 港股: `00700` 或 `700` (腾讯)
- 美股: `AAPL` (苹果)

## 核心功能

### 📊 财务质量分析

四大核心指标,快速判断股票质量:

1. **💰 利润是否为真(净现比)** - 利润质量分析
2. **💵 现金转化能力(自由现金流)** - 现金充裕度
3. **📈 营收是否增长(成长性)** - 业务扩张能力
4. **💰 盈利能力如何(EBIT利润率)** - 核心业务盈利

### 🎯 智能识别

自动识别股票代码所属市场,无需手动选择!
- 输入错误代码时智能提示(如APPL→AAPL)

### 📈 可视化图表

- 双Y轴图表:柱状图+折线图组合
- 合格线参考:0.8分界线清晰标注
- 关键指标:一目了然的核心数据

## 项目架构

```
AKShare价值投资分析系统
├── 🌐 FastAPI Web API  (后端数据服务)
│   └── 提供财务数据查询API
└── 📊 Streamlit Web应用 (前端可视化)
    └── 股票质量分析界面
```

## API服务 (开发者)

### 启动API服务

```bash
poe api
```

### 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 健康检查

```bash
curl http://localhost:8000/health
```

### 快速查询

```bash
# A股财务指标
curl "http://localhost:8000/api/v1/financial/indicators?symbol=SH600519&market=a_stock"

# 港股财务三表
curl "http://localhost:8000/api/v1/financial/statements?symbol=00700&query_type=hk_financial_statements"

# 美股财务指标
curl "http://localhost:8000/api/v1/financial/indicators?symbol=AAPL&market=us_stock"
```

## 技术特性

- **跨市场支持**: A股、港股、美股全覆盖
- **财务数据**: 财务指标 + 财务三表完整覆盖
- **SOLID架构**: 基于设计模式的优雅架构
- **类型安全**: 完整类型注解和Pydantic验证
- **测试覆盖**: 多层级测试覆盖

## 详细文档

- **API文档**: http://localhost:8000/docs (启动服务后访问)
- **财报检查清单**: [doc/财报检查清单.md](doc/财报检查清单.md)
- **字段说明**: [doc/README.md](doc/README.md)

## 环境要求

- Python >= 3.13
- uv 包管理器
- akshare >= 1.0.0

## 常见问题

### Q: 启动提示"无法连接到API服务"?
A: 请确保先启动API服务 `poe api`,再启动Web应用 `poe streamlit`

### Q: 股票代码输入错误怎么办?
A: 系统会智能提示常见错误(如APPL→AAPL),并给出正确代码建议

### Q: 支持多少年的数据查询?
A: 默认查询最近10年数据,可在界面调整查询年数

---

**当前版本**: v3.1.0 (Streamlit Web应用版)
**技术栈**: Python 3.13, Streamlit, FastAPI, akshare, Plotly
**最后更新**: 2025-12-24
