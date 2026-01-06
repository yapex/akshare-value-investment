# IFRS 财务报表字段参考 (IFRS Financial Statement Fields Reference)

## 📋 概述

本文档提供了**国际财务报告准则 (IFRS)** 中定义的财务报表字段完整参考，供跨市场财务数据标准化时使用。

**数据来源**:
- IAS 1 - 财务报表列报 (Presentation of Financial Statements)
- IAS 7 - 现金流量表 (Statement of Cash Flows)
- IFRS 实例财务报表 2025

**与本项目的关系**:
- 本项目的 `StandardFields` 类基于 IFRS 核心字段设计
- 本文列出了完整的 IFRS 字段体系，供扩展时参考

---

## 🎯 IFRS 财务报表组成

根据 **IAS 1**，一套完整的财务报表包括：

1. **Statement of Financial Position** - 财务状况表（资产负债表）
2. **Statement of Profit or Loss** - 利得和损失表（利润表）
3. **Statement of Other Comprehensive Income** - 其他综合收益表
4. **Statement of Changes in Equity** - 权益变动表
5. **Statement of Cash Flows** - 现金流量表
6. **Notes** - 附注（包括重要会计政策）

---

## 📊 IFRS 核心字段体系

### 1️⃣ 财务状况表字段 (Statement of Financial Position)

#### 资产 (Assets)

| IFRS 字段名 | 中文名称 | IFRS 编号 | 本项目映射 | 说明 |
|------------|---------|----------|----------|------|
| **Current Assets** | 流动资产 | IAS 1.54 | ✅ `current_assets` | |
| ├── Cash and Cash Equivalents | 现金及现金等价物 | IAS 1.54 | | |
| ├── Trade and Other Receivables | 应收账款 | IAS 1.54 | | |
| ├── Financial Assets | 金融资产 | IFRS 9 | | |
| ├── Inventories | 存货 | IAS 2 | | |
| └── Prepayments | 预付款项 | | | |
| **Non-current Assets** | 非流动资产 | IAS 1.54 | | |
| ├── Property, Plant and Equipment | 不动产、厂房和设备 | IAS 16 | | |
| ├── Intangible Assets | 无形资产 | IAS 38 | | |
| ├── Goodwill | 商誉 | IFRS 3 | | |
| ├── Investment Properties | 投资性房地产 | IAS 40 | | |
| └── Deferred Tax Assets | 递延所得税资产 | IAS 12 | | |
| **Total Assets** | 资产总计 | IAS 1.54 | ✅ `total_assets` | |

#### 负债 (Liabilities)

| IFRS 字段名 | 中文名称 | IFRS 编号 | 本项目映射 | 说明 |
|------------|---------|----------|----------|------|
| **Current Liabilities** | 流动负债 | IAS 1.60 | ✅ `current_liabilities` | |
| ├── Trade and Other Payables | 应付账款 | IAS 1.60 | | |
| ├── Short-term Debt | 短期债务 | | ✅ `short_term_debt` | |
| ├── Current Portion of Long-term Debt | 一年内到期的长期债务 | | | |
| └── Current Tax Liabilities | 当期所得税负债 | IAS 12 | | |
| **Non-current Liabilities** | 非流动负债 | IAS 1.60 | | |
| ├── Long-term Debt | 长期债务 | | ✅ `long_term_debt` | |
| ├── Deferred Tax Liabilities | 递延所得税负债 | IAS 12 | | |
| ├── Provisions | 预计负债 | IAS 37 | | |
| └── Lease Liabilities | 租赁负债 | IFRS 16 | | |
| **Total Liabilities** | 负债总计 | IAS 1.60 | ✅ `total_liabilities` | |

#### 权益 (Equity)

| IFRS 字段名 | 中文名称 | IFRS 编号 | 本项目映射 | 说明 |
|------------|---------|----------|----------|------|
| **Issued Capital** | 发行股本 | IAS 1.80 | | |
| **Share Premium** | 股本溢价 | IAS 1.80 | | |
| **Retained Earnings** | 留存收益 | IAS 1.80 | | |
| **Other Comprehensive Income** | 其他综合收益 | IAS 1.80 | | |
| **Total Equity** | 权益总计 | IAS 1.54 | ✅ `total_equity` | |

---

### 2️⃣ 利得和损失表字段 (Statement of Profit or Loss)

#### 收入 (Revenue)

| IFRS 字段名 | 中文名称 | IFRS 编号 | 本项目映射 | 说明 |
|------------|---------|----------|----------|------|
| **Revenue** | 收入/营业收入 | IFRS 15 | ✅ `total_revenue` | |
| ├── Revenue from Contracts with Customers | 与客户合同产生的收入 | IFRS 15 | | |
| └── Other Income | 其他收入 | | | |

#### 费用 (Expenses)

| IFRS 字段名 | 中文名称 | IFRS 编号 | 本项目映射 | 说明 |
|------------|---------|----------|----------|------|
| **Cost of Sales** | 销售成本/营业成本 | | | |
| **Gross Profit** | 毛利润 | | ✅ `gross_profit` | Revenue - Cost of Sales |
| ├── Other Income | 其他收益 | | | |
| ├── Selling Expenses | 销售费用 | | | |
| ├── Administrative Expenses | 管理费用 | | | |
| ├── Research and Development Expenses | 研发费用 | | | |
| ├── Other Expenses | 其他费用 | | | |
| **Finance Costs** | 财务费用/利息费用 | IAS 1.82 | ✅ `interest_expense` | |
| **Profit before Tax** | 税前利润 | | ✅ `operating_income` | EBIT 近似值 |
| ├── Income Tax Expense | 所得税费用 | IAS 12 | ✅ `income_tax` | |
| └── **Profit for the Year** | 当期净利润 | IAS 1.82 | ✅ `net_income` | |

---

### 3️⃣ 现金流量表字段 (Statement of Cash Flows)

根据 **IAS 7**，现金流量表应按经营活动、投资活动和筹资活动分类。

#### 经营活动 (Operating Activities)

| IFRS 字段名 | 中文名称 | IAS 7 编号 | 本项目映射 | 说明 |
|------------|---------|-----------|----------|------|
| **Cash Flows from Operating Activities** | 经营活动现金流量 | IAS 7.14 | | |
| ├── Receipts from Customers | 从客户收取的现金 | IAS 7.18 | | |
| ├── Cash Paid to Suppliers | 支付给供应商的现金 | IAS 7.19 | | |
| ├── Cash Paid to Employees | 支付给员工的现金 | IAS 7.19 | | |
| ├── Income Taxes Paid | 支付的所得税 | IAS 7.21 | | |
| └── **Net Cash from Operating Activities** | 经营活动现金流量净额 | IAS 7.14 | ✅ `operating_cash_flow` | |

#### 投资活动 (Investing Activities)

| IFRS 字段名 | 中文名称 | IAS 7 编号 | 本项目映射 | 说明 |
|------------|---------|-----------|----------|------|
| **Cash Flows from Investing Activities** | 投资活动现金流量 | IAS 7.14 | | |
| ├── Capital Expenditures | 资本支出 | IAS 7.23 | | 购建固定资产 |
| ├── Proceeds from Sales of PPE | 出售固定资产收款 | IAS 7.23 | | |
| ├── Acquisition of Subsidiaries | 收购子公司 | IAS 7.25 | | |
| └── **Net Cash from Investing Activities** | 投资活动现金流量净额 | IAS 7.14 | ✅ `investing_cash_flow` | |

#### 筹资活动 (Financing Activities)

| IFRS 字段名 | 中文名称 | IAS 7 编号 | 本项目映射 | 说明 |
|------------|---------|-----------|----------|------|
| **Cash Flows from Financing Activities** | 筹资活动现金流量 | IAS 7.14 | | |
| ├── Proceeds from Issuing Shares | 发行股票收款 | IAS 7.29 | | |
| ├── Proceeds from Borrowings | 借款收款 | IAS 7.30 | | |
| ├── Repayment of Borrowings | 偿还借款 | IAS 7.30 | | |
| ├── Dividends Paid | 支付股利 | IAS 7.31 | | |
| └── **Net Cash from Financing Activities** | 筹资活动现金流量净额 | IAS 7.14 | ✅ `financing_cash_flow` | |

---

## 🔗 IFRS 字段与本项目标准字段映射

### ✅ 已映射的标准字段 (17个)

| 本项目标准字段 | IFRS 术语 | IAS 编号 | 用途 |
|-------------|----------|---------|------|
| `report_date` | Reporting Date | IAS 1.38 | 报告日期 |
| `total_revenue` | Revenue | IFRS 15 | 营业收入 |
| `operating_income` | Profit before Tax | IAS 1.82 | 营业利润/EBIT |
| `gross_profit` | Gross Profit | IAS 1.82 | 毛利润 |
| `net_income` | Profit for the Year | IAS 1.82 | 净利润 |
| `income_tax` | Income Tax Expense | IAS 12 | 所得税费用 |
| `interest_expense` | Finance Costs | IAS 1.82 | 利息费用 |
| `total_assets` | Total Assets | IAS 1.54 | 资产总计 |
| `current_assets` | Current Assets | IAS 1.54 | 流动资产 |
| `total_liabilities` | Total Liabilities | IAS 1.60 | 负债合计 |
| `current_liabilities` | Current Liabilities | IAS 1.60 | 流动负债 |
| `total_equity` | Total Equity | IAS 1.54 | 权益合计 |
| `short_term_debt` | Short-term Debt | | 短期借款 |
| `long_term_debt` | Long-term Debt | | 长期借款 |
| `operating_cash_flow` | Net Cash from Operating Activities | IAS 7.14 | 经营现金流 |
| `investing_cash_flow` | Net Cash from Investing Activities | IAS 7.14 | 投资现金流 |
| `financing_cash_flow` | Net Cash from Financing Activities | IAS 7.14 | 筹资现金流 |

### ⚠️ 潜在可扩展字段 (未来可选)

| IFRS 字段 | 中文名称 | 可能用途 |
|----------|---------|---------|
| Capital Expenditures | 资本支出 | FCF 计算 |
| Depreciation and Amortization | 折旧和摊销 | EBITDA 计算 |
| Basic Earnings per Share | 基本每股收益 | 每股分析 |
| Diluted Earnings per Share | 稀释每股收益 | 每股分析 |
| Inventories | 存货 | 营运资本周转率 |
| Trade Receivables | 应收账款 | 营运资本分析 |
| Trade Payables | 应付账款 | 营运资本分析 |
| Dividends Paid | 支付股利 | 股息收益率 |

---

## 📚 IFRS 完整字段清单

### 按报表类型分类

#### 财务状况表 (Balance Sheet) - 约 30+ 个核心字段

**资产侧**:
1. Current Assets - 流动资产
   - Cash and Cash Equivalents - 现金及现金等价物
   - Trade and Other Receivables - 应收账款
   - Contract Assets - 合同资产
   - Financial Assets - 金融资产
   - Inventories - 存货
   - Prepayments - 预付款项
   - Other Current Assets - 其他流动资产

2. Non-current Assets - 非流动资产
   - Property, Plant and Equipment (PPE) - 不动产、厂房和设备
   - Intangible Assets - 无形资产
   - Goodwill - 商誉
   - Investment Properties - 投资性房地产
   - Right-of-Use Assets - 使用权资产
   - Deferred Tax Assets - 递延所得税资产
   - Other Non-current Assets - 其他非流动资产

**负债侧**:
3. Current Liabilities - 流动负债
   - Trade and Other Payables - 应付账款
   - Contract Liabilities - 合同负债
   - Short-term Borrowings - 短期借款
   - Current Portion of Long-term Debt - 一年内到期的长期债务
   - Current Tax Liabilities - 当期所得税负债
   - Lease Liabilities - 租赁负债（当期部分）
   - Provisions - 预计负债
   - Other Current Liabilities - 其他流动负债

4. Non-current Liabilities - 非流动负债
   - Long-term Borrowings - 长期借款
   - Deferred Tax Liabilities - 递延所得税负债
   - Lease Liabilities - 租赁负债（非流动部分）
   - Provisions - 预计负债
   - Other Non-current Liabilities - 其他非流动负债

**权益侧**:
5. Equity - 权益
   - Issued Capital - 发行股本
   - Share Premium - 股本溢价
   - Retained Earnings - 留存收益
   - Revaluation Reserve - 重估储备
   - Other Reserves - 其他储备
   - Non-controlling Interests - 非控制性权益

#### 利得和损失表 (Income Statement) - 约 20+ 个核心字段

**收入和费用**:
1. Revenue - 收入/营业收入
2. Cost of Sales - 销售成本
3. Gross Profit - 毛利润
4. Other Income - 其他收益
5. Distribution Costs - 分销费用
6. Administrative Expenses - 管理费用
7. Research and Development Expenses - 研发费用
8. Other Expenses - 其他费用
9. Finance Costs - 财务费用
10. Finance Income - 财务收益
11. Share of Profit of Associates - 联营企业利润份额
12. Profit before Tax - 税前利润
13. Income Tax Expense - 所得税费用
14. Profit for the Year - 当期净利润

**每股收益**:
15. Basic Earnings per Share - 基本每股收益
16. Diluted Earnings per Share - 稀释每股收益

#### 现金流量表 (Cash Flow Statement) - 约 15+ 个核心字段

**经营活动**:
1. Receipts from Customers - 从客户收取的现金
2. Cash Paid to Suppliers and Employees - 支付给供应商和员工的现金
3. Cash Paid for Taxes - 支付的税费
4. Other Operating Cash Flows - 其他经营活动现金流量
5. **Net Cash from Operating Activities** - 经营活动现金流量净额 ✅

**投资活动**:
6. Capital Expenditures - 资本支出
7. Proceeds from Sales of PPE - 出售固定资产收款
8. Acquisition of Subsidiaries, net of cash acquired - 收购子公司净现金
9. Proceeds from Sales of Subsidiaries - 出售子公司收款
10. Interest and Dividends Received - 收到的利息和股利
11. **Net Cash from Investing Activities** - 投资活动现金流量净额 ✅

**筹资活动**:
12. Proceeds from Issuing Shares - 发行股票收款
13. Proceeds from Borrowings - 借款收款
14. Repayment of Borrowings - 偿还借款
15. Dividends Paid - 支付股利
16. Interest Paid - 支付利息
17. **Net Cash from Financing Activities** - 筹资活动现金流量净额 ✅

---

## 🎯 IFRS 核心准则速查

### IAS 1 - 财务报表列报

**核心要求**:
- 财务报表必须公允呈现
- 必须包含完整的资产负债表、利润表、现金流量表、权益变动表和附注
- 必须提供比较信息（至少上一期间）
- 必须明确区分流动和非流动项目

**关键字段定义**:
- **流动资产**: 预期在12个月内变现、出售或消耗的资产
- **流动负债**: 预期在12内结算的负债

### IAS 7 - 现金流量表

**核心要求**:
- 现金流量必须按经营、投资、筹资活动分类
- 鼓励采用直接法报告经营活动现金流量
- 必须披露利息和股利的支付/收到金额

**现金定义**:
- 库存现金和银行存款
- 现金等价物（3个月内到期的短期投资）

### IFRS 15 - 客户合同收入

**核心原则**:
- 识别与客户的合同
- 识别合同中的履约义务
- 确定交易价格
- 分摊交易价格至履约义务
- 在履行履约义务时确认收入

### IFRS 16 - 租赁

**核心变化**:
- 承租人必须确认使用权资产和租赁负债
- 出租人分类为融资租赁或经营租赁

### IFRS 9 - 金融工具

**核心要求**:
- 金融资产分类：摊余成本、公允价值通过其他综合收益、公允价值通过损益
- 金融负债分类：摊余成本、公允价值通过损益
- 套期会计

---

## 📖 参考资料

### 官方 IFRS 文档

1. **IFRS Foundation** - https://www.ifrs.org/
   - IFRS 会计准则完整文本
   - IFRS 实例财务报表

2. **IASPlus** - https://www.iasplus.com/
   - IFRS 准则解读和比较
   - 国家间准则差异分析

3. **Grant Thornton IFRS Example Financial Statements 2025**
   - 实例财务报表
   - 披露示例

### 本项目相关文档

- [doc/STANDARD_FIELDS_DEFINITION.md](STANDARD_FIELDS_DEFINITION.md) - 标准字段定义
- [doc/a_stock_fields.md](a_stock_fields.md) - A股字段说明
- [doc/hk_stock_fields.md](hk_stock_fields.md) - 港股字段说明
- [doc/us_stock_fields.md](us_stock_fields.md) - 美股字段说明
- [src/akshare_value_investment/domain/models/financial_standard.py](../src/akshare_value_investment/domain/models/financial_standard.py) - StandardFields 类定义
- [src/akshare_value_investment/normalization/config.py](../src/akshare_value_investment/normalization/config.py) - 字段映射配置

---

## 🎓 使用指南

### 如何添加新的标准字段？

1. **需求验证**: 确认业务计算器确实需要此字段
2. **IFRS 对照**: 在本文档中查找对应的 IFRS 术语
3. **市场可用性**: 检查三地市场 API 是否提供该字段
4. **更新配置**:
   - 在 `StandardFields` 类添加常量
   - 在 `config.py` 添加映射
   - 更新 `STANDARD_FIELDS_DEFINITION.md`
5. **测试验证**: 添加单元测试确保映射正确

### IFRS 字段查找技巧

1. **已知中文**: 在本文档中使用 `Ctrl+F` 搜索中文名称
2. **已知英文**: 在本文档中搜索英文术语
3. **不确定类型**: 先确定属于哪个报表（资产负债表/利润表/现金流量表）
4. **查看 IFRS 编号**: 参考 IAS/IFRS 编号直接查阅官方准则

---

**文档版本**: v1.0
**最后更新**: 2026-01-06
**维护者**: AI Agent + User
**数据来源**: IFRS Foundation, IAS 1, IAS 7, IFRS 15, IFRS 16, IFRS 9
