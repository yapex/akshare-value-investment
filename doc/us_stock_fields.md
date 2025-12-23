# 美股财务数据字段清单

## 📋 概述

基于 FastAPI 字段发现 API 的完整 美股财务数据字段清单，包含财务指标、资产负债表、利润表和现金流量表的所有可用字段。

## 🔍 字段发现API端点

- **财务指标**: `GET /api/v1/financial/fields/us_stock/us_stock_indicators` (49个字段)
- **财务三表**: `GET /api/v1/financial/fields/us_stock/us_financial_statements`
  - 资产负债表: 45个字段
  - 利润表: 36个字段
  - 现金流量表: 40个字段

---

## 📊 美股财务数据接口

### 支持的查询类型 (4个接口)
- `us_stock_indicators` (美股财务指标)
- `us_stock_balance_sheet` (美股资产负债表)
- `us_stock_income_statement` (美股利润表)
- `us_stock_cash_flow` (美股现金流量表)

---

## 📈 财务指标字段 (49个)

### 📋 报表基础字段
- `SECUCODE` - 证券代码
- `SECURITY_CODE` - 证券代码
- `SECURITY_NAME_ABBR` - 证券简称
- `ORG_CODE` - 机构代码
- `SECURITY_INNER_CODE` - 证券内部代码
- `ACCOUNTING_STANDARDS` - 会计准则
- `NOTICE_DATE` - 公告日期
- `START_DATE` - 开始日期
- `REPORT_DATE` - 报告日期
- `FINANCIAL_DATE` - 财务日期
- `STD_REPORT_DATE` - 标准报告日期
- `CURRENCY` - 货币单位
- `DATE_TYPE` - 日期类型
- `DATE_TYPE_CODE` - 日期类型代码
- `REPORT_TYPE` - 报告类型
- `REPORT_DATA_TYPE` - 报告数据类型
- `ORGTYPE` - 机构类型
- `CURRENCY_ABBR` - 货币缩写

### 💰 盈利能力指标
- `OPERATE_INCOME` - 营业收入
- `OPERATE_INCOME_YOY` - 营业收入同比增长(%)
- `GROSS_PROFIT` - 毛利润
- `GROSS_PROFIT_YOY` - 毛利润同比增长(%)
- `PARENT_HOLDER_NETPROFIT` - 归属于母公司股东净利润
- `PARENT_HOLDER_NETPROFIT_YOY` - 归属于母公司股东净利润同比增长(%)
- `BASIC_EPS` - 基本每股收益
- `DILUTED_EPS` - 稀释每股收益
- `GROSS_PROFIT_RATIO` - 毛利率(%)
- `NET_PROFIT_RATIO` - 净利率(%)
- `ROE_AVG` - 平均净资产收益率(%)
- `ROA` - 总资产收益率(%)

### 📊 运营效率指标
- `ACCOUNTS_RECE_TR` - 应收账款周转率
- `INVENTORY_TR` - 存货周转率
- `TOTAL_ASSETS_TR` - 总资产周转率
- `ACCOUNTS_RECE_TDAYS` - 应收账款周转天数
- `INVENTORY_TDAYS` - 存货周转天数
- `TOTAL_ASSETS_TDAYS` - 总资产周转天数

### 💪 偿债能力指标
- `CURRENT_RATIO` - 流动比率
- `SPEED_RATIO` - 速动比率
- `OCF_LIQDEBT` - 经营现金流/流动负债
- `DEBT_ASSET_RATIO` - 资产负债率(%)
- `EQUITY_RATIO` - 权益乘数

### 📈 增长率指标
- `BASIC_EPS_YOY` - 基本每股收益同比增长(%)
- `GROSS_PROFIT_RATIO_YOY` - 毛利率同比增长(%)
- `NET_PROFIT_RATIO_YOY` - 净利率同比增长(%)
- `ROE_AVG_YOY` - 平均净资产收益率同比增长(%)
- `ROA_YOY` - 总资产收益率同比增长(%)
- `DEBT_ASSET_RATIO_YOY` - 资产负债率同比增长(%)
- `CURRENT_RATIO_YOY` - 流动比率同比增长(%)
- `SPEED_RATIO_YOY` - 速动比率同比增长(%)

---

## 📋 资产负债表字段 (45个)

### 📋 报表基础字段
- `REPORT_DATE` - 报告日期
- `SECURITY_CODE` - 证券代码
- `SECURITY_NAME_ABBR` - 证券简称

### 💰 资产类字段
- `TOTAL_ASSETS` - 总资产
- `CURRENT_ASSETS` - 流动资产合计
- `NON_CURRENT_ASSETS` - 非流动资产合计
- `CASH_EQUIVALENTS` - 现金及现金等价物
- `ACCOUNTS_RECEIVABLE` - 应收账款
- `INVENTORY` - 存货
- `PROPERTY_PLANT_EQUIPMENT` - 物业、厂房及设备
- `INTANGIBLE_ASSETS` - 无形资产
- `GOODWILL` - 商誉
- `OTHER_CURRENT_ASSETS` - 其他流动资产
- `OTHER_NON_CURRENT_ASSETS` - 其他非流动资产
- `MARKETABLE_SECURITIES_CURRENT` - 有价证券投资(流动)
- `MARKETABLE_SECURITIES_NON_CURRENT` - 有价证券投资(非流动)

### 💸 负债类字段
- `TOTAL_LIABILITIES` - 总负债
- `CURRENT_LIABILITIES` - 流动负债合计
- `NON_CURRENT_LIABILITIES` - 非流动负债合计
- `ACCOUNTS_PAYABLE` - 应付账款
- `SHORT_TERM_DEBT` - 短期债务
- `LONG_TERM_DEBT` - 长期负债
- `OTHER_CURRENT_LIABILITIES` - 其他流动负债
- `OTHER_NON_CURRENT_LIABILITIES` - 其他非流动负债
- `DEFERRED_TAX_LIABILITY_NON_CURRENT` - 递延所得税负债(非流动)
- `DEFERRED_TAX_ASSET_CURRENT` - 递延所得税资产(流动)

### 💎 股东权益字段
- `TOTAL_EQUITY` - 股东权益合计
- `PARENT_COMPANY_EQUITY` - 归属于母公司股东权益
- `MINORITY_INTERESTS` - 少数股东权益
- `TOTAL_LIABILITIES_EQUITY` - 负债及股东权益合计
- `ORDINARY_SHARE` - 普通股
- `PREFERRED_SHARE` - 优先股
- `RETAINED_EARNINGS` - 留存收益
- `RESERVES` - 储备
- `TREASURY_STOCK` - 库存股

### ⚠️ 其他字段
- `OTHER_RECEIVABLES` - 其他应收款
- `PREPAID_EXPENSES` - 预付费用
- `CASH_DEPOSITS` - 现金及存款
- `RESTRICTED_CASH` - 受限制现金
- `GOODWILL_NET` - 商誉净值
- `INVESTMENT_PROPERTY` - 投资性房地产
- `BANK_BORROWINGS` - 银行借款
- `BORROWINGS` - 借款
- `INTEREST_BEARING_BORROWINGS` - 计息借款
- `ACCUMULATED_OTHER_COMPREHENSIVE_INCOME` - 累计其他综合收益
- `SHAREHOLDER_EQUITY` - 股东权益

---

## 💹 利润表字段 (36个)

### 📋 报表基础字段
- `REPORT_DATE` - 报告日期
- `SECURITY_CODE` - 证券代码
- `SECURITY_NAME_ABBR` - 证券简称

### 📈 收入类指标
- `MAIN_BUSINESS_INCOME` - 主营业收入
- `MAIN_BUSINESS_COST` - 主营业务成本
- `GROSS_PROFIT` - 毛利润
- `OPERATING_INCOME` - 营业收入

### 💸 费用类指标
- `OPERATING_EXPENSE` - 营业费用
- `SELLING_EXPENSE` - 销售费用
- `ADMINISTRATIVE_EXPENSE` - 管理费用
- `RESEARCH_DEVELOPMENT_EXPENSE` - 研发费用
- `FINANCIAL_EXPENSE` - 财务费用
- `INTEREST_INCOME` - 利息收入
- `SELLING_GENERAL_ADMINISTRATIVE_EXPENSE` - 销售及管理费用

### 📊 利润类指标
- `OPERATING_PROFIT` - 营业利润
- `TOTAL_PROFIT` - 利润总额
- `INCOME_TAX_EXPENSE` - 所得税费用
- `NET_PROFIT` - 净利润
- `NET_PROFIT_PARENT_COMPANY` - 归属于母公司净利润
- `NET_PROFIT_MINORITY_INTERESTS` - 归属于少数股东净利润
- `TOTAL_COMPREHENSIVE_INCOME` - 综合收益总额
- `OTHER_INCOME` - 其他收益
- `OTHER_EXPENSE` - 其他费用
- `OTHER_BUSINESS_INCOME` - 其他业务收入
- `OTHER_BUSINESS_COST` - 其他业务成本
- `INVESTMENT_INCOME` - 投资收益
- `FAIR_VALUE_CHANGE_GAIN` - 公允价值变动收益
- `EXCHANGE_INCOME` - 汇兑收益
- `NON_OPERATING_INCOME` - 营业外收入
- `NON_OPERATING_EXPENSE` - 营业外支出
- `NET_NON_OPERATING_INCOME` - 营业外收入净额
- `EARNINGS_BEFORE_TAX` - 税前利润
- `NET_INCOME_LOSS_CONTINUING_OPERATIONS` - 持续经营业务净利润
- `NET_INCOME_LOSS_DISCONTINUED_OPERATIONS` - 终止经营业务净利润

### 📊 每股指标
- `BASIC_EPS` - 基本每股收益
- `DILUTED_EPS` - 稀释每股收益
- `EPS_WEIGHTED_AVERAGE_BASIC` - 基本加权平均每股收益
- `EPS_WEIGHTED_AVERAGE_DILUTED` - 稀释加权平均每股收益
- `DIVIDEND_PER_SHARE` - 每股股息

---

## 🌊 现金流量表字段 (40个)

### 📋 报表基础字段
- `REPORT_DATE` - 报告日期
- `SECURITY_CODE` - 证券代码
- `SECURITY_NAME_ABBR` - 证券简称

### 💰 一、经营活动产生的现金流量
- `NET_CASH_OPERATE` - 经营活动产生的现金流量净额
- `CASH_RECEIVE_FROM_SALE` - 销售商品、提供劳务收到的现金
- `CASH_PAID_FOR_GOODS_SERVICES` - 购买商品、接受劳务支付的现金
- `CASH_RECEIVE_FROM_TAX` - 收到的税费返还
- `CASH_PAID_TO_EMPLOYEE` - 支付给职工以及为职工支付的现金
- `CASH_PAID_FOR_TAXES` - 支付的各项税费
- `CASH_PAID_OTHER_OPERATE` - 支付其他与经营活动有关的现金
- `CASH_RECEIVE_OTHER_OPERATE` - 收到其他与经营活动有关的现金

### 🏗️ 二、投资活动产生的现金流量
- `NET_CASH_INVEST` - 投资活动产生的现金流量净额
- `CASH_RECEIVE_FROM_INVEST_INCOME` - 取得投资收益收到的现金
- `CASH_PAID_FOR_INVEST` - 投资支付的现金
- `CASH_RECEIVE_FROM_DISPOSAL_INVESTMENT` - 处置固定资产、无形资产和其他长期资产收回的现金净额
- `CASH_RECEIVE_FROM_DISPOSAL_SUBSIDIARY` - 处置子公司及其他营业单位收到的现金净额
- `CASH_PAID_FOR_ACQUISITION_LONGTERM_ASSET` - 购建固定资产、无形资产和其他长期资产支付的现金
- `CASH_RECEIVE_FROM_INVESTMENT` - 收到投资相关的现金
- `CASH_PAID_OTHER_INVEST` - 支付其他与投资活动有关的现金
- `CASH_RECEIVE_OTHER_INVEST` - 收到其他与投资活动有关的现金

### 💳 三、筹资活动产生的现金流量
- `NET_CASH_FINANCE` - 筹资活动产生的现金流量净额
- `CASH_RECEIVE_FROM_INVESTOR` - 吸收投资收到的现金
- `CASH_RECEIVE_FROM_BORROWING` - 取得借款收到的现金
- `CASH_PAID_FOR_REPAYMENT_BORROWING` - 偿还债务支付的现金
- `CASH_PAID_FOR_DIVIDEND` - 分配股利、利润或偿付利息支付的现金
- `CASH_PAID_FOR_SUBSIDIARY_INVESTOR` - 子公司支付给少数股东的股利、利润
- `CASH_PAID_OTHER_FINANCE` - 支付其他与筹资活动有关的现金
- `CASH_RECEIVE_OTHER_FINANCE` - 收到其他与筹资活动有关的现金

### 🔄 四、现金及现金等价物净增加额
- `CASH_INCREASE` - 现金及现金等价物净增加额
- `CASH_BEGINNING` - 现金及现金等价物期初余额
- `CASH_END` - 现金及现金等价物期末余额
- `FOREX_EFFECT_CASH` - 汇率变动对现金及现金等价物的影响

### 📊 补充资料
- `NET_INCOME_SUPPLEMENT` - 将净利润调节为经营活动现金流量
- `DEPRECIATION_AMORTIZATION` - 固定资产折旧、无形资产摊销
- `ASSET_IMPAIRMENT_LOSS` - 资产减值准备
- `FAIR_VALUE_CHANGE_LOSS` - 公允价值变动损失
- `INVESTMENT_LOSS` - 投资损失
- `DEFERRED_TAX_ASSET_DECREASE` - 递延所得税资产减少
- `DEFERRED_TAX_LIABILITY_INCREASE` - 递延所得税负债增加
- `INVENTORY_DECREASE_INCREASE` - 存货减少(增加)
- `ACCOUNTS_RECEIVABLE_DECREASE_INCREASE` - 经营性应收项目减少(增加)
- `ACCOUNTS_PAYABLE_DECREASE_INCREASE` - 经营性应付项目增加(减少)
- `OTHER_NON_CASH_ITEMS` - 其他非现金项目

---

## 📅 更新记录

- **2025-12-23**: 严格基于 FastAPI 字段发现 API 验证并更新所有字段
  - 修正API端点为财务三表聚合接口: `us_financial_statements`
  - 财务指标: 49个字段 ✅
  - 资产负债表: 45个字段 ✅
  - 利润表: 36个字段 ✅
  - 现金流量表: 40个字段 ✅
  - **总计**: 170个字段 ✅
- **数据来源**: FastAPI 字段发现API
- **验证端点**:
  - `GET /api/v1/financial/fields/us_stock/us_stock_indicators`
  - `GET /api/v1/financial/fields/us_stock/us_financial_statements`

---

## 📋 使用说明

### 1. API 调用格式

```python
import httpx

# 获取财务指标字段
response = httpx.get("http://localhost:8000/api/v1/financial/fields/us_stock/us_stock_indicators")
indicators_fields = response.json()["data"]["columns"]

# 获取财务三表字段
response = httpx.get("http://localhost:8000/api/v1/financial/fields/us_stock/us_financial_statements")
data = response.json()["data"]

# 资产负债表字段
balance_fields = data["balance_sheet"]["columns"]

# 利润表字段
income_fields = data["income_statement"]["columns"]

# 现金流量表字段
cashflow_fields = data["cash_flow"]["columns"]
```

### 2. 参数说明

- **market**: `us_stock` (美股市场)
- **query_type**:
  - `us_stock_indicators` (财务指标) - 财务绩效指标
  - `us_financial_statements` (财务三表) - 资产负债、盈利能力、现金流量

### 3. 注意事项

- 所有货币类字段根据市场规则以纯数字形式显示（如 15.00）
- 不同报表类型的数据具有相应的专业财务字段
- 字段数量随财务数据更新而动态变化
- 可根据实际需要查询最新字段配置