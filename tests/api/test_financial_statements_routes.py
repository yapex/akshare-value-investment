"""
财务三表聚合查询API路由测试

测试/api/v1/financial/statements端点功能。
"""

import pytest
from fastapi.testclient import TestClient
from akshare_value_investment.api.main import create_app


class TestFinancialStatementsRoutes:
    """财务三表聚合查询路由测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        return TestClient(app)

    def test_a_financial_statements_success(self, client):
        """测试A股财务三表聚合查询成功"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "a_financial_statements",
                "symbol": "SH600519",
                "frequency": "annual",
                "limit": 3
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "metadata" in data

        # 验证三表数据结构
        statements = ["balance_sheet", "income_statement", "cash_flow"]
        for statement in statements:
            assert statement in data["data"]
            assert "columns" in data["data"][statement]
            assert "data" in data["data"][statement]
            assert "record_count" in data["data"][statement]

        # 验证元数据
        metadata = data["metadata"]
        assert metadata["symbol"] == "SH600519"
        assert metadata["query_type"] == "A股财务三表"
        assert metadata["frequency"] == "年度数据"
        assert metadata["limit"] == 3
        assert "record_counts" in metadata

    def test_hk_financial_statements_success(self, client):
        """测试港股财务三表聚合查询成功"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "hk_financial_statements",
                "symbol": "00700",
                "frequency": "annual",
                "limit": 2
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["metadata"]["symbol"] == "00700"
        assert data["metadata"]["query_type"] == "港股财务三表"

    def test_us_financial_statements_success(self, client):
        """测试美股财务三表聚合查询成功"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "us_financial_statements",
                "symbol": "AAPL",
                "frequency": "annual",
                "limit": 2
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["metadata"]["symbol"] == "AAPL"
        assert data["metadata"]["query_type"] == "美股财务三表"

    def test_financial_statements_invalid_query_type(self, client):
        """测试无效查询类型"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "a_stock_indicators",  # 非聚合查询类型
                "symbol": "SH600519",
                "frequency": "annual"
            }
        )

        assert response.status_code == 400

        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["type"] == "invalid_query_type"

    def test_financial_statements_missing_required_fields(self, client):
        """测试缺少必填字段"""
        # 缺少query_type
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "symbol": "SH600519",
                "frequency": "annual"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_financial_statements_invalid_limit(self, client):
        """测试无效的limit参数"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "a_financial_statements",
                "symbol": "SH600519",
                "frequency": "annual",
                "limit": 0  # limit必须>=1
            }
        )

        assert response.status_code == 422  # Validation error

    def test_financial_statements_quarterly_frequency(self, client):
        """测试季度数据频率"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "a_financial_statements",
                "symbol": "SH600519",
                "frequency": "quarterly",
                "limit": 5
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["metadata"]["frequency"] == "报告期数据"

    def test_financial_statements_without_limit(self, client):
        """测试不指定limit参数"""
        response = client.post(
            "/api/v1/financial/statements",
            json={
                "query_type": "a_financial_statements",
                "symbol": "SH600519",
                "frequency": "annual"
                # 不指定limit
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["metadata"]["limit"] is None


class TestStatementsFieldDiscovery:
    """测试财务三表聚合字段发现"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = create_app()
        return TestClient(app)

    def test_a_financial_statements_field_discovery(self, client):
        """测试A股财务三表字段发现"""
        response = client.get(
            "/api/v1/financial/fields/a_stock/a_financial_statements"
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

        # 验证三张表的字段信息
        statements = ["balance_sheet", "income_statement", "cash_flow"]
        for statement in statements:
            assert statement in data["data"]
            assert "columns" in data["data"][statement]
            assert "field_count" in data["data"][statement]

        # 验证元数据
        assert data["metadata"]["market"] == "a_stock"
        assert data["metadata"]["query_type"] == "A股财务三表"
        assert "sample_symbol" in data["metadata"]

    def test_hk_financial_statements_field_discovery(self, client):
        """测试港股财务三表字段发现"""
        response = client.get(
            "/api/v1/financial/fields/hk_stock/hk_financial_statements"
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["metadata"]["sample_symbol"] == "00700"

    def test_us_financial_statements_field_discovery(self, client):
        """测试美股财务三表字段发现"""
        response = client.get(
            "/api/v1/financial/fields/us_stock/us_financial_statements"
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["metadata"]["sample_symbol"] == "AAPL"
