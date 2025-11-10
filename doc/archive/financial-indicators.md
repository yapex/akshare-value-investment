# 统一财务指标使用指南

## 🎯 核心设计理念

为了解决不同市场（A股、港股、美股）原始字段名不统一的问题，架构采用**统一指标名**策略。用户只需要记住一套标准化的指标名称，系统会自动将其映射到各市场的对应字段。

## 📊 标准化指标列表

### 💰 盈利能力指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 单位 |
|----------|----------|---------|----------|----------|------|
| `basic_eps` | 基本每股收益 | 摊薄每股收益(元) | BASIC_EPS | BASIC_EPS | 元 |
| `diluted_eps` | 稀释每股收益 | 基本每股收益(元) | DILUTED_EPS | DILUTED_EPS | 元 |
| `net_profit` | 净利润 | 净利润 | HOLDER_PROFIT | PARENT_HOLDER_NETPROFIT | 元 |
| `revenue` | 营业收入 | 营业总收入 | - | OPERATE_INCOME | 元 |
| `gross_profit` | 毛利润 | - | GROSS_PROFIT | GROSS_PROFIT | 元 |
| `gross_margin` | 毛利率 | 销售毛利率(%) | - | GROSS_PROFIT_RATIO | % |
| `net_margin` | 净利率 | - | - | NET_PROFIT_RATIO | % |

### 🏦 财务结构指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 单位 |
|----------|----------|---------|----------|----------|------|
| `total_equity` | 每股净资产 | 每股净资产 | BPS | - | 元 |
| `debt_ratio` | 资产负债率 | 资产负债率(%) | DEBT_ASSET_RATIO | DEBT_ASSET_RATIO | % |
| `equity_ratio` | 股东权益比率 | - | - | EQUITY_RATIO | % |
| `current_ratio` | 流动比率 | 流动比率 | CURRENT_RATIO | CURRENT_RATIO | 倍 |

### 📈 投资回报指标

| 统一字段 | 指标名称 | A股字段 | 港股字段 | 美股字段 | 单位 |
|----------|----------|---------|----------|----------|------|
| `roe` | 净资产收益率 | 净资产收益率(%) | ROE_YEARLY | ROE_AVG | % |
| `roa` | 总资产收益率 | 总资产净利润率(%) | ROA | ROA | % |

## 💡 使用方法

### 1. 基础使用（统一接口）

```python
from query_engine import QueryEngine

engine = QueryEngine()

# 查询不同市场的股票，使用统一的指标名称
symbols = ["600519", "00700", "TSLA"]  # A股、港股、美股
results = engine.batch_query(symbols, recent_years=1)

for symbol, result in results.items():
    if result.success and result.data:
        latest = result.data[0]  # 获取最新数据
        indicators = latest.indicators

        print(f"{latest.company_name} ({latest.market.value})")
        print(f"每股收益: {indicators.get('basic_eps', 0):.2f} {latest.currency}")
        print(f"净资产收益率: {indicators.get('roe', 0):.2%}")
        print(f"净利润: {indicators.get('net_profit', 0):,.0f} {latest.currency}")
```

### 2. 指标对比分析

```python
def compare_companies(symbols, indicator_name):
    """对比不同公司的同一指标"""
    engine = QueryEngine()
    comparison = engine.get_core_indicators_comparison(symbols)

    print(f"{'公司':<15} {'市场':<6} {'货币':<6} {indicator_name}")
    print("-" * 50)

    for symbol, data in comparison.items():
        if "error" not in data:
            indicators = data["indicators"]
            value = indicators.get(indicator_name, 0)

            # 根据指标类型格式化显示
            if indicator_name in ["roe", "roa", "gross_margin", "debt_ratio"]:
                formatted = f"{value:.2%}"
            elif indicator_name == "basic_eps":
                formatted = f"{value:.2f}"
            else:
                formatted = f"{value:,.0f}"

            print(f"{data['company_name']:<15} {data['market']:<6} {data['currency']:<6} {formatted}")

# 使用示例
compare_companies(["600519", "00700", "TSLA"], "roe")
```

### 3. 指标可用性检查

```python
def get_available_indicators(symbol):
    """获取指定股票可用的所有指标"""
    engine = QueryEngine()
    result = engine.query(symbol, recent_years=1)

    if result.success and result.data:
        available_indicators = result.data[0].indicators.keys()
        print(f"{symbol} 可用指标:")
        for indicator in sorted(available_indicators):
            print(f"  - {indicator}")
        return list(available_indicators)
    return []

# 使用示例
available = get_available_indicators("600519")
```

### 4. 多指标综合分析

```python
def comprehensive_analysis(symbols):
    """综合财务分析"""
    engine = QueryEngine()

    # 核心指标列表
    core_indicators = [
        "basic_eps", "net_profit", "roe", "roa",
        "gross_margin", "debt_ratio", "current_ratio"
    ]

    for symbol in symbols:
        result = engine.query(symbol, recent_years=1, period_types=["年度"])

        if result.success and result.data:
            company = result.data[0]
            print(f"\n📊 {company.company_name} ({company.market.value})")
            print(f"报告日期: {company.report_date.strftime('%Y-%m-%d')}")
            print(f"货币单位: {company.currency}")
            print("-" * 40)

            for indicator in core_indicators:
                value = company.indicators.get(indicator)
                if value is not None:
                    if indicator in ["roe", "roa", "gross_margin", "debt_ratio"]:
                        print(f"{indicator:<15}: {value:.2%}")
                    else:
                        print(f"{indicator:<15}: {value:,.2f}")

# 使用示例
comprehensive_analysis(["600519", "00700"])
```

## 🔧 高级用法

### 1. 指标计算和衍生

```python
def calculate_derived_indicators(financial_indicator):
    """计算衍生指标"""
    indicators = financial_indicator.indicators

    derived = {}

    # 市盈率（需要股价数据）
    # pe_ratio = stock_price / indicators.get('basic_eps', 0)

    # 市净率（需要股价数据）
    # pb_ratio = stock_price / indicators.get('total_equity', 0)

    # 净利润率
    if indicators.get('revenue') and indicators.get('net_profit'):
        derived['net_profit_margin'] = indicators['net_profit'] / indicators['revenue']

    # 资产周转率（需要总资产数据）
    # asset_turnover = revenue / total_assets

    return derived
```

### 2. 指标趋势分析

```python
def trend_analysis(symbol, indicator_name, years=3):
    """指标趋势分析"""
    engine = QueryEngine()

    # 获取多年数据
    start_date, end_date = engine.build_year_range(datetime.now().year - years + 1, datetime.now().year)
    result = engine.query(symbol, start_date=start_date, end_date=end_date, period_types=["年度"])

    if result.success:
        print(f"{indicator_name} 趋势分析 ({symbol})")
        print("-" * 30)

        for data in sorted(result.data, key=lambda x: x.report_date):
            year = data.report_date.year
            value = data.indicators.get(indicator_name, 0)

            if indicator_name in ["roe", "roa", "gross_margin"]:
                formatted = f"{value:.2%}"
            else:
                formatted = f"{value:,.2f}"

            print(f"{year}: {formatted}")
```

## ⚠️ 重要说明

### 指标覆盖度
- **A股**: 覆盖最全面，包含86个财务指标
- **港股**: 覆盖36个财务指标，部分指标如`revenue`可能缺失
- **美股**: 覆盖49个财务指标，仅支持年报数据

### 数据质量
- 所有百分比指标已统一转换为小数形式（如36.99% → 0.3699）
- 数值精度使用`Decimal`确保财务计算的准确性
- 缺失指标返回`None`，使用时需要做空值检查

### 扩展性
- 新增指标只需在各市场适配器的`FIELD_MAPPING`中添加映射关系
- 支持自定义指标计算和衍生指标开发
- 可根据业务需求扩展核心指标列表

---

**最后更新**: 2025-11-10
**维护者**: Claude AI Assistant