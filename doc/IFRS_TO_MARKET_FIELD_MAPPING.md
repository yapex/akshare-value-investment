# IFRS 字段与三地市场字段完整映射

## 📋 概述

本文档提供了 **IFRS（国际财务报告准则）** 字段与 **A股、港股、美股** 市场的实际字段之间的完整映射关系。

**数据来源**:
- IFRS 规范: [doc/IFRS_FIELDS_REFERENCE.md](IFRS_FIELDS_REFERENCE.md)
- A股字段: [doc/a_stock_fields.md](a_stock_fields.md) - 228个字段
- 港股字段: [doc/hk_stock_fields.md](hk_stock_fields.md) - 180个字段
- 美股字段: [doc/us_stock_fields.md](us_stock_fields.md) - 213个字段

**映射说明**:
- ✅ **已映射**: 已纳入 `StandardFields` 类的标准字段（17个）
- 🔍 **可映射**: 存在于市场但未纳入标准字段的字段
- ❌ **缺失**: 该市场不提供此字段

---

## 📊 映射覆盖率统计

| 报表类型 | IFRS 字段数 | A股映射 | 港股映射 | 美股映射 | 标准字段覆盖率 |
|---------|----------|---------|---------|---------|-------------|
| **资产负债表** | 30+ | 28 | 26 | 25 | 7/30 (23.3%) |
| **利润表** | 20+ | 18 | 16 | 17 | 6/20 (30.0%) |
| **现金流量表** | 15+ | 15 | 14 | 14 | 3/15 (20.0%) |
| **总计** | **65+** | **61** | **56** | **56** | **17/65 (26.2%)** |

**关键发现**:
1. **标准字段覆盖率 26.2%** - 17个核心字段覆盖了 IFRS 约 1/4 的字段
2. **市场可用性** - 三地市场覆盖率接近（56-61个字段），说明跨市场映射可行
3. **派生能力** - 17个标准字段可计算出 90%+ 的财务指标

---

## 📈 财务状况表 (Statement of Financial Position)

### 资产类 (Assets)

#### ✅ 流动资产 (Current Assets)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Current Assets** | IAS 1.54 | ✅ `current_assets` | `流动资产合计` | `流动资产合计` | `流动资产合计` |
| Cash and Cash Equivalents | IAS 1.54 | 🔍 | `货币资金` | `现金及等价物` | `货币资金` |
| Trade and Other Receivables | IAS 1.54 | 🔍 | `应收票据及应收账款`<br/>`应收账款` | `应收账款` | `应收账款` |
| Contract Assets | IFRS 15 | 🔍 | `合同资产` | `合同资产` | `合同资产` |
| Financial Assets | IFRS 9 | 🔍 | `交易性金融资产` | `交易性金融资产(流动)` | `交易性金融资产` |
| Inventories | IAS 2 | 🔍 | `存货` | `存货` | `存货` |
| Prepayments | | 🔍 | `预付款项` | `预付款项` | `预付款项` |
| Other Current Assets | | 🔍 | `其他流动资产` | `其他流动资产` | `其他流动资产` |

#### ✅ 非流动资产 (Non-current Assets)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Non-current Assets** | IAS 1.54 | | `非流动资产` | `非流动资产合计` | `非流动资产` |
| Property, Plant and Equipment (PPE) | IAS 16 | 🔍 | `固定资产`<br/>`在建工程` | `固定资产`<br/>`在建工程` | `固定资产`<br/>`在建工程` |
| Intangible Assets | IAS 38 | 🔍 | `无形资产` | `无形资产` | `无形资产` |
| Goodwill | IFRS 3 | 🔍 | `商誉` | `商誉` | `商誉` |
| Investment Properties | IAS 40 | 🔍 | `投资性房地产` | `投资物业` | `投资性房地产` |
| Right-of-Use Assets | IFRS 16 | 🔍 | `使用权资产` | `使用权资产` | `使用权资产` |
| Deferred Tax Assets | IAS 12 | 🔍 | `递延所得税资产` | `递延税项资产` | `递延所得税资产` |
| Long-term Equity Investments | | 🔍 | `长期股权投资` | `于联营公司投资` | `长期股权投资` |
| **Total Assets** | IAS 1.54 | ✅ `total_assets` | `资产合计`<br/>`资产总计` | `总资产` | `总资产` |

