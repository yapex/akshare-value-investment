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

# 检查FastAPI服务
echo ""
echo "📡 检测FastAPI服务状态..."
if check_fastapi; then
    echo "✅ FastAPI服务已在运行 (端口8000)"
    echo ""
    read -p "💡 是否重启FastAPI服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 查找并停止现有的FastAPI进程
        FASTAPI_PIDS=$(lsof -ti:8000 2>/dev/null)
        if [ -n "$FASTAPI_PIDS" ]; then
            echo "🛑 停止现有FastAPI服务..."
            kill $FASTAPI_PIDS 2>/dev/null
            sleep 2
        fi

        # 启动新的FastAPI服务
        echo "🚀 启动FastAPI服务..."
        PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
        FASTAPI_PID=$!
        FASTAPI_STARTED_BY_SCRIPT=true

        # 等待FastAPI启动
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
        FASTAPI_PID=""
        FASTAPI_STARTED_BY_SCRIPT=false
    fi
else
    echo "❌ FastAPI服务未运行，正在启动..."
    PYTHONPATH=src uv run uvicorn akshare_value_investment.api.main:create_app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    FASTAPI_PID=$!
    FASTAPI_STARTED_BY_SCRIPT=true

    # 等待FastAPI启动
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

# 检查Streamlit服务
echo ""
echo "📊 检测Streamlit服务状态..."
if check_streamlit; then
    echo "⚠️  Streamlit服务已在运行 (端口8501)"
    echo ""
    read -p "💡 是否重启Streamlit服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 查找并停止现有的Streamlit进程
        STREAMLIT_PIDS=$(lsof -ti:8501 2>/dev/null)
        if [ -n "$STREAMLIT_PIDS" ]; then
            echo "🛑 停止现有Streamlit服务..."
            kill $STREAMLIT_PIDS 2>/dev/null
            sleep 1
        fi

        # 启动新的Streamlit服务
        echo "🚀 启动Streamlit应用..."
        cd webapp
        PYTHONPATH=../src uv run streamlit run app.py --server.port 8501
    else
        echo "ℹ️  保持现有Streamlit服务运行"
        echo ""
        echo "💡 提示: Web应用已在运行"
        echo "   访问地址: http://localhost:8501"

        # 如果FastAPI是本脚本启动的，询问是否保持运行
        if [ "$FASTAPI_STARTED_BY_SCRIPT" = true ] && [ -n "$FASTAPI_PID" ]; then
            echo ""
            read -p "FastAPI服务由本脚本启动，是否停止? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "🛑 停止FastAPI服务..."
                kill $FASTAPI_PID 2>/dev/null
                echo "✅ FastAPI服务已停止"
            else
                echo "ℹ️  FastAPI服务将继续在后台运行"
                echo "   停止命令: kill $FASTAPI_PID"
            fi
        fi
    fi
else
    # 启动Streamlit服务
    echo "🚀 启动Streamlit应用..."
    cd webapp
    PYTHONPATH=../src uv run streamlit run app.py --server.port 8501

    # Streamlit退出时的清理逻辑
    echo ""
    echo "========================================"
    echo "🛑 Streamlit服务已停止"

    # 如果FastAPI是由本脚本启动的，则停止它
    if [ "$FASTAPI_STARTED_BY_SCRIPT" = true ] && [ -n "$FASTAPI_PID" ]; then
        echo "🛑 停止FastAPI服务 (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID 2>/dev/null
        echo "✅ 所有服务已停止"
    else
        echo "ℹ️  FastAPI服务继续运行（非本脚本启动）"
    fi
fi
echo ""
