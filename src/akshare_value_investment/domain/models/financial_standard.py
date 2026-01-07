from .base_fields import StrictFieldMeta


class StandardFields(metaclass=StrictFieldMeta):
    """
    标准财务字段常量定义。

    设计原则：
    1. 基于IFRS（国际财务报告准则）框架
    2. 满足价值投资核心分析需求（ROIC、DCF等）
    3. 确保跨市场（A股、港股、美股）可用
    4. 只定义必需字段，避免过度设计

    所有的业务计算应仅依赖于这些标准字段，以屏蔽市场差异。

    使用StrictFieldMeta元类,防止子类意外覆盖标准字段。

    详见: doc/STANDARD_FIELDS_DEFINITION.md
    """
    # ========== 基础字段 ==========
    REPORT_DATE = "report_date"          # 报告期/财务日期

    # ========== 利润表字段 (Income Statement) ==========
    TOTAL_REVENUE = "total_revenue"      # 营业总收入/营业收入
    OPERATING_INCOME = "operating_income" # 营业利润/经营溢利 (EBIT)
    GROSS_PROFIT = "gross_profit"        # 毛利润
    NET_INCOME = "net_income"            # 净利润/股东应占溢利
    INCOME_TAX = "income_tax"            # 所得税费用
    INTEREST_EXPENSE = "interest_expense" # 利息费用/融资成本

    # ========== 资产负债表字段 (Balance Sheet) ==========
    TOTAL_ASSETS = "total_assets"        # 资产总计
    CURRENT_ASSETS = "current_assets"    # 流动资产合计
    TOTAL_LIABILITIES = "total_liabilities" # 负债合计
    CURRENT_LIABILITIES = "current_liabilities" # 流动负债合计
    TOTAL_EQUITY = "total_equity"        # 所有者权益合计/股东权益
    SHORT_TERM_DEBT = "short_term_debt"  # 短期借款/短期债务
    LONG_TERM_DEBT = "long_term_debt"    # 长期借款/长期债务

    # ========== 现金流量表字段 (Cash Flow Statement) ==========
    OPERATING_CASH_FLOW = "operating_cash_flow" # 经营活动产生的现金流量净额
    INVESTING_CASH_FLOW = "investing_cash_flow" # 投资活动产生的现金流量净额
    FINANCING_CASH_FLOW = "financing_cash_flow" # 筹资活动产生的现金流量净额

    # ========== 每股指标 (Per-Share Metrics) ==========
    BASIC_EPS = "basic_eps"              # 基本每股收益
    DILUTED_EPS = "diluted_eps"          # 稀释每股收益

    # ========== 营运资本字段 (Working Capital) ==========
    CASH_AND_EQUIVALENTS = "cash_and_equivalents" # 现金及现金等价物
    ACCOUNTS_RECEIVABLE = "accounts_receivable"   # 应收账款
    INVENTORY = "inventory"                        # 存货
    ACCOUNTS_PAYABLE = "accounts_payable"          # 应付账款

    # ========== 现金流量分析字段 (Cash Flow Analysis) ========== ✨ 新增
    CAPITAL_EXPENDITURE = "capital_expenditure"           # 资本支出 (FCF计算)
    DIVIDENDS_PAID = "dividends_paid"                     # 支付股利 (股息收益率)
    DEPRECIATION_AMORTIZATION = "depreciation_amortization" # 折旧摊销 (EBITDA计算)

    # ========== 利润表扩展字段 (Income Statement Extended) ========== ✨ 新增
    COST_OF_SALES = "cost_of_sales"                       # 营业成本 (毛利率分析)
    RD_EXPENSES = "rd_expenses"                           # 研发费用 (研发强度分析)

    # ========== 资产负债表扩展字段 (Balance Sheet Extended) ========== ✨ 新增
    PPE_NET = "ppe_net"                                   # 固定资产净值 (资产周转率)
    INTANGIBLE_ASSETS = "intangible_assets"               # 无形资产 (IAS 38)
    GOODWILL = "goodwill"                                 # 商誉 (IFRS 3)
    LONG_TERM_EQUITY_INVESTMENT = "long_term_equity_investment"  # 长期股权投资
    INVESTMENT_PROPERTY = "investment_property"           # 投资性房地产 (IAS 40)
    DEFERRED_TAX_ASSETS = "deferred_tax_assets"           # 递延所得税资产 (IAS 12)
    DEFERRED_TAX_LIABILITIES = "deferred_tax_liabilities" # 递延所得税负债 (IAS 12)

    # ========== 利润表扩展字段 (Income Statement Extended) ========== ✨ 新增
    SELLING_EXPENSES = "selling_expenses"                 # 销售费用 (费用率分析)
    ADMIN_EXPENSES = "admin_expenses"                     # 管理费用 (费用率分析)
    OTHER_INCOME = "other_income"                         # 其他收益 (盈利质量)

    # ========== 股东权益字段 (Shareholder Equity) ========== ✨ 新增
    ISSUED_CAPITAL = "issued_capital"                     # 股本 (IAS 1.80)
    SHARE_PREMIUM = "share_premium"                       # 资本公积 (IAS 1.80)
    RETAINED_EARNINGS = "retained_earnings"               # 留存收益 (IAS 1.80)
    OTHER_COMPREHENSIVE_INCOME = "other_comprehensive_income"  # 其他综合收益 (IAS 1.80)
    MINORITY_INTEREST = "minority_interest"               # 少数股东权益/非控股权益

    # ========== 其他资产负债表字段 ========== ✨ 新增
    CONTRACT_ASSETS = "contract_assets"                   # 合同资产 (IFRS 15)
    FINANCIAL_ASSETS = "financial_assets"                 # 金融资产 (IFRS 9)
    PREPAYMENTS = "prepayments"                           # 预付款项
    OTHER_CURRENT_ASSETS = "other_current_assets"         # 其他流动资产
    CONTRACT_LIABILITIES = "contract_liabilities"         # 合同负债 (IFRS 15)
    CURRENT_TAX_LIABILITIES = "current_tax_liabilities"   # 应交税费 (IAS 12)
    NON_CURRENT_ASSETS = "non_current_assets"             # 非流动资产合计 ✨新增
    CURRENT_PORTION_LONG_TERM_DEBT = "current_portion_long_term_debt"  # 一年内到期的长期债务 ✨新增

    # ========== 现金流量表详细字段 ========== ✨ 新增
    RECEIPTS_FROM_CUSTOMERS = "receipts_from_customers"   # 从客户收取的现金 (IAS 7.18)
    CASH_PAID_TO_SUPPLIERS = "cash_paid_to_suppliers"     # 支付给供应商的现金 (IAS 7.19)
    PROCEEDS_FROM_BORROWINGS = "proceeds_from_borrowings" # 借款收款 (IAS 7.30)

    # ========== 其他负债字段 (阶段2新增) ========== ✨ 新增
    OTHER_CURRENT_LIABILITIES = "other_current_liabilities"  # 其他流动负债
    PROVISIONS = "provisions"                                 # 预计负债 (IAS 37)

    # ========== 其他收益字段 (阶段2新增) ========== ✨ 新增
    FINANCE_INCOME = "finance_income"                         # 财务收益
    PROFIT_OF_ASSOCIATES = "profit_of_associates"             # 联营企业利润份额

    # ========== 现金流量表详细字段 (阶段2新增) ========== ✨ 新增
    CASH_PAID_TO_EMPLOYEES = "cash_paid_to_employees"         # 支付给员工的现金
    INCOME_TAXES_PAID = "income_taxes_paid"                   # 支付的所得税

    # ========== IFRS 16 租赁相关字段 (阶段3新增) ========== ✨ 新增
    RIGHT_OF_USE_ASSETS = "right_of_use_assets"               # 使用权资产 (IFRS 16)
    LEASE_LIABILITIES_CURRENT = "lease_liabilities_current"   # 租赁负债(当期) (IFRS 16)
    LEASE_LIABILITIES_NON_CURRENT = "lease_liabilities_non_current"  # 租赁负债(非流动) (IFRS 16)

    # ========== 筹资活动详细字段 (阶段3新增) ========== ✨ 新增
    PROCEEDS_FROM_ISSUING_SHARES = "proceeds_from_issuing_shares"  # 发行股票收款
    REPAYMENT_OF_BORROWINGS = "repayment_of_borrowings"            # 偿还借款