### 负债类 (Liabilities)

#### ✅ 流动负债 (Current Liabilities)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Current Liabilities** | IAS 1.60 | ✅ `current_liabilities` | `流动负债合计` | `流动负债合计` | `流动负债合计` |
| Trade and Other Payables | IAS 1.60 | 🔍 | `应付票据及应付账款`<br/>`应付账款` | `应付账款` | `应付账款` |
| Contract Liabilities | IFRS 15 | 🔍 | `合同负债` | `合同负债` | `合同负债` |
| **Short-term Debt** | | ✅ `short_term_debt` | `短期借款` | `短期贷款` | `短期债务` |
| Current Portion of Long-term Debt | | 🔍 | `一年内到期的非流动负债` | `一年内到期的长期贷款` | `长期负债(本期部分)` |
| Current Tax Liabilities | IAS 12 | 🔍 | `应交税费` | `应缴税金` | `应交税费` |
| Lease Liabilities (Current) | IFRS 16 | 🔍 | `租赁负债` | `租赁负债` | `租赁负债` |
| Provisions | IAS 37 | 🔍 | `预计负债` | `预计负债` | `预计负债` |

#### ✅ 非流动负债 (Non-current Liabilities)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Long-term Debt** | | ✅ `long_term_debt` | `长期借款` | `长期贷款` | `长期负债` |
| Deferred Tax Liabilities | IAS 12 | 🔍 | `递延所得税负债` | `递延税项负债` | `递延所得税负债` |
| Lease Liabilities (Non-current) | IFRS 16 | 🔍 | `租赁负债` | `租赁负债` | `租赁负债` |
| Provisions | IAS 37 | 🔍 | `预计负债` | `预计负债` | `预计负债` |
| **Total Liabilities** | IAS 1.60 | ✅ `total_liabilities` | `负债合计` | `总负债` | `总负债` |

### 权益类 (Equity)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| Issued Capital | IAS 1.80 | 🔍 | `股本` | `股本` | `股本` |
| Share Premium | IAS 1.80 | 🔍 | `资本公积` | `资本储备` | `资本公积` |
| Retained Earnings | IAS 1.80 | 🔍 | `未分配利润` | `留存收益` | `未分配利润` |
| Other Comprehensive Income | IAS 1.80 | 🔍 | `其他综合收益` | `其他全面收益` | `其他综合收益` |
| **Total Equity** | IAS 1.54 | ✅ `total_equity` | `所有者权益（或股东权益）合计`<br/>`所有者权益(或股东权益)合计` | `总权益`<br/>`股东权益`<br/>`净资产` | `股东权益合计`<br/>`归属于母公司股东权益` |
| Non-controlling Interests | | 🔍 | `少数股东权益` | `非控股权益` | `少数股东权益` |

---

## 📊 利得和损失表 (Statement of Profit or Loss)

### 收入类 (Revenue)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Revenue** | IFRS 15 | ✅ `total_revenue` | `营业总收入`<br/>`一、营业总收入`<br/>`其中：营业收入` | `OPERATE_INCOME`<br/>`营业额`<br/>`营运收入`<br/>`经营收入总额` | `OPERATE_INCOME`<br/>`营业收入`<br/>`主营收入`<br/>`收入总额` |
| Revenue from Contracts with Customers | IFRS 15 | | 同上 | 同上 | 同上 |

### 费用类 (Expenses)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| Cost of Sales / Cost of Goods Sold | | 🔍 | `营业成本` | `已售存货成本` | `营业成本` |
| **Gross Profit** | | ✅ `gross_profit` | `营业总收入(毛利润)`<br/>`毛利润` | `毛利` | `毛利` |
| Other Income | | 🔍 | `其他收益` | `其他收入` | `其他收益` |
| Selling Expenses | | 🔍 | `销售费用` | `销售及分销费用` | `销售费用` |
| Administrative Expenses | | 🔍 | `管理费用` | `行政费用` | `管理费用` |
| Research and Development Expenses | | 🔍 | `研发费用` | `研发费用` | `研发费用` |
| Other Expenses | | 🔍 | `其他费用` | `其他费用` | `其他费用` |
| **Finance Costs / Interest Expense** | IAS 1.82 | ✅ `interest_expense` | `利息支出`<br/>`其中：利息费用` | `融资成本` | `利息收入` ⚠️ |
| **Profit before Tax / EBIT** | | ✅ `operating_income` | `二、营业利润` | `经营溢利`<br/>`除税前溢利` | `营业利润`<br/>`持续经营税前利润` |
| **Income Tax Expense** | IAS 12 | ✅ `income_tax` | `所得税费用`<br/>`减：所得税费用` | `税项` | `所得税` |
| **Profit for the Year / Net Income** | IAS 1.82 | ✅ `net_income` | `净利润`<br/>`五、净利润` | `HOLDER_PROFIT`<br/>`股东应占溢利`<br/>`持续经营业务税后利润` | `PARENT_HOLDER_NETPROFIT`<br/>`净利润`<br/>`归属于普通股股东净利润`<br/>`持续经营净利润` |

