class StandardFields:
    """
    标准财务字段常量定义。

    设计原则：
    1. 基于IFRS（国际财务报告准则）框架
    2. 满足价值投资核心分析需求（ROIC、DCF等）
    3. 确保跨市场（A股、港股、美股）可用
    4. 只定义必需字段，避免过度设计

    所有的业务计算应仅依赖于这些标准字段，以屏蔽市场差异。

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
