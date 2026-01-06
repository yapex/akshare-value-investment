import pytest
from src.akshare_value_investment.normalization.registry import FieldMappingRegistry

def test_registry_register_and_get():
    registry = FieldMappingRegistry()
    
    # 注册映射
    registry.register_mapping("a_stock", "total_revenue", ["营业总收入", "一、营业总收入"])
    
    # 检索映射
    mapping = registry.get_mapping("a_stock")
    assert mapping["营业总收入"] == "total_revenue"
    assert mapping["一、营业总收入"] == "total_revenue"

def test_registry_empty_for_unknown_market():
    registry = FieldMappingRegistry()
    assert registry.get_mapping("non_existent") == {}

def test_registry_overwrite_protection():
    registry = FieldMappingRegistry()
    registry.register_mapping("a_stock", "f1", ["raw1"])
    registry.register_mapping("a_stock", "f2", ["raw1"]) # 同一个原始字段映射到不同的标准字段
    
    mapping = registry.get_mapping("a_stock")
    assert mapping["raw1"] == "f2" # 允许后来的覆盖
