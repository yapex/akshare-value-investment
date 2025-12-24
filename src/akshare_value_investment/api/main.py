"""
FastAPI应用主入口

采用应用工厂模式，遵循SOLID原则，保持单一职责。
集成依赖注入和业务服务。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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

    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源（开发环境）
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有请求头
    )

    # 注册路由
    app.include_router(field_discovery_router)
    app.include_router(financial_router)

    # 根路径重定向到文档页面
    @app.get("/", include_in_schema=False)
    async def root():
        """根路径重定向到API文档"""
        return RedirectResponse(url="/docs")

    # 添加健康检查端点，验证依赖注入
    @app.get("/health")
    async def health_check():
        """健康检查端点，验证容器集成"""
        get_container()  # 验证容器可以正常初始化

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
