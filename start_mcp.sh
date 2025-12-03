#!/bin/bash

# akshare-value-investment MCP 服务启动脚本
set -e

# 设置环境变量
export PYTHONPATH="/Users/yapex/workspace/akshare-value-investment/src"
export PYTHONUNBUFFERED=1

# 切换到项目目录
cd "/Users/yapex/workspace/akshare-value-investment"

# 启动 MCP 服务
exec "/Users/yapex/workspace/akshare-value-investment/.venv/bin/python" \
    -m akshare_value_investment.mcp \
    --stdio