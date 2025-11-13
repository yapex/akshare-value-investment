# MCP集成文档

本目录包含akshare-value-investment项目的Claude Code MCP服务器集成文档。

## 📋 文档说明

### [README_MCP.md](./README_MCP.md)
**MCP服务器主要文档** - 包含完整的MCP集成指南

- ✅ 快速开始指南
- ✅ MCP工具详细说明
- ✅ 架构设计原理
- ✅ 使用场景示例
- ✅ 开发和测试说明

### [CLAUDE_CODE_MCP_SETUP.md](./CLAUDE_CODE_MCP_SETUP.md)
**Claude Code MCP配置指南** - 详细的配置步骤

- ✅ 一键配置命令（poethepoet集成）
- ✅ 本地范围 vs 项目范围配置
- ✅ 手动配置方式
- ✅ 测试验证步骤
- ✅ 故障排除指南

### [MCP_CONFIG_GUIDE.md](./MCP_CONFIG_GUIDE.md)
**MCP服务器配置指南** - 技术配置细节

- ✅ poethepoet任务配置
- ✅ 多种启动方式
- ✅ pyproject.toml配置
- ✅ 项目目录要求
- ✅ 最佳实践建议

## 🚀 快速开始

### 1. 安装依赖
```bash
uv pip install -e .
```

### 2. 一键配置（推荐）
```bash
# 添加MCP服务器到Claude Code（本地范围）
uv run poe mcp-add-local

# 验证配置成功
uv run poe mcp-list
```

### 3. 测试功能
```bash
# 直接启动Claude Code测试
claude "查询招商银行的财务指标"
```

## 💡 核心功能

### MCP工具：`query_financial_indicators`

```python
# 查询关键指标
query_financial_indicators(symbol="600036")

# 按定字段查询，节省token
query_financial_indicators(
    symbol="00700",
    fields=["BASIC_EPS", "ROE_YEARLY"]
)

# 只要数据，不要元数据
query_financial_indicators(
    symbol="AAPL",
    include_metadata=False
)
```

## 🎯 技术特性

- ✅ **100%字段覆盖**：151个财务指标完全访问
- ✅ **按需过滤**：支持指定字段返回
- ✅ **跨市场支持**：A股、港股、美股
- ✅ **智能默认**：自动选择关键指标
- ✅ **极简设计**：150行核心代码
- ✅ **零配置**：开箱即用

## 🔧 架构设计

```
Claude Code → MCP协议 → AkshareMCPServer → 现有QueryService → akshare → 原始数据
```

**设计原则**：
- 单一职责：只做财务指标查询
- 直接复用：100%使用现有架构
- 标准协议：严格遵循MCP规范
- 零学习成本：直接使用现有股票代码

## 📝 相关文档

- [简化版使用指南](../SIMPLIFIED_USAGE_GUIDE.md)
- [项目架构文档](../../CLAUDE.md)
- [MCP协议规范](https://modelcontextprotocol.io/)

---

*极简设计，强大功能* - 让Claude Code轻松访问专业财务数据