# AkShare API 调用方式参考文档

## 概述

本文档详细记录了当前系统中各个市场（A股、港股、美股）的主要数据获取方式和 akshare API 调用方法。

## 📚 目录

- [A股数据获取](#a股数据获取)
- [港股数据获取](#港股数据获取)
- [美股数据获取](#美股数据获取)
- [数据结构说明](#数据结构说明)
- [缓存机制](#缓存机制)
- [错误处理](#错误处理)

---

## A股数据获取

### 1. 财务指标数据

**API 调用方式**：
```python
import akshare as ak

# 获取A股财务指标数据
df = ak.stock_financial_abstract(threshold="1", symbol="600519")
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/a_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/a_stock_queryers.py)
- 类：`AStockIndicatorQueryer`
- 方法：`_query_raw()`

**数据结构**：
- **宽表格式**：每行代表一个财务指标，每列代表不同报告期
- **关键字段**：`指标`、`选项`、`YYYYMMDD`格式的日期列
- **数据特点**：多年份数据横向排列，适合时间序列分析

**示例输出**：
```
     指标         选项     20241231    20231231    20221231
0  基本每股收益    年报      35.17       29.69       24.12
1  净资产收益率    年报      34.18%      31.15%      28.16%
```

### 2. 财务三表数据

#### 2.1 资产负债表
```python
# 获取A股资产负债表数据
df = ak.stock_balance_sheet_by_quarterly_em(symbol="600519")
```

#### 2.2 利润表
```python
# 获取A股利润表数据
df = ak.stock_profit_sheet_by_quarterly_em(symbol="600519")
```

#### 2.3 现金流量表
```python
# 获取A股现金流量表数据
df = ak.stock_cash_flow_sheet_by_quarterly_em(symbol="600519")
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/a_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/a_stock_queryers.py)
- 类：`AStockBalanceSheetQueryer`、`AStockIncomeStatementQueryer`、`AStockCashFlowQueryer`

---

## 港股数据获取

### 1. 财务指标数据

**API 调用方式**：
```python
import akshare as ak

# 获取港股财务指标数据
df = ak.stock_financial_analysis_indicator(symbol="00700")
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/hk_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/hk_stock_queryers.py)
- 类：`HKStockIndicatorQueryer`

### 2. 财务三表数据

**API 调用方式**：
```python
# 获取港股财务三表数据（统一API）
df = ak.stock_financial_hk_report_em(symbol="00700", indicator="年报")
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/hk_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/hk_stock_queryers.py)
- 类：`HKStockStatementQueryer`

---

## 美股数据获取

### 1. 财务指标数据

**API 调用方式**：
```python
import akshare as ak

# 获取美股财务指标数据
df = ak.stock_financial_us_analysis_indicator_em(symbol="AAPL")
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/us_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/us_stock_queryers.py)
- 类：`USStockIndicatorQueryer`

**数据结构**：
- **宽表格式**：标准财务指标，每个指标一列
- **关键字段**：包含ROE、ROA、EPS等标准财务指标

### 2. 财务三表数据（窄表结构）

**API 调用方式**：
```python
import akshare as ak

# 获取美股财务三表数据（窄表结构）
df = ak.stock_financial_us_report_em(
    stock="AAPL",
    symbol="资产负债表",  # 可选：资产负债表、现金流量表
    indicator="年报"
)
```

**系统调用位置**：
- 文件：[`src/akshare_value_investment/datasource/queryers/us_stock_queryers.py`](src/akshare_value_investment/datasource/queryers/us_stock_queryers.py)
- 类：`USStockStatementQueryer`

**窄表数据结构**：
```
   SECUCODE SECURITY_CODE SECURITY_NAME_ABBR REPORT_DATE REPORT_TYPE REPORT STD_ITEM_CODE      AMOUNT ITEM_NAME
0     00002         AAPL                  苹果     2024-09-28        年报  合并    310050     6803000000    总资产
1     00002         AAPL                  苹果     2024-09-28        年报  合并    310100     3002000000    总负债
```

**窄表特点**：
- **ITEM_NAME**：存储具体的财务项目名称
- **AMOUNT**：存储对应的数值
- **结构特点**：一行一个财务项目，需要通过ITEM_NAME字段进行筛选

**窄表字段配置示例**：
```yaml
"总资产":
  name: "总资产"
  keywords: ["总资产", "资产总额", "全部资产", "Total Assets", "ASSETS"]
  priority: 1
  api_field: "ITEM_NAME"
  filter_value: "总资产"
  value_field: "AMOUNT"
```

---

## 数据结构说明

### 1. 宽表结构（A股财务指标）

**特点**：
- 每行是一个财务指标
- 每列是一个报告期（日期）
- 适合多年份数据对比分析

**处理方式**：
```python
# 转换为按报告期组织的财务指标对象
for date_col in date_columns:
    report_date = datetime.strptime(date_col, "%Y%m%d")
    period_data = {}
    for raw_data in raw_data_list:
        indicator_name = raw_data.get('指标', '')
        indicator_value = raw_data.get(date_col)
        if indicator_name and indicator_value is not None:
            period_data[indicator_name] = indicator_value
```

### 2. 窄表结构（美股财务三表）

**特点**：
- ITEM_NAME字段存储财务项目
- AMOUNT字段存储数值
- 需要基于配置进行字段映射

**处理方式**：
```python
# 筛选匹配的财务项目
filtered_rows = df[df['ITEM_NAME'] == filter_value]
if not filtered_rows.empty:
    amount_value = filtered_rows['AMOUNT'].iloc[0]
```

---

## 缓存机制

### SQLite智能缓存

**缓存配置**：
- **财务指标**：缓存类型 `indicators`
- **财务报表**：缓存类型 `statements`
- **缓存字段**：基于`date`字段进行增量更新

**缓存实现**：
```python
# 基础查询器使用智能缓存装饰器
class BaseDataQueryer(IDataQueryer):
    cache_date_field = 'date'
    cache_query_type = 'indicators'

    def __init__(self):
        self._query_with_dates = smart_sqlite_cache(
            date_field=self.cache_date_field,
            query_type=self.cache_query_type
        )(self._query_with_dates_original)
```

**缓存效果**：
- API调用减少70%+
- 支持增量数据更新
- 显著提升查询性能

---

## 错误处理

### 1. 网络错误处理

```python
try:
    df = ak.stock_financial_abstract(threshold="1", symbol="600519")
except Exception as e:
    raise RuntimeError(f"获取A股 {symbol} 财务数据失败: {str(e)}")
```

### 2. 数据验证

```python
if df is None or df.empty:
    return {
        "success": False,
        "message": f"无法获取 {symbol} 的财务数据",
        "data": []
    }

# 窄表结构验证
required_fields = ["ITEM_NAME", "AMOUNT"]
if not all(field in df.columns for field in required_fields):
    raise ValueError("数据格式不正确，缺少必需字段")
```

### 3. 字段映射错误处理

```python
try:
    mapped_fields, suggestions = field_mapper.resolve_fields_sync(symbol, [field_query])
    if not mapped_fields:
        return {
            "success": False,
            "message": f"无法映射查询字段 '{field_query}'。建议: {suggestions[:3]}"
        }
except Exception as e:
    return {
        "success": False,
        "message": f"字段映射失败: {str(e)}"
    }
```

---

## 市场代码识别

### 市场推断规则

```python
def infer_market_type(symbol: str) -> Optional[str]:
    # A股：6位纯数字 或 SH/SZ前缀 + 6位数字
    if re.match(r'^[0-9]{6}$', symbol) or re.match(r'^(SH|SZ)[0-9]{6}$', symbol):
        return "a_stock"

    # 港股：4-5位数字 或 数字+.HK
    if re.match(r'^[0-9]{4,5}(\.HK)?$', symbol):
        return "hk_stock"

    # 美股：1-5位大写字母
    if re.match(r'^[A-Z]{1,5}$', symbol):
        return "us_stock"

    return None
```

### 代码示例
- **A股**：`600519`、`SH600519`、`SZ000001`
- **港股**：`00700`、`09988.HK`、`00700.HK`
- **美股**：`AAPL`、`MSFT`、`TSLA`

---

## 扩展指南

### 添加新的数据源

1. **创建Queryer类**：
```python
class NewMarketQueryer(BaseDataQueryer):
    def _query_raw(self, symbol: str) -> pd.DataFrame:
        return ak.new_market_api(symbol=symbol)
```

2. **注册到财务服务**：
```python
# 在 FinancialDataService 中添加
self.queryers[(MarketType.NEW_MARKET, 'indicators')] = new_market_queryer
```

3. **配置字段映射**：
```yaml
# 在对应的YAML配置文件中添加字段定义
markets:
  new_market:
    name: "新市场"
    currency: "NEW"
    "INDICATOR_NAME":
      name: "指标名称"
      keywords: ["关键字1", "关键字2"]
      priority: 1
```

### 添加窄表支持

1. **创建窄表配置**：
```yaml
field_name:
  name: "字段名称"
  keywords: ["关键字"]
  api_field: "ITEM_NAME"  # 筛选字段
  filter_value: "筛选值"   # 筛选条件
  value_field: "AMOUNT"    # 数值字段
```

2. **使用窄表服务**：
```python
from src.akshare_value_investment.services.narrow_table_service import NarrowTableService

narrow_service = NarrowTableService()
field_data = narrow_service.extract_field_data(df, field_info, symbol)
```

---

## 📖 相关文档

- [系统架构文档](./SYSTEM_ARCHITECTURE_SUMMARY.md)
- [MCP集成文档](./mcp/)
- [智能字段算法设计](./algorithms/INTELLIGENT_FIELD_ALGORITHMS_DESIGN.md)

---

**最后更新**：2025-11-13
**文档版本**：v1.0.0