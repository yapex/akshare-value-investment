# AKShare价值投资分析系统

> 基于akshare和MCP的智能财务数据查询系统

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![akshare](https://img.shields.io/badge/akshare-1.0.0+-green.svg)](https://www.akshare.xyz/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**项目愿景**: 基于akshare和MCP协议的跨市场财务数据查询系统，为AI助手提供标准化的财务数据访问接口。

## 🎯 核心特性

- 🔍 **跨市场覆盖**: A股、港股、美股财务数据
- 🤖 **MCP协议**: Model Context Protocol标准化接口
- 💾 **智能缓存**: DiskCache缓存系统，API调用减少70%+
- 🏗️ **SOLID架构**: 基于设计模式的可扩展架构
- ⚡ **严格字段过滤**: 按需返回数据，减少传输开销
- 📊 **Web交互界面**: Streamlit财务分析应用，支持可视化图表

## 🚀 快速开始

### 基础查询

```python
from akshare_value_investment import create_container

# 创建容器
container = create_container()

# 获取查询器
a_stock_queryer = container.a_stock_indicators()

# 查询A股财务数据
data = a_stock_queryer.query("600519", "2023-01-01", "2023-12-31")
print(f"贵州茅台ROE: {data.iloc[0]['净资产收益率(%)']}")
```

### Web应用使用

```bash
# 启动Streamlit财务分析应用
poe streamlit
# 或者
PYTHONPATH=src:webapp uv run streamlit run webapp/main.py

# 访问应用
# 浏览器打开 http://localhost:8501
```

**Web应用功能**:
- 📈 **四大财务报表**: 财务指标、资产负债表、利润表、现金流量表
- 🎯 **交互式图表**: 点击任意指标查看深度分析和趋势图
- 📅 **智能时间选择**: 支持5年、10年、全部历史数据
- 📊 **窄表格式**: 年份横向排列，便于趋势分析
- 🔍 **数据过滤**: 自动隐藏空值和无效指标
- 📱 **响应式设计**: 适配不同屏幕尺寸

### MCP服务器使用

```bash
# 启动MCP服务器
uv run python -m akshare_value_investment.mcp.server --stdio

# 或查看工具信息
uv run python -m akshare_value_investment.mcp.server --info
```

## 📊 支持的市场和查询类型

### A股市场 (4个查询类型)
- **财务指标**: 净资产收益率、净利润、毛利率等25+指标
- **资产负债表**: 资产总计、负债合计等75+字段
- **利润表**: 营业收入、营业成本等46+字段
- **现金流量表**: 经营活动现金流等72+字段

### 港股市场 (2个查询类型)
- **财务指标**: ROE、净利润等核心指标
- **财务三表**: 完整财务报表数据

### 美股市场 (4个查询类型)
- **财务指标**: ROE、EPS等财务指标
- **资产负债表**: 完整资产负债表
- **利润表**: 收入、成本、利润等
- **现金流量表**: 经营、投资、筹资现金流

## 🛠️ MCP工具集

### 1. query_financial_data
查询财务数据，支持严格字段过滤和时间频率处理

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

### 2. get_available_fields
获取指定查询类型的所有可用字段

```json
{
  "tool": "get_available_fields",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators"
  }
}
```

### 3. validate_fields
验证字段有效性并提供智能建议

```json
{
  "tool": "validate_fields",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators",
    "fields": ["净利润", "不存在的字段"]
  }
}
```

### 4. discover_fields
发现指定查询类型的字段

```json
{
  "tool": "discover_fields",
  "parameters": {
    "market": "a_stock",
    "query_type": "a_stock_indicators"
  }
}
```

### 5. discover_all_market_fields
发现指定市场下所有查询类型的字段

```json
{
  "tool": "discover_all_market_fields",
  "parameters": {
    "market": "a_stock"
  }
}
```

## 🏗️ 系统架构

```
src/akshare_value_investment/
├── core/                   # 核心组件
│   ├── models.py          # 数据模型定义
│   └── stock_identifier.py # 智能股票代码识别
├── datasource/queryers/    # SOLID查询器架构
│   ├── base_queryer.py    # 模板方法基类
│   ├── a_stock_queryers.py # A股查询器
│   ├── hk_stock_queryers.py # 港股查询器
│   └── us_stock_queryers.py # 美股查询器
├── cache/                 # SQLite智能缓存
│   ├── sqlite_cache.py    # 缓存核心实现
│   └── smart_decorator.py # 透明缓存装饰器
├── business/              # 业务服务层
│   ├── financial_query_service.py # 统一查询接口
│   ├── field_discovery_service.py # 字段发现服务
│   └── mcp_response.py    # MCP标准化响应
├── mcp/                   # MCP协议实现
│   ├── server.py          # MCP服务器核心
│   ├── tools/             # MCP工具集
│   └── schemas/           # Schema定义
└── container.py           # 依赖注入容器
```

## 💾 缓存系统

### 智能增量更新
- **API调用减少70%+**: 智能识别缺失数据范围
- **查询速度提升50%+**: SQL范围查询优于多次键值查询
- **存储效率提升60%+**: 按条精确缓存，无冗余字段
- **线程安全保障**: 支持高并发访问

### 使用示例

```python
from akshare_value_investment.cache import SQLiteCache, smart_sqlite_cache

# 创建缓存实例
cache = SQLiteCache(db_path=".cache/financial_data.db")

# 应用装饰器
@smart_sqlite_cache(
    date_field='date',
    query_type='indicators',
    cache_adapter=cache
)
def get_financial_data(symbol, start_date, end_date):
    return akshare_api_call(symbol)

# 透明缓存使用
data1 = get_financial_data("600519", "2023-01-01", "2023-12-31")  # API调用
data2 = get_financial_data("600519", "2023-01-01", "2023-12-31")  # 缓存命中
```

## 🧪 测试覆盖

```bash
# 运行所有测试
uv run pytest tests/

# 运行MCP集成测试
uv run python test_mcp_integration.py

# 运行缓存业务场景测试
uv run pytest tests/test_financial_cache_business_scenarios.py
```

**测试统计**: 293个测试用例，100%通过率

## 📈 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 总测试数 | 293个 | 100%通过率 |
| API调用减少 | 70%+ | 智能缓存效果 |
| 查询速度提升 | 50%+ | SQL优化效果 |
| 存储效率提升 | 60%+ | 精确缓存策略 |
| 字段覆盖 | 218个 | A股全市场字段 |

## 🔧 开发指南

### 环境要求
- Python >= 3.13
- uv 包管理器
- akshare >= 1.0.0

### 核心原则
- **SOLID架构**: 基于设计模式的可扩展架构
- **智能缓存**: 透明的缓存机制，提升性能
- **原始数据完整**: 保留所有原始字段，用户自主选择
- **跨市场统一**: 同一接口支持三地市场

## 📚 文档

### 用户指南
- [📊 财报检查清单](./doc/a_stock_check_list.md) - **A股财务分析完整指南**，包含42项详细检查指标和计算方法
- [📈 Web应用使用](./webapp/) - Streamlit财务分析应用，可视化界面

### 技术文档
- [MCP集成文档](./src/akshare_value_investment/mcp/README.md) - MCP服务器完整文档
- [时间范围过滤修复](./doc/TIME_RANGE_FILTERING_FIX.md) - API时间过滤功能说明
- [A股字段说明](./doc/a_stock_fields.md) - A股财务数据字段详解

## 🚀 版本历史

### v3.0.0 (2025-12-03) - MCP集成版
- ✅ **完整MCP集成**: 5个核心MCP工具
- ✅ **标准化响应**: MCP协议兼容的响应格式
- ✅ **智能字段验证**: 字段有效性检查和建议
- ✅ **跨市场统一**: 统一接口支持A股/港股/美股

### v2.1.0 (2025-12-01) - SOLID架构优化
- ✅ **美股查询器重构**: 恢复基类架构，消除代码重复
- ✅ **港股字段修复**: 修复REPORT_DATE字段缺失问题
- ✅ **测试完善**: 293个测试全部通过

### v2.0.0 (2025-11-13) - SQLite智能缓存系统
- ✅ **架构重构**: 复合主键设计，摒弃冗余存储
- ✅ **智能增量更新**: 6种数据缺失场景处理
- ✅ **装饰器模式**: 透明集成缓存功能

---

## 💡 快速上手

### 🚀 想要快速分析A股财务报表？
```bash
# 1. 启动Web应用
poe streamlit

# 2. 打开浏览器访问 http://localhost:8501

# 3. 输入股票代码（如600519），选择时间范围，点击查询

# 4. 点击任意财务指标查看深度图表分析
```

### 📚 需要详细的财报分析指导？
- 阅读 [财报检查清单](./doc/a_stock_check_list.md) - 42项完整财务检查清单
- 包含详细计算公式、评估标准和实际案例

### 🔧 想要集成到自己的项目？
- 参考 [基础查询](#基础查询) 代码示例
- 查阅 [MCP文档](./src/akshare_value_investment/mcp/README.md) 了解协议接口

---

**当前版本**: v3.1.0 (Web应用版)
**技术栈**: Python 3.13, akshare, Streamlit, Plotly, FastAPI, MCP
**最后更新**: 2025-12-16