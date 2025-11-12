# akshare-value-investment 项目全面概览

## 项目状态更新时间
2025-11-11

## 🎯 项目愿景与定位

**核心目标**：基于 akshare 的价值投资分析系统，提供跨市场（A股、港股、美股）财务指标原始数据访问功能

**设计理念**：简化优先，专注原始数据访问，100%字段覆盖率，避免过度设计

## 🏗️ 当前架构状态 - 简化版生产就绪

### 核心设计原则
1. **简化设计**：直接返回akshare原始数据，不进行字段映射
2. **完整覆盖**：用户可访问所有原始字段（A股86个，港股36个，美股49个）
3. **优雅架构**：保留依赖注入和Protocol接口的优秀设计
4. **易于使用**：通过`FinancialIndicator.raw_data`直接访问任意字段

### 项目目录结构
```
akshare-value-investment/
├── src/akshare_value_investment/     # 核心模块
│   ├── core/                         # 核心组件
│   │   ├── models.py                 # 数据模型（FinancialIndicator, QueryResult等）
│   │   ├── interfaces.py             # Protocol接口定义
│   │   └── stock_identifier.py       # 股票市场识别
│   ├── services/                     # 业务服务层
│   │   ├── financial_query_service.py # 财务查询服务
│   │   └── field_discovery_service.py # 字段发现服务
│   ├── container.py                  # 依赖注入容器
│   └── mcp_server.py                 # MCP服务器（已重构函数名）
├── examples/                         # 示例代码
│   └── demo.py                       # 简化版演示
├── tests/                            # 测试套件
├── doc/                              # 文档系统
│   └── SIMPLIFIED_USAGE_GUIDE.md     # 简化版使用指南
└── .mcp.json                         # MCP配置文件
```

## 🔧 技术栈与工具

### 核心技术
- **Python 3.13+** - 现代Python特性
- **uv** - 快速包管理器
- **akshare >= 1.0.0** - 财务数据源
- **dependency-injector >= 4.0.0** - 依赖注入框架
- **MCP (Model Context Protocol)** - Claude Code集成

### 架构模式
- **依赖注入** - 使用 dependency-injector 容器
- **Protocol接口** - I前缀命名，最小化设计
- **数据模型** - dataclass + Decimal精确计算
- **服务分层** - 清晰的业务逻辑分离

## 📊 核心功能特性

### 1. 跨市场数据访问
- **A股市场**：86个原始字段，100%覆盖
- **港股市场**：36个原始字段，100%覆盖  
- **美股市场**：49个原始字段，100%覆盖

### 2. 原始数据访问模式
```python
# 核心访问模式
result = service.query("600036")  # 招商银行
if result.success and result.data:
    latest = result.data[0]
    # 直接访问原始字段
    raw_fields = list(latest.raw_data.keys())
    eps = latest.raw_data.get("摊薄每股收益(元)")
```

### 3. MCP集成工具
**最新重构状态**：
- `query_financial_indicators` - 智能查询股票财务指标（已重命名）
- `search_financial_fields` - 搜索财务指标字段
- `get_field_details` - 获取财务指标详细信息

## 🧪 测试覆盖情况

### 测试统计
- **总测试数**：19个测试用例，100%通过
- **核心测试**：模型测试(5个)、股票识别(6个)、原始数据访问(8个)
- **无跳过测试**：所有测试都与简化版功能相关

### 测试覆盖范围
- 数据模型验证
- 股票市场识别逻辑
- 原始数据访问功能
- MCP工具功能

## 📈 性能表现

### 字段覆盖率对比
| 股票 | 市场字段数 | 简化版覆盖率 | 原版本覆盖率 |
|------|-----------|-------------|-------------|
| 招商银行 | 86个字段 | 100% | ~11% |
| 腾讯控股 | 36个字段 | 100% | ~30% |
| 苹果 | 49个字段 | 100% | ~20% |

## 🔄 最新变更记录

### 2025-11-11 函数重构
- **重构内容**：`query_financial_data` → `query_financial_indicators`
- **重构原因**：原函数名过于宽泛，新名称更精确地体现财务指标查询功能
- **影响位置**：5处代码更新（工具定义、路由判断、处理方法等）
- **验证结果**：语法检查通过，功能测试正常

### 项目演进历程
1. **复杂架构阶段**：完整字段映射系统（已归档）
2. **简化重构阶段**：移除字段映射，专注原始数据
3. **生产就绪阶段**：100%字段覆盖，稳定运行
4. **持续优化阶段**：函数重命名，代码质量提升

## 🚀 使用方式

### 基本查询
```bash
# 运行简化版演示
uv run python examples/demo.py

# 运行测试
uv run pytest tests/
```

### MCP集成
```json
{
  "mcpServers": {
    "akshare-value-investment": {
      "command": "uv",
      "args": ["run", "python", "-m", "akshare_value_investment.mcp_server"]
    }
  }
}
```

## 🎯 项目优势

1. **简化优先**：避免过度设计，专注核心功能
2. **数据完整性**：100%字段覆盖率，无数据丢失
3. **架构优雅**：保留优秀设计模式，易于扩展
4. **生产就绪**：完整测试覆盖，稳定运行
5. **用户友好**：直接访问原始数据，使用灵活

## 📋 总结

akshare-value-investment项目已完成简化版重构，实现了：

- **架构简化**：移除复杂字段映射，专注原始数据访问
- **功能完整**：跨市场财务指标查询，100%字段覆盖
- **质量保证**：19个测试用例全部通过，代码质量优秀
- **集成完善**：MCP服务器集成，Claude Code直接调用
- **文档齐全**：详细使用指南和API文档

项目已达到生产就绪状态，为价值投资分析提供可靠的财务数据基础。