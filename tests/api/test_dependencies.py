"""
API依赖注入测试

TDD测试：验证FastAPI依赖注入与现有容器的集成
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

# 这个测试会先失败，因为我们还没有创建main.py和dependencies.py
def test_container_integration():
    """测试现有容器与FastAPI的集成"""
    # 这会先失败，因为还没有main.py
    from akshare_value_investment.api.main import create_app

    app = create_app()
    client = TestClient(app)

    # 测试健康检查端点（这个端点还没实现）
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "container" in data