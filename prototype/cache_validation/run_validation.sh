#!/bin/bash
# 缓存验证测试脚本 - 使用uv运行

echo "🧪 安装依赖..."
uv add diskcache

echo ""
echo "🚀 运行缓存验证测试..."
uv run python test_cache_performance.py

echo ""
echo "📊 查看缓存目录..."
ls -la cache_data/ 2>/dev/null || echo "缓存目录未创建（首次运行）"

echo ""
echo "🗑️ 清理测试缓存..."
rm -rf cache_data/
echo "✅ 清理完成"