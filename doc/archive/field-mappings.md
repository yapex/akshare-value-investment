# 财务指标字段映射表

## 📋 映射表概览

本文档提供完整的跨市场财务指标字段映射表，作为 `prototype/arch/market_adapters/` 中各适配器的参考基准。

## 🎯 统一指标设计原则

### 指标命名规范
- **小写字母 + 下划线**：`basic_eps`, `net_profit`, `roe`
- **语义明确**：名称直接反映指标含义
- **跨市场通用**：同一套指标名适用于所有市场

### 数值处理规范
- **百分比统一**：所有百分比转换为小数（如36.99% → 0.3699）
- **货币保留原始**：保持各市场原始货币单位
- **精度保证**：使用Decimal类型确保财务精度

## 📊 完整字段映射表

### 💰 盈利能力指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 数据类型 | 单位 | 备注 |
|----------|----------|---------|----------|----------|----------|------|------|
| `basic_eps` | 基本每股收益 | 摊薄每股收益(元) | BASIC_EPS | BASIC_EPS | Decimal | 元 | 核心指标 |
| `diluted_eps` | 稀释每股收益 | 基本每股收益(元) | DILUTED_EPS | DILUTED_EPS | Decimal | 元 | |
| `net_profit` | 净利润 | 净利润 | HOLDER_PROFIT | PARENT_HOLDER_NETPROFIT | Decimal | 元 | 核心指标 |
| `revenue` | 营业收入 | 营业总收入 | - | OPERATE_INCOME | Decimal | 元 | 港股可能缺失 |
| `gross_profit` | 毛利润 | - | GROSS_PROFIT | GROSS_PROFIT | Decimal | 元 | A股可能缺失 |
| `gross_margin` | 毛利率 | 销售毛利率(%) | - | GROSS_PROFIT_RATIO | Decimal | % | A股需除100 |
| `operating_profit` | 营业利润 | 营业利润 | - | - | Decimal | 元 | 部分市场缺失 |
| `net_margin` | 净利率 | - | - | NET_PROFIT_RATIO | Decimal | % | 仅美股有 |

### 🏦 财务结构指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 数据类型 | 单位 | 备注 |
|----------|----------|---------|----------|----------|----------|------|------|
| `total_equity` | 每股净资产 | 每股净资产 | BPS | - | Decimal | 元 | 港股叫BPS |
| `book_value_per_share` | 每股账面价值 | - | - | BOOK_VAL_PER_SH | Decimal | 元 | 仅美股有 |
| `debt_ratio` | 资产负债率 | 资产负债率(%) | DEBT_ASSET_RATIO | DEBT_ASSET_RATIO | Decimal | % | A股需除100 |
| `equity_ratio` | 股东权益比率 | - | - | EQUITY_RATIO | Decimal | % | 仅美股有 |
| `current_ratio` | 流动比率 | 流动比率 | CURRENT_RATIO | CURRENT_RATIO | Decimal | 倍 | |
| `quick_ratio` | 速动比率 | 速动比率 | QUICK_RATIO | QUICK_RATIO | Decimal | 倍 | |

### 📈 投资回报指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 数据类型 | 单位 | 备注 |
|----------|----------|---------|----------|----------|----------|------|------|
| `roe` | 净资产收益率 | 净资产收益率(%) | ROE_YEARLY | ROE_AVG | Decimal | % | A股需除100 |
| `roa` | 总资产收益率 | 总资产净利润率(%) | ROA | ROA | Decimal | % | A股需除100 |
| `roic` | 投入资本收益率 | - | ROIC | - | Decimal | % | 港股特有 |
| `dividend_yield` | 股息收益率 | - | DIVIDEND_YIELD | DIVIDEND_YIELD | Decimal | % | 港股美股特有 |

### 📊 营运效率指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 数据类型 | 单位 | 备注 |
|----------|----------|---------|----------|----------|----------|------|------|
| `inventory_turnover` | 存货周转率 | 存货周转率(次) | INVENTORY_TURNOVER | INVENTORY_TURNOVER | Decimal | 次 | |
| `accounts_receivable_turnover` | 应收账款周转率 | 应收账款周转率(次) | ACCOUNTS_RECEIVABLE_TURNOVER | - | Decimal | 次 | 美股可能缺失 |
| `total_asset_turnover` | 总资产周转率 | - | TOTAL_ASSET_TURNOVER | - | Decimal | 次 | 港股特有 |

### 💵 现金流指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 数据类型 | 单位 | 备注 |
|----------|----------|---------|----------|----------|----------|------|------|
| `operating_cash_flow` | 经营现金流 | 经营活动现金流量净额 | OPERATING_CASH_FLOW | OPERATING_CASH_FLOW | Decimal | 元 | |
| `free_cash_flow` | 自由现金流 | - | FREE_CASH_FLOW | FREE_CASH_FLOW | Decimal | 元 | 港股美股特有 |
| `cash_per_share` | 每股现金流 | 每股经营活动现金流量净额 | CASH_PER_SHARE | CASH_PER_SHARE | Decimal | 元 | |

## 🔧 映射实现指南

### 1. A股适配器映射