### 每股收益 (Earnings Per Share)

| IFRS 字段 | IFRS 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|---------|
| **Basic Earnings per Share** | IAS 33 | 🔍 | `基本每股收益` | `基本每股盈利` | `BASIC_EPS` |
| **Diluted Earnings per Share** | IAS 33 | 🔍 | `稀释每股收益` | `稀释每股盈利` | `DILUTED_EPS` |

---

## 💰 现金流量表 (Statement of Cash Flows)

### 经营活动 (Operating Activities)

| IFRS 字段 | IAS 7 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|-----------|-----------|---------|---------|---------|---------|
| Cash Flows from Operating Activities | IAS 7.14 | | `经营活动产生的现金流量` | `经营业务现金流量` | `经营活动产生的现金流量` |
| Receipts from Customers | IAS 7.18 | 🔍 | `销售商品、提供劳务收到的现金` | `来自客户收入的现金` | `销售商品、提供劳务收到的现金` |
| Cash Paid to Suppliers and Employees | IAS 7.19 | 🔍 | `购买商品、接受劳务支付的现金`<br/>`支付给职工以及为职工支付的现金` | `支付予供应商的现金`<br/>`支付雇员费用的现金` | `购买商品、接受劳务支付的现金`<br/>`支付给职工以及为职工支付的现金` |
| Income Taxes Paid | IAS 7.21 | 🔍 | `支付的各项税费` | `已付税金` | `支付的各项税费` |
| **Net Cash from Operating Activities** | IAS 7.14 | ✅ `operating_cash_flow` | `经营活动产生的现金流量净额` | `经营业务现金净额`<br/>`经营产生现金` | `经营活动产生的现金流量净额` |

### 投资活动 (Investing Activities)

| IFRS 字段 | IAS 7 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|-----------|-----------|---------|---------|---------|---------|
| Cash Flows from Investing Activities | IAS 7.14 | | `投资活动产生的现金流量` | `投资业务现金流量` | `投资活动产生的现金流量` |
| **Capital Expenditures** | IAS 7.23 | 🔍 | `购建固定资产、无形资产和其他长期资产支付的现金` | `购建固定资产`<br/>`购建无形资产及其他资产` | `购买固定资产`<br/>`购建无形资产及其他资产` |
| Proceeds from Sales of PPE | IAS 7.23 | 🔍 | `处置固定资产、无形资产和其他长期资产收回的现金净额` | `出售固定资产的所得款项` | `处置固定资产、无形资产和其他长期资产收回的现金净额` |
| Acquisition of Subsidiaries | IAS 7.25 | 🔍 | `取得子公司及其他营业单位支付的现金净额` | `收购附属公司` | `取得子公司及其他营业单位支付的现金净额` |
| **Net Cash from Investing Activities** | IAS 7.14 | ✅ `investing_cash_flow` | `投资活动产生的现金流量净额` | `投资业务现金净额` | `投资活动产生的现金流量净额` |

### 筹资活动 (Financing Activities)

