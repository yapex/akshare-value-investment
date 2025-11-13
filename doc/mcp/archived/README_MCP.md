# akshare-value-investment MCP 服务器

基于现有简化版架构的极简MCP实现，让Claude Code能够查询财务指标数据。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装MCP依赖
uv pip install -e .
```

### 2. 测试MCP服务器

```bash
# 直接测试MCP服务器
uv run python -m akshare_value_investment.mcp_server
```

### 3. 在Claude Code中使用

将以下配置添加到Claude Code的MCP配置中：

```json
{
  "mcpServers": {
    "akshare-value-investment": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "akshare_value_investment.mcp_server"
      ]
    }
  }
}
```

## 📋 MCP工具

### `query_financial_indicators`

查询股票财务指标数据，支持按需过滤字段。

**参数**：
- `symbol` (必需): 股票代码
  - A股：6位数字，如 `600036`
  - 港股：5位数字，如 `00700`
  - 美股：英文字母，如 `AAPL`
- `fields` (可选): 需要返回的字段名列表
  - 如不指定，返回关键字段（每股收益、ROE等5个指标）
  - 指定字段：`["摊薄每股收益(元)", "净资产收益率(%)"]`
- `include_metadata` (可选): 是否包含元数据，默认`true`

**示例**：
```python
# 查询招商银行的关键指标
query_financial_indicators(symbol="600036")

# 查询指定字段，节省token
query_financial_indicators(
    symbol="600036",
    fields=["摊薄每股收益(元)", "净资产收益率(%)", "净利润"]
)

# 只要数据，不要元数据
query_financial_indicators(
    symbol="00700",
    fields=["BASIC_EPS", "ROE_YEARLY"],
    include_metadata=False
)
```

## 🏗️ 架构设计

### 极简设计原则

- **单一职责**：只做财务指标查询，不做复杂NLP处理
- **直接复用**：100%复用现有的`create_production_service()`
- **零配置**：开箱即用，无需额外配置
- **标准协议**：严格遵循MCP协议规范

### 核心特性

- ✅ **100%字段覆盖**：继承151个财务指标的完整覆盖
- ✅ **按需过滤**：支持指定字段返回，节省LLM token
- ✅ **跨市场支持**：A股、港股、美股三市场
- ✅ **智能默认**：自动返回各市场关键字段（5个核心指标）
- ✅ **简化设计**：一个工具函数，清晰直接
- ✅ **零学习成本**：直接使用现有股票代码格式

## 💡 使用场景

在Claude Code中，你可以这样使用：

```
用户：帮我查询招商银行(600036)的财务指标
Claude：我来为你查询招商银行的财务数据。
[调用 query_financial_indicators(symbol="600036")]

用户：我只需要腾讯的每股收益和ROE
Claude：我来查询腾讯控股的每股收益和ROE数据。
[调用 query_financial_indicators(symbol="00700", fields=["BASIC_EPS", "ROE_YEARLY"])]

用户：比较一下腾讯和阿里巴巴的ROE，只要数据
Claude：我来查询腾讯和阿里巴巴的ROE数据。
[调用 query_financial_indicators(symbol="00700", fields=["ROE_YEARLY"], include_metadata=False)]
[调用 query_financial_indicators(symbol="09988", fields=["ROE_YEARLY"], include_metadata=False)]
```

## 🔧 开发说明

### 文件结构

```
src/akshare_value_investment/
├── mcp_server.py           # MCP服务器主文件
├── interfaces.py           # 现有Protocol接口
├── adapters.py             # 现有市场适配器
├── query_service.py        # 现有查询服务
└── models.py              # 现有数据模型
```

### 依赖关系

- `mcp>=1.0.0` - MCP协议支持
- `akshare>=1.17.83` - 财务数据源
- `dependency-injector>=4.48.2` - 依赖注入框架

### 核心代码

MCP服务器只有150行代码，核心逻辑：

```python
# 1. 创建MCP服务器
self.server = Server("akshare-value-investment")

# 2. 复用现有查询服务
self.query_service = create_production_service()

# 3. 定义一个工具
Tool(
    name="query_financial_indicators",
    description="查询股票财务指标数据",
    inputSchema={"properties": {"symbol": {"type": "string"}}}
)

# 4. 直接调用现有服务
result = self.query_service.query(symbol)
```

## 🧪 测试

```bash
# 运行现有测试（确保基础功能正常）
uv run pytest tests/

# 测试MCP服务器启动
uv run python -c "from akshare_value_investment.mcp_server import AkshareMCPServer; print('MCP服务器加载成功')"
```

## 📝 相关文档

- [简化版使用指南](./doc/SIMPLIFIED_USAGE_GUIDE.md)
- [项目架构文档](./CLAUDE.md)
- [MCP协议规范](https://modelcontextprotocol.io/)

---

*极简设计，强大功能* - 让Claude Code轻松访问专业财务数据