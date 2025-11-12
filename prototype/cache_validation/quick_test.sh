#!/bin/bash
# 从项目根目录运行的快速测试脚本

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PROTOTYPE_DIR=$(cd "$(dirname "$0")" && pwd)

echo "🚀 从项目根目录运行缓存验证测试"
echo "📁 项目根目录: $PROJECT_ROOT"
echo "🧪 原型目录: $PROTOTYPE_DIR"
echo ""

cd "$PROJECT_ROOT"

echo "🧪 安装diskcache依赖..."
uv add diskcache

echo ""
echo "🚀 运行缓存验证测试..."
cd "$PROTOTYPE_DIR" && uv run python test_cache_performance.py