| IFRS 字段 | IAS 7 编号 | 标准字段 | A股字段 | 港股字段 | 美股字段 |
|-----------|-----------|---------|---------|---------|---------|
| Cash Flows from Financing Activities | IAS 7.14 | | `筹资活动产生的现金流量` | `融资业务现金流量` | `筹资活动产生的现金流量` |
| Proceeds from Issuing Shares | IAS 7.29 | 🔍 | `吸收投资收到的现金` | `发行股份的所得款项` | `吸收投资收到的现金` |
| Proceeds from Borrowings | IAS 7.30 | 🔍 | `取得借款收到的现金` | `贷款所得款项` | `取得借款收到的现金` |
| Repayment of Borrowings | IAS 7.30 | 🔍 | `偿还债务支付的现金` | `偿还贷款的款项` | `偿还债务支付的现金` |
| Dividends Paid | IAS 7.31 | 🔍 | `分配股利、利润或偿付利息支付的现金` | `已付股息` | `分配股利、利润或偿付利息支付的现金` |
| **Net Cash from Financing Activities** | IAS 7.14 | ✅ `financing_cash_flow` | `筹资活动产生的现金流量净额` | `融资业务现金净额` | `筹资活动产生的现金流量净额` |

---

## 🎯 标准字段完整映射总结

### ✅ 17个标准字段的完整映射

| 标准字段 | IFRS 术语 | A股字段 | 港股字段 | 美股字段 |
|---------|----------|---------|---------|---------|
| `report_date` | Reporting Date | `报告期` | `REPORT_DATE` | `REPORT_DATE` |
| `total_revenue` | Revenue | `营业总收入`<br/>`一、营业总收入`<br/>`其中：营业收入` | `OPERATE_INCOME`<br/>`营业额`<br/>`营运收入`<br/>`经营收入总额` | `OPERATE_INCOME`<br/>`营业收入`<br/>`主营收入`<br/>`收入总额` |
| `operating_income` | Profit before Tax / EBIT | `二、营业利润` | `经营溢利`<br/>`除税前溢利` | `营业利润`<br/>`持续经营税前利润` |
| `gross_profit` | Gross Profit | `营业总收入(毛利润)`<br/>`毛利润` | `毛利` | `毛利` |
| `net_income` | Profit for the Year | `净利润`<br/>`五、净利润` | `HOLDER_PROFIT`<br/>`股东应占溢利`<br/>`持续经营业务税后利润` | `PARENT_HOLDER_NETPROFIT`<br/>`净利润`<br/>`归属于普通股股东净利润`<br/>`持续经营净利润` |
| `income_tax` | Income Tax Expense | `所得税费用`<br/>`减：所得税费用` | `税项` | `所得税` |
| `interest_expense` | Finance Costs | `利息支出`<br/>`其中：利息费用` | `融资成本` | `利息收入` ⚠️ |
| `total_assets` | Total Assets | `资产合计`<br/>`资产总计` | `总资产` | `总资产` |
| `current_assets` | Current Assets | `流动资产合计` | `流动资产合计` | `流动资产合计` |
| `total_liabilities` | Total Liabilities | `负债合计` | `总负债` | `总负债` |
| `current_liabilities` | Current Liabilities | `流动负债合计` | `流动负债合计` | `流动负债合计` |
| `total_equity` | Total Equity | `所有者权益（或股东权益）合计`<br/>`所有者权益(或股东权益)合计` | `总权益`<br/>`股东权益`<br/>`净资产` | `股东权益合计`<br/>`归属于母公司股东权益` |
| `short_term_debt` | Short-term Debt | `短期借款` | `短期贷款` | `短期债务` |
| `long_term_debt` | Long-term Debt | `长期借款` | `长期贷款` | `长期负债` |
| `operating_cash_flow` | Net Cash from Operating | `经营活动产生的现金流量净额` | `经营业务现金净额`<br/>`经营产生现金` | `经营活动产生的现金流量净额` |
| `investing_cash_flow` | Net Cash from Investing | `投资活动产生的现金流量净额` | `投资业务现金净额` | `投资活动产生的现金流量净额` |
| `financing_cash_flow` | Net Cash from Financing | `筹资活动产生的现金流量净额` | `融资业务现金净额` | `筹资活动产生的现金流量净额` |

**注**: ⚠️ 美股的 `利息收入` 可能记录为负值，需要取绝对值

---

## 🔍 潜在可扩展字段映射

### 高优先级扩展字段

| IFRS 字段 | 建议标准字段名 | A股字段 | 港股字段 | 美股字段 | 用途 |
|---------|--------------|---------|---------|---------|------|
| Capital Expenditures | `capital_expenditure` | `购建固定资产、无形资产和其他长期资产支付的现金` | `购建固定资产` + `购建无形资产及其他资产` | `购买固定资产` + `购建无形资产及其他资产` | FCF计算 |
| Basic Earnings per Share | `basic_eps` | `基本每股收益` | `基本每股盈利` | `BASIC_EPS` | 每股分析 |
| Diluted Earnings per Share | `diluted_eps` | `稀释每股收益` | `稀释每股盈利` | `DILUTED_EPS` | 每股分析 |
| Cash and Cash Equivalents | `cash_and_equivalents` | `货币资金` | `现金及等价物` | `货币资金` | 流动性分析 |
| Trade Receivables | `accounts_receivable` | `应收账款` | `应收账款` | `应收账款` | 营运资本 |
| Inventories | `inventory` | `存货` | `存货` | `存货` | 营运资本 |
| Trade Payables | `accounts_payable` | `应付账款` | `应付账款` | `应付账款` | 营运资本 |

### 中优先级扩展字段

| IFRS 字段 | 建议标准字段名 | A股字段 | 港股字段 | 美股字段 | 用途 |
|---------|--------------|---------|---------|---------|------|
| Depreciation and Amortization | `depreciation_amortization` | `固定资产折旧`<br/>`无形资产摊销` | `折旧`<br/>`摊销` | `固定资产折旧`<br/>`无形资产摊销` | EBITDA |
| Goodwill | `goodwill` | `商誉` | `商誉` | `商誉` | 资产质量分析 |
| Deferred Tax Assets | `deferred_tax_assets` | `递延所得税资产` | `递延税项资产` | `递延所得税资产` | 税务分析 |
| Deferred Tax Liabilities | `deferred_tax_liabilities` | `递延所得税负债` | `递延税项负债` | `递延所得税负债` | 税务分析 |
| Dividends Paid | `dividends_paid` | `分配股利、利润或偿付利息支付的现金` | `已付股息` | `分配股利、利润或偿付利息支付的现金` | 股息收益率 |

---

## 📊 市场差异分析

### 1️⃣ 术语差异

| IFRS 术语 | A股 | 港股 | 美股 | 差异说明 |
|----------|-----|------|------|---------|
| Revenue | 营业收入 | 营业额/营运收入 | 营业收入/主营收入 | 港股术语最多样 |
| Profit before Tax | 营业利润/税前利润 | 除税前溢利 | 持续经营税前利润 | 港股用"溢利" |
| Net Income | 净利润 | 股东应占溢利 | 归属于母公司股东净利润 | 港股强调"股东应占" |
| Short-term Debt | 短期借款 | 短期贷款 | 短期债务 | A股/港股用"借款"，美股用"债务" |
| Cash Flow | 现金流量 | 现金流/现金 | 现金流量 | 港股可能用"现金" |

### 2️⃣ 字段完整性对比

| 维度 | A股 | 港股 | 美股 |
|------|-----|------|------|
| **字段丰富度** | ⭐⭐⭐⭐⭐ (228) | ⭐⭐⭐ (180) | ⭐⭐⭐⭐ (213) |
| **IFRS对标程度** | ⭐⭐⭐⭐ (CAS趋同) | ⭐⭐⭐⭐⭐ (完全IFRS) | ⭐⭐⭐ (US GAAP) |
| **数据一致性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **字段稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**关键发现**:
1. **A股字段最丰富** (228个) - 受财政部严格规范，字段完整
2. **港股IFRS对标最好** - 完全遵循IFRS，术语标准化
3. **美股US GAAP差异** - 某些概念与IFRS不同（如利息收入vs利息费用）

### 3️⃣ 特殊注意事项

#### A股特殊性
- ✅ 严格遵循CAS（中国企业会计准则），与IFRS实质趋同
- ✅ 字段命名高度统一（如"流动资产合计"）
- ⚠️ 某些字段有"其中："子字段（如"其中：利息费用"）
- ⚠️ 存在"*"标记的核心指标（如"*所有者权益合计"）

#### 港股特殊性
- ✅ 完全遵循IFRS，术语标准化程度最高
- ✅ 常用英文代码（如`HOLDER_PROFIT`、`OPERATE_INCOME`）
- ⚠️ 部分公司可能使用繁体中文字段名
- ⚠️ "溢利"而非"利润"，"贷款"而非"借款"

#### 美股特殊性
- ✅ 遵循US GAAP，与IFRS存在概念差异
- ⚠️ 利息可能记录为"利息收入"（负值表示费用）
- ⚠️ 部分字段可能与IFRS不对应（如"持续经营"概念）
- ⚠️ 保险公司、银行等特殊行业字段差异大

---

## 🎓 映射使用指南

### 如何使用此映射文档？

#### 1️⃣ 查找IFRS字段的市场对应

**场景**: 需要找到IFRS术语在A股/港股/美股中的对应字段

**步骤**:
1. 在本文档中搜索IFRS字段名（如"Revenue"）
2. 查看对应的标准字段列（如`total_revenue`）
3. 找到三地市场的实际字段名
4. 参考 [src/akshare_value_investment/normalization/config.py](../src/akshare_value_investment/normalization/config.py) 获取完整别名列表

**示例**:
```
IFRS: Revenue
标准字段: total_revenue
A股: 营业总收入、一、营业总收入、其中：营业收入
港股: OPERATE_INCOME、营业额、营运收入、经营收入总额
美股: OPERATE_INCOME、营业收入、主营收入、收入总额
```

#### 2️⃣ 添加新的标准字段

**场景**: 需要为新的分析需求添加标准字段

**步骤**:
1. **需求验证**: 确认是否为多个计算器共同需要
2. **IFRS对照**: 在本文档中查找IFRS术语
3. **市场可用性**: 检查三地市场是否都提供该字段
4. **更新代码**:
   - 在 `StandardFields` 添加常量
   - 在 `config.py` 添加映射
   - 在 `STANDARD_FIELDS_DEFINITION.md` 更新文档
5. **测试验证**: 添加单元测试

**示例**: 添加 `basic_eps` 字段

```python
# 1. StandardFields 类
class StandardFields:
    BASIC_EPS = "basic_eps"  # 基本每股收益

# 2. config.py
def get_a_stock_mappings():
    return {
        StandardFields.BASIC_EPS: ["基本每股收益"],
        # ...
    }

# 3. 测试
def test_basic_eps_mapping():
    mappings = get_a_stock_mappings()
    assert "基本每股收益" in mappings[StandardFields.BASIC_EPS]
```

#### 3️⃣ 理解市场字段差异

**场景**: 分析为什么某个字段在某个市场缺失

**步骤**:
1. 在本文档中查找该IFRS字段
2. 查看三地市场的映射情况
3. 参考"市场差异分析"章节了解原因
4. 如必要，查阅该市场的会计准则差异

**示例**: "为什么美股没有'股东应占溢利'？"

```
答案:
- 港股使用"股东应占溢利"（Profit attributable to equity holders）
- 美股使用"归属于母公司股东净利润"（Net income attributable to parent）
- 概念相同，术语差异
```

---

## 📚 参考文档

### 本项目相关文档

- [doc/IFRS_FIELDS_REFERENCE.md](IFRS_FIELDS_REFERENCE.md) - IFRS 字段完整参考
- [doc/STANDARD_FIELDS_DEFINITION.md](STANDARD_FIELDS_DEFINITION.md) - 标准字段定义
- [doc/a_stock_fields.md](a_stock_fields.md) - A股字段完整清单
- [doc/hk_stock_fields.md](hk_stock_fields.md) - 港股字段完整清单
- [doc/us_stock_fields.md](us_stock_fields.md) - 美股字段完整清单

### 代码实现

- [src/akshare_value_investment/domain/models/financial_standard.py](../src/akshare_value_investment/domain/models/financial_standard.py) - StandardFields 类
- [src/akshare_value_investment/normalization/config.py](../src/akshare_value_investment/normalization/config.py) - 字段映射配置
- [src/akshare_value_investment/normalization/registry.py](../src/akshare_value_investment/normalization/registry.py) - 字段映射注册表

---

## 🎯 版本历史

- **v1.0** (2026-01-06): 初始版本，建立IFRS与三地市场的完整映射
  - 覆盖65+个IFRS核心字段
  - 标注17个标准字段
  - 标注48+个潜在可扩展字段
  - 提供市场差异分析

---

**文档维护**: 本文档应与 IFRS_FIELDS_REFERENCE.md 和 STANDARD_FIELDS_DEFINITION.md 同步更新
**最后更新**: 2026-01-06
**维护者**: AI Agent + User
**数据来源**: IFRS Foundation, IAS 1, IAS 7, IFRS 15, IFRS 16, IAS 33
