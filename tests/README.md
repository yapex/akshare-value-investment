# 测试文档

## pytest 配置和 Fixtures

本测试目录使用 pytest 作为测试框架，通过 `conftest.py` 提供共享的 fixtures。

### 主要 Fixtures

- `mock_loader`: Session 级别的 MockDataLoader，提供测试数据
- `sample_data_info`: 样本数据信息摘要
- 各种测试数据 fixtures: `a_stock_indicators_data`, `hk_stock_indicators_data` 等

### 使用示例

```python
import pytest

def test_example(mock_loader):
    """使用 mock_loader fixture"""
    data = mock_loader.get_a_stock_indicators_mock()
    assert len(data) > 0

@pytest.fixture
def custom_data(mock_loader):
    """创建自定义 fixture"""
    return mock_loader.get_a_stock_balance_sheet_mock(symbol="SZ000001")

def test_with_custom_data(custom_data):
    """使用自定义 fixture"""
    assert not custom_data.empty
```

### 测试标记

- `@pytest.mark.slow`: 标记慢速测试
- `@pytest.mark.integration`: 标记集成测试
- `@pytest.mark.production`: 标记调用真实API的测试

### 运行测试

```bash
# 运行所有测试
pytest

# 跳过慢速和生产环境测试
pytest -k "not slow and not production"

# 运行特定标记的测试
pytest -m integration

# 运行特定文件
pytest tests/test_a_stock_queryers_pytest.py

# 详细输出
pytest -v

# 并行运行（需要安装 pytest-xdist）
pytest -n auto
```

## 测试文件

### A股查询器测试
- `test_a_stock_queryers.py`: unittest 版本
- `test_a_stock_queryers_pytest.py`: pytest 版本（推荐）

### 其他查询器测试
- `test_hk_stock_queryers.py`: 港股查询器测试
- `test_us_stock_queryers.py`: 美股查询器测试

## Mock 数据

样本数据存储在 `tests/sample_data/` 目录：

- `a_stock_indicators_sample.csv`: A股财务指标
- `a_stock_balance_sheet_sample.csv`: A股资产负债表
- `a_stock_profit_sheet_sample.csv`: A股利润表
- `a_stock_cash_flow_sheet_sample.csv`: A股现金流量表
- `hk_stock_indicators_sample.csv`: 港股财务指标
- `hk_stock_statements_sample.csv`: 港股财务三表
- `us_stock_indicators_sample.csv`: 美股财务指标
- `us_stock_statements_sample.csv`: 美股财务三表

## 最佳实践

1. **优先使用 pytest fixtures** 而不是手动导入
2. **使用参数化测试** 减少重复代码
3. **使用测试标记** 区分不同类型的测试
4. **编写有意义的断言消息** 便于调试
5. **保持测试独立**，不要依赖测试执行顺序