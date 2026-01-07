"""
港股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class HKStockMarketFields(StandardFields):
    """
    港股市场字段 = IFRS标准字段 + 港股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        HKStockMarketFields (港股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[HKStockMarketFields.TOTAL_REVENUE]

        # 港股特定字段 (未来添加)
        # goodwill = df[HKStockMarketFields.GOODWILL]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加港股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== 港股特定字段 ========== ✨ 新增

    # ========== 资产负债表特有字段 ==========
    # 流动资产特有
    MEDIUM_LONG_TERM_DEPOSITS = "hk_medium_long_term_deposits"  # 中长期存款
    REDEEMABLE_INSTRUMENTS_ASSOCIATES = "hk_redeemable_instruments_associates"  # 于联营公司可赎回工具的投资
    AVAILABLE_FOR_SALE_INVESTMENT = "hk_available_for_sale_investment"  # 可供出售投资
    JOINT_VENTURE_EQUITY = "hk_joint_venture_equity"  # 合营公司权益
    LAND_USE_RIGHTS = "hk_land_use_rights"  # 土地使用权
    ASSETS_HELD_FOR_SALE = "hk_assets_held_for_sale"  # 持作出售的资产(流动)
    HELD_TO_MATURITY_INVESTMENT_CURRENT = "hk_held_to_maturity_investment_current"  # 持有至到期投资(流动)
    DESIGNATED_FINANCIAL_ASSETS = "hk_designated_financial_assets"  # 指定以公允价值记账之金融资产
    DESIGNATED_FINANCIAL_ASSETS_CURRENT = "hk_designated_financial_assets_current"  # 指定以公允价值记账之金融资产(流动)
    OTHER_FINANCIAL_ASSETS_CURRENT = "hk_other_financial_assets_current"  # 其他金融资产(流动)
    OTHER_FINANCIAL_ASSETS_NON_CURRENT = "hk_other_financial_assets_non_current"  # 其他金融资产(非流动)
    SHORT_TERM_DEPOSITS = "hk_short_term_deposits"  # 短期存款
    RESTRICTED_DEPOSITS_CASH = "hk_restricted_deposits_cash"  # 受限制存款及现金
    PREPAYMENTS_OTHER_RECEIVABLES = "hk_prepayments_other_receivables"  # 预付款按金及其他应收款
    RECEIVABLES_RELATED_PARTIES = "hk_receivables_related_parties"  # 应收关联方款项
    PROPERTY_PLANT_EQUIPMENT = "hk_property_plant_equipment"  # 物业厂房及设备
    OTHER_NON_CURRENT_ASSETS_ITEMS = "hk_other_non_current_assets_items"  # 非流动资产其他项目

    # 流动负债特有
    PAYABLES_RELATED_PARTIES_CURRENT = "hk_payables_related_parties_current"  # 应付关联方款项(流动)
    NOTES_PAYABLE = "hk_notes_payable"  # 应付票据
    NOTES_PAYABLE_NON_CURRENT = "hk_notes_payable_non_current"  # 应付票据(非流动)
    OTHER_PAYABLES_ACCRUED_EXPENSES = "hk_other_payables_accrued_expenses"  # 其他应付款及应计费用
    OTHER_FINANCIAL_LIABILITIES_CURRENT = "hk_other_financial_liabilities_current"  # 其他金融负债(流动)
    OTHER_FINANCIAL_LIABILITIES_NON_CURRENT = "hk_other_financial_liabilities_non_current"  # 其他金融负债(非流动)
    FINANCE_LEASE_LIABILITIES_CURRENT = "hk_finance_lease_liabilities_current"  # 融资租赁负债(流动)
    FINANCE_LEASE_LIABILITIES_NON_CURRENT = "hk_finance_lease_liabilities_non_current"  # 融资租赁负债(非流动)
    DERIVATIVES_LIABILITIES_CURRENT = "hk_derivatives_liabilities_current"  # 衍生金融工具-负债(流动)
    DEFERRED_INCOME_CURRENT = "hk_deferred_income_current"  # 递延收入(流动)
    DEFERRED_INCOME_NON_CURRENT = "hk_deferred_income_non_current"  # 递延收入(非流动)
    LONG_TERM_PAYABLES_OTHER = "hk_long_term_payables_other"  # 长期应付款

    # 所有者权益特有
    TOTAL_EQUITY_AND_LIABILITIES = "hk_total_equity_and_liabilities"  # 总权益及总负债
    TOTAL_EQUITY_AND_NON_CURRENT_LIABILITIES = "hk_total_equity_and_non_current_liabilities"  # 总权益及非流动负债
    SHARE_CAPITAL_PREMIUM = "hk_share_capital_premium"  # 股本溢价
    RESERVES = "hk_reserves"  # 储备
    OTHER_RESERVES = "hk_other_reserves"  # 其他储备
    RETAINED_EARNINGS_DEFICIT = "hk_retained_earnings_deficit"  # 保留溢利(累计亏损)
    NET_ASSETS = "hk_net_assets"  # 净资产
    NET_CURRENT_ASSETS = "hk_net_current_assets"  # 净流动资产
    TOTAL_ASSETS_MINUS_LIABILITIES = "hk_total_assets_minus_liabilities"  # 总资产减总负债合计
    TOTAL_ASSETS_MINUS_CURRENT_LIABILITIES = "hk_total_assets_minus_current_liabilities"  # 总资产减流动负债

    # ========== 利润表特有字段 ==========
    # 收入与其他收益
    OPERATING_REVENUE = "hk_operating_revenue"  # 营运收入
    OTHER_OPERATING_REVENUE = "hk_other_operating_revenue"  # 其他营业收入
    PROFIT_BEFORE_TAX = "hk_profit_before_tax"  # 除税前溢利
    PROFIT_AFTER_TAX = "hk_profit_after_tax"  # 除税后溢利
    PROFIT_ATTRIBUTABLE_TO_ASSOCIATES = "hk_profit_attributable_to_associates"  # 应占合营公司溢利

    # 费用指标
    OPERATING_EXPENDITURE = "hk_operating_expenditure"  # 营运支出
    SELLING_DISTRIBUTION_EXPENSES = "hk_selling_distribution_expenses"  # 销售及分销费用
    ADMINISTRATIVE_EXPENSES_HK = "hk_administrative_expenses"  # 行政开支

    # 其他收益项目
    NON_OPERATING_ITEMS = "hk_non_operating_items"  # 非运算项目
    OTHER_PROFIT_ITEMS = "hk_other_profit_items"  # 溢利其他项目

    # 每股与股息指标
    DIVIDENDS_PER_SHARE = "hk_dividends_per_share"  # 每股股息
    DIVIDENDS = "hk_dividends"  # 股息

    # 综合收益
    TOTAL_COMPREHENSIVE_INCOME_HK = "hk_total_comprehensive_income"  # 全面收益总额
    OTHER_COMPREHENSIVE_INCOME_ITEMS = "hk_other_comprehensive_income_items"  # 其他全面收益其他项目
    COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_COMP = "hk_comprehensive_income_attributable_to_comp"  # 本公司拥有人应占全面收益总额
    COMPREHENSIVE_INCOME_NON_CONTROLLING = "hk_comprehensive_income_non_controlling"  # 非控股权益应占全面收益总额

    # ========== 现金流量表特有字段 ==========
    # 经营活动
    PROFIT_BEFORE_TAX_OPERATING = "hk_profit_before_tax_operating"  # 除税前溢利(业务利润)
    ADD_INTEREST_EXPENSE = "hk_add_interest_expense"  # 加:利息支出
    ADD_DEPRECIATION_AMORTIZATION = "hk_add_depreciation_amortization"  # 加:折旧及摊销
    ADD_IMPAIRMENT_PROVISIONS = "hk_add_impairment_provisions"  # 加:减值及拨备
    ADD_OPERATING_ADJUSTMENT_OTHER = "hk_add_operating_adjustment_other"  # 加:经营调整其他项目
    OPERATING_PROFIT_BEFORE_WORKING_CAPITAL = "hk_operating_profit_before_working_capital"  # 营运资金变动前经营溢利
    INVENTORY_INCREASE_DECREASE = "hk_inventory_increase_decrease"  # 存货(增加)减少
    RECEIVABLES_DECREASE = "hk_receivables_decrease"  # 应收帐款减少
    PREPAYMENTS_DECREASE_INCREASE = "hk_prepayments_decrease_increase"  # 预付款项、按金及其他应收款项减少(增加)
    PAYABLES_INCREASE_DECREASE = "hk_payables_increase_decrease"  # 应付帐款及应计费用增加(减少)
    DEFERRED_INCOME_INCREASE_DECREASE = "hk_deferred_income_increase_decrease"  # 预收账款、按金及其他应付款增加(减少)
    PAYABLES_RELATED_PARTIES_INCREASE_DECREASE = "hk_payables_related_parties_increase_decrease"  # 应付关联方款项增加(减少)
    WORKING_CAPITAL_CHANGE_OTHER = "hk_working_capital_change_other"  # 营运资本变动其他项目
    INTEREST_PAID_OPERATING = "hk_interest_paid_operating"  # 已付利息(经营)
    TAX_PAID = "hk_tax_paid"  # 已付税项

    # 投资活动
    SUBTRACT_INTEREST_INCOME = "hk_subtract_interest_income"  # 减:利息收入
    SUBTRACT_ASSOCIATES_PROFIT = "hk_subtract_associates_profit"  # 减:应占附属公司溢利
    SUBTRACT_INVESTMENT_INCOME = "hk_subtract_investment_income"  # 减:投资收益
    INTEREST_RECEIVED_INVESTING = "hk_interest_received_investing"  # 已收利息(投资)
    DIVIDENDS_RECEIVED_INVESTING = "hk_dividends_received_investing"  # 已收股息(投资)
    DISPOSAL_FIXED_ASSETS = "hk_disposal_fixed_assets"  # 处置固定资产
    DISPOSAL_INTANGIBLE_OTHER_ASSETS = "hk_disposal_intangible_other_assets"  # 处置无形资产及其他资产
    DISPOSAL_SUBSIDIARIES = "hk_disposal_subsidiaries"  # 出售附属公司
    SUBTRACT_DISPOSAL_GAIN = "hk_subtract_disposal_gain"  # 减:出售资产之溢利
    ACQUISITION_FIXED_ASSETS = "hk_acquisition_fixed_assets"  # 购建固定资产
    ACQUISITION_INTANGIBLE_OTHER_ASSETS = "hk_acquisition_intangible_other_assets"  # 购建无形资产及其他资产
    ACQUISITION_SUBSIDIARIES = "hk_acquisition_subsidiaries"  # 收购附属公司
    PURCHASE_MINORITY_INTEREST = "hk_purchase_minority_interest"  # 购买子公司少数股权而支付的现金
    TRADING_INVESTMENTS_INCREASE_DECREASE = "hk_trading_investments_increase_decrease"  # 持作买卖投资(增加)减少
    DEPOSITS_DECREASE_INCREASE = "hk_deposits_decrease_increase"  # 存款减少(增加)
    RECEIVABLES_RELATED_PARTIES_INVESTING = "hk_receivables_related_parties_investing"  # 应收关联方款项(增加)减少(投资)
    INVESTING_OTHER_ITEMS = "hk_investing_other_items"  # 投资业务其他项目

    # 筹资活动
    NEW_BORROWINGS = "hk_new_borrowings"  # 新增借款
    REPAYMENT_BORROWINGS = "hk_repayment_borrowings"  # 偿还借款
    INTEREST_PAID_FINANCING = "hk_interest_paid_financing"  # 已付利息(融资)
    DIVIDENDS_PAID_FINANCING = "hk_dividends_paid_financing"  # 已付股息(融资)
    ISSUE_SHARES = "hk_issue_shares"  # 发行股份
    BUYBACK_SHARES = "hk_buyback_shares"  # 回购股份
    INVESTMENT_RECEIVED = "hk_investment_received"  # 吸收投资所得
    ISSUE_BONDS = "hk_issue_bonds"  # 发行债券
    REDEEM_BONDS = "hk_redeem_bonds"  # 赎回债券
    REPAYMENT_FINANCE_LEASE = "hk_repayment_finance_lease"  # 偿还融资租赁
    ISSUE_RELATED_COSTS = "hk_issue_related_costs"  # 发行相关费用
    FINANCING_OTHER_ITEMS = "hk_financing_other_items"  # 融资业务其他项目

    # 现金净变动
    CASH_BEFORE_FINANCING = "hk_cash_before_financing"  # 融资前现金净额
    SUBTRACT_EXCHANGE_GAIN = "hk_subtract_exchange_gain"  # 减:汇兑收益
    PERIOD_CHANGE_OTHER_ITEMS = "hk_period_change_other_items"  # 期间变动其他项目

    # ========== 财务指标字段 (37个) ========== ✨ 新增
    # 盈利能力指标
    OPERATING_CASH_FLOW_PER_SHARE_HK = "hk_operating_cash_flow_per_share"  # 每股经营现金流(港元)
    OPERATING_INCOME_PER_SHARE = "hk_operating_income_per_share"  # 每股营业收入(港元)
    NET_ASSETS_PER_SHARE = "hk_net_assets_per_share"  # 每股净资产(港元)
    BASIC_EPS_HKD = "hk_basic_eps_hkd"  # 基本每股收益(港元)
    DILUTED_EPS_HKD = "hk_diluted_eps_hkd"  # 稀释每股收益(港元)
    OPERATING_INCOME_HUNDRED_MILLION = "hk_operating_income_hundred_million"  # 营业收入(亿港元)
    OPERATING_INCOME_YOY = "hk_operating_income_yoy"  # 营业收入同比增长(%)
    GROSS_PROFIT_HUNDRED_MILLION = "hk_gross_profit_hundred_million"  # 毛利润(亿港元)
    GROSS_PROFIT_YOY = "hk_gross_profit_yoy"  # 毛利润同比增长(%)
    HOLDER_PROFIT_HUNDRED_MILLION = "hk_holder_profit_hundred_million"  # 股东净利润(亿港元)
    HOLDER_PROFIT_YOY = "hk_holder_profit_yoy"  # 股东净利润同比增长(%)
    GROSS_PROFIT_RATIO = "hk_gross_profit_ratio"  # 毛利率(%)
    EPS_TTM = "hk_eps_ttm"  # 滚动市盈率
    OPERATING_INCOME_QOQ = "hk_operating_income_qoq"  # 营业收入环比增长(%)
    NET_PROFIT_RATIO = "hk_net_profit_ratio"  # 净利率(%)
    ROE_AVG = "hk_roe_avg"  # 平均净资产收益率(%)
    GROSS_PROFIT_QOQ = "hk_gross_profit_qoq"  # 毛利润环比增长(%)
    ROA = "hk_roa"  # 总资产收益率(%)
    HOLDER_PROFIT_QOQ = "hk_holder_profit_qoq"  # 股东净利润环比增长(%)
    ROE_YEARLY = "hk_roe_yearly"  # 年度净资产收益率(%)
    ROIC_YEARLY = "hk_roic_yearly"  # 年度投入资本回报率(%)
    TAX_EBT = "hk_tax_ebt"  # 税前利润税率(%)
    OCF_SALES = "hk_ocf_sales"  # 经营活动现金流/营业收入(%)

    # 偿债能力指标
    DEBT_ASSET_RATIO = "hk_debt_asset_ratio"  # 资产负债率(%)
    CURRENT_RATIO_HK = "hk_current_ratio"  # 流动比率
    CURRENT_DEBT_TO_TOTAL_DEBT = "hk_current_debt_to_total_debt"  # 流动负债/总负债(%)
