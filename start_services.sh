#!/bin/bash
# 启动脚本：同时启动FastAPI和Streamlit服务

echo "🚀 启动AK投资分析服务..."
echo ""

# 启动FastAPI服务（后台）
echo "1️⃣ 启动FastAPI服务 (端口8000)..."
PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# 等待FastAPI启动
echo "⏳ 等待FastAPI服务启动..."
sleep 5

# 检查FastAPI是否成功启动
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ FastAPI服务启动成功"
else
    echo "❌ FastAPI服务启动失败"
    kill $FASTAPI_PID 2>/dev/null
    exit 1
fi

# 启动Streamlit服务
echo ""
echo "2️⃣ 启动Streamlit应用 (端口8501)..."
cd webapp
PYTHONPATH=../src uv run streamlit run app.py --server.port 8501

# Streamlit退出时清理FastAPI进程
echo ""
echo "🛑 正在停止服务..."
kill $FASTAPI_PID 2>/dev/null
echo "✅ 所有服务已停止"
