#!/bin/bash
# AKShare MCP 服务器启动脚本

set -e

echo "🚀 启动 AKShare Value Investment MCP 服务器"
echo "================================================"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python 环境"
    exit 1
fi

# 检查 uv 环境
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未找到 uv 包管理器"
    exit 1
fi

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 读取配置
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已加载环境配置"
fi

# 检查 FastAPI 服务是否运行
FASTAPI_URL=${AKSHARE_FASTAPI_URL:-http://localhost:8000}
echo "🔗 检查 FastAPI 服务: $FASTAPI_URL"

if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 3 "$FASTAPI_URL/health" > /dev/null 2>&1; then
        echo "✅ FastAPI 服务运行正常"
    else
        echo "⚠️  FastAPI 服务未运行，请先启动: poe api"
        read -p "是否继续启动 MCP 服务器? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  未找到 curl，跳过 FastAPI 服务检查"
fi

# 启动 MCP 服务器
echo "🎯 启动 MCP 服务器..."
echo "📡 监听地址: ${AKSHARE_MCP_HOST:-localhost}:${AKSHARE_MCP_PORT:-8080}"
echo "🔗 FastAPI 服务: $FASTAPI_URL"
echo "🐛 调试模式: ${AKSHARE_MCP_DEBUG:-false}"
echo "================================================"

# 使用 uv 运行 MCP 服务器
if [ "${AKSHARE_MCP_DEBUG:-false}" = "true" ]; then
    exec uv run poe mcp-debug
else
    exec uv run poe mcp
fi