import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.akshare_value_investment.datasource.queryers.a_stock_queryers import AStockIncomeStatementQueryer
from src.akshare_value_investment.normalization.registry import FieldMappingRegistry
from src.akshare_value_investment.normalization.schema_normalizer import SchemaNormalizer
from src.akshare_value_investment.domain.models.financial_standard import StandardFields

@pytest.fixture
def mock_akshare():
    with patch("akshare.stock_financial_benefit_ths") as mock:
        yield mock

@pytest.fixture
def configured_normalizer():
    registry = FieldMappingRegistry()
    registry.register_mapping(
        "a_stock", 
        StandardFields.TOTAL_REVENUE, 
        ["一、营业总收入"]
    )
    return SchemaNormalizer(registry)

def test_queryer_uses_normalizer(mock_akshare, configured_normalizer):
    # 1. 模拟 AkShare 返回原始数据
    mock_akshare.return_value = pd.DataFrame({
        "一、营业总收入": [5000],
        "无关列": [1]
    })
    
    # 2. 实例化 Queryer (注入 Normalizer)
    queryer = AStockIncomeStatementQueryer(
        cache=MagicMock(),
        schema_normalizer=configured_normalizer # 注入
    )
    
    # 3. 调用查询
    result = queryer.query("600519")
    df = result["data"]
    
    # 4. 验证结果 (应该是标准化后的)
    assert StandardFields.TOTAL_REVENUE in df.columns
    assert df[StandardFields.TOTAL_REVENUE].iloc[0] == 5000
    
    # 5. 验证原始列被替换或保留 (取决于是否做了 drop，目前策略是保留未映射列)
    assert "无关列" in df.columns
