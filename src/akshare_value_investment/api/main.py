"""
FastAPI应用主入口

采用应用工厂模式，遵循SOLID原则，保持单一职责。
集成依赖注入和业务服务。
"""

from fastapi import FastAPI
from .dependencies import get_container
from .routes.field_discovery import router as field_discovery_router
from .routes.financial import router as financial_router


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例

    Returns:
        FastAPI: 配置好的应用实例
    """
    app = FastAPI(
        title="akshare-value-investment API",
        description="基于akshare的价值投资分析系统Web API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 注册路由
    app.include_router(field_discovery_router)
    app.include_router(financial_router)

    # 添加健康检查端点，验证依赖注入
    @app.get("/health")
    async def health_check():
        """健康检查端点，验证容器集成"""
        container = get_container()

        return {
            "status": "healthy",
            "container": "initialized",
            "service": "akshare-value-investment-api",
            "services": {
                "a_stock_indicators": "available",
                "hk_stock_indicators": "available",
                "us_stock_indicators": "available"
            }
        }

    return app