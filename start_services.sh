#!/bin/bash
# 启动脚本：智能检测并启动FastAPI和Streamlit服务

echo "🚀 AK投资分析服务启动脚本"
echo "========================================"

# 检测FastAPI服务是否已运行
check_fastapi() {
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        return 0  # 服务已运行
    else
        return 1  # 服务未运行
    fi
}

# 检测Streamlit服务是否已运行
check_streamlit() {
    if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口已被占用
    else
        return 1  # 端口空闲
    fi
}

# 显示服务信息和停止命令
show_service_info() {
    echo ""
    echo "========================================"
    echo "📋 服务信息"
    echo "========================================"
    echo ""
    echo "🌐 Web应用: http://localhost:8501"
    echo "📡 API文档: http://localhost:8000/docs"
    echo ""
    echo "🛑 停止服务命令："
    echo "   # 停止 FastAPI"
    echo "   lsof -ti:8000 | xargs kill"
    echo ""
    echo "   # 停止 Streamlit"
    echo "   lsof -ti:8501 | xargs kill"
    echo ""
    echo "   # 或者使用端口查找"
    echo "   lsof -i:8000  # 查看 FastAPI 进程"
    echo "   lsof -i:8501  # 查看 Streamlit 进程"
    echo ""
    echo "========================================"
}

# ==================== FastAPI 服务处理 ====================
echo ""
echo "📡 检测FastAPI服务状态..."
if check_fastapi; then
    echo "✅ FastAPI服务已在运行 (端口8000)"
    echo ""
    read -p "💡 是否重启FastAPI服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止现有FastAPI服务..."
        FASTAPI_PIDS=$(lsof -ti:8000 2>/dev/null)
        if [ -n "$FASTAPI_PIDS" ]; then
            kill $FASTAPI_PIDS 2>/dev/null
            sleep 2
        fi

        echo "🚀 启动FastAPI服务..."
        PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
        FASTAPI_PID=$!

        echo "⏳ 等待FastAPI服务启动..."
        for i in {1..10}; do
            if check_fastapi; then
                echo "✅ FastAPI服务启动成功 (PID: $FASTAPI_PID)"
                break
            fi
            if [ $i -eq 10 ]; then
                echo "❌ FastAPI服务启动失败"
                exit 1
            fi
            sleep 1
        done
    else
        echo "ℹ️  保持现有FastAPI服务运行"
    fi
else
    echo "❌ FastAPI服务未运行，正在启动..."
    PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    FASTAPI_PID=$!

    echo "⏳ 等待FastAPI服务启动..."
    for i in {1..10}; do
        if check_fastapi; then
            echo "✅ FastAPI服务启动成功 (PID: $FASTAPI_PID)"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ FastAPI服务启动失败"
            exit 1
        fi
        sleep 1
    done
fi

# ==================== Streamlit 服务处理 ====================
echo ""
echo "📊 检测Streamlit服务状态..."
if check_streamlit; then
    echo "⚠️  Streamlit服务已在运行 (端口8501)"
    echo ""
    read -p "💡 是否重启Streamlit服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止现有Streamlit服务..."
        STREAMLIT_PIDS=$(lsof -ti:8501 2>/dev/null)
        if [ -n "$STREAMLIT_PIDS" ]; then
            kill $STREAMLIT_PIDS 2>/dev/null
            sleep 1
        fi

        echo "🚀 启动Streamlit应用..."
        cd webapp
        PYTHONPATH=../src uv run streamlit run app.py --server.port 8501
    else
        echo "ℹ️  保持现有Streamlit服务运行"
        echo ""
        show_service_info
        exit 0
    fi
else
    echo "🚀 启动Streamlit应用..."
    cd webapp
    PYTHONPATH=../src uv run streamlit run app.py --server.port 8501
fi

# Streamlit退出后显示信息
echo ""
echo "========================================"
echo "🛑 Streamlit服务已停止"
show_service_info
