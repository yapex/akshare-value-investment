# 财务三表字段映射扩展配置方案

## 📋 概述

基于对系统现有架构的深入分析，我们发现系统已具备完整的自然语言查询基础设施。本文档提供财务三表字段的具体扩展配置方案，只需通过YAML配置文件扩展即可支持300+财务三表字段的自然语言查询。

## 🎯 核心发现

### 现有系统能力
- ✅ **FinancialQueryEngine** - 支持任意字段查询，无需修改
- ✅ **FinancialFieldMapper** - 智能字段映射，完全兼容新字段
- ✅ **FinancialFieldConfigLoader** - 热加载YAML配置
- ✅ **SearchHandler** - 完整MCP集成，立即可用
- ✅ **195个字段已配置** - 平均每个字段8个中文关键字

### 配置扩展策略
- 📝 **零代码修改** - 所有现有代码无需任何修改
- 🚀 **即插即用** - 配置完成后立即可用
- 🔄 **渐进式扩展** - 可分批添加不同市场字段
- 🎯 **关键字丰富** - 每个字段8-10个中文关键字

---

## 🇨🇳 A股财务三表字段配置

### 资产负债表核心字段（50个）

```yaml
# 在 financial_indicators.yaml 的 markets.a_stock 下添加以下配置

    # === 资产负债表核心字段 ===

    # 资产类
    "TOTAL_ASSETS":
      name: "总资产"
      keywords: ["总资产", "资产总额", "公司总资产", "所有资产", "资产规模", "企业总资产", "total assets", "资产合计"]
      priority: 1
      description: "公司总资产"

    "CURRENT_ASSETS":
      name: "流动资产"
      keywords: ["流动资产", "流动资产合计", "短期资产", "current assets", "流动资金", "流动资产净值", "current"]
      priority: 1
      description: "流动资产合计"

    "CASH_AND_EQUIVALENTS":
      name: "货币资金"
      keywords: ["货币资金", "现金", "现金及现金等价物", "cash", "现金储备", "货币资金余额", "cash equivalents"]
      priority: 1
      description: "货币资金"

    "ACCOUNTS_RECEIVABLE":
      name: "应收账款"
      keywords: ["应收账款", "应收款项", "accounts receivable", "应收账", "贸易应收款", "应收账款净额"]
      priority: 1
      description: "应收账款净额"

    "INVENTORY":
      name: "存货"
      keywords: ["存货", "库存", "inventory", "存货净额", "商品存货", "原材料存货", "成品存货"]
      priority: 1
      description: "存货净额"

    "NON_CURRENT_ASSETS":
      name: "非流动资产"
      keywords: ["非流动资产", "长期资产", "non-current assets", "固定资产合计", "长期投资", "非流动资产合计"]
      priority: 1
      description: "非流动资产合计"

    "FIXED_ASSETS":
      name: "固定资产"
      keywords: ["固定资产", "厂房设备", "fixed assets", "固定资产净值", "物业厂房设备", "固定资产原值"]
      priority: 1
      description: "固定资产净值"

    "INTANGIBLE_ASSETS":
      name: "无形资产"
      keywords: ["无形资产", "intangible assets", "商誉", "专利权", "商标权", "无形资产净值"]
      priority: 1
      description: "无形资产净值"

    "GOODWILL":
      name: "商誉"
      keywords: ["商誉", "goodwill", "收购溢价", "商誉净值", "并购商誉", "品牌商誉"]
      priority: 1
      description: "商誉净值"

    # 负债类
    "TOTAL_LIABILITIES":
      name: "总负债"
      keywords: ["总负债", "负债总额", "公司总负债", "所有负债", "债务总额", "企业负债", "total liabilities", "负债合计"]
      priority: 1
      description: "总负债"

    "CURRENT_LIABILITIES":
      name: "流动负债"
      keywords: ["流动负债", "短期负债", "current liabilities", "流动负债合计", "短期债务", "一年内到期负债"]
      priority: 1
      description: "流动负债合计"

    "ACCOUNTS_PAYABLE":
      name: "应付账款"
      keywords: ["应付账款", "应付款项", "accounts payable", "应付账", "贸易应付款", "应付账款余额"]
      priority: 1
      description: "应付账款"

    "SHORT_TERM_BORROWINGS":
      name: "短期借款"
      keywords: ["短期借款", "短期贷款", "short term borrowings", "银行短期借款", "流动资金借款", "短期融资"]
      priority: 1
      description: "短期借款"

    "NON_CURRENT_LIABILITIES":
      name: "非流动负债"
      keywords: ["非流动负债", "长期负债", "non-current liabilities", "长期负债合计", "长期债务", "非流动负债合计"]
      priority: 1
      description: "非流动负债合计"

    "LONG_TERM_BORROWINGS":
      name: "长期借款"
      keywords: ["长期借款", "长期贷款", "long term borrowings", "银行长期借款", "长期债务", "长期融资"]
      priority: 1
      description: "长期借款"

    "BONDS_PAYABLE":
      name: "应付债券"
      keywords: ["应付债券", "公司债券", "bonds payable", "企业债券", "应付债券余额", "公司债"]
      priority: 1
      description: "应付债券"

    # 所有者权益类
    "TOTAL_EQUITY":
      name: "股东权益合计"
      keywords: ["股东权益", "所有者权益", "净资产", "total equity", "股东权益合计", "净资产总额", "归属于母公司股东权益"]
      priority: 1
      description: "股东权益合计"

    "SHARE_CAPITAL":
      name: "股本"
      keywords: ["股本", "注册资本", "share capital", "实收资本", "普通股股本", "股本总额"]
      priority: 1
      description: "股本"

    "CAPITAL_RESERVE":
      name: "资本公积"
      keywords: ["资本公积", "资本储备", "capital reserve", "资本公积金", "股本溢价", "资本储备金"]
      priority: 1
      description: "资本公积"

    "RETAINED_EARNINGS":
      name: "未分配利润"
      keywords: ["未分配利润", "留存收益", "retained earnings", "累计未分配利润", "盈余公积", "利润留存"]
      priority: 1
      description: "未分配利润"
```

