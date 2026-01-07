"""
A股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class AStockMarketFields(StandardFields):
    """
    A股市场字段 = IFRS标准字段 + A股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        AStockMarketFields (A股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[AStockMarketFields.TOTAL_REVENUE]

        # A股特定字段 (未来添加)
        # minority = df[AStockMarketFields.MINORITY_INTEREST]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加A股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== A股特定字段 ========== ✨ 新增

    # ========== 资产负债表特有字段 ==========
    # 流动资产特有
    SPLIT_OUT_CAPITAL = "a_split_out_capital"  # 拆出资金
    OTHER_RECEIVABLES = "a_other_receivables"  # 其他应收款
    INTEREST_RECEIVABLE = "a_interest_receivable"  # 应收利息
    TOTAL_CASH = "a_total_cash"  # 总现金

    # 非流动资产特有
    AVAILABLE_FOR_SALE_SECURITIES = "a_available_for_sale_securities"  # 可供出售金融资产
    HELD_TO_MATURITY_INVESTMENT = "a_held_to_maturity_investment"  # 持有至到期投资
    OTHER_NON_CURRENT_FINANCIAL_ASSETS = "a_other_non_current_financial_assets"  # 其他非流动金融资产
    FIXED_ASSETS_CLEAN_UP = "a_fixed_assets_clean_up"  # 固定资产清理
    CONSTRUCTION_IN_PROGRESS = "a_construction_in_progress"  # 在建工程
    CONSTRUCTION_MATERIALS = "a_construction_materials"  # 工程物资
    LONG_TERM_PREPAID_EXPENSES = "a_long_term_prepaid_expenses"  # 长期待摊费用
    OTHER_NON_CURRENT_ASSETS = "a_other_non_current_assets"  # 其他非流动资产

    # 流动负债特有
    NOTES_AND_ACCOUNTS_PAYABLE = "a_notes_and_accounts_payable"  # 应付票据及应付账款
    CONTRACTS_RECEIVED = "a_contracts_received"  # 预收款项
    EMPLOYEE_BENEFITS_PAYABLE = "a_employee_benefits_payable"  # 应付职工薪酬
    OTHER_PAYABLES = "a_other_payables"  # 其他应付款合计
    DIVIDENDS_PAYABLE = "a_dividends_payable"  # 应付股利

    # 非流动负债特有
    LONG_TERM_PAYABLES = "a_long_term_payables"  # 长期应付款合计
    SPECIAL_PAYABLES = "a_special_payables"  # 专项应付款

    # 所有者权益特有
    PAID_IN_CAPITAL = "a_paid_in_capital"  # 实收资本(或股本)
    SURPLUS_RESERVE = "a_surplus_reserve"  # 盈余公积
    TOTAL_EQUITY_PARENT_COMPANY = "a_total_equity_parent_company"  # 归属于母公司所有者权益合计
    MINORITY_INTEREST_IN_EQUITY = "a_minority_interest_equity"  # 少数股东权益
    TOTAL_LIABILITIES_AND_EQUITY = "a_total_liabilities_and_equity"  # 负债和所有者权益合计

    # ========== 利润表特有字段 ==========
    # 营业收入与成本
    TOTAL_OPERATING_REVENUE = "a_total_operating_revenue"  # 营业总收入
    OPERATING_REVENUE = "a_operating_revenue"  # 营业收入(其中)
    TOTAL_OPERATING_COST = "a_total_operating_cost"  # 营业总成本
    OPERATING_COST = "a_operating_cost"  # 营业成本(其中)

    # 期间费用
    TAXES_AND_SURCHARGES = "a_taxes_and_surcharges"  # 营业税金及附加
    FINANCING_EXPENSE = "a_financing_expense"  # 财务费用
    INTEREST_EXPENSE_DETAIL = "a_interest_expense_detail"  # 其中:利息费用
    INTEREST_INCOME = "a_interest_income"  # 利息收入

    # 其他收益与损失
    ASSET_IMPAIRMENT_LOSS = "a_asset_impairment_loss"  # 资产减值损失
    CREDIT_IMPAIRMENT_LOSS = "a_credit_impairment_loss"  # 信用减值损失
    FAIR_VALUE_CHANGE_GAIN = "a_fair_value_change_gain"  # 公允价值变动收益
    INVESTMENT_GAIN = "a_investment_gain"  # 投资收益
    ASSET_DISPOSAL_GAIN = "a_asset_disposal_gain"  # 资产处置收益
    OTHER_INCOME_DETAIL = "a_other_income_detail"  # 其他收益(利润表)

    # 利润项目
    OPERATING_PROFIT = "a_operating_profit"  # 营业利润
    NON_CURRENT_ASSET_DISPOSAL_GAIN = "a_non_current_asset_disposal_gain"  # 其中:非流动资产处置利得
    NON_CURRENT_ASSET_DISPOSAL_LOSS = "a_non_current_asset_disposal_loss"  # 其中:非流动资产处置损失
    TOTAL_PROFIT = "a_total_profit"  # 利润总额
    PROFIT_SURPLUS_ADJUSTMENT = "a_profit_surplus_adjustment"  # 净利润差额(合计平衡项目)
    CONTINUING_OPERATING_NET_PROFIT = "a_continuing_operating_net_profit"  # 持续经营净利润
    ATTRIBUTABLE_TO_PARENT_NET_PROFIT = "a_attributable_to_parent_net_profit"  # 归属于母公司所有者的净利润
    MINORITY_INTEREST_PROFIT = "a_minority_interest_profit"  # 少数股东损益
    NET_PROFIT_AFTER_NON_RECURRING = "a_net_profit_after_non_recurring"  # 扣除非经常性损益后的净利润

    # 综合收益
    OTHER_COMPREHENSIVE_INCOME_PARENT = "a_other_comprehensive_income_parent"  # 归属母公司所有者的其他综合收益
    TOTAL_COMPREHENSIVE_INCOME = "a_total_comprehensive_income"  # 综合收益总额
    COMPREHENSIVE_INCOME_PARENT = "a_comprehensive_income_parent"  # 归属于母公司股东的综合收益总额
    COMPREHENSIVE_INCOME_MINORITY = "a_comprehensive_income_minority"  # 归属于少数股东的综合收益总额

    # ========== 现金流量表特有字段 ==========
    # 经营活动
    TAXES_AND_FEES_RECEIVED = "a_taxes_and_fees_received"  # 收到的税费与返还
    OTHER_OPERATING_CASH_RECEIVED = "a_other_operating_cash_received"  # 收到其他与经营活动有关的现金
    OTHER_OPERATING_CASH_PAID = "a_other_operating_cash_paid"  # 支付其他与经营活动有关的现金

    # 投资活动
    INVESTMENT_RECOVERY_CASH = "a_investment_recovery_cash"  # 收回投资收到的现金
    INVESTMENT_INCOME_CASH = "a_investment_income_cash"  # 取得投资收益收到的现金
    DISPOSAL_LONG_ASSET_CASH = "a_disposal_long_asset_cash"  # 处置固定资产、无形资产和其他长期资产收回的现金净额
    OTHER_INVESTING_CASH_RECEIVED = "a_other_investing_cash_received"  # 收到其他与投资活动有关的现金
    INVESTMENT_CASH_PAID = "a_investment_cash_paid"  # 投资支付的现金
    OTHER_INVESTING_CASH_PAID = "a_other_investing_cash_paid"  # 支付其他与投资活动有关的现金

    # 筹资活动
    SUBSIDIARY_MINORITY_INVESTMENT_CASH = "a_subsidiary_minority_investment_cash"  # 其中:子公司吸收少数股东投资收到的现金
    OTHER_FINANCING_CASH_RECEIVED = "a_other_financing_cash_received"  # 收到其他与筹资活动有关的现金
    SUBSIDIARY_MINORITY_DIVIDEND = "a_subsidiary_minority_dividend"  # 其中:子公司支付给少数股东的股利、利润
    OTHER_FINANCING_CASH_PAID = "a_other_financing_cash_paid"  # 支付其他与筹资活动有关的现金

    # 汇率变动
    EXCHANGE_CHANGE_CASH = "a_exchange_change_cash"  # 汇率变动对现金及现金等价物的影响

    # ========== 补充资料字段 ==========
    NET_ADJUSTMENT_FOR_OPERATING_CASH = "a_net_adjustment_for_operating_cash"  # 间接法-经营活动产生的现金流量净额
    NON_CASH_MAJORITY_INVEST_FINANCING = "a_non_cash_majority_invest_financing"  # 不涉及现金收支的重大投资和筹资活动
    CASH_EQUIVALENTS_CHANGE = "a_cash_equivalents_change"  # 现金及现金等价物净变动情况

    # ========== 财务指标字段 (25个) ========== ✨ 新增
    # 盈利能力指标
    NET_PROFIT_AFTER_NON_RECURRING = "a_net_profit_after_non_recurring"  # 扣非净利润
    SALES_NET_PROFIT_MARGIN = "a_sales_net_profit_margin"  # 销售净利率
    SALES_GROSS_PROFIT_MARGIN = "a_sales_gross_profit_margin"  # 销售毛利率
    RETURN_ON_EQUITY = "a_return_on_equity"  # 净资产收益率
    RETURN_ON_EQUITY_DILUTED = "a_return_on_equity_diluted"  # 净资产收益率-摊薄

    # 成长能力指标
    NET_PROFIT_GROWTH_RATE = "a_net_profit_growth_rate"  # 净利润同比增长率
    DILUTED_NET_PROFIT_GROWTH_RATE = "a_diluted_net_profit_growth_rate"  # 扣非净利润同比增长率
    TOTAL_OPERATING_REVENUE_GROWTH_RATE = "a_total_operating_revenue_growth_rate"  # 营业总收入同比增长率

    # 每股指标
    EARNINGS_PER_SHARE = "a_earnings_per_share"  # 每股净资产
    CAPITAL_RESERVE_PER_SHARE = "a_capital_reserve_per_share"  # 每股资本公积金
    UNDISTRIBUTED_PROFIT_PER_SHARE = "a_undistributed_profit_per_share"  # 每股未分配利润
    OPERATING_CASH_FLOW_PER_SHARE = "a_operating_cash_flow_per_share"  # 每股经营现金流

    # 运营效率指标
    OPERATING_CYCLE = "a_operating_cycle"  # 营业周期
    INVENTORY_TURNOVER = "a_inventory_turnover"  # 存货周转率
    INVENTORY_TURNOVER_DAYS = "a_inventory_turnover_days"  # 存货周转天数
    RECEIVABLE_TURNOVER_DAYS = "a_receivable_turnover_days"  # 应收账款周转天数

    # 偿债能力指标
    CURRENT_RATIO = "a_current_ratio"  # 流动比率
    QUICK_RATIO = "a_quick_ratio"  # 速动比率
    CONSERVATIVE_QUICK_RATIO = "a_conservative_quick_ratio"  # 保守速动比率
    DEBT_TO_EQUITY_RATIO = "a_debt_to_equity_ratio"  # 产权比率
    DEBT_TO_ASSET_RATIO = "a_debt_to_asset_ratio"  # 资产负债率
