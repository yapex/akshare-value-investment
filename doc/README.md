# AKShare价值投资分析系统 - 文档目录

## 📋 文档概览

本目录包含 AKShare价值投资分析系统 的核心文档。

**当前版本**: v3.0.0 (MCP集成版)
**架构类型**: SOLID架构 + MCP协议 + 智能缓存

## 🎯 核心文档

### [SYSTEM_ARCHITECTURE_SUMMARY.md](./SYSTEM_ARCHITECTURE_SUMMARY.md)
**系统架构总结** - 项目的整体架构设计和技术实现

- ✅ 当前版本：v3.0.0 (MCP集成版)
- ✅ 核心能力：MCP协议接口 + 跨市场财务数据查询
- ✅ 架构设计：SOLID原则 + MCP协议 + 智能缓存
- ✅ 技术特性：5个MCP工具、标准化响应、智能字段验证

### [CACHE_SYSTEM_TECHNICAL_GUIDE.md](./CACHE_SYSTEM_TECHNICAL_GUIDE.md)
**缓存系统技术指南** - SQLite智能缓存系统的详细技术文档

- ✅ 智能增量更新算法 (API调用减少70%+)
- ✅ 复合主键设计 (存储效率提升60%+)
- ✅ 装饰器模式集成 (透明缓存)
- ✅ 线程安全机制

## 🤖 MCP集成文档

### [MCP_DESIGN_SUMMARY.md](./MCP_DESIGN_SUMMARY.md)
**MCP设计总结** - Model Context Protocol集成的设计文档

- ✅ MCP工具集设计和实现
- ✅ JSON-RPC协议适配
- ✅ 字段验证和建议机制
- ✅ 标准化错误处理

**详细MCP文档**: [`../src/akshare_value_investment/mcp/README.md`](../src/akshare_value_investment/mcp/README.md)

## 📊 数据示例

### [sample_data/](./sample_data/)
**数据示例** - 各市场财务数据的实际样本

- **A股数据**：财务指标、资产负债表、利润表、现金流量表样本
- **港股数据**：财务指标和财务三表样本
- **美股数据**：标准化财务报表样本
- **API参考**：AKShare API调用示例

## 🗂️ 文档使用指南

### 新手入门
1. **项目概览**: 首先阅读 [`../README.md`](../README.md) 了解完整功能
2. **系统架构**: 查看 [SYSTEM_ARCHITECTURE_SUMMARY.md](./SYSTEM_ARCHITECTURE_SUMMARY.md) 了解技术架构
3. **MCP使用**: 参考 [`../src/akshare_value_investment/mcp/README.md`](../src/akshare_value_investment/mcp/README.md) 了解MCP工具
4. **数据格式**: 查看 [sample_data/](./sample_data/) 了解数据结构

### 开发者参考
- **MCP协议**: JSON-RPC工具调用、Schema定义、响应格式
- **查询器架构**: SOLID原则、设计模式应用、跨市场统一接口
- **缓存优化**: 智能算法、增量更新策略、性能优化
- **股票代码**: 智能格式化、AKShare API适配

### MCP用户指南
- **启动服务器**: `uv run python -m akshare_value_investment.mcp.server --stdio`
- **工具调用**: query_financial_data、get_available_fields、validate_fields等
- **配置设置**: `.mcp.json` 配置文件
- **错误处理**: 标准化错误响应和调试模式

## 🔗 相关资源

- **项目主页**：[`../README.md`](../README.md) - 完整功能介绍和快速开始
- **MCP服务器**：[`../src/akshare_value_investment/mcp/`](../src/akshare_value_investment/mcp/) - MCP协议实现
- **业务服务**：[`../src/akshare_value_investment/business/`](../src/akshare_value_investment/business/) - 核心业务逻辑
- **测试用例**：[`../tests/`](../tests/) - 293个测试用例
- **缓存系统**：[`../src/akshare_value_investment/cache/`](../src/akshare_value_investment/cache/) - 智能缓存实现

## 📈 版本历史

- **v3.0.0** (2025-12-03): MCP集成版 - 5个MCP工具，标准化响应
- **v2.1.0** (2025-12-01): SOLID架构优化 - 美股查询器重构，测试完善
- **v2.0.0** (2025-11-13): SQLite智能缓存系统 - 智能增量更新，装饰器模式
- **v1.0.0**: 基础架构实现

---

**当前状态**: ✅ 生产就绪 - MCP驱动的智能财务数据查询系统