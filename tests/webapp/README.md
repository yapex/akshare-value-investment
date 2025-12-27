# Webapp 测试框架

## 测试概述

Webapp 测试框架已建立，为 Streamlit 财务分析应用提供全面的测试覆盖。

## 测试统计

### 当前状态（首次运行）

```
总测试数: 69
通过: 43 (62%)
失败: 26 (38%)
代码覆盖率: 65%
```

### 测试覆盖范围

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| `services/calculators/common.py` | **98%** | ✅ 优秀 |
| `services/calculators/ebit_margin.py` | **100%** | ✅ 完美 |
| `services/calculators/net_income_valuation.py` | **84%** | ✅ 良好 |
| `services/calculators/debt_to_fcf_ratio.py` | **92%** | ✅ 良好 |
| `services/calculators/roic.py` | **72%** | 🟡 中等 |
| `services/calculators/dcf_valuation.py` | **59%** | 🟡 中等 |
| `services/calculators/debt_to_equity.py` | **66%** | 🟡 中等 |
| `services/data_service.py` | **60%** | 🟡 中等 |
| `components/roic.py` | **93%** | ✅ 优秀 |

## 测试结构

```
tests/webapp/
├── __init__.py                      # 测试模块初始化
├── conftest.py                      # pytest 配置和 fixtures
├── components/                      # 组件测试
│   └── test_components_base.py      # 组件接口和结构测试
└── services/                        # 服务测试
    ├── test_calculators_common.py   # 通用计算函数测试
    ├── test_roic_calculator.py      # ROIC 计算器测试
    └── test_net_income_valuation_calculator.py  # 净利润估值计算器测试
```

## 测试类别

### 1. 单元测试（已实现 ✅）

#### `test_calculators_common.py` - 通用计算函数
- ✅ `calculate_cagr`: 复合年增长率计算
  - 正常增长、高增长、负增长
  - 边界情况：单值、零值、负值
- ✅ `calculate_interest_bearing_debt`: 有息债务计算
  - A股、港股、美股市场
  - 完整字段、缺失字段、NaN 值处理
- ✅ `calculate_ebit`: EBIT 和 EBIT 利润率
  - 三地市场计算规则
  - 替代字段处理
  - 错误处理
- ✅ `calculate_free_cash_flow`: 自由现金流计算
  - 三地市场资本支出计算
  - 负数处理
  - 缺失字段错误处理

#### `test_roic_calculator.py` - ROIC 计算器
- ⚠️ API 集成测试（部分失败）
- ✅ 错误处理测试
- ⚠️ 跨市场测试（需要修复）

#### `test_net_income_valuation_calculator.py` - 净利润估值
- ⚠️ 估值计算测试（需要修复）
- ✅ API 错误处理
- ✅ 参数验证

### 2. 组件测试（已实现 ✅）

#### `test_components_base.py` - 组件接口规范
- ✅ 所有组件都有 `title` 属性
- ✅ 所有组件都有 `render` 方法
- ✅ `render` 方法签名正确 `(symbol, market, years)`
- ✅ 组件标题有意义
- ✅ 组件分组完整
- ✅ 所有组件都在分组中

### 3. 集成测试（计划中 📋）

- [ ] 组件与计算器集成
- [ ] 完整用户流程测试
- [ ] API 集成测试

## Fixtures 和测试工具

### 可用 Fixtures

```python
# Mock 数据
@pytest.fixture
def mock_financial_statements_response()  # Mock 财务三表 API 响应

@pytest.fixture
def mock_api_requests()  # Mock requests.get

# 测试数据
@pytest.fixture
def sample_income_data()  # 样本利润表数据

@pytest.fixture
def sample_balance_data()  # 样本资产负债表数据

@pytest.fixture
def sample_cashflow_data()  # 样本现金流量表数据

@pytest.fixture
def sample_financial_data()  # 完整财务数据

# Streamlit Mock
@pytest.fixture
def mock_streamlit()  # Mock Streamlit 模块

# 组件测试辅助
@pytest.fixture
def component_test_helper()  # 组件测试辅助类
```

## 运行测试

### 运行所有 webapp 测试
```bash
PYTHONPATH=webapp uv run pytest tests/webapp/ -v
```

### 运行特定测试文件
```bash
PYTHONPATH=webapp uv run pytest tests/webapp/services/test_calculators_common.py -v
```

### 运行特定测试类
```bash
PYTHONPATH=webapp uv run pytest tests/webapp/services/test_calculators_common.py::TestCalculateCAGR -v
```

### 运行并显示覆盖率
```bash
PYTHONPATH=webapp uv run pytest tests/webapp/ --cov=webapp --cov-report=term-missing
```

### 生成 HTML 覆盖率报告
```bash
PYTHONPATH=webapp uv run pytest tests/webapp/ --cov=webapp --cov-report=html
open htmlcov/index.html
```

## 已知问题和修复计划

### 高优先级 🔴

1. **API 集成测试失败** (26个失败)
   - 问题：Mock 路径不正确，导入延迟
   - 修复：调整 mock 路径，使用正确的导入位置
   - 影响：ROIC、DCF、净利润估值计算器测试

2. **数据服务缺少 `extract_year_column` 方法**
   - 问题：测试调用不存在的方法
   - 修复：实现该方法或调整测试

### 中优先级 🟡

3. **组件测试需要改进**
   - 问题：部分测试因导入路径失败
   - 修复：使用延迟导入模拟

4. **覆盖率提升**
   - 目标：从 65% 提升到 80%+
   - 重点关注：
     - `services/calculators/dcf_valuation.py` (59%)
     - `services/calculators/cash_flow_pattern.py` (56%)
     - `services/calculators/liquidity_ratio.py` (38%)

### 低优先级 🟢

5. **添加更多计算器测试**
   - `ebit_margin.py`
   - `revenue_growth.py`
   - `debt_to_equity.py`
   - `cash_flow_pattern.py`

6. **集成测试**
   - 端到端用户流程
   - 多组件协同工作

## 测试最佳实践

### 1. 使用 fixtures 减少重复
```python
@pytest.fixture
def sample_data():
    return pd.DataFrame({...})

def test_calculation(sample_data):
    result = calculate(sample_data)
    assert result is not None
```

### 2. Mock 外部依赖
```python
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value = Mock(status_code=200, json={...})
    # 测试代码
```

### 3. 测试边界情况
```python
def test_zero_values():
    assert calculate(0) == 0

def test_negative_values():
    assert calculate(-100) raises ValueError
```

### 4. 使用描述性测试名称
```python
# ✅ 好的测试名称
def test_roic_calculation_with_negative_net_income_returns_zero()

# ❌ 不好的测试名称
def test_roic_1()
```

## 下一步计划

### 短期（1-2周）
- [ ] 修复所有失败的测试（26个）
- [ ] 提升核心计算器覆盖率到 85%+
- [ ] 添加缺失的 `extract_year_column` 实现

### 中期（1个月）
- [ ] 为所有 10 个计算器添加完整测试
- [ ] 添加组件集成测试
- [ ] 达到 80%+ 代码覆盖率

### 长期（持续）
- [ ] 添加性能测试
- [ ] 添加端到端测试
- [ ] 集成 CI/CD 自动测试

## 贡献指南

### 添加新测试

1. 在相应目录创建测试文件
2. 使用现有的 fixtures
3. 遵循命名约定：`test_<功能>_<场景>.py`
4. 运行测试确保通过
5. 更新此文档

### 测试命名规范

```python
class Test<ClassName>:           # 测试类
    def test_<function>_<scenario>  # 测试方法
```

## 相关文档

- [项目主文档](../../README.md)
- [CLAUDE.md](../../CLAUDE.md)
- [测试最佳实践](../README.md)

## 联系方式

如有问题或建议，请提交 issue 或 pull request。
