# Claude Code MCP配置指南

## 🚀 通过命令行配置MCP服务器

项目已集成`poethepoet`任务，提供一键配置Claude Code MCP服务器的命令。

### 📋 可用配置命令

```bash
# 查看所有可用任务
uv run poe --help

# 添加MCP服务器到Claude Code (本地范围 - 推荐)
uv run poe mcp-add-local

# 添加MCP服务器到Claude Code (项目范围)
uv run poe mcp-add-project

# 移除MCP服务器
uv run poe mcp-remove

# 列出所有已配置的MCP服务器
uv run poe mcp-list

# 获取akshare-value-investment MCP服务器详情
uv run poe mcp-get

# 验证MCP服务器功能正常
uv run poe verify-mcp
```

## 🎯 推荐配置步骤

### 1. 添加MCP服务器（推荐本地范围）

```bash
# 添加到本地配置，对当前用户所有项目有效
uv run poe mcp-add-local
```

### 2. 验证配置成功

```bash
# 查看是否添加成功
uv run poe mcp-list

# 应该能看到类似输出：
# context7: npx -y @upstash/context7-mcp@latest - ✓ Connected
# akshare-value-investment: uv run poe mcp-server - ✓ Connected  # ← 这行
# ...
```

### 3. 测试MCP功能

```bash
# 直接启动Claude Code测试
claude "查询招商银行的财务指标"
```

## 🔧 配置详解

### 本地范围 vs 项目范围

**本地范围（推荐）**：
```bash
uv run poe mcp-add-local
```
- 对当前用户的所有Claude Code会话有效
- 配保存在用户配置目录
- 一次配置，永久使用

**项目范围**：
```bash
uv run poe mcp-add-project
```
- 仅对当前项目目录有效
- 配置保存在项目的`.mcp.json`文件
- 适合项目特定的MCP服务器

### 手动配置方式

如果不使用poethepoet任务，也可以直接使用Claude Code命令：

```bash
# 本地范围配置
claude mcp add --scope local --transport stdio akshare-value-investment -- uv run poe mcp-server

# 项目范围配置
claude mcp add --scope project --transport stdio akshare-value-investment -- uv run poe mcp-server
```

## 🧪 测试和验证

### 1. 验证MCP服务器可运行

```bash
uv run poe verify-mcp
# 输出：✅ MCP服务器验证通过
```

### 2. 验证Claude Code配置

```bash
uv run poe mcp-list
# 检查列表中是否包含 akshare-value-investment
```

### 3. 功能测试

在Claude Code中测试以下查询：

```
用户：查询招商银行(600036)的财务指标
期望：返回招商银行的关键财务指标

用户：只查询腾讯的每股收益和ROE
期望：使用fields参数过滤返回

用户：比较苹果和微软的净利润，只要数据
期望：使用include_metadata=false减少token
```

## 🐛 故障排除

### 问题1：MCP服务器添加失败

```bash
# 检查poethepoet任务是否正确配置
uv run poe --help | grep mcp

# 手动验证MCP服务器
uv run python -c "from akshare_value_investment.mcp_server import AkshareMCPServer; print('✅')"
```

### 问题2：Claude Code无法连接MCP

```bash
# 检查MCP服务器状态
uv run poe mcp-list

# 重新添加MCP服务器
uv run poe mcp-remove
uv run poe mcp-add-local
```

### 问题3：查询返回错误

```bash
# 验证基础功能
uv run python examples/demo.py

# 检查akshare数据连接
uv run python -c "
from akshare_value_investment import create_production_service
result = create_production_service().query('600036')
print('Success:', result.success)
if result.success:
    print('Fields:', len(result.data[0].raw_data))
"
```

## 🔄 配置管理

### 查看当前配置
```bash
uv run poe mcp-get
```

### 更新配置
```bash
# 先移除旧配置
uv run poe mcp-remove

# 再添加新配置
uv run poe mcp-add-local
```

### 重置配置
```bash
# 重置项目范围内的MCP选择
claude mcp reset-project-choices
```

## 📁 配置文件位置

- **本地配置**: `~/.config/claude-code/mcp-servers.json`
- **项目配置**: `.mcp.json` (项目根目录)

## 🎉 完成后的效果

配置成功后，您可以在Claude Code中：

1. **自然语言查询财务数据**
2. **按需过滤字段，节省token**
3. **跨市场数据访问**（A股、港股、美股）
4. **智能默认指标**（自动选择关键财务指标）

示例对话：
```
用户：帮我分析一下贵州茅台的盈利能力
Claude：[调用MCP查询茅台的每股收益、ROE、毛利率等指标]
用户：再对比一下五粮液的数据
Claude：[调用MCP查询五粮液的相同指标进行对比]
```

现在您可以使用`uv run poe mcp-add-local`一键配置完成！