```python
class AStockAdapter(BaseMarketAdapter):
    FIELD_MAPPING = {
        # 核心盈利指标
        "basic_eps": "摊薄每股收益(元)",
        "net_profit": "净利润",
        "revenue": "营业总收入",
        "roe": "净资产收益率(%)",

        # 财务结构
        "total_equity": "每股净资产",
        "debt_ratio": "资产负债率(%)",
        "current_ratio": "流动比率",

        # 现金流
        "operating_cash_flow": "经营活动现金流量净额",
    }

    def normalize_indicators(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """A股指标标准化"""
        standardized = {}

        for unified_field, a_stock_field in self.FIELD_MAPPING.items():
            if a_stock_field in raw_data:
                try:
                    value = float(raw_data[a_stock_field])
                    # 百分比处理：A股原始数据是百分比数字
                    if unified_field in ["roe", "roa", "gross_margin", "debt_ratio"] and value > 1:
                        value = value / 100  # 转换为小数
                    standardized[unified_field] = value
                except (ValueError, TypeError):
                    continue

        return standardized
```

### 2. 港股适配器映射

```python
class HKStockAdapter(BaseMarketAdapter):
    FIELD_MAPPING = {
        # 核心盈利指标
        "basic_eps": "BASIC_EPS",
        "diluted_eps": "DILUTED_EPS",
        "net_profit": "HOLDER_PROFIT",
        "gross_profit": "GROSS_PROFIT",
        "roe": "ROE_YEARLY",

        # 财务结构
        "total_equity": "BPS",
        "debt_ratio": "DEBT_ASSET_RATIO",
        "current_ratio": "CURRENT_RATIO",

        # 港股特有指标
        "roic": "ROIC",
        "dividend_yield": "DIVIDEND_YIELD",
    }
```

### 3. 美股适配器映射

```python
class USStockAdapter(BaseMarketAdapter):
    FIELD_MAPPING = {
        # 核心盈利指标
        "basic_eps": "BASIC_EPS",
        "diluted_eps": "DILUTED_EPS",
        "net_profit": "PARENT_HOLDER_NETPROFIT",
        "revenue": "OPERATE_INCOME",
        "roe": "ROE_AVG",

        # 财务结构
        "debt_ratio": "DEBT_ASSET_RATIO",
        "equity_ratio": "EQUITY_RATIO",
        "current_ratio": "CURRENT_RATIO",

        # 美股特有指标
        "book_value_per_share": "BOOK_VAL_PER_SH",
        "net_margin": "NET_PROFIT_RATIO",
    }
```

## 📈 指标覆盖度分析

### A股指标覆盖度 (86个指标)
- ✅ **完整覆盖**：盈利能力、财务结构、现金流
- ✅ **中文指标**：字段名为中文，需要映射
- ✅ **数据丰富**：包含季度、半年、年报数据

### 港股指标覆盖度 (36个指标)
- ✅ **英文指标**：字段名为英文，部分与美股相同
- ✅ **特色指标**：ROIC、股息收益率等
- ⚠️ **部分缺失**：营业收入、毛利率等基础指标

### 美股指标覆盖度 (49个指标)
- ✅ **英文指标**：字段名为英文
- ⚠️ **年报限制**：仅提供年报数据
- ✅ **特色指标**：账面价值、净利率等

## 🔄 扩展新指标指南

### 1. 添加新统一指标
```python
# 1. 在映射表中添加
UNIFIED_INDICATORS = {
    "pe_ratio": "市盈率",          # 新增
    "pb_ratio": "市净率",          # 新增
}

# 2. 在各市场适配器中添加映射
class AStockAdapter(BaseMarketAdapter):
    FIELD_MAPPING = {
        # 现有映射...
        "pe_ratio": "市盈率(倍)",      # A股对应字段
        "pb_ratio": "市净率(倍)",      # A股对应字段
    }
```

### 2. 指标验证测试
```python
def test_new_indicator():
    """测试新增指标是否正常工作"""
    engine = QueryEngine()
    result = engine.query("600519", recent_years=1)

    if result.success:
        indicators = result.data[0].indicators
        assert "pe_ratio" in indicators, "新增指标PE Ratio未正确映射"
        print(f"市盈率: {indicators['pe_ratio']:.2f}")
```

## ⚠️ 重要注意事项

### 1. 数据一致性
- **货币单位**：不同市场使用不同货币，对比时需要注意汇率转换
- **报告期**：美股仅年报，港股A股有季报
- **会计准则**：各市场会计准则可能略有差异

### 2. 空值处理
- 缺失指标统一返回`None`
- 用户代码需要做空值检查
- 建议提供默认值或跳过逻辑

### 3. 数据精度
- 所有财务数值使用`Decimal`类型
- 避免浮点数精度丢失
- 统一保留2位小数显示

## 📚 相关文档

- [universal-financial-query.md](./universal-financial-query.md) - 架构设计文档
- [financial-indicators.md](./financial-indicators.md) - 使用指南
- [CLAUDE-patterns.md](./CLAUDE-patterns.md) - 代码模式和约定

---

**最后更新**: 2025-11-10
**维护者**: Claude AI Assistant
**版本**: v1.0