# MCP服务器配置指南

## 🚀 通过poethepoet启动MCP服务器

项目已配置`poethepoet`任务管理器，提供便捷的MCP服务器启动方式。

### 📋 可用任务

```bash
# 查看所有可用任务
uv run poe --help

# 启动MCP服务器（用于Claude Code）
uv run poe mcp-server

# 运行测试
uv run poe test

# 运行演示程序
uv run poe demo

# 安装项目
uv run poe install

# 开发环境设置
uv run poe dev

# 健康检查
uv run poe check

# 验证MCP服务器（推荐）
uv run poe verify-mcp
```

## 🔧 Claude Code配置

### 方法1：使用poethepoet任务

在Claude Code的MCP配置中添加：

```json
{
  "mcpServers": {
    "akshare-value-investment": {
      "command": "uv",
      "args": [
        "run",
        "poe",
        "mcp-server"
      ],
      "cwd": "/path/to/akshare-value-investment"
    }
  }
}
```

### 方法2：直接启动

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
      ],
      "cwd": "/path/to/akshare-value-investment"
    }
  }
}
```

### 方法3：使用已安装的脚本

```json
{
  "mcpServers": {
    "akshare-value-investment": {
      "command": "akshare-mcp-server"
    }
  }
}
```

## ⚙️ pyproject.toml配置详情

```toml
[tool.poe.tasks]
# MCP服务器任务
mcp-server = "python -m akshare_value_investment.mcp_server"

# 基础任务
test = "pytest"
demo = "python examples/demo.py"
install = "pip install -e ."

# 开发任务组合
dev = ["install", "test"]
check = ["test", "mcp-server --help"]
```

## 🧪 测试配置

### 1. 测试MCP服务器是否能正常启动

```bash
# 测试导入
uv run python -c "from akshare_value_investment.mcp_server import AkshareMCPServer; print('✅ MCP服务器可以正常导入')"

# 测试poethepoet任务
uv run poe mcp-server
```

### 2. 在Claude Code中测试

配置完成后，在Claude Code中测试：

```
用户：查询招商银行的财务指标
Claude：[调用 query_financial_indicators(symbol="600036")]

用户：只查询腾讯的每股收益和ROE
Claude：[调用 query_financial_indicators(symbol="00700", fields=["BASIC_EPS", "ROE_YEARLY"])]
```

## 📁 项目目录要求

确保Claude Code能够找到项目：

- **完整路径**: `/Users/yapex/workspace/akshare-value-investment`
- **包含文件**: `pyproject.toml`, `src/akshare_value_investment/`
- **虚拟环境**: 项目目录下的`.venv/`或全局uv环境

## 🐛 故障排除

### 问题1：找不到poethepoet
```bash
# 解决方案：重新安装依赖
uv pip install -e .
```

### 问题2：MCP服务器启动失败
```bash
# 检查依赖
uv pip list | grep mcp

# 重新安装mcp
uv pip install mcp>=1.0.0
```

### 问题3：Claude Code无法连接
1. 确认工作目录路径正确
2. 确认uv环境可用
3. 检查MCP服务器能否独立启动
4. 查看Claude Code的错误日志

### 问题4：字段不存在错误
```bash
# 查看可用字段
uv run python -c "
from akshare_value_investment import create_production_service
result = create_production_service().query('600036')
if result.success:
    print('可用字段:', list(result.data[0].raw_data.keys()))
"
```

## 🎯 最佳实践

1. **使用poethepoet任务**：统一管理各种启动方式
2. **指定工作目录**：确保相对路径正确
3. **定期更新**：保持依赖包最新版本
4. **错误监控**：关注Claude Code的连接状态

## 📞 支持

如遇问题，请检查：
1. Python版本 >= 3.13
2. uv包管理器正常工作
3. 网络连接正常（访问akshare数据源）
4. Claude Code版本支持MCP