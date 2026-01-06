import pytest
import pandas as pd
from src.akshare_value_investment.normalization.registry import FieldMappingRegistry
from src.akshare_value_investment.normalization.schema_normalizer import SchemaNormalizer
from src.akshare_value_investment.domain.models.financial_standard import StandardFields

@pytest.fixture
def mock_registry():
    """创建一个预配置的注册表"""
    registry = FieldMappingRegistry()
    registry.register_mapping(
        "a_stock", 
        StandardFields.TOTAL_REVENUE, 
        ["营业总收入", "一、营业总收入"]
    )
    registry.register_mapping(
        "a_stock",
        StandardFields.NET_INCOME,
        ["净利润"]
    )
    return registry

def test_normalizer_renames_columns_correctly(mock_registry):
    normalizer = SchemaNormalizer(mock_registry)
    
    # 模拟原始 A股数据 (包含别名和无关列)
    raw_df = pd.DataFrame({
        "一、营业总收入": [1000, 2000],
        "净利润": [100, 200],
        "无关字段": ["x", "y"]
    })
    
    std_df = normalizer.standardize(raw_df, "a_stock")
    
    # 验证列名已更改
    assert StandardFields.TOTAL_REVENUE in std_df.columns
    assert StandardFields.NET_INCOME in std_df.columns
    
    # 验证数据正确性 (Vectorization check)
    assert std_df[StandardFields.TOTAL_REVENUE].iloc[0] == 1000
    assert std_df[StandardFields.NET_INCOME].iloc[1] == 200

def test_normalizer_handles_empty_dataframe(mock_registry):
    normalizer = SchemaNormalizer(mock_registry)
    empty_df = pd.DataFrame()
    result = normalizer.standardize(empty_df, "a_stock")
    assert result.empty

def test_normalizer_preserves_unmapped_columns(mock_registry):
    """验证未映射的字段被保留（放入 extensions 的前置条件）"""
    normalizer = SchemaNormalizer(mock_registry)
    raw_df = pd.DataFrame({
        "一、营业总收入": [100],
        "特殊字段": [999]
    })
    
    std_df = normalizer.standardize(raw_df, "a_stock")
    
    assert StandardFields.TOTAL_REVENUE in std_df.columns
    assert "特殊字段" in std_df.columns # 未映射字段应保留
    assert std_df["特殊字段"].iloc[0] == 999

def test_normalizer_handles_none_input(mock_registry):
    normalizer = SchemaNormalizer(mock_registry)
    result = normalizer.standardize(None, "a_stock")
    assert isinstance(result, pd.DataFrame)
    assert result.empty