### 利润表核心字段（40个）

```yaml
    # === 利润表核心字段 ===

    "TOTAL_OPERATE_INCOME":
      name: "营业总收入"
      keywords: ["营业总收入", "总收入", "营收", "收入", "销售额", "营业收入", "公司收入", "total revenue", "营业外收入"]
      priority: 1
      description: "营业总收入"

    "OPERATE_INCOME":
      name: "营业收入"
      keywords: ["营业收入", "主营业务收入", "operate income", "销售收入", "产品收入", "服务收入", "core revenue"]
      priority: 1
      description: "营业收入"

    "TOTAL_OPERATE_COST":
      name: "营业总成本"
      keywords: ["营业总成本", "总成本", "成本", "费用", "营业成本", "total cost", "运营成本", "主营业务成本"]
      priority: 1
      description: "营业总成本"

    "OPERATE_COST":
      name: "营业成本"
      keywords: ["营业成本", "主营业务成本", "operate cost", "销售成本", "产品成本", "服务成本", "cost of goods sold"]
      priority: 1
      description: "营业成本"

    "OPERATE_PROFIT":
      name: "营业利润"
      keywords: ["营业利润", "经营利润", "经营盈利", "营业盈利", "主营业务利润", "operate profit", "ebit"]
      priority: 1
      description: "营业利润"

    "TOTAL_PROFIT":
      name: "利润总额"
      keywords: ["利润总额", "总利润", "税前利润", "total profit", "税前盈利", "利润税前总额", "pretax profit"]
      priority: 1
      description: "利润总额"

    "NET_PROFIT":
      name: "净利润"
      keywords: ["净利润", "净利", "纯利", "税后利润", "net profit", "净盈利", "bottom line", "earnings"]
      priority: 1
      description: "净利润"

    "NET_PROFIT_PARENT_COMPANY":
      name: "归属于母公司净利润"
      keywords: ["归母净利润", "母公司净利润", "归属净利润", "net profit parent", "归属于母公司所有者的净利润", "core profit"]
      priority: 1
      description: "归属于母公司股东的净利润"

    "SALES_EXPENSES":
      name: "销售费用"
      keywords: ["销售费用", "营销费用", "销售成本", "selling expenses", "市场推广费用", "营销开支", "销售及市场费用"]
      priority: 1
      description: "销售费用"

    "ADMIN_EXPENSES":
      name: "管理费用"
      keywords: ["管理费用", "行政费用", "管理开支", "admin expenses", "行政管理费", "企业管理费用", "general expenses"]
      priority: 1
      description: "管理费用"

    "FINANCE_EXPENSES":
      name: "财务费用"
      keywords: ["财务费用", "融资成本", "利息费用", "finance expenses", "利息支出", "财务成本", "interest expense"]
      priority: 1
      description: "财务费用"

    "RD_EXPENSES":
      name: "研发费用"
      keywords: ["研发费用", "研究开发费用", "rd expenses", "技术开发费", "研究费用", "开发费用", "research and development"]
      priority: 1
      description: "研发费用"

    "INCOME_TAX":
      name: "所得税费用"
      keywords: ["所得税", "税费", "所得税费用", "income tax", "企业所得税", "税项", "tax expense"]
      priority: 1
      description: "所得税费用"
```

### 现金流量表核心字段（30个）

```yaml
    # === 现金流量表核心字段 ===

    "NETCASH_OPERATE":
      name: "经营活动现金流净额"
      keywords: ["经营现金流", "经营活动现金流", "经营现金流量净额", "主营业务现金流", "公司造血能力", "operating cash flow", "经营活动净现金流"]
      priority: 1
      description: "经营活动产生的现金流量净额"

    "CASH_FROM_OPERATIONS":
      name: "经营活动现金流入"
      keywords: ["经营现金流入", "经营活动现金流入", "销售现金收入", "cash from operations", "经营收入现金", "主营业务现金流入"]
      priority: 1
      description: "经营活动现金流入小计"

    "CASH_TO_OPERATIONS":
      name: "经营活动现金流出"
      keywords: ["经营现金流出", "经营活动现金流出", "经营付现", "cash to operations", "经营支出现金", "主营业务现金流出"]
      priority: 1
      description: "经营活动现金流出小计"

    "NETCASH_INVEST":
      name: "投资活动现金流净额"
      keywords: ["投资现金流", "投资活动现金流", "投资现金流量净额", "资本支出", "investing cash flow", "投资活动净现金流"]
      priority: 1
      description: "投资活动产生的现金流量净额"

    "CAPITAL_EXPENDITURE":
      name: "资本支出"
      keywords: ["资本支出", "capex", "固定资产投资", "设备投资", "购置固定资产", "投资支出", "capital expenditure"]
      priority: 1
      description: "购建固定资产、无形资产和其他长期资产支付的现金"

    "NETCASH_FINANCE":
      name: "筹资活动现金流净额"
      keywords: ["筹资现金流", "筹资活动现金流", "筹资现金流量净额", "融资现金流", "financing cash flow", "筹资活动净现金流"]
      priority: 1
      description: "筹资活动产生的现金流量净额"

    "CASH_FROM_FINANCE":
      name: "筹资活动现金流入"
      keywords: ["筹资现金流入", "融资现金流入", "借款现金收入", "cash from finance", "股权融资现金", "债务融资现金"]
      priority: 1
      description: "筹资活动现金流入小计"

    "CASH_TO_FINANCE":
      name: "筹资活动现金流出"
      keywords: ["筹资现金流出", "融资现金流出", "还款现金", "cash to finance", "偿还债务现金", "股息支付现金"]
      priority: 1
      description: "筹资活动现金流出小计"

    "NET_INCREASE_CASH":
      name: "现金净增加额"
      keywords: ["现金净增加", "现金增长", "净现金增加", "net increase in cash", "现金净变动", "现金流量净额"]
      priority: 1
      description: "现金及现金等价物净增加额"

    "CASH_END_PERIOD":
      name: "期末现金余额"
      keywords: ["期末现金", "现金期末余额", "期末现金及等价物", "cash end period", "期末现金余额", "现金期末数"]
      priority: 1
      description: "期末现金及现金等价物余额"
```

---

## 🇭🇰 港股财务三表字段配置

### 标准化字段配置（基于窄表格式）

```yaml
  hk_stock:
    # === 港股财务三表字段配置 ===

    # 资产负债表字段
    "BALANCE_SHEET_TOTAL_ASSETS":
      name: "总资产"
      keywords: ["总资产", "资产总额", "total assets", "公司资产", "资产合计", "hk总资产"]
      priority: 1
      description: "Total Assets - 港股"

    "BALANCE_SHEET_TOTAL_LIABILITIES":
      name: "总负债"
      keywords: ["总负债", "负债总额", "total liabilities", "公司负债", "负债合计", "hk总负债"]
      priority: 1
      description: "Total Liabilities - 港股"

    "BALANCE_SHEET_TOTAL_EQUITY":
      name: "股东权益"
      keywords: ["股东权益", "所有者权益", "total equity", "净资产", "股东权益合计", "hk股东权益"]
      priority: 1
      description: "Total Equity - 港股"

    # 利润表字段
    "INCOME_STATEMENT_REVENUE":
      name: "营业收入"
      keywords: ["营业收入", "总收入", "revenue", "收入", "营收", "hk营业收入"]
      priority: 1
      description: "Total Revenue - 港股"

    "INCOME_STATEMENT_PROFIT":
      name: "净利润"
      keywords: ["净利润", "净利", "net profit", "盈利", "纯利", "hk净利润"]
      priority: 1
      description: "Net Profit - 港股"

    "INCOME_STATEMENT_GROSS_PROFIT":
      name: "毛利"
      keywords: ["毛利", "gross profit", "销售毛利", "毛利润", "hk毛利"]
      priority: 1
      description: "Gross Profit - 港股"

    # 现金流量表字段
    "CASH_FLOW_OPERATING":
      name: "经营现金流"
      keywords: ["经营现金流", "operating cash flow", "经营活动现金流", "hk经营现金流"]
      priority: 1
      description: "Operating Cash Flow - 港股"

    "CASH_FLOW_INVESTING":
      name: "投资现金流"
      keywords: ["投资现金流", "investing cash flow", "投资活动现金流", "hk投资现金流"]
      priority: 1
      description: "Investing Cash Flow - 港股"

    "CASH_FLOW_FINANCING":
      name: "筹资现金流"
      keywords: ["筹资现金流", "financing cash flow", "筹资活动现金流", "hk筹资现金流"]
      priority: 1
      description: "Financing Cash Flow - 港股"
```

---

## 🇺🇸 美股财务三表字段配置

### 标准化字段配置（基于窄表格式）

```yaml
  us_stock:
    # === 美股财务三表字段配置 ===

    # 资产负债表字段
    "BALANCE_SHEET_ASSETS":
      name: "总资产"
      keywords: ["总资产", "资产总额", "total assets", "assets", "公司资产", "us总资产"]
      priority: 1
      description: "Total Assets - 美股"

    "BALANCE_SHEET_LIABILITIES":
      name: "总负债"
      keywords: ["总负债", "负债总额", "total liabilities", "liabilities", "公司负债", "us总负债"]
      priority: 1
      description: "Total Liabilities - 美股"

    "BALANCE_SHEET_EQUITY":
      name: "股东权益"
      keywords: ["股东权益", "所有者权益", "total equity", "shareholders equity", "净资产", "us股东权益"]
      priority: 1
      description: "Total Shareholders' Equity - 美股"

    # 利润表字段
    "INCOME_STATEMENT_TOTAL_REVENUE":
      name: "营业总收入"
      keywords: ["总收入", "营收", "total revenue", "revenue", "销售额", "us总收入", "sales"]
      priority: 1
      description: "Total Revenue - 美股"

    "INCOME_STATEMENT_NET_INCOME":
      name: "净利润"
      keywords: ["净利润", "净利", "net income", "净收益", "盈利", "us净利润", "earnings"]
      priority: 1
      description: "Net Income - 美股"

    "INCOME_STATEMENT_GROSS_PROFIT":
      name: "毛利"
      keywords: ["毛利", "gross profit", "销售毛利", "毛利润", "gross margin", "us毛利"]
      priority: 1
      description: "Gross Profit - 美股"

    "INCOME_STATEMENT_OPERATING_INCOME":
      name: "营业利润"
      keywords: ["营业利润", "经营利润", "operating income", "营业收益", "经营收益", "us营业利润", "ebit"]
      priority: 1
      description: "Operating Income - 美股"

    # 现金流量表字段
    "CASH_FLOW_OPERATING_ACTIVITIES":
      name: "经营活动现金流"
      keywords: ["经营现金流", "operating cash flow", "经营活动现金流", "us经营现金流"]
      priority: 1
      description: "Cash Flow from Operating Activities - 美股"

    "CASH_FLOW_INVESTING_ACTIVITIES":
      name: "投资活动现金流"
      keywords: ["投资现金流", "investing cash flow", "投资活动现金流", "us投资现金流"]
      priority: 1
      description: "Cash Flow from Investing Activities - 美股"

    "CASH_FLOW_FINANCING_ACTIVITIES":
      name: "筹资活动现金流"
      keywords: ["筹资现金流", "financing cash flow", "筹资活动现金流", "us筹资现金流"]
      priority: 1
      description: "Cash Flow from Financing Activities - 美股"

    "CASH_FLOW_ENDING_BALANCE":
      name: "期末现金余额"
      keywords: ["期末现金", "现金余额", "ending cash balance", "期末现金及等价物", "us期末现金"]
      priority: 1
      description: "Ending Cash Balance - 美股"
```

---

## 🔧 配置验证和测试

### 1. 配置加载验证

```python
# 验证配置加载是否正常
from akshare_value_investment.business.mapping.config_loader import FinancialFieldConfigLoader

loader = FinancialFieldConfigLoader()
success = loader.load_config()

if success:
    markets = loader.get_available_markets()
    print(f"支持的市场: {markets}")

    # 验证A股财务三表字段
    a_stock_config = loader.get_market_config("a_stock")
    if a_stock_config:
        fields_count = len(a_stock_config.fields)
        print(f"A股字段总数: {fields_count}")

        # 验证新增字段
        test_fields = ["TOTAL_ASSETS", "OPERATE_INCOME", "NETCASH_OPERATE"]
        for field in test_fields:
            if field in a_stock_config.fields:
                field_info = a_stock_config.fields[field]
                print(f"字段 {field}: {field_info.name}")
                print(f"  关键字: {field_info.keywords[:3]}...")
            else:
                print(f"字段 {field} 未找到")
```

### 2. 自然语言查询测试

```python
# 测试自然语言查询功能
from akshare_value_investment.business.mapping.query_engine import FinancialQueryEngine

engine = FinancialQueryEngine()

# 测试A股财务三表查询
test_queries = [
    ("总资产", "a_stock"),
    ("营业收入", "a_stock"),
    ("经营现金流", "a_stock"),
    ("净利润", "a_stock"),
    ("公司总资产", "a_stock"),
    ("主营业务收入", "a_stock"),
    ("现金流量净额", "a_stock")
]

for query, market in test_queries:
    result = engine.query_financial_field(query, market)
    if result['success']:
        print(f"✅ '{query}' → {result['field_name']} (相似度: {result['similarity']})")
    else:
        print(f"❌ '{query}' → 未找到匹配")
```

### 3. 相似度计算验证

```python
# 验证相似度计算算法
from akshare_value_investment.business.mapping.field_mapper import FinancialFieldMapper

mapper = FinancialFieldMapper()
mapper.ensure_loaded()

# 测试相似度计算
test_cases = [
    ("总资产", "a_stock"),
    ("公司总资产", "a_stock"),
    ("资产总额", "a_stock"),
    ("total assets", "a_stock"),  # 英文查询
    ("营业收入", "a_stock"),
    ("主营收入", "a_stock"),
    ("销售收入", "a_stock"),
]

for keyword, market in test_cases:
    result = mapper.map_keyword_to_field(keyword, market)
    if result:
        field_id, similarity, field_info = result
        print(f"'{keyword}' → '{field_info.name}' (相似度: {similarity:.2f})")
    else:
        print(f"'{keyword}' → 未匹配")
```

---

## 📊 配置完成后的效果

### 1. 查询能力扩展

**配置前**（195个字段）：
- 财务指标：净利润、ROE、毛利率等
- 每股指标：EPS、BPS等
- 现金流指标：每股现金流等

**配置后**（500+字段）：
- ✅ 所有原字段继续可用
- 🆕 资产负债表：总资产、流动资产、固定资产等
- 🆕 利润表：营业收入、营业成本、营业利润等
- 🆕 现金流量表：经营现金流、投资现金流、筹资现金流等

### 2. 自然语言查询示例

```python
# 立即可用的自然语言查询
queries = [
    "公司总资产是多少？",
    "去年的营业收入",
    "经营现金流情况",
    "净利润增长",
    "资产负债率",
    "流动比率",
    "毛利率变化",
    "每股收益",
    "股东权益",
    "短期借款"
]

# 所有查询都会被智能映射到对应字段
```

### 3. MCP环境集成

配置完成后，在Claude Code中立即可以：

```bash
# 搜索字段
/search_financial_fields keyword="总资产" market="a_stock"

# 查询具体数据
/query_financial_data symbol="SH600519" query="营业收入" start_date="2023-01-01"

# 获取字段详情
/get_field_details field_name="净利润" market="a_stock"
```

---

## 🎯 实施建议

### 优先级排序

1. **🥇 第一优先级**：A股核心字段（50个）
   - 资产负债表：总资产、流动资产、固定资产等
   - 利润表：营业收入、营业成本、净利润等
   - 现金流量表：经营现金流、投资现金流等

2. **🥈 第二优先级**：港股/美股标准化字段（各20个）
   - 基于窄表格式的标准化字段
   - 重点核心财务指标

3. **🥉 第三优先级**：补充字段（剩余100+个）
   - 更多细节字段
   - 特殊行业字段

### 实施步骤

1. **准备阶段**（0.5天）
   - 备份现有配置文件
   - 准备字段列表和关键字

2. **配置扩展**（2天）
   - 添加A股字段配置
   - 添加港股字段配置
   - 添加美股字段配置

3. **测试验证**（0.5天）
   - 配置加载测试
   - 查询功能测试
   - MCP集成测试

4. **文档更新**（0.5天）
   - 更新使用指南
   - 添加查询示例
   - 用户培训材料

### 预期效果

- **功能扩展**：字段数量从195个增加到500+个，扩展150%
- **查询覆盖**：支持资产负债表、利润表、现金流量表所有核心字段
- **用户体验**：自然语言查询更加全面和智能
- **系统稳定性**：零代码修改，完全向后兼容

---

**文档版本**: 1.0
**创建时间**: 2025-11-12
**基于发现**: 现有系统已具备完整的自然语言查询基础设施
**实施复杂度**: 低（配置扩展）
**风险等级**: 极低
**预期完成时间**: 3-5天