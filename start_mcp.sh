#!/bin/bash
# AKShare MCP 服务器启动脚本 (HTTP客户端架构)

set -e

echo "🚀 启动 AKShare Value Investment MCP 服务器 (v3.1.0)"
echo "================================================"
echo "📋 架构: HTTP客户端 → FastAPI服务"

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

# 配置默认值
FASTAPI_URL=${AKSHARE_FASTAPI_URL:-http://localhost:8000}
MCP_HOST=${AKSHARE_MCP_HOST:-localhost}
MCP_PORT=${AKSHARE_MCP_PORT:-8080}
MCP_DEBUG=${AKSHARE_MCP_DEBUG:-false}

echo "🔗 FastAPI 服务地址: $FASTAPI_URL"
echo "📡 MCP监听地址: $MCP_HOST:$MCP_PORT"
echo "🐛 MCP调试模式: $MCP_DEBUG"

# 检查 FastAPI 服务是否运行 (重要：MCP依赖FastAPI)
echo ""
echo "🔍 检查 FastAPI 服务依赖..."

if command -v curl &> /dev/null; then
    if curl -s --connect-timeout 5 "$FASTAPI_URL/health" > /dev/null 2>&1; then
        echo "✅ FastAPI 服务运行正常"
        echo "📊 服务状态: $(curl -s "$FASTAPI_URL/health" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data.get('status', 'unknown')} ({data.get('service', 'unknown')})\")")"
    else
        echo "❌ FastAPI 服务未运行或不可访问"
        echo ""
        echo "📋 启动要求:"
        echo "   1. 必须先启动 FastAPI 服务: poe api"
        echo "   2. 确保服务运行在: $FASTAPI_URL"
        echo ""
        echo "🔄 自动尝试启动 FastAPI 服务..."
        echo ""

        # 尝试启动 FastAPI 服务
        if command -v poe &> /dev/null; then
            echo "🚀 启动 FastAPI 服务..."
            # 在后台启动 FastAPI，等待几秒
            nohup poe api > /tmp/fastapi.log 2>&1 &
            FASTAPI_PID=$!
            echo "📋 FastAPI 进程ID: $FASTAPI_PID"

            # 等待服务启动
            echo "⏳ 等待 FastAPI 服务启动..."
            sleep 8

            # 检查服务是否成功启动
            if curl -s --connect-timeout 3 "$FASTAPI_URL/health" > /dev/null 2>&1; then
                echo "✅ FastAPI 服务启动成功"
            else
                echo "❌ FastAPI 服务启动失败"
                echo "📋 请检查日志: tail -f /tmp/fastapi.log"
                kill $FASTAPI_PID 2>/dev/null || true
                exit 1
            fi
        else
            echo "❌ 未找到 poe 命令，请手动启动 FastAPI 服务"
            echo "💡 手动启动: uvicorn akshare_value_investment.api.main:create_app --reload"
            exit 1
        fi
    fi
else
    echo "⚠️  未找到 curl，跳过 FastAPI 服务检查"
    echo "💡 请确保 FastAPI 服务运行在: $FASTAPI_URL"
fi

# 显示架构信息
echo ""
echo "🏗️  MCP架构信息:"
echo "   - MCP服务器: 协议适配层 (HTTP客户端)"
echo "   - FastAPI服务: 核心业务服务"
echo "   - 数据流向: MCP → HTTP → FastAPI → SQLite缓存"
echo ""

# 启动 MCP 服务器
echo "🎯 启动 MCP 服务器..."
echo "================================================"

# 准备启动命令
MCP_CMD="uv run poe mcp"
if [ "$MCP_DEBUG" = "true" ]; then
    MCP_CMD="uv run poe mcp-debug"
    echo "🐛 调试模式已启用"
fi

echo "🚀 执行命令: $MCP_CMD"
echo ""

# 启动 MCP 服务器
exec $MCP_CMD