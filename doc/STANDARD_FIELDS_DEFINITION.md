# 标准财务字段定义 (Standard Financial Fields)

## 📋 概述

本文档定义了跨市场（A股、港股、美股）财务数据归一化的标准字段体系。

**设计原则**:
1. **基于IFRS框架** - 采用国际财务报告准则的核心概念
2. **业务驱动** - 满足价值投资核心分析需求（ROIC、DCF等）
3. **跨市场可用** - 确保三地市场都能映射到这些字段
4. **最小核心集** - 只定义必需字段，避免过度设计

---

## 🎯 标准字段分类

### 1️⃣ **基础字段 (Fundamental Fields)**

| 标准字段名 | IFRS术语 | 说明 | 业务用途 |
|-----------|----------|------|---------|
| `report_date` | Reporting Date | 报告期/财务日期 | 数据关联、时间序列分析 |

**映射示例**:
- A股: `报告期`
- 港股: `REPORT_DATE`
- 美股: `REPORT_DATE`

---

### 2️⃣ **利润表字段 (Income Statement Fields)**

| 标准字段名 | IFRS术语 | 说明 | 业务用途 |
|-----------|----------|------|---------|
| `total_revenue` | Revenue / Income | 营业总收入/营业收入 | 盈利能力分析、增长率计算 |
| `operating_income` | Operating Profit | 营业利润/经营溢利 | EBIT计算、ROIC分析 |
| `net_income` | Profit/Loss | 净利润/股东应占溢利 | ROE、估值基础 |
| `income_tax` | Tax Expense | 所得税费用 | EBIT计算、税率分析 |
| `interest_expense` | Finance Cost | 利息费用/融资成本 | EBIT计算、偿债能力分析 |
| `gross_profit` | Gross Profit | 毛利润 | 毛利率分析 |

**核心公式**:
```python
# EBIT (息税前利润) 计算
EBIT = net_income + income_tax + interest_expense
# 或直接使用 operating_income（如果存在）
```

**映射示例**:

#### `total_revenue` (营业收入)
- A股: `营业总收入`, `一、营业总收入`, `其中：营业收入`
- 港股: `OPERATE_INCOME`, `营业额`, `营运收入`, `经营收入总额`
- 美股: `OPERATE_INCOME`, `营业收入`, `主营收入`, `收入总额`

#### `operating_income` (营业利润)
- A股: `二、营业利润`
- 港股: `经营溢利`, `除税前溢利`（近似）
- 美股: `营业利润`, `持续经营税前利润`

#### `net_income` (净利润)
- A股: `净利润`, `五、净利润`
- 港股: `HOLDER_PROFIT`, `股东应占溢利`, `持续经营业务税后利润`
- 美股: `PARENT_HOLDER_NETPROFIT`, `净利润`, `归属于普通股股东净利润`

---

### 3️⃣ **资产负债表字段 (Balance Sheet Fields)**

| 标准字段名 | IFRS术语 | 说明 | 业务用途 |
|-----------|----------|------|---------|
| `total_assets` | Total Assets | 资产总计/总资产 | ROA、资产周转率 |
| `current_assets` | Current Assets | 流动资产合计 | 流动比率、营运资本 |
| `total_liabilities` | Total Liabilities | 负债合计/总负债 | 资产负债率 |
| `current_liabilities` | Current Liabilities | 流动负债合计 | 流动比率、速动比率 |
| `total_equity` | Total Equity | 权益合计/股东权益 | ROE、负债权益比 |
| `short_term_debt` | Short-term Debt | 短期借款/短期债务 | 有息债务计算 |
| `long_term_debt` | Long-term Debt | 长期借款/长期债务 | 有息债务计算 |

**核心公式**:
```python
# 有息债务 (Interest-bearing Debt)
interest_bearing_debt = short_term_debt + long_term_debt

# 投入资本 (Invested Capital) - 用于ROIC计算
invested_capital = total_assets - current_liabilities
# 或: invested_capital = total_equity + interest_bearing_debt

# 流动比率
current_ratio = current_assets / current_liabilities
```

**映射示例**:

#### `current_assets` (流动资产)
- A股: `流动资产合计`
- 港股: `流动资产合计`
- 美股: `流动资产合计`

#### `current_liabilities` (流动负债)
- A股: `流动负债合计`
- 港股: `流动负债合计`
- 美股: `流动负债合计`

---

### 4️⃣ **现金流量表字段 (Cash Flow Statement Fields)**

| 标准字段名 | IFRS术语 | 说明 | 业务用途 |
|-----------|----------|------|---------|
| `operating_cash_flow` | Cash Flow from Operating Activities | 经营活动现金流量净额 | 自由现金流计算 |
| `investing_cash_flow` | Cash Flow from Investing Activities | 投资活动现金流量净额 | 资本支出分析 |
| `financing_cash_flow` | Cash Flow from Financing Activities | 筹资活动现金流量净额 | 股息回购分析 |
| `capital_expenditure` | Capital Expenditure (CapEx) | 资本支出 | 自由现金流、投资强度 |

**核心公式**:
```python
# 自由现金流 (Free Cash Flow)
free_cash_flow = operating_cash_flow - capital_expenditure

# 资本支出 (从投资现金流量中提取)
# 通常为负值，需要取绝对值
capital_expenditure = abs(
    购建固定资产 + 购建无形资产及其他资产
)
```

**映射示例**:

#### `operating_cash_flow` (经营现金流)
- A股: `经营活动产生的现金流量净额`
- 港股: `经营业务现金净额`, `经营产生现金`
- 美股: `经营活动产生的现金流量净额`

#### `capital_expenditure` (资本支出 - 组合字段)
- A股: `购建固定资产、无形资产和其他长期资产支付的现金`
- 港股: `购建固定资产` + `购建无形资产及其他资产`
- 美股: `购买固定资产` + `购建无形资产及其他资产`

---

## 📊 字段覆盖情况统计

### 📈 **三地市场字段总量**

| 市场 | 文档字段总数 | 已映射标准字段 | 映射覆盖率 | 原始字段映射数 | 平均别名数 |
|------|------------|--------------|-----------|-------------|-----------|
| **A股** | 234 | 23 | 9.8% | 33 | 1.4 |
| **港股** | 219 | 23 | 10.5% | 32 | 1.4 |
| **美股** | 186 | 23 | 12.4% | 31 | 1.3 |
| **合计** | **639** | **23** | **3.6%** | **96** | **1.4** |

**数据来源**: 基于 `doc/a_stock_fields.md`, `doc/hk_stock_fields.md`, `doc/us_stock_fields.md`

### ✅ **已定义的标准字段** (23个)

```python
class StandardFields:
    # ========== 基础字段 (1个) ==========
    REPORT_DATE = "report_date"

    # ========== 利润表字段 (6个) ==========
    TOTAL_REVENUE = "total_revenue"      # ✅ 营业总收入
    OPERATING_INCOME = "operating_income" # ✅ 营业利润 (EBIT)
    GROSS_PROFIT = "gross_profit"        # ✅ 毛利润
    NET_INCOME = "net_income"            # ✅ 净利润
    INCOME_TAX = "income_tax"            # ✅ 所得税费用
    INTEREST_EXPENSE = "interest_expense" # ✅ 利息费用

    # ========== 资产负债表字段 (7个) ==========
    TOTAL_ASSETS = "total_assets"        # ✅ 资产总计
    CURRENT_ASSETS = "current_assets"    # ✅ 流动资产
    TOTAL_LIABILITIES = "total_liabilities" # ✅ 负债合计
    CURRENT_LIABILITIES = "current_liabilities" # ✅ 流动负债
    TOTAL_EQUITY = "total_equity"        # ✅ 权益合计
    SHORT_TERM_DEBT = "short_term_debt"  # ✅ 短期借款
    LONG_TERM_DEBT = "long_term_debt"    # ✅ 长期借款

    # ========== 现金流量表字段 (3个) ==========
    OPERATING_CASH_FLOW = "operating_cash_flow" # ✅ 经营现金流
    INVESTING_CASH_FLOW = "investing_cash_flow" # ✅ 投资现金流
    FINANCING_CASH_FLOW = "financing_cash_flow" # ✅ 筹资现金流

    # ========== 每股指标 (2个) ✨ 新增 ==========
    BASIC_EPS = "basic_eps"              # ✅ 基本每股收益
    DILUTED_EPS = "diluted_eps"          # ✅ 稀释每股收益

    # ========== 营运资本字段 (4个) ✨ 新增 ==========
    CASH_AND_EQUIVALENTS = "cash_and_equivalents" # ✅ 现金及现金等价物
    ACCOUNTS_RECEIVABLE = "accounts_receivable"   # ✅ 应收账款
    INVENTORY = "inventory"                        # ✅ 存货
    ACCOUNTS_PAYABLE = "accounts_payable"          # ✅ 应付账款
```

### 📊 **覆盖策略说明**

#### **为什么只有2.7%的覆盖率？**

这是**有意为之的设计决策**，而非不足！原因如下：

1️⃣ **最小核心集原则**
   - 只定义价值投资**核心必需**的字段
   - 避免过度设计，保持系统简洁
   - 17个标准字段可以派生出数百个指标

2️⃣ **业务驱动设计**
   - 基于ROIC、DCF、流动性比率等核心计算器的实际需求
   - 每个标准字段都有明确的业务用途
   - 不是简单的"字段字典"，而是"分析框架"

3️⃣ **派生能力强大**
   ```python
   # 17个标准字段可以计算：
   ROE = net_income / total_equity
   ROA = net_income / total_assets
   ROIC = operating_income / (total_assets - current_liabilities)
   Current_Ratio = current_assets / current_liabilities
   Debt_to_Equity = (short_term_debt + long_term_debt) / total_equity
   Gross_Profit_Margin = gross_profit / total_revenue
   # ... 数百个指标
   ```

#### **如果需要更多字段怎么办？**

**添加新标准字段的三层验证**:

1. **需求验证**: 是否为多个计算器共同需要？
2. **市场可用性**: 三地市场API是否都提供？
3. **IFRS对照**: 是否符合国际财务报告准则？

**不建议添加的字段类型**:
- ❌ 行业特定字段（如存货、应收账款）
- ❌ 稀缺字段（如商誉、递延税项）
- ❌ 派生指标（如ROE、毛利率 - 应计算而非存储）

### ⚠️ **潜在扩展字段** (未来可选)

#### 高优先级（如需增强分析能力）

1. **`capital_expenditure`** (资本支出)
   - 用途: 自由现金流计算 (FCF = OCF - CapEx)
   - 可行性: 可从现金流量表组合计算
   - 建议: 添加为计算字段，非直接映射

2. **`depreciation_amortization`** (折旧摊销)
   - 用途: EBITDA计算
   - 可行性: 现金流量表补充信息
   - 建议: 可选，用于EBITDA分析

3. **每股指标**
   - `basic_eps` (基本每股收益)
   - `diluted_eps` (稀释每股收益)
   - 用途: 每股分析
   - 可行性: 部分市场缺失

#### 中优先级（特定分析场景）

4. **营运资本相关**
   - `inventory` (存货)
   - `accounts_receivable` (应收账款)
   - `accounts_payable` (应付账款)
   - 用途: 营运资本周转率分析
   - 注意: 行业差异大，不适合作为通用标准

---

## 🎯 业务需求验证

### ROIC计算器需要的字段

✅ **已有 (17个全部满足)**:
- `total_revenue` (收入)
- `operating_income` (营业利润/EBIT) - ✅ 新增
- `net_income` (净利润)
- `income_tax` (所得税)
- `interest_expense` (利息)
- `total_assets` (总资产)
- `current_liabilities` (流动负债) - ✅ 新增

✅ **完全满足** - 所有核心计算字段已齐全！

### DCF估值器需要的字段

✅ **已有**:
- `operating_cash_flow` (经营现金流)
- `total_revenue` (收入)
- `net_income` (净利润)

⚠️ **部分缺失**:
- `capital_expenditure` (资本支出) - 可从现金流量表计算，非直接映射

### 流动性比率计算器需要的字段

✅ **已有 (全部满足)**:
- `current_assets` (流动资产) - ✅ 新增
- `current_liabilities` (流动负债) - ✅ 新增

✅ **完全满足** - 流动性分析字段已齐全！

---

## 📚 参考标准

### 国际财务报告准则 (IFRS)

**IAS 1 - 财务报表列报**:
- 收入 (Revenue)
- 财务费用 (Finance Costs)
- 所得税费用 (Tax Expense)
- 资产、负债、权益的定义

**IAS 7 - 现金流量表**:
- 经营活动、投资活动、筹资活动分类

### 美国通用会计准则 (US GAAP)

**ASC 210 - 资产负债表**:
- 流动/非流动分类

**ASC 225 - 利润表**:
- 收入、费用分类

### 中国企业会计准则 (CAS)

**基本准则**:
- 与IFRS实质趋同
- 术语本地化（如"营业收入"而非"Revenue"）

---

## 🎓 设计决策记录

### 为什么选择这些字段？

1. **核心性**: 这些字段在所有财务分析中都是必需的
2. **通用性**: 跨市场、跨行业都适用
3. **可计算性**: 可以派生出其他指标（如ROE、ROIC）
4. **数据可得性**: 三地市场API都提供这些字段

### 为什么只有2.7%的覆盖率？

这是**有意为之的设计决策**：

1️⃣ **最小核心集原则**
   - 只定义价值投资**核心必需**的字段
   - 避免过度设计，保持系统简洁
   - 17个标准字段可以派生出数百个指标

2️⃣ **业务驱动设计**
   - 基于ROIC、DCF、流动性比率等核心计算器的实际需求
   - 每个标准字段都有明确的业务用途
   - 不是简单的"字段字典"，而是"分析框架"

3️⃣ **派生能力强大**
   ```python
   # 17个标准字段可以计算：
   ROE = net_income / total_equity
   ROA = net_income / total_assets
   ROIC = operating_income / (total_assets - current_liabilities)
   Current_Ratio = current_assets / current_liabilities
   Debt_to_Equity = (short_term_debt + long_term_debt) / total_equity
   Gross_Profit_Margin = gross_profit / total_revenue
   # ... 数百个指标
   ```

### 为什么不包括某些字段？

- **行业特定字段**（如存货、应收账款）: 不同行业差异大，不适合作为通用标准
- **衍生指标**（如ROE、毛利率）: 这些应该由计算器生成，不是原始数据
- **稀少字段**（如商誉、递延税项）: 不是所有公司都有，不适合作为核心标准

### 字段命名原则

1. **使用小写+下划线**: 遵循Python命名规范
2. **使用英文术语**: 便于代码理解和国际化
3. **避免缩写**: `total_revenue` 而非 `tot_rev`
4. **语义清晰**: `operating_cash_flow` 而非 `ocf`

---

## 📝 维护指南

### 添加新标准字段流程

1. **需求验证**: 确认业务计算器确实需要此字段
2. **市场可用性**: 检查三地市场API是否提供
3. **IFRS对照**: 确认与IFRS术语对应
4. **更新配置**:
   - 在 `StandardFields` 添加常量
   - 在 `config.py` 添加映射
   - 更新本文档
5. **测试验证**: 添加单元测试确保映射正确

### 版本历史

- **v1.0** (2026-01-06): 初始版本，定义11个核心字段
- **v1.1** (2026-01-06): 新增6个字段（operating_income, gross_profit, current_assets, current_liabilities等），达到17个标准字段
- **v1.2** (2026-01-06): **当前版本** - 新增6个扩展字段（basic_eps, diluted_eps, cash_and_equivalents, accounts_receivable, inventory, accounts_payable），达到23个标准字段
- **v1.3** (待定): 计划添加资本支出计算字段

---

**文档维护**: 本文档应与 `StandardFields` 类同步更新
**最后更新**: 2026-01-06
**维护者**: AI Agent + User

---

**文档维护**: 本文档应与 `StandardFields` 类同步更新
**最后更新**: 2026-01-06
**维护者**: AI Agent + User
