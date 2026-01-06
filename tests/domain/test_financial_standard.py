from src.akshare_value_investment.domain.models.financial_standard import StandardFields

def test_standard_fields_definition():
    """验证核心财务字段已定义且唯一"""
    # 利润表字段
    assert hasattr(StandardFields, "NET_INCOME")
    assert hasattr(StandardFields, "INCOME_TAX")
    assert hasattr(StandardFields, "INTEREST_EXPENSE")
    assert hasattr(StandardFields, "TOTAL_REVENUE")
    
    # 资产负债表字段
    assert hasattr(StandardFields, "TOTAL_EQUITY")
    assert hasattr(StandardFields, "TOTAL_ASSETS")
    assert hasattr(StandardFields, "SHORT_TERM_DEBT")
    assert hasattr(StandardFields, "LONG_TERM_DEBT")
    
    # 时间字段
    assert hasattr(StandardFields, "REPORT_DATE")

def test_standard_fields_values_are_unique():
    """验证所有字段的值是唯一的，避免重叠"""
    fields = [
        getattr(StandardFields, attr) 
        for attr in dir(StandardFields) 
        if not attr.startswith("__")
    ]
    assert len(fields) == len(set(fields))
