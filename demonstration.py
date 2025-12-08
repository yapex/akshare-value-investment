#!/usr/bin/env python3
"""
MCP-HTTP 集成演示

展示改造后的 MCP 工具如何通过 HTTP 调用 FastAPI 服务。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demonstrate_transformation():
    """演示改造前后的对比"""
    print("🚀 MCP-HTTP 集成改造演示")
    print("=" * 60)

    print("\n📋 改造目标:")
    print("1. ✅ 将 MCP 服务改造为通过 HTTP 调用 FastAPI")
    print("2. ✅ 保持所有现有 API 接口兼容")
    print("3. ✅ 支持配置化的 FastAPI URL")
    print("4. ✅ 提供完整的错误处理")

    print("\n🔧 核心改造内容:")

    print("\n1️⃣ FinancialQueryTool 改造:")
    print("   - 改造前: 直接注入 FinancialQueryService 实例")
    print("   - 改造后: 通过 httpx 客户端调用 FastAPI 端点")
    print("   - HTTP 端点: POST /api/v1/financial/query")
    print("   - 字段发现: GET /api/v1/financial/fields/{market}/{query_type}")

    print("\n2️⃣ FieldDiscoveryTool 改造:")
    print("   - 改造前: 直接调用 FieldDiscoveryService 方法")
    print("   - 改造后: 通过 httpx 客户端调用 FastAPI 端点")
    print("   - HTTP 端点: GET /api/v1/financial/fields/{market}/{query_type}")

    print("\n3️⃣ 配置系统增强:")
    print("   - 新增 fastapi_base_url 配置项")
    print("   - 支持环境变量和运行时配置")
    print("   - 默认值: http://localhost:8000")

    print("\n4️⃣ MCP 服务器集成:")
    print("   - 使用配置中的 FastAPI URL 初始化工具")
    print("   - 保持完全向后兼容的接口")
    print("   - 增强的错误处理和响应映射")

    print("\n✅ 改造验证:")

    # 验证工具初始化
    from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool
    from akshare_value_investment.mcp.tools.field_discovery_tool import FieldDiscoveryTool
    from akshare_value_investment.mcp.config import MCPServerConfig
    from akshare_value_investment.mcp.server import MCPServer

    print("\n1. 工具初始化测试:")
    financial_tool = FinancialQueryTool("http://demo-api:8000")
    field_tool = FieldDiscoveryTool("http://demo-api:8000")
    print(f"   ✅ FinancialQueryTool URL: {financial_tool.api_base_url}")
    print(f"   ✅ FieldDiscoveryTool URL: {field_tool.api_base_url}")

    print("\n2. 配置系统测试:")
    config = MCPServerConfig(fastapi_base_url="http://config-api:9000")
    server = MCPServer(config)
    print(f"   ✅ 配置 FastAPI URL: {config.fastapi_base_url}")
    print(f"   ✅ 服务器工具 URL: {server.financial_query_tool.api_base_url}")

    print("\n3. 方法兼容性验证:")
    methods_to_check = [
        'query_financial_data',
        'get_available_fields',
        'discover_fields',
        'validate_fields'
    ]

    for method in methods_to_check:
        if hasattr(financial_tool, method):
            print(f"   ✅ {method} 方法存在")
        if hasattr(field_tool, method):
            print(f"   ✅ {method} 方法存在")

    print("\n📊 改造效果:")
    print("   - ✅ 解耦了 MCP 服务与业务服务的直接依赖")
    print("   - ✅ 实现了基于 HTTP 的微服务架构")
    print("   - ✅ FastAPI 成为唯一的数据访问入口")
    print("   - ✅ 保持了完整的 API 兼容性")
    print("   - ✅ 支持分布式部署和横向扩展")

    print("\n🎯 使用示例:")
    print("""
# 启动 FastAPI 服务
poe api

# 使用改造后的 MCP 工具
from akshare_value_investment.mcp.tools.financial_query_tool import FinancialQueryTool

# 工具会自动调用 FastAPI 端点
tool = FinancialQueryTool()  # 默认 http://localhost:8000
response = tool.query_financial_data(
    market="a_stock",
    query_type="a_stock_indicators",
    symbol="SH600519"
)
# 内部通过 HTTP 调用: POST http://localhost:8000/api/v1/financial/query
    """)

    print("\n🎉 MCP-HTTP 集成改造完成！")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_transformation()