"""
美股市场特定字段

通过继承StandardFields自动获得所有标准字段。
"""

from ..financial_standard import StandardFields


class USStockMarketFields(StandardFields):
    """
    美股市场字段 = IFRS标准字段 + 美股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        USStockMarketFields (美股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[USStockMarketFields.TOTAL_REVENUE]

        # 美股特定字段 (未来添加)
        # goodwill = df[USStockMarketFields.GOODWILL]

    注意:
        - 不要在子类中重复定义StandardFields已有的字段
        - 如需添加美股特定字段,直接在类中定义即可
        - 所有标准字段自动可用,无需重复定义
    """

    # ========== 美股特定字段 ========== ✨ 新增

    # ========== 资产负债表特有字段 ==========
    # 流动资产特有
    MARKETABLE_SECURITIES_CURRENT = "us_marketable_securities_current"  # 有价证券投资(流动)
    MARKETABLE_SECURITIES_NON_CURRENT = "us_marketable_securities_non_current"  # 有价证券投资(非流动)
    SHORT_TERM_INVESTMENTS = "us_short_term_investments"  # 短期投资
    LONG_TERM_INVESTMENTS = "us_long_term_investments"  # 长期投资

    # 流动负债特有
    NOTES_PAYABLE_CURRENT = "us_notes_payable_current"  # 应付票据(流动)
    DEFERRED_TAX_LIABILITIES_NON_CURRENT = "us_deferred_tax_liabilities_non_current"  # 递延所得税负债(非流动)
    DEFERRED_TAX_ASSETS_CURRENT = "us_deferred_tax_assets_current"  # 递延所得税资产(流动)
    DEFERRED_REVENUE_CURRENT = "us_deferred_revenue_current"  # 递延收入(流动)
    DEFERRED_REVENUE_NON_CURRENT = "us_deferred_revenue_non_current"  # 递延收入(非流动)
    ADVANCE_PAYMENTS_ACCRUED_EXPENSES = "us_advance_payments_accrued_expenses"  # 预收及预提费用

    # 所有者权益特有
    ATTRIBUTABLE_TO_PARENT_EQUITY_OTHER_ITEMS = "us_attributable_to_parent_equity_other_items"  # 归属于母公司股东权益其他项目
    PREFERRED_STOCK = "us_preferred_stock"  # 优先股

    # ========== 利润表特有字段 ==========
    # 收入类指标
    MAIN_OPERATING_REVENUE = "us_main_operating_revenue"  # 主营收入
    MAIN_OPERATING_COST = "us_main_operating_cost"  # 主营成本

    # 费用类指标
    OPERATING_EXPENSES_US = "us_operating_expenses"  # 营业费用
    MARKETING_EXPENSES = "us_marketing_expenses"  # 营销费用
    RESTRUCTURING_EXPENSES = "us_restructuring_expenses"  # 重组费用
    OTHER_OPERATING_EXPENSES = "us_other_operating_expenses"  # 其他营业费用

    # 利润类指标
    CONTINUING_OPERATIONS_INCOME_BEFORE_TAX = "us_continuing_operations_income_before_tax"  # 持续经营税前利润
    CONTINUING_OPERATIONS_NET_INCOME = "us_continuing_operations_net_income"  # 持续经营净利润
    ATTRIBUTABLE_TO_COMMON_SHAREHOLDERS = "us_attributable_to_common_shareholders"  # 归属于普通股股东净利润
    NET_INCOME_OTHER_ITEMS = "us_net_income_other_items"  # 税后利润其他项目
    EQUITY_INVESTMENT_GAIN_LOSS = "us_equity_investment_gain_loss"  # 权益性投资损益
    OTHER_INCOME_EXPENSE = "us_other_income_expense"  # 其他收入(支出)

    # 每股指标
    BASIC_WEIGHTED_SHARES_COMMON = "us_basic_weighted_shares_common"  # 基本加权平均股数-普通股
    BASIC_EPS_COMMON = "us_basic_eps_common"  # 基本每股收益-普通股
    DILUTED_WEIGHTED_SHARES_COMMON = "us_diluted_weighted_shares_common"  # 摊薄加权平均股数-普通股
    DILUTED_EPS_COMMON = "us_diluted_eps_common"  # 摊薄每股收益-普通股
    DIVIDENDS_PER_SHARE_COMMON = "us_dividends_per_share_common"  # 每股股息-普通股

    # 综合收益
    ATTRIBUTABLE_TO_COMPANY_COMPREHENSIVE_INCOME = "us_attributable_to_company_comprehensive_income"  # 本公司拥有人占全面收益总额
    OTHER_COMPREHENSIVE_INCOME_OTHER_ITEMS = "us_other_comprehensive_income_other_items"  # 其他全面收益其他项目
    OTHER_COMPREHENSIVE_INCOME_TOTAL = "us_other_comprehensive_income_total"  # 其他全面收益合计项
    NON_CONTROLLING_COMPREHENSIVE_INCOME = "us_non_controlling_comprehensive_income"  # 非控股权益占全面收益总额

    # ========== 现金流量表特有字段 ==========
    # 经营活动
    DEPRECIATION_AMORTIZATION_US = "us_depreciation_amortization"  # 折旧及摊销
    IMPAIRMENT_PROVISIONS = "us_impairment_provisions"  # 减值及拨备
    STOCK_BASED_COMPENSATION = "us_stock_based_compensation"  # 基于股票的补偿费
    DEFERRED_TAX_US = "us_deferred_tax"  # 递延所得税
    EXCESS_TAX_BENEFIT = "us_excess_tax_benefit"  # 超额税收优惠
    ASSET_DISPOSAL_GAIN_LOSS = "us_asset_disposal_gain_loss"  # 资产处置损益
    ACCOUNTS_RECEIVABLE_NOTES = "us_accounts_receivable_notes"  # 应收账款及票据
    ACCOUNTS_PAYABLE_NOTES = "us_accounts_payable_notes"  # 应付账款及票据
    OPERATING_ADJUSTMENT_OTHER_ITEMS = "us_operating_adjustment_other_items"  # 经营业务调整其他项目
    OPERATING_OTHER_ITEMS = "us_operating_other_items"  # 经营业务其他项目
    INVESTMENT_GAIN_LOSS_CF = "us_investment_gain_loss_cf"  # 投资损益

    # 投资活动
    PURCHASE_FIXED_ASSETS = "us_purchase_fixed_assets"  # 购买固定资产
    PURCHASE_INTANGIBLE_OTHER_ASSETS = "us_purchase_intangible_other_assets"  # 购建无形资产及其他资产
    LOAN_INCOME = "us_loan_income"  # 贷款收益
    INVESTING_OTHER_ITEMS = "us_investing_other_items"  # 投资业务其他项目
    OTHER_INVESTING_CASH_FLOW = "us_other_investing_cash_flow"  # 其他投资活动产生的现金流量净额

    # 筹资活动
    DIVIDEND_PAYMENT = "us_dividend_payment"  # 股息支付
    FINANCING_OTHER_ITEMS = "us_financing_other_items"  # 筹资业务其他项目
    OTHER_FINANCING_CASH_FLOW = "us_other_financing_cash_flow"  # 其他筹资活动产生的现金流量净额

    # 现金变动
    CASH_EQUIVALENTS_INCREASE_DECREASE = "us_cash_equivalents_increase_decrease"  # 现金及现金等价物增加(减少)额
    REVALUATION_SURPLUS = "us_revaluation_surplus"  # 重估盈余

    # ========== 财务指标字段 (49个) ========== ✨ 新增
    # 盈利能力指标
    OPERATE_INCOME_US = "us_operate_income"  # 营业收入
    OPERATE_INCOME_YOY_US = "us_operate_income_yoy"  # 营业收入同比增长(%)
    GROSS_PROFIT_US = "us_gross_profit"  # 毛利润
    GROSS_PROFIT_YOY_US = "us_gross_profit_yoy"  # 毛利润同比增长(%)
    PARENT_HOLDER_NETPROFIT = "us_parent_holder_netprofit"  # 归属于母公司股东净利润
    PARENT_HOLDER_NETPROFIT_YOY = "us_parent_holder_netprofit_yoy"  # 归属于母公司股东净利润同比增长(%)
    GROSS_PROFIT_RATIO_US = "us_gross_profit_ratio"  # 毛利率(%)
    NET_PROFIT_RATIO_US = "us_net_profit_ratio"  # 净利率(%)
    ROE_AVG_US = "us_roe_avg"  # 平均净资产收益率(%)
    ROA_US = "us_roa"  # 总资产收益率(%)

    # 运营效率指标
    ACCOUNTS_RECEIVABLE_TURNOVER = "us_accounts_receivable_turnover"  # 应收账款周转率
    INVENTORY_TURNOVER_US = "us_inventory_turnover"  # 存货周转率
    TOTAL_ASSETS_TURNOVER = "us_total_assets_turnover"  # 总资产周转率
    ACCOUNTS_RECEIVABLE_DAYS = "us_accounts_receivable_days"  # 应收账款周转天数
    INVENTORY_DAYS = "us_inventory_days"  # 存货周转天数
    TOTAL_ASSETS_DAYS = "us_total_assets_days"  # 总资产周转天数

    # 偿债能力指标
    CURRENT_RATIO_US = "us_current_ratio"  # 流动比率
    SPEED_RATIO = "us_speed_ratio"  # 速动比率
    OCF_TO_CURRENT_DEBT = "us_ocf_to_current_debt"  # 经营现金流/流动负债
    DEBT_ASSET_RATIO_US = "us_debt_asset_ratio"  # 资产负债率(%)
    EQUITY_RATIO = "us_equity_ratio"  # 权益乘数

    # 增长率指标
    BASIC_EPS_YOY = "us_basic_eps_yoy"  # 基本每股收益同比增长(%)
    GROSS_PROFIT_RATIO_YOY = "us_gross_profit_ratio_yoy"  # 毛利率同比增长(%)
    NET_PROFIT_RATIO_YOY = "us_net_profit_ratio_yoy"  # 净利率同比增长(%)
    ROE_AVG_YOY = "us_roe_avg_yoy"  # 平均净资产收益率同比增长(%)
    ROA_YOY = "us_roa_yoy"  # 总资产收益率同比增长(%)
    DEBT_ASSET_RATIO_YOY = "us_debt_asset_ratio_yoy"  # 资产负债率同比增长(%)
    CURRENT_RATIO_YOY = "us_current_ratio_yoy"  # 流动比率同比增长(%)
    SPEED_RATIO_YOY = "us_speed_ratio_yoy"  # 速动比率同比增长(%)
