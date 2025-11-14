# AkShare 样本数据 API 参考手册

## 文档说明
本文档汇总了`doc/sample_data/`目录下所有样本数据的具体API调用方法，方便开发者回溯和复现数据获取过程。

## 📊 数据文件总览

| 市场 | 代表股票 | 数据文件 | API数量 | 数据提供方 |
|------|----------|----------|---------|------------|
| **A股** | 贵州茅台(600519) | 4个CSV + 1个分析文档 | 4个API | 同花顺 (ths) |
| **港股** | 腾讯控股(00700) | 2个CSV + 1个分析文档 | 2个API | 东方财富 (em) |
| **美股** | Apple(AAPL) | 2个CSV + 1个分析文档 | 2个API | 东方财富 (em) |

## 🇨🇳 A股数据 API (同花顺)

### 财务指标数据
```python
import akshare as ak

# A股财务指标 - 贵州茅台(600519)
df_indicators = ak.stock_financial_abstract_ths(symbol='600519')
# 保存为: a_stock_indicators_sample.csv
# 数据结构: 100行 × 25列，27年历史数据(1998-2025)
```

### 资产负债表数据
```python
import akshare as ak

# A股资产负债表 - 贵州茅台(600519)
df_balance_sheet = ak.stock_financial_debt_ths(symbol='600519')
# 保存为: a_stock_balance_sheet_sample.csv
# 数据结构: 100行 × 75列，完整资产负债表数据
# 注意: 虽然API名为debt，实际包含完整的资产负债表(资产+负债+权益)
```

### 利润表数据
```python
import akshare as ak

# A股利润表 - 贵州茅台(600519)
df_profit_sheet = ak.stock_financial_benefit_ths(symbol='600519')
# 保存为: a_stock_profit_sheet_sample.csv
# 数据结构: 100行 × 46列，完整利润表数据
# 注意: 虽然API名为benefit，实际包含完整的利润表(收入+成本+利润)
```

### 现金流量表数据
```python
import akshare as ak

# A股现金流量表 - 贵州茅台(600519)
df_cash_flow = ak.stock_financial_cash_ths(symbol='600519')
# 保存为: a_stock_cash_flow_sheet_sample.csv
# 数据结构: 96行 × 72列，完整现金流量表数据
```

## 🇭🇰 港股数据 API (东方财富)

### 财务指标数据
```python
import akshare as ak

# 港股财务指标 - 腾讯控股(00700)
df_indicators = ak.stock_financial_hk_analysis_indicator_em(symbol='00700')
# 保存为: hk_stock_indicators_sample.csv
# 数据结构: 9行 × 36列，宽表结构
```

### 财务三表数据
```python
import akshare as ak

# 港股财务三表 - 腾讯控股(00700)
df_statements = ak.stock_financial_hk_report_em(stock='00700')
# 保存为: hk_stock_statements_sample.csv
# 数据结构: 1069行 × 11列，窄表结构
# 注意: 使用ITEM_NAME字段存储具体财务项目，AMOUNT字段存储数值
```

## 🇺🇸 美股数据 API (东方财富)

### 财务指标数据
```python
import akshare as ak

# 美股财务指标 - Apple(AAPL)
df_indicators = ak.stock_financial_us_analysis_indicator_em(symbol='AAPL')
# 保存为: us_stock_indicators_sample.csv
# 数据结构: 49列宽表结构，包含标准财务指标
```

### 财务三表数据
```python
import akshare as ak

# 美股财务三表 - Apple(AAPL)
df_statements = ak.stock_financial_us_report_em(symbol='AAPL')
# 保存为: us_stock_statements_sample.csv
# 数据结构: 窄表结构 (734行×9列)
# 注意: 使用ITEM_NAME字段存储具体财务项目(41种)，AMOUNT字段存储数值
#       包含26年历史数据(2000-2025)，每个报告期约26-31条财务项目记录
```

## 🔄 数据重现脚本

### 完整重现所有样本数据
```python
import akshare as ak
import pandas as pd
from pathlib import Path

def regenerate_all_sample_data():
    """重现所有样本数据"""
    sample_dir = Path('doc/sample_data')
    sample_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 开始重现所有样本数据...")

    # A股数据 - 贵州茅台
    print("\n📊 获取A股数据(贵州茅台)...")

    # 财务指标
    df_a_indicators = ak.stock_financial_abstract_ths(symbol='600519')
    df_a_indicators.to_csv(sample_dir / 'a_stock_indicators_sample.csv', index=False, encoding='utf-8-sig')

    # 资产负债表
    df_a_balance = ak.stock_financial_debt_ths(symbol='600519')
    df_a_balance.to_csv(sample_dir / 'a_stock_balance_sheet_sample.csv', index=False, encoding='utf-8-sig')

    # 利润表
    df_a_profit = ak.stock_financial_benefit_ths(symbol='600519')
    df_a_profit.to_csv(sample_dir / 'a_stock_profit_sheet_sample.csv', index=False, encoding='utf-8-sig')

    # 现金流量表
    df_a_cashflow = ak.stock_financial_cash_ths(symbol='600519')
    df_a_cashflow.to_csv(sample_dir / 'a_stock_cash_flow_sheet_sample.csv', index=False, encoding='utf-8-sig')

    # 港股数据 - 腾讯
    print("\n📈 获取港股数据(腾讯)...")

    df_hk_indicators = ak.stock_financial_hk_analysis_indicator_em(symbol='00700')
    df_hk_indicators.to_csv(sample_dir / 'hk_stock_indicators_sample.csv', index=False, encoding='utf-8-sig')

    df_hk_statements = ak.stock_financial_hk_report_em(stock='00700')
    df_hk_statements.to_csv(sample_dir / 'hk_stock_statements_sample.csv', index=False, encoding='utf-8-sig')

    # 美股数据 - Apple
    print("\n💰 获取美股数据(Apple)...")

    df_us_indicators = ak.stock_financial_us_analysis_indicator_em(symbol='AAPL')
    df_us_indicators.to_csv(sample_dir / 'us_stock_indicators_sample.csv', index=False, encoding='utf-8-sig')

    df_us_statements = ak.stock_financial_us_report_em(symbol='AAPL')
    df_us_statements.to_csv(sample_dir / 'us_stock_statements_sample.csv', index=False, encoding='utf-8-sig')

    print("\n✅ 所有样本数据重现完成！")

# 运行重现脚本
if __name__ == "__main__":
    regenerate_all_sample_data()
```

## 📋 API特点总结

### 同花顺API (A股)
- ✅ **稳定性高**: 经过验证，API调用稳定
- ✅ **数据完整**: 三个财务表完全分离，字段详细
- ✅ **历史久**: 27年历史数据
- ⚠️ **参数统一**: 都使用`symbol`参数

### 东方财富API (港股/美股)
- ✅ **统一接口**: 港股和美股使用类似的数据结构
- ✅ **双重结构**: 财务指标(宽表) + 财务三表(窄表)
- ⚠️ **参数差异**: 注意港股用`symbol`，财务三表用`stock`
- ⚠️ **API可用性**: 需要注意API的稳定性和可用性

## 🔍 使用建议

1. **开发测试**: 使用这些样本数据进行功能开发和测试
2. **API验证**: 在实际部署前验证API的可用性
3. **错误处理**: 添加适当的重试和错误处理机制
4. **数据缓存**: 考虑实现数据缓存，减少API调用频率
5. **版本兼容**: 注意akshare版本更新可能带来的API变化

## 📞 技术支持

如遇到API问题，建议：
1. 检查akshare版本: `import akshare; print(ak.__version__)`
2. 查看akshare官方文档: https://www.akshare.xyz/
3. 检查网络连接和API可用性
4. 尝试更新akshare: `pip install akshare --upgrade`

---
**最后更新**: 2025-11-13
**akshare版本**: 1.17.83
**数据日期**: 2025年Q3最新数据