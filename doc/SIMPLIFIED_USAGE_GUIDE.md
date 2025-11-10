# 财务指标查询系统 - 简化版使用指南

## 🎯 简化理念

基于您的需求，我们创建了简化版本的财务指标查询系统：

> "我现在倾向于简化实现，统一字段映射现阶段感觉要求过高，太早陷入到这些细节，我们应该有一层不映射的原始数据的api，以后想要做映射再加工返回数据即可，我希望能退回到没有字段映射的简单模式"

## 📊 简化版本特性

### ✅ 核心优势
- **100% 字段覆盖率**: 直接返回 akshare 原始数据，无字段映射限制
- **简化架构**: 移除复杂的字段映射逻辑，易于理解和维护
- **保留优秀设计**: 保持依赖注入和 Protocol 接口的优雅架构
- **灵活数据访问**: 用户通过 `raw_data` 自主选择需要的字段
- **面向未来**: 保留扩展空间，可选择性添加字段映射功能

### 📈 测试结果对比
| 股票 | 市场字段数 | 简化版覆盖率 | 原版本覆盖率 |
|------|-----------|-------------|-------------|
| 招商银行 | 86个字段 | 100% | ~11% |
| 腾讯控股 | 36个字段 | 100% | ~30% |
| 苹果 | 49个字段 | 100% | ~20% |

## 🚀 快速开始

### 基本用法
```python
from akshare_value_investment.container_simplified import create_production_service

# 创建查询服务
service = create_production_service()

# 查询A股
result = service.query("600036")  # 招商银行

# 查询港股
result = service.query("00700")  # 腾讯控股

# 查询美股
result = service.query("AAPL")   # 苹果
```

### 访问原始数据
```python
if result.success and result.data:
    latest = result.data[0]

    # 查看所有可用字段
    print("所有字段:", list(latest.raw_data.keys()))

    # 访问特定字段
    if "摊薄每股收益(元)" in latest.raw_data:
        eps = latest.raw_data["摊薄每股收益(元)"]
        print(f"每股收益: {eps}")

    # A股特有字段
    a_stock_fields = [
        "净资产收益率(%)", "销售毛利率(%)", "资产负债率(%)",
        "流动比率", "净利润增长率(%)"
    ]

    # 港股特有字段
    hk_stock_fields = [
        "BASIC_EPS", "ROE_YEARLY", "GROSS_PROFIT_RATIO",
        "DEBT_ASSET_RATIO", "CURRENT_RATIO"
    ]

    # 美股特有字段
    us_stock_fields = [
        "BASIC_EPS", "ROE_AVG", "GROSS_PROFIT_RATIO",
        "DEBT_ASSET_RATIO", "CURRENT_RATIO"
    ]
```

### 高级查询
```python
# 日期范围过滤
result = service.query("600036", start_date="2024-01-01", end_date="2024-12-31")

# 获取可用字段（简化版返回空，通过raw_data访问）
fields = service.get_available_fields(MarketType.A_STOCK)
print(fields)  # [] - 使用 raw_data 访问所有字段
```

## 🏗️ 架构对比

### 简化版架构
```
查询用户
    ↓
IQueryService (简化版)
    ↓
AdapterManager (简化版)
    ↓
MarketAdapter (A/HK/US) → 直接调用 akshare → 返回原始数据
```

### 移除的组件
- ❌ `FieldMapper` - 字段映射器
- ❌ `IFieldMapper` - 字段映射接口
- ❌ 复杂的字段转换逻辑

### 保留的组件
- ✅ `IQueryService` - 查询服务接口
- ✅ `IMarketAdapter` - 市场适配器接口
- ✅ `IMarketIdentifier` - 市场识别接口
- ✅ `FinancialIndicator` - 财务指标模型（包含 `raw_data` 字段）
- ✅ 依赖注入容器
- ✅ Protocol 接口设计

## 📋 文件结构

### 简化版文件
```
src/akshare_value_investment/
├── models.py                     # 数据模型（无变化）
├── stock_identifier.py           # 股票识别器（无变化）
├── interfaces_simplified.py      # 简化版接口定义
├── adapters_simplified.py        # 简化版适配器实现
├── query_service_simplified.py   # 简化版查询服务
├── container_simplified.py       # 简化版DI容器
└── ...

# 演示文件
demo_simplified.py                # 简化版演示程序
SIMPLIFIED_USAGE_GUIDE.md         # 本使用指南
```

## 💡 使用建议

### 1. 字段访问策略
```python
# 通用策略：先查看所有字段，再选择需要的
all_fields = list(latest.raw_data.keys())
print(f"可用字段数: {len(all_fields)}")

# 常见财务指标（需要根据市场选择字段名）
if latest.market == MarketType.A_STOCK:
    # A股字段名
    eps = latest.raw_data.get("摊薄每股收益(元)")
    roe = latest.raw_data.get("净资产收益率(%)")
elif latest.market == MarketType.HK_STOCK:
    # 港股字段名
    eps = latest.raw_data.get("BASIC_EPS")
    roe = latest.raw_data.get("ROE_YEARLY")
elif latest.market == MarketType.US_STOCK:
    # 美股字段名
    eps = latest.raw_data.get("BASIC_EPS")
    roe = latest.raw_data.get("ROE_AVG")
```

### 2. 数据处理建议
```python
# 处理可能的空值或特殊值
def safe_get_float(raw_data, field_name):
    value = raw_data.get(field_name)
    if value is None or str(value).lower() == 'nan':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# 使用示例
eps = safe_get_float(latest.raw_data, "摊薄每股收益(元)")
if eps is not None:
    print(f"每股收益: {eps:.2f}")
else:
    print("每股收益: 数据不可用")
```

### 3. 市场适配建议
```python
def get_core_indicators(latest):
    """获取核心财务指标，自动适配不同市场"""
    indicators = {}

    if latest.market == MarketType.A_STOCK:
        indicators = {
            "eps": latest.raw_data.get("摊薄每股收益(元)"),
            "roe": latest.raw_data.get("净资产收益率(%)"),
            "gross_margin": latest.raw_data.get("销售毛利率(%)"),
            "debt_ratio": latest.raw_data.get("资产负债率(%)"),
        }
    elif latest.market == MarketType.HK_STOCK:
        indicators = {
            "eps": latest.raw_data.get("BASIC_EPS"),
            "roe": latest.raw_data.get("ROE_YEARLY"),
            "gross_margin": latest.raw_data.get("GROSS_PROFIT_RATIO"),
            "debt_ratio": latest.raw_data.get("DEBT_ASSET_RATIO"),
        }
    elif latest.market == MarketType.US_STOCK:
        indicators = {
            "eps": latest.raw_data.get("BASIC_EPS"),
            "roe": latest.raw_data.get("ROE_AVG"),
            "gross_margin": latest.raw_data.get("GROSS_PROFIT_RATIO"),
            "debt_ratio": latest.raw_data.get("DEBT_ASSET_RATIO"),
        }

    return indicators
```

## 🔄 运行演示

```bash
# 运行简化版演示
uv run python demo_simplified.py
```

演示程序将展示：
- 三个市场的原始数据访问
- 100% 字段覆盖率验证
- 字段访问示例
- 性能统计报告

## 🔮 未来扩展

### 可选的增强功能
1. **按需字段映射**: 为常用字段提供便捷访问函数
2. **数据验证器**: 增强数据质量检查
3. **缓存机制**: 提升重复查询性能
4. **批量查询**: 支持多股票同时查询
5. **数据导出**: 支持多种格式导出

### 扩展示例
```python
# 未来可能的便捷访问函数
def get_standardized_indicators(latest):
    """未来可添加的标准化指标访问"""
    # 自动处理不同市场的字段名差异
    # 返回标准化的指标字典
    pass
```

## 📞 总结

简化版本成功实现了您的需求：

1. **移除复杂性**: 不再需要进行复杂的字段映射
2. **保留完整性**: 100% 的字段覆盖率，无数据丢失
3. **优雅架构**: 保持依赖注入和 Protocol 接口的设计优势
4. **面向未来**: 为后续的功能扩展保留了充足的空间

这个简化版本为您提供了一个清晰、可维护且功能完整的财务数据访问解决方案。