# AKShare价值投资分析系统

> 跨市场股票财务分析工具 - 支持A股、港股、美股

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![akshare](https://img.shields.io/badge/akshare-1.0.0+-green.svg)](https://www.akshare.xyz/)

## 1分钟上手

### 第一次使用

```bash
# 1. 克隆项目
git clone <repository_url>
cd akshare-value-investment

# 2. 安装依赖
uv sync

# 3. 启动服务(自动启动API和Web应用)
./start_services.sh
```

### 日常使用

```bash
# 方式1: 使用启动脚本(推荐)
./start_services.sh

# 方式2: 手动启动
# 终端1: 启动后端API服务
poe api

# 终端2: 启动前端Web应用
poe streamlit
```

访问 **http://localhost:8501**,输入股票代码即可开始分析!

**支持格式**：
- A股: `600519` 或 `SH600519` (茅台)
- 港股: `00700` 或 `700` (腾讯)
- 美股: `AAPL` (苹果)

## 核心功能

### 📊 财务质量分析

#### 💰 盈利分析（5大核心指标）

价值投资分析逻辑，从核心到质量：

1. **💎 投入资本回报率(ROIC)** - 资本使用效率（好生意的第一标准）
2. **💰 盈利能力如何(EBIT利润率)** - 核心业务盈利（优秀标准：>25%）
3. **📈 营收是否增长(成长性)** - 业务扩张能力
4. **💰 利润是否为真(净现比)** - 利润质量分析
5. **💵 现金转化能力(自由现金流)** - 真金白银

#### 💳 债务分析

评估公司财务杠杆和偿债能力：

1. **💳 有息债务权益比** - 债务水平分析
2. **💰 有息债务与自由现金流比率** - 债务偿还能力
3. **💧 流动性分析** - 流动比率、速动比率、利息覆盖比率

### 🎯 智能识别

自动识别股票代码所属市场,无需手动选择!
- 输入错误代码时智能提示(如APPL→AAPL)
- **搜索历史**: 自动记录查询过的股票,支持快速搜索
- **代码标准化**: 港股自动补零(700→00700),避免重复记录

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

### Q: 第一次使用需要做什么?
A:
```bash
# 1. 安装uv包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目并安装依赖
git clone <repository_url>
cd akshare-value-investment
uv sync

# 3. 启动服务
./start_services.sh
```

### Q: 启动提示"无法连接到API服务"?
A: 请确保先启动API服务 `poe api`,再启动Web应用 `poe streamlit`,或直接使用 `./start_services.sh` 一键启动

### Q: 如何使用启动脚本?
A: 运行 `./start_services.sh` 会自动启动API和Web应用,推荐使用!

### Q: 股票代码输入错误怎么办?
A: 系统会智能提示常见错误(如APPL→AAPL),并给出正确代码建议

### Q: 支持多少年的数据查询?
A: 默认查询最近10年数据,可在界面调整查询年数

### Q: 搜索历史记录保存在哪里?
A: 历史记录保存在 `webapp/.cache/stock_history.json`,支持持久化存储

### Q: 港股代码格式为什么有变化?
A: 系统自动将港股代码标准化为5位数字(如700→00700),避免重复记录

### Q: 如何手动停止服务?
A:
```bash
# 停止FastAPI服务 (端口8000)
lsof -ti:8000 | xargs kill

# 停止Streamlit服务 (端口8501)
lsof -ti:8501 | xargs kill

# 一次性停止所有服务
lsof -ti:8000,8501 | xargs kill
```

---

**当前版本**: v3.3.0 (股票搜索历史版)
**技术栈**: Python 3.13, Streamlit, FastAPI, akshare, Plotly
**最后更新**: 2025-12-26

## 更新日志

### v3.3.0 (2025-12-26) - 股票搜索历史版 ✨
- ✨ **新增**: streamlit-searchbox 智能搜索框
- ✨ **新增**: 股票查询历史记录(持久化存储)
- ✨ **新增**: 代码自动标准化(港股700→00700)
- ✨ **新增**: 搜索结果去重逻辑
- 🐛 **修复**: 港股代码重复问题(0700/00700合并)
- 📝 **文档**: 更新README,添加搜索历史说明

### v3.2.0 (2025-12-25) - ROIC杜邦拆解分析版
- ✨ **新增**: ROIC杜邦拆解分析
- 📊 **优化**: 净利润周转率分析图表
