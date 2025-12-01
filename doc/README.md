# 文档目录

## 📋 文档概览

本目录包含 akshare-value-investment 项目的核心文档。

## 🎯 核心文档

### [SYSTEM_ARCHITECTURE_SUMMARY.md](./SYSTEM_ARCHITECTURE_SUMMARY.md)
**系统架构总结** - 项目的整体架构设计和技术实现

- ✅ 当前版本：v2.1.0 (SOLID架构优化)
- ✅ 核心能力：跨市场财务数据查询系统
- ✅ 架构设计：SOLID原则 + 查询器模式
- ✅ 技术特性：SQLite智能缓存、依赖注入、设计模式

### [CACHE_SYSTEM_TECHNICAL_GUIDE.md](./CACHE_SYSTEM_TECHNICAL_GUIDE.md)
**缓存系统技术指南** - SQLite智能缓存系统的详细技术文档

- ✅ 智能增量更新算法
- ✅ 复合主键设计
- ✅ 装饰器模式集成
- ✅ 线程安全机制

## 📊 数据示例

### [sample_data/](./sample_data/)
**数据示例** - 各市场财务数据的实际样本

- **A股数据**：`a_stock_data_analysis.md` + CSV样本文件
- **港股数据**：`hk_stock_data_analysis.md` + CSV样本文件
- **美股数据**：`us_stock_data_analysis.md` + CSV样本文件
- **API参考**：`DATA_SOURCE_API_REFERENCE.md`

## 🗂️ 文档使用指南

### 新手入门
1. 首先阅读 [SYSTEM_ARCHITECTURE_SUMMARY.md](./SYSTEM_ARCHITECTURE_SUMMARY.md) 了解系统概览
2. 查看 [sample_data/](./sample_data/) 了解数据格式和API调用
3. 参考 [CACHE_SYSTEM_TECHNICAL_GUIDE.md](./CACHE_SYSTEM_TECHNICAL_GUIDE.md) 了解缓存机制

### 开发者参考
- **架构设计**：SOLID原则、设计模式应用、查询器架构
- **性能优化**：智能缓存算法、增量更新策略
- **数据格式**：跨市场数据标准化、窄表宽表转换

## 🔗 相关资源

- **项目根目录**：[`../README.md`](../README.md)
- **代码示例**：[`../examples/demo.py`](../examples/demo.py)
- **测试用例**：[`../tests/`](../tests/)
- **核心代码**：[`../src/akshare_value_investment/`](../src/akshare_value_investment/)

## 📈 文档维护

文档与代码保持同步更新：

- **v2.1.0** (2025-12-01): SOLID架构优化，删除过时文档
- **v2.0.0** (2025-11-13): SQLite智能缓存系统
- **v1.0.0**: 基础架构实现

---

**注意**: 本项目专注于原始数据访问和智能缓存，文档内容反映了当前简化版本的架构设计。