"""
字段映射配置模块

职责：
- 集中管理所有市场的字段映射配置
- 提供类型安全的配置访问接口
- 支持配置的独立测试和维护

设计原则：
- 单一职责：只负责配置定义，不包含业务逻辑
- 可测试性：配置函数可以独立测试
- 可扩展性：易于添加新市场或新字段映射
"""

from typing import Dict, List
from ..domain.models.financial_standard import StandardFields
from ..domain.models.market_fields.a_stock_fields import AStockMarketFields
from ..domain.models.market_fields.hk_stock_fields import HKStockMarketFields
from ..domain.models.market_fields.us_stock_fields import USStockMarketFields


def get_a_stock_mappings() -> Dict[str, List[str]]:
    """
    获取A股字段映射配置

    基于文档: doc/a_stock_fields.md

    Returns:
        Dict[标准字段, 原始字段列表]
    """
    return {
        StandardFields.REPORT_DATE: ["报告期"],

        # 利润表字段
        StandardFields.TOTAL_REVENUE: ["营业总收入", "一、营业总收入", "其中：营业收入"],
        StandardFields.OPERATING_INCOME: ["二、营业利润"],  # EBIT
        StandardFields.GROSS_PROFIT: ["营业总收入(毛利润)", "毛利润"],
        StandardFields.NET_INCOME: ["净利润", "五、净利润"],
        StandardFields.INCOME_TAX: ["所得税费用", "减：所得税费用"],
        StandardFields.INTEREST_EXPENSE: ["利息支出", "其中：利息费用"],

        # 资产负债表字段
        StandardFields.TOTAL_ASSETS: ["资产总计", "资产合计"],
        StandardFields.CURRENT_ASSETS: ["流动资产合计"],
        StandardFields.TOTAL_LIABILITIES: ["负债合计"],
        StandardFields.CURRENT_LIABILITIES: ["流动负债合计"],
        StandardFields.TOTAL_EQUITY: ["所有者权益（或股东权益）合计", "所有者权益(或股东权益)合计"],
        StandardFields.SHORT_TERM_DEBT: ["短期借款"],
        StandardFields.LONG_TERM_DEBT: ["长期借款"],

        # 现金流量表字段
        StandardFields.OPERATING_CASH_FLOW: ["经营活动产生的现金流量净额"],
        StandardFields.INVESTING_CASH_FLOW: ["投资活动产生的现金流量净额"],
        StandardFields.FINANCING_CASH_FLOW: ["筹资活动产生的现金流量净额"],

        # 每股指标
        StandardFields.BASIC_EPS: ["基本每股收益"],
        StandardFields.DILUTED_EPS: ["稀释每股收益"],

        # 营运资本字段
        StandardFields.CASH_AND_EQUIVALENTS: ["货币资金"],
        StandardFields.ACCOUNTS_RECEIVABLE: ["应收账款", "应收票据及应收账款"],
        StandardFields.INVENTORY: ["存货"],
        StandardFields.ACCOUNTS_PAYABLE: ["应付账款", "应付票据及应付账款"],

        # 现金流量分析字段
        StandardFields.CAPITAL_EXPENDITURE: ["购建固定资产、无形资产和其他长期资产支付的现金"],  # 主字段
        StandardFields.DIVIDENDS_PAID: ["分配股利、利润或偿付利息支付的现金"],  # 包含利息(简化版)
        StandardFields.DEPRECIATION_AMORTIZATION: ["固定资产折旧"],  # 主字段

        # 利润表扩展字段
        StandardFields.COST_OF_SALES: ["营业成本"],
        StandardFields.RD_EXPENSES: ["研发费用"],

        # 资产负债表扩展字段
        StandardFields.PPE_NET: ["固定资产"],
        StandardFields.INTANGIBLE_ASSETS: ["无形资产"],
        StandardFields.GOODWILL: ["商誉"],
        StandardFields.LONG_TERM_EQUITY_INVESTMENT: ["长期股权投资"],
        StandardFields.INVESTMENT_PROPERTY: ["投资性房地产"],
        StandardFields.DEFERRED_TAX_ASSETS: ["递延所得税资产"],
        StandardFields.DEFERRED_TAX_LIABILITIES: ["递延所得税负债"],

        # 利润表扩展字段 (新增)
        StandardFields.SELLING_EXPENSES: ["销售费用"],
        StandardFields.ADMIN_EXPENSES: ["管理费用"],
        StandardFields.OTHER_INCOME: ["其他收益"],

        # 股东权益字段 (新增)
        StandardFields.ISSUED_CAPITAL: ["股本"],
        StandardFields.SHARE_PREMIUM: ["资本公积"],
        StandardFields.RETAINED_EARNINGS: ["未分配利润"],
        StandardFields.OTHER_COMPREHENSIVE_INCOME: ["其他综合收益"],
        StandardFields.MINORITY_INTEREST: ["少数股东权益"],

        # 其他资产负债表字段 (新增)
        StandardFields.CONTRACT_ASSETS: ["合同资产"],
        StandardFields.FINANCIAL_ASSETS: ["交易性金融资产"],
        StandardFields.PREPAYMENTS: ["预付款项"],
        StandardFields.OTHER_CURRENT_ASSETS: ["其他流动资产"],
        StandardFields.CONTRACT_LIABILITIES: ["合同负债"],
        StandardFields.CURRENT_TAX_LIABILITIES: ["应交税费"],

        # 现金流量表详细字段 (新增)
        StandardFields.RECEIPTS_FROM_CUSTOMERS: ["销售商品、提供劳务收到的现金"],
        StandardFields.CASH_PAID_TO_SUPPLIERS: ["购买商品、接受劳务支付的现金"],
        StandardFields.PROCEEDS_FROM_BORROWINGS: ["取得借款收到的现金"],

        # 其他资产负债表字段 (阶段1新增)
        StandardFields.NON_CURRENT_ASSETS: ["非流动资产合计", "非流动资产"],
        StandardFields.CURRENT_PORTION_LONG_TERM_DEBT: ["一年内到期的非流动负债"],

        # 其他负债字段 (阶段2新增)
        StandardFields.OTHER_CURRENT_LIABILITIES: ["其他流动负债"],
        StandardFields.PROVISIONS: ["预计负债"],

        # 其他收益字段 (阶段2新增)
        StandardFields.FINANCE_INCOME: ["财务收益", "利息收入"],
        StandardFields.PROFIT_OF_ASSOCIATES: ["对联营企业和合营企业的投资收益"],

        # 现金流量表详细字段 (阶段2新增)
        StandardFields.CASH_PAID_TO_EMPLOYEES: ["支付给职工以及为职工支付的现金"],
        StandardFields.INCOME_TAXES_PAID: ["支付的各项税费", "支付的所得税"],

        # IFRS 16 租赁相关字段 (阶段3新增)
        StandardFields.RIGHT_OF_USE_ASSETS: ["使用权资产"],
        StandardFields.LEASE_LIABILITIES_CURRENT: ["租赁负债"],
        StandardFields.LEASE_LIABILITIES_NON_CURRENT: ["租赁负债"],

        # 筹资活动详细字段 (阶段3新增)
        StandardFields.PROCEEDS_FROM_ISSUING_SHARES: ["吸收投资收到的现金"],
        StandardFields.REPAYMENT_OF_BORROWINGS: ["偿还债务支付的现金"],
    }


def get_hk_stock_mappings() -> Dict[str, List[str]]:
    """
    获取港股字段映射配置

    基于文档: doc/hk_stock_fields.md

    Returns:
        Dict[标准字段, 原始字段列表]
    """
    return {
        StandardFields.REPORT_DATE: ["REPORT_DATE"],

        # 利润表字段
        StandardFields.TOTAL_REVENUE: ["OPERATE_INCOME", "营业额", "营运收入", "经营收入总额"],
        StandardFields.OPERATING_INCOME: ["经营溢利", "除税前溢利"],  # EBIT近似值
        StandardFields.GROSS_PROFIT: ["毛利"],
        StandardFields.NET_INCOME: ["HOLDER_PROFIT", "股东应占溢利", "持续经营业务税后利润"],
        StandardFields.INTEREST_EXPENSE: ["融资成本"],
        StandardFields.INCOME_TAX: ["税项"],

        # 资产负债表字段
        StandardFields.TOTAL_ASSETS: ["总资产"],
        StandardFields.CURRENT_ASSETS: ["流动资产合计"],
        StandardFields.TOTAL_LIABILITIES: ["总负债"],
        StandardFields.CURRENT_LIABILITIES: ["流动负债合计"],
        StandardFields.TOTAL_EQUITY: ["总权益", "股东权益", "净资产"],
        StandardFields.SHORT_TERM_DEBT: ["短期贷款"],
        StandardFields.LONG_TERM_DEBT: ["长期贷款"],

        # 现金流量表字段
        StandardFields.OPERATING_CASH_FLOW: ["经营业务现金净额", "经营产生现金"],
        StandardFields.INVESTING_CASH_FLOW: ["投资业务现金净额"],
        StandardFields.FINANCING_CASH_FLOW: ["融资业务现金净额"],

        # 每股指标
        StandardFields.BASIC_EPS: ["基本每股盈利"],
        StandardFields.DILUTED_EPS: ["稀释每股盈利"],

        # 营运资本字段
        StandardFields.CASH_AND_EQUIVALENTS: ["现金及等价物"],
        StandardFields.ACCOUNTS_RECEIVABLE: ["应收账款"],
        StandardFields.INVENTORY: ["存货"],
        StandardFields.ACCOUNTS_PAYABLE: ["应付账款"],

        # 现金流量分析字段
        StandardFields.CAPITAL_EXPENDITURE: ["购建固定资产"],  # 主字段(需+购建无形资产及其他资产)
        StandardFields.DIVIDENDS_PAID: ["已付股息"],  # 纯股息
        StandardFields.DEPRECIATION_AMORTIZATION: ["折旧"],  # 主字段(需+摊销)

        # 利润表扩展字段
        StandardFields.COST_OF_SALES: ["已售存货成本"],
        StandardFields.RD_EXPENSES: ["研发费用"],

        # 资产负债表扩展字段
        StandardFields.PPE_NET: ["固定资产"],
        StandardFields.INTANGIBLE_ASSETS: ["无形资产"],
        StandardFields.GOODWILL: ["商誉"],
        StandardFields.LONG_TERM_EQUITY_INVESTMENT: ["于联营公司投资"],
        StandardFields.INVESTMENT_PROPERTY: ["投资物业"],
        StandardFields.DEFERRED_TAX_ASSETS: ["递延税项资产"],
        StandardFields.DEFERRED_TAX_LIABILITIES: ["递延税项负债"],

        # 利润表扩展字段 (新增)
        StandardFields.SELLING_EXPENSES: ["销售费用"],
        StandardFields.ADMIN_EXPENSES: ["管理费用"],
        StandardFields.OTHER_INCOME: ["其他收益"],

        # 股东权益字段 (新增)
        StandardFields.ISSUED_CAPITAL: ["股本"],
        StandardFields.SHARE_PREMIUM: ["资本储备"],
        StandardFields.RETAINED_EARNINGS: ["留存收益"],
        StandardFields.OTHER_COMPREHENSIVE_INCOME: ["其他全面收益"],
        StandardFields.MINORITY_INTEREST: ["非控股权益"],

        # 其他资产负债表字段 (新增)
        StandardFields.CONTRACT_ASSETS: ["合同资产"],
        StandardFields.FINANCIAL_ASSETS: ["交易性金融资产(流动)"],
        StandardFields.PREPAYMENTS: ["预付款项"],
        StandardFields.OTHER_CURRENT_ASSETS: ["其他流动资产"],
        StandardFields.CONTRACT_LIABILITIES: ["合同负债"],
        StandardFields.CURRENT_TAX_LIABILITIES: ["应缴税金"],

        # 现金流量表详细字段 (新增)
        StandardFields.RECEIPTS_FROM_CUSTOMERS: ["从客户收取的现金"],
        StandardFields.CASH_PAID_TO_SUPPLIERS: ["支付给供应商的现金"],
        StandardFields.PROCEEDS_FROM_BORROWINGS: ["借款收款"],

        # 其他资产负债表字段 (阶段1新增)
        StandardFields.NON_CURRENT_ASSETS: ["非流动资产合计"],
        StandardFields.CURRENT_PORTION_LONG_TERM_DEBT: ["一年内到期的长期贷款"],

        # 其他负债字段 (阶段2新增)
        StandardFields.OTHER_CURRENT_LIABILITIES: ["其他流动负债"],
        StandardFields.PROVISIONS: ["预计负债"],

        # 其他收益字段 (阶段2新增)
        StandardFields.FINANCE_INCOME: ["财务收入", "利息收入"],
        StandardFields.PROFIT_OF_ASSOCIATES: ["于联营公司之溢利"],

        # 现金流量表详细字段 (阶段2新增)
        StandardFields.CASH_PAID_TO_EMPLOYEES: ["支付给员工的现金"],
        StandardFields.INCOME_TAXES_PAID: ["支付的所得税"],

        # IFRS 16 租赁相关字段 (阶段3新增)
        StandardFields.RIGHT_OF_USE_ASSETS: ["使用权资产"],
        StandardFields.LEASE_LIABILITIES_CURRENT: ["租赁负债"],
        StandardFields.LEASE_LIABILITIES_NON_CURRENT: ["租赁负债"],

        # 筹资活动详细字段 (阶段3新增)
        StandardFields.PROCEEDS_FROM_ISSUING_SHARES: ["发行股票收款"],
        StandardFields.REPAYMENT_OF_BORROWINGS: ["偿还借款"],
    }


def get_us_stock_mappings() -> Dict[str, List[str]]:
    """
    获取美股字段映射配置

    基于文档: doc/us_stock_fields.md

    Returns:
        Dict[标准字段, 原始字段列表]
    """
    return {
        StandardFields.REPORT_DATE: ["REPORT_DATE"],

        # 利润表字段
        StandardFields.TOTAL_REVENUE: ["OPERATE_INCOME", "营业收入", "主营收入", "收入总额"],
        StandardFields.OPERATING_INCOME: ["营业利润", "持续经营税前利润"],  # EBIT
        StandardFields.GROSS_PROFIT: ["毛利"],
        StandardFields.NET_INCOME: ["PARENT_HOLDER_NETPROFIT", "净利润", "归属于普通股股东净利润", "持续经营净利润"],
        StandardFields.INCOME_TAX: ["所得税"],
        StandardFields.INTEREST_EXPENSE: ["利息收入"],  # 美股可能记录为负值

        # 资产负债表字段
        StandardFields.TOTAL_ASSETS: ["总资产"],
        StandardFields.CURRENT_ASSETS: ["流动资产合计"],
        StandardFields.TOTAL_LIABILITIES: ["总负债"],
        StandardFields.CURRENT_LIABILITIES: ["流动负债合计"],
        StandardFields.TOTAL_EQUITY: ["股东权益合计", "归属于母公司股东权益"],
        StandardFields.SHORT_TERM_DEBT: ["短期债务"],
        StandardFields.LONG_TERM_DEBT: ["长期负债"],

        # 现金流量表字段
        StandardFields.OPERATING_CASH_FLOW: ["经营活动产生的现金流量净额"],
        StandardFields.INVESTING_CASH_FLOW: ["投资活动产生的现金流量净额"],
        StandardFields.FINANCING_CASH_FLOW: ["筹资活动产生的现金流量净额"],

        # 每股指标
        StandardFields.BASIC_EPS: ["BASIC_EPS"],
        StandardFields.DILUTED_EPS: ["DILUTED_EPS"],

        # 营运资本字段
        StandardFields.CASH_AND_EQUIVALENTS: ["货币资金"],
        StandardFields.ACCOUNTS_RECEIVABLE: ["应收账款"],
        StandardFields.INVENTORY: ["存货"],
        StandardFields.ACCOUNTS_PAYABLE: ["应付账款"],

        # 现金流量分析字段
        StandardFields.CAPITAL_EXPENDITURE: ["购买固定资产"],  # 主字段(需+购建无形资产及其他资产)
        StandardFields.DIVIDENDS_PAID: ["分配股利、利润或偿付利息支付的现金"],  # 包含利息(简化版)
        StandardFields.DEPRECIATION_AMORTIZATION: ["固定资产折旧"],  # 主字段(需+无形资产摊销)

        # 利润表扩展字段
        StandardFields.COST_OF_SALES: ["营业成本"],
        StandardFields.RD_EXPENSES: ["研发费用"],

        # 资产负债表扩展字段
        StandardFields.PPE_NET: ["固定资产"],  # 可能缺失,标记为部分支持
        StandardFields.INTANGIBLE_ASSETS: ["无形资产"],
        StandardFields.GOODWILL: ["商誉"],
        StandardFields.LONG_TERM_EQUITY_INVESTMENT: ["长期股权投资"],
        StandardFields.INVESTMENT_PROPERTY: ["投资性房地产"],
        StandardFields.DEFERRED_TAX_ASSETS: ["递延所得税资产"],
        StandardFields.DEFERRED_TAX_LIABILITIES: ["递延所得税负债"],

        # 利润表扩展字段 (新增)
        StandardFields.SELLING_EXPENSES: ["销售费用"],
        StandardFields.ADMIN_EXPENSES: ["管理费用"],
        StandardFields.OTHER_INCOME: ["其他收益"],

        # 股东权益字段 (新增)
        StandardFields.ISSUED_CAPITAL: ["股本"],
        StandardFields.SHARE_PREMIUM: ["资本公积"],
        StandardFields.RETAINED_EARNINGS: ["未分配利润"],
        StandardFields.OTHER_COMPREHENSIVE_INCOME: ["其他综合收益"],
        StandardFields.MINORITY_INTEREST: ["少数股东权益"],

        # 其他资产负债表字段 (新增)
        StandardFields.CONTRACT_ASSETS: ["合同资产"],
        StandardFields.FINANCIAL_ASSETS: ["交易性金融资产"],
        StandardFields.PREPAYMENTS: ["预付款项"],
        StandardFields.OTHER_CURRENT_ASSETS: ["其他流动资产"],
        StandardFields.CONTRACT_LIABILITIES: ["合同负债"],
        StandardFields.CURRENT_TAX_LIABILITIES: ["应交税费"],

        # 现金流量表详细字段 (新增)
        StandardFields.RECEIPTS_FROM_CUSTOMERS: ["销售商品、提供劳务收到的现金"],
        StandardFields.CASH_PAID_TO_SUPPLIERS: ["购买商品、接受劳务支付的现金"],
        StandardFields.PROCEEDS_FROM_BORROWINGS: ["取得借款收到的现金"],

        # 其他资产负债表字段 (阶段1新增)
        StandardFields.NON_CURRENT_ASSETS: ["非流动资产"],
        StandardFields.CURRENT_PORTION_LONG_TERM_DEBT: ["长期负债(本期部分)"],

        # 其他负债字段 (阶段2新增)
        StandardFields.OTHER_CURRENT_LIABILITIES: ["其他流动负债"],
        StandardFields.PROVISIONS: ["预计负债"],

        # 其他收益字段 (阶段2新增)
        StandardFields.FINANCE_INCOME: ["财务收益", "利息收入"],
        StandardFields.PROFIT_OF_ASSOCIATES: ["对联营企业和合营企业的投资收益"],

        # 现金流量表详细字段 (阶段2新增)
        StandardFields.CASH_PAID_TO_EMPLOYEES: ["支付给职工以及为职工支付的现金"],
        StandardFields.INCOME_TAXES_PAID: ["支付的各项税费", "支付的所得税"],

        # IFRS 16 租赁相关字段 (阶段3新增)
        StandardFields.RIGHT_OF_USE_ASSETS: ["使用权资产"],
        StandardFields.LEASE_LIABILITIES_CURRENT: ["租赁负债"],
        StandardFields.LEASE_LIABILITIES_NON_CURRENT: ["租赁负债"],

        # 筹资活动详细字段 (阶段3新增)
        StandardFields.PROCEEDS_FROM_ISSUING_SHARES: ["吸收投资收到的现金"],
        StandardFields.REPAYMENT_OF_BORROWINGS: ["偿还债务支付的现金"],
    }


def load_market_mappings() -> Dict[str, Dict[str, List[str]]]:
    """
    加载所有市场的字段映射配置

    Returns:
        Dict[市场名称, Dict[标准字段, 原始字段列表]]

    Example:
        >>> config = load_market_mappings()
        >>> config['a_stock'][StandardFields.TOTAL_REVENUE]
        ['营业总收入', '一、营业总收入']
    """
    return {
        'a_stock': get_a_stock_mappings(),
        'hk_stock': get_hk_stock_mappings(),
        'us_stock': get_us_stock_mappings(),
    }


def get_a_stock_specific_mappings() -> Dict[str, List[str]]:
    """
    获取A股特有字段映射配置

    基于文档: doc/a_stock_fields.md

    Returns:
        Dict[A股特有字段, 原始字段列表]

    Note:
        这些字段仅在A股市场存在，不在StandardFields中定义
    """
    return {
        # 资产负债表特有字段
        AStockMarketFields.SPLIT_OUT_CAPITAL: ["拆出资金"],
        AStockMarketFields.OTHER_RECEIVABLES: ["其他应收款合计", "其他应收款"],
        AStockMarketFields.INTEREST_RECEIVABLE: ["其中：应收利息", "应收利息"],
        AStockMarketFields.TOTAL_CASH: ["总现金"],
        AStockMarketFields.AVAILABLE_FOR_SALE_SECURITIES: ["可供出售金融资产"],
        AStockMarketFields.HELD_TO_MATURITY_INVESTMENT: ["持有至到期投资"],
        AStockMarketFields.OTHER_NON_CURRENT_FINANCIAL_ASSETS: ["其他非流动金融资产"],
        AStockMarketFields.FIXED_ASSETS_CLEAN_UP: ["固定资产清理"],
        AStockMarketFields.CONSTRUCTION_IN_PROGRESS: ["其中：在建工程", "在建工程"],
        AStockMarketFields.CONSTRUCTION_MATERIALS: ["工程物资"],
        AStockMarketFields.LONG_TERM_PREPAID_EXPENSES: ["长期待摊费用"],
        AStockMarketFields.OTHER_NON_CURRENT_ASSETS: ["其他非流动资产"],
        AStockMarketFields.NOTES_AND_ACCOUNTS_PAYABLE: ["应付票据及应付账款"],
        AStockMarketFields.CONTRACTS_RECEIVED: ["预收款项"],
        AStockMarketFields.EMPLOYEE_BENEFITS_PAYABLE: ["应付职工薪酬"],
        AStockMarketFields.OTHER_PAYABLES: ["其他应付款合计", "其他应付款"],
        AStockMarketFields.DIVIDENDS_PAYABLE: ["应付股利"],
        AStockMarketFields.LONG_TERM_PAYABLES: ["长期应付款合计", "其中：长期应付款"],
        AStockMarketFields.SPECIAL_PAYABLES: ["专项应付款"],
        AStockMarketFields.PAID_IN_CAPITAL: ["实收资本(或股本)", "股本"],
        AStockMarketFields.SURPLUS_RESERVE: ["盈余公积"],
        AStockMarketFields.TOTAL_EQUITY_PARENT_COMPANY: ["归属于母公司所有者权益合计"],
        AStockMarketFields.MINORITY_INTEREST_IN_EQUITY: ["少数股东权益"],
        AStockMarketFields.TOTAL_LIABILITIES_AND_EQUITY: ["负债和所有者权益（或股东权益）合计"],

        # 利润表特有字段
        AStockMarketFields.TOTAL_OPERATING_REVENUE: ["一、营业总收入", "营业总收入"],
        AStockMarketFields.OPERATING_REVENUE: ["其中：营业收入"],
        AStockMarketFields.TOTAL_OPERATING_COST: ["二、营业总成本", "营业总成本"],
        AStockMarketFields.OPERATING_COST: ["其中：营业成本"],
        AStockMarketFields.TAXES_AND_SURCHARGES: ["营业税金及附加"],
        AStockMarketFields.FINANCING_EXPENSE: ["财务费用"],
        AStockMarketFields.INTEREST_EXPENSE_DETAIL: ["其中：利息费用"],
        AStockMarketFields.INTEREST_INCOME: ["利息收入"],
        AStockMarketFields.ASSET_IMPAIRMENT_LOSS: ["资产减值损失"],
        AStockMarketFields.CREDIT_IMPAIRMENT_LOSS: ["信用减值损失"],
        AStockMarketFields.FAIR_VALUE_CHANGE_GAIN: ["加：公允价值变动收益"],
        AStockMarketFields.INVESTMENT_GAIN: ["投资收益"],
        AStockMarketFields.ASSET_DISPOSAL_GAIN: ["资产处置收益"],
        AStockMarketFields.OTHER_INCOME_DETAIL: ["其他收益"],
        AStockMarketFields.OPERATING_PROFIT: ["三、营业利润"],
        AStockMarketFields.NON_CURRENT_ASSET_DISPOSAL_GAIN: ["其中：非流动资产处置利得"],
        AStockMarketFields.NON_CURRENT_ASSET_DISPOSAL_LOSS: ["其中：非流动资产处置损失"],
        AStockMarketFields.TOTAL_PROFIT: ["四、利润总额", "利润总额"],
        AStockMarketFields.PROFIT_SURPLUS_ADJUSTMENT: ["净利润差额(合计平衡项目)"],
        AStockMarketFields.CONTINUING_OPERATING_NET_PROFIT: ["（一）持续经营净利润"],
        AStockMarketFields.ATTRIBUTABLE_TO_PARENT_NET_PROFIT: ["归属于母公司所有者的净利润"],
        AStockMarketFields.MINORITY_INTEREST_PROFIT: ["少数股东损益"],
        AStockMarketFields.OTHER_COMPREHENSIVE_INCOME_PARENT: ["归属母公司所有者的其他综合收益"],
        AStockMarketFields.TOTAL_COMPREHENSIVE_INCOME: ["八、综合收益总额"],
        AStockMarketFields.COMPREHENSIVE_INCOME_PARENT: ["归属于母公司股东的综合收益总额"],
        AStockMarketFields.COMPREHENSIVE_INCOME_MINORITY: ["归属于少数股东的综合收益总额"],

        # 现金流量表特有字段
        AStockMarketFields.TAXES_AND_FEES_RECEIVED: ["收到的税费与返还"],
        AStockMarketFields.OTHER_OPERATING_CASH_RECEIVED: ["收到其他与经营活动有关的现金"],
        AStockMarketFields.OTHER_OPERATING_CASH_PAID: ["支付其他与经营活动有关的现金"],
        AStockMarketFields.INVESTMENT_RECOVERY_CASH: ["收回投资收到的现金"],
        AStockMarketFields.INVESTMENT_INCOME_CASH: ["取得投资收益收到的现金"],
        AStockMarketFields.DISPOSAL_LONG_ASSET_CASH: ["处置固定资产、无形资产和其他长期资产收回的现金净额"],
        AStockMarketFields.OTHER_INVESTING_CASH_RECEIVED: ["收到其他与投资活动有关的现金"],
        AStockMarketFields.INVESTMENT_CASH_PAID: ["投资支付的现金"],
        AStockMarketFields.OTHER_INVESTING_CASH_PAID: ["支付其他与投资活动有关的现金"],
        AStockMarketFields.SUBSIDIARY_MINORITY_INVESTMENT_CASH: ["其中：子公司吸收少数股东投资收到的现金"],
        AStockMarketFields.OTHER_FINANCING_CASH_RECEIVED: ["收到其他与筹资活动有关的现金"],
        AStockMarketFields.SUBSIDIARY_MINORITY_DIVIDEND: ["其中：子公司支付给少数股东的股利、利润"],
        AStockMarketFields.OTHER_FINANCING_CASH_PAID: ["支付其他与筹资活动有关的现金"],
        AStockMarketFields.EXCHANGE_CHANGE_CASH: ["四、汇率变动对现金及现金等价物的影响"],
        AStockMarketFields.NET_ADJUSTMENT_FOR_OPERATING_CASH: ["间接法-经营活动产生的现金流量净额"],
        AStockMarketFields.NON_CASH_MAJORITY_INVEST_FINANCING: ["不涉及现金收支的重大投资和筹资活动"],
        AStockMarketFields.CASH_EQUIVALENTS_CHANGE: ["五、现金及现金等价物净增加额"],

        # 财务指标字段
        AStockMarketFields.NET_PROFIT_AFTER_NON_RECURRING: ["扣非净利润", "扣除非经常性损益后的净利润"],
        AStockMarketFields.SALES_NET_PROFIT_MARGIN: ["销售净利率"],
        AStockMarketFields.SALES_GROSS_PROFIT_MARGIN: ["销售毛利率"],
        AStockMarketFields.RETURN_ON_EQUITY: ["净资产收益率"],
        AStockMarketFields.RETURN_ON_EQUITY_DILUTED: ["净资产收益率-摊薄"],
        AStockMarketFields.NET_PROFIT_GROWTH_RATE: ["净利润同比增长率"],
        AStockMarketFields.DILUTED_NET_PROFIT_GROWTH_RATE: ["扣非净利润同比增长率"],
        AStockMarketFields.TOTAL_OPERATING_REVENUE_GROWTH_RATE: ["营业总收入同比增长率"],
        AStockMarketFields.EARNINGS_PER_SHARE: ["每股净资产"],
        AStockMarketFields.CAPITAL_RESERVE_PER_SHARE: ["每股资本公积金"],
        AStockMarketFields.UNDISTRIBUTED_PROFIT_PER_SHARE: ["每股未分配利润"],
        AStockMarketFields.OPERATING_CASH_FLOW_PER_SHARE: ["每股经营现金流"],
        AStockMarketFields.OPERATING_CYCLE: ["营业周期"],
        AStockMarketFields.INVENTORY_TURNOVER: ["存货周转率"],
        AStockMarketFields.INVENTORY_TURNOVER_DAYS: ["存货周转天数"],
        AStockMarketFields.RECEIVABLE_TURNOVER_DAYS: ["应收账款周转天数"],
        AStockMarketFields.CURRENT_RATIO: ["流动比率"],
        AStockMarketFields.QUICK_RATIO: ["速动比率"],
        AStockMarketFields.CONSERVATIVE_QUICK_RATIO: ["保守速动比率"],
        AStockMarketFields.DEBT_TO_EQUITY_RATIO: ["产权比率"],
        AStockMarketFields.DEBT_TO_ASSET_RATIO: ["资产负债率"],
    }


def get_hk_stock_specific_mappings() -> Dict[str, List[str]]:
    """
    获取港股特有字段映射配置

    基于文档: doc/hk_stock_fields.md

    Returns:
        Dict[港股特有字段, 原始字段列表]

    Note:
        这些字段仅在港股市场存在，不在StandardFields中定义
    """
    return {
        # 资产负债表特有字段
        HKStockMarketFields.MEDIUM_LONG_TERM_DEPOSITS: ["中长期存款"],
        HKStockMarketFields.REDEEMABLE_INSTRUMENTS_ASSOCIATES: ["于联营公司可赎回工具的投资"],
        HKStockMarketFields.AVAILABLE_FOR_SALE_INVESTMENT: ["可供出售投资"],
        HKStockMarketFields.JOINT_VENTURE_EQUITY: ["合营公司权益"],
        HKStockMarketFields.LAND_USE_RIGHTS: ["土地使用权"],
        HKStockMarketFields.ASSETS_HELD_FOR_SALE: ["持作出售的资产(流动)"],
        HKStockMarketFields.HELD_TO_MATURITY_INVESTMENT_CURRENT: ["持有至到期投资(流动)"],
        HKStockMarketFields.DESIGNATED_FINANCIAL_ASSETS: ["指定以公允价值记账之金融资产"],
        HKStockMarketFields.DESIGNATED_FINANCIAL_ASSETS_CURRENT: ["指定以公允价值记账之金融资产(流动)"],
        HKStockMarketFields.OTHER_FINANCIAL_ASSETS_CURRENT: ["其他金融资产(流动)"],
        HKStockMarketFields.OTHER_FINANCIAL_ASSETS_NON_CURRENT: ["其他金融资产(非流动)"],
        HKStockMarketFields.SHORT_TERM_DEPOSITS: ["短期存款"],
        HKStockMarketFields.RESTRICTED_DEPOSITS_CASH: ["受限制存款及现金"],
        HKStockMarketFields.PREPAYMENTS_OTHER_RECEIVABLES: ["预付款按金及其他应收款"],
        HKStockMarketFields.RECEIVABLES_RELATED_PARTIES: ["应收关联方款项"],
        HKStockMarketFields.PROPERTY_PLANT_EQUIPMENT: ["物业厂房及设备"],
        HKStockMarketFields.OTHER_NON_CURRENT_ASSETS_ITEMS: ["非流动资产其他项目"],
        HKStockMarketFields.PAYABLES_RELATED_PARTIES_CURRENT: ["应付关联方款项(流动)"],
        HKStockMarketFields.NOTES_PAYABLE: ["应付票据"],
        HKStockMarketFields.NOTES_PAYABLE_NON_CURRENT: ["应付票据(非流动)"],
        HKStockMarketFields.OTHER_PAYABLES_ACCRUED_EXPENSES: ["其他应付款及应计费用"],
        HKStockMarketFields.OTHER_FINANCIAL_LIABILITIES_CURRENT: ["其他金融负债(流动)"],
        HKStockMarketFields.OTHER_FINANCIAL_LIABILITIES_NON_CURRENT: ["其他金融负债(非流动)"],
        HKStockMarketFields.FINANCE_LEASE_LIABILITIES_CURRENT: ["融资租赁负债(流动)"],
        HKStockMarketFields.FINANCE_LEASE_LIABILITIES_NON_CURRENT: ["融资租赁负债(非流动)"],
        HKStockMarketFields.DERIVATIVES_LIABILITIES_CURRENT: ["衍生金融工具-负债(流动)"],
        HKStockMarketFields.DEFERRED_INCOME_CURRENT: ["递延收入(流动)"],
        HKStockMarketFields.DEFERRED_INCOME_NON_CURRENT: ["递延收入(非流动)"],
        HKStockMarketFields.LONG_TERM_PAYABLES_OTHER: ["长期应付款"],
        HKStockMarketFields.TOTAL_EQUITY_AND_LIABILITIES: ["总权益及总负债"],
        HKStockMarketFields.TOTAL_EQUITY_AND_NON_CURRENT_LIABILITIES: ["总权益及非流动负债"],
        HKStockMarketFields.SHARE_CAPITAL_PREMIUM: ["股本溢价"],
        HKStockMarketFields.RESERVES: ["储备"],
        HKStockMarketFields.OTHER_RESERVES: ["其他储备"],
        HKStockMarketFields.RETAINED_EARNINGS_DEFICIT: ["保留溢利(累计亏损)"],
        HKStockMarketFields.NET_ASSETS: ["净资产"],
        HKStockMarketFields.NET_CURRENT_ASSETS: ["净流动资产"],
        HKStockMarketFields.TOTAL_ASSETS_MINUS_LIABILITIES: ["总资产减总负债合计"],
        HKStockMarketFields.TOTAL_ASSETS_MINUS_CURRENT_LIABILITIES: ["总资产减流动负债"],

        # 利润表特有字段
        HKStockMarketFields.OPERATING_REVENUE: ["营运收入"],
        HKStockMarketFields.OTHER_OPERATING_REVENUE: ["其他营业收入"],
        HKStockMarketFields.PROFIT_BEFORE_TAX: ["除税前溢利"],
        HKStockMarketFields.PROFIT_AFTER_TAX: ["除税后溢利"],
        HKStockMarketFields.PROFIT_ATTRIBUTABLE_TO_ASSOCIATES: ["应占合营公司溢利"],
        HKStockMarketFields.OPERATING_EXPENDITURE: ["营运支出"],
        HKStockMarketFields.SELLING_DISTRIBUTION_EXPENSES: ["销售及分销费用"],
        HKStockMarketFields.ADMINISTRATIVE_EXPENSES_HK: ["行政开支"],
        HKStockMarketFields.NON_OPERATING_ITEMS: ["非运算项目"],
        HKStockMarketFields.OTHER_PROFIT_ITEMS: ["溢利其他项目"],
        HKStockMarketFields.DIVIDENDS_PER_SHARE: ["每股股息"],
        HKStockMarketFields.DIVIDENDS: ["股息"],
        HKStockMarketFields.TOTAL_COMPREHENSIVE_INCOME_HK: ["全面收益总额"],
        HKStockMarketFields.OTHER_COMPREHENSIVE_INCOME_ITEMS: ["其他全面收益其他项目"],
        HKStockMarketFields.COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_COMP: ["本公司拥有人应占全面收益总额"],
        HKStockMarketFields.COMPREHENSIVE_INCOME_NON_CONTROLLING: ["非控股权益应占全面收益总额"],

        # 现金流量表特有字段
        HKStockMarketFields.PROFIT_BEFORE_TAX_OPERATING: ["除税前溢利(业务利润)"],
        HKStockMarketFields.ADD_INTEREST_EXPENSE: ["加:利息支出"],
        HKStockMarketFields.ADD_DEPRECIATION_AMORTIZATION: ["加:折旧及摊销"],
        HKStockMarketFields.ADD_IMPAIRMENT_PROVISIONS: ["加:减值及拨备"],
        HKStockMarketFields.ADD_OPERATING_ADJUSTMENT_OTHER: ["加:经营调整其他项目"],
        HKStockMarketFields.OPERATING_PROFIT_BEFORE_WORKING_CAPITAL: ["营运资金变动前经营溢利"],
        HKStockMarketFields.INVENTORY_INCREASE_DECREASE: ["存货(增加)减少"],
        HKStockMarketFields.RECEIVABLES_DECREASE: ["应收帐款减少"],
        HKStockMarketFields.PREPAYMENTS_DECREASE_INCREASE: ["预付款项、按金及其他应收款项减少(增加)"],
        HKStockMarketFields.PAYABLES_INCREASE_DECREASE: ["应付帐款及应计费用增加(减少)"],
        HKStockMarketFields.DEFERRED_INCOME_INCREASE_DECREASE: ["预收账款、按金及其他应付款增加(减少)"],
        HKStockMarketFields.PAYABLES_RELATED_PARTIES_INCREASE_DECREASE: ["应付关联方款项增加(减少)"],
        HKStockMarketFields.WORKING_CAPITAL_CHANGE_OTHER: ["营运资本变动其他项目"],
        HKStockMarketFields.INTEREST_PAID_OPERATING: ["已付利息(经营)"],
        HKStockMarketFields.TAX_PAID: ["已付税项"],
        HKStockMarketFields.SUBTRACT_INTEREST_INCOME: ["减:利息收入"],
        HKStockMarketFields.SUBTRACT_ASSOCIATES_PROFIT: ["减:应占附属公司溢利"],
        HKStockMarketFields.SUBTRACT_INVESTMENT_INCOME: ["减:投资收益"],
        HKStockMarketFields.INTEREST_RECEIVED_INVESTING: ["已收利息(投资)"],
        HKStockMarketFields.DIVIDENDS_RECEIVED_INVESTING: ["已收股息(投资)"],
        HKStockMarketFields.DISPOSAL_FIXED_ASSETS: ["处置固定资产"],
        HKStockMarketFields.DISPOSAL_INTANGIBLE_OTHER_ASSETS: ["处置无形资产及其他资产"],
        HKStockMarketFields.DISPOSAL_SUBSIDIARIES: ["出售附属公司"],
        HKStockMarketFields.SUBTRACT_DISPOSAL_GAIN: ["减:出售资产之溢利"],
        HKStockMarketFields.ACQUISITION_FIXED_ASSETS: ["购建固定资产"],
        HKStockMarketFields.ACQUISITION_INTANGIBLE_OTHER_ASSETS: ["购建无形资产及其他资产"],
        HKStockMarketFields.ACQUISITION_SUBSIDIARIES: ["收购附属公司"],
        HKStockMarketFields.PURCHASE_MINORITY_INTEREST: ["购买子公司少数股权而支付的现金"],
        HKStockMarketFields.TRADING_INVESTMENTS_INCREASE_DECREASE: ["持作买卖投资(增加)减少"],
        HKStockMarketFields.DEPOSITS_DECREASE_INCREASE: ["存款减少(增加)"],
        HKStockMarketFields.RECEIVABLES_RELATED_PARTIES_INVESTING: ["应收关联方款项(增加)减少(投资)"],
        HKStockMarketFields.INVESTING_OTHER_ITEMS: ["投资业务其他项目"],
        HKStockMarketFields.NEW_BORROWINGS: ["新增借款"],
        HKStockMarketFields.REPAYMENT_BORROWINGS: ["偿还借款"],
        HKStockMarketFields.INTEREST_PAID_FINANCING: ["已付利息(融资)"],
        HKStockMarketFields.DIVIDENDS_PAID_FINANCING: ["已付股息(融资)"],
        HKStockMarketFields.ISSUE_SHARES: ["发行股份"],
        HKStockMarketFields.BUYBACK_SHARES: ["回购股份"],
        HKStockMarketFields.INVESTMENT_RECEIVED: ["吸收投资所得"],
        HKStockMarketFields.ISSUE_BONDS: ["发行债券"],
        HKStockMarketFields.REDEEM_BONDS: ["赎回债券"],
        HKStockMarketFields.REPAYMENT_FINANCE_LEASE: ["偿还融资租赁"],
        HKStockMarketFields.ISSUE_RELATED_COSTS: ["发行相关费用"],
        HKStockMarketFields.FINANCING_OTHER_ITEMS: ["融资业务其他项目"],
        HKStockMarketFields.CASH_BEFORE_FINANCING: ["融资前现金净额"],
        HKStockMarketFields.SUBTRACT_EXCHANGE_GAIN: ["减:汇兑收益"],
        HKStockMarketFields.PERIOD_CHANGE_OTHER_ITEMS: ["期间变动其他项目"],

        # 财务指标字段
        HKStockMarketFields.OPERATING_CASH_FLOW_PER_SHARE_HK: ["PER_NETCASH_OPERATE", "每股经营现金流(港元)"],
        HKStockMarketFields.OPERATING_INCOME_PER_SHARE: ["PER_OI", "每股营业收入(港元)"],
        HKStockMarketFields.NET_ASSETS_PER_SHARE: ["BPS", "每股净资产(港元)"],
        HKStockMarketFields.BASIC_EPS_HKD: ["BASIC_EPS", "基本每股收益(港元)"],
        HKStockMarketFields.DILUTED_EPS_HKD: ["DILUTED_EPS", "稀释每股收益(港元)"],
        HKStockMarketFields.OPERATING_INCOME_HUNDRED_MILLION: ["OPERATE_INCOME", "营业收入(亿港元)"],
        HKStockMarketFields.OPERATING_INCOME_YOY: ["OPERATE_INCOME_YOY", "营业收入同比增长(%)"],
        HKStockMarketFields.GROSS_PROFIT_HUNDRED_MILLION: ["GROSS_PROFIT", "毛利润(亿港元)"],
        HKStockMarketFields.GROSS_PROFIT_YOY: ["GROSS_PROFIT_YOY", "毛利润同比增长(%)"],
        HKStockMarketFields.HOLDER_PROFIT_HUNDRED_MILLION: ["HOLDER_PROFIT", "股东净利润(亿港元)"],
        HKStockMarketFields.HOLDER_PROFIT_YOY: ["HOLDER_PROFIT_YOY", "股东净利润同比增长(%)"],
        HKStockMarketFields.GROSS_PROFIT_RATIO: ["GROSS_PROFIT_RATIO", "毛利率(%)"],
        HKStockMarketFields.EPS_TTM: ["EPS_TTM", "滚动市盈率"],
        HKStockMarketFields.OPERATING_INCOME_QOQ: ["OPERATE_INCOME_QOQ", "营业收入环比增长(%)"],
        HKStockMarketFields.NET_PROFIT_RATIO: ["NET_PROFIT_RATIO", "净利率(%)"],
        HKStockMarketFields.ROE_AVG: ["ROE_AVG", "平均净资产收益率(%)"],
        HKStockMarketFields.GROSS_PROFIT_QOQ: ["GROSS_PROFIT_QOQ", "毛利润环比增长(%)"],
        HKStockMarketFields.ROA: ["ROA", "总资产收益率(%)"],
        HKStockMarketFields.HOLDER_PROFIT_QOQ: ["HOLDER_PROFIT_QOQ", "股东净利润环比增长(%)"],
        HKStockMarketFields.ROE_YEARLY: ["ROE_YEARLY", "年度净资产收益率(%)"],
        HKStockMarketFields.ROIC_YEARLY: ["ROIC_YEARLY", "年度投入资本回报率(%)"],
        HKStockMarketFields.TAX_EBT: ["TAX_EBT", "税前利润税率(%)"],
        HKStockMarketFields.OCF_SALES: ["OCF_SALES", "经营活动现金流/营业收入(%)"],
        HKStockMarketFields.DEBT_ASSET_RATIO: ["DEBT_ASSET_RATIO", "资产负债率(%)"],
        HKStockMarketFields.CURRENT_RATIO_HK: ["CURRENT_RATIO", "流动比率"],
        HKStockMarketFields.CURRENT_DEBT_TO_TOTAL_DEBT: ["CURRENTDEBT_DEBT", "流动负债/总负债(%)"],
    }


def get_us_stock_specific_mappings() -> Dict[str, List[str]]:
    """
    获取美股特有字段映射配置

    基于文档: doc/us_stock_fields.md

    Returns:
        Dict[美股特有字段, 原始字段列表]

    Note:
        这些字段仅在美股市场存在，不在StandardFields中定义
    """
    return {
        # 资产负债表特有字段
        USStockMarketFields.MARKETABLE_SECURITIES_CURRENT: ["有价证券投资(流动)"],
        USStockMarketFields.MARKETABLE_SECURITIES_NON_CURRENT: ["有价证券投资(非流动)"],
        USStockMarketFields.SHORT_TERM_INVESTMENTS: ["短期投资"],
        USStockMarketFields.LONG_TERM_INVESTMENTS: ["长期投资"],
        USStockMarketFields.NOTES_PAYABLE_CURRENT: ["应付票据(流动)"],
        USStockMarketFields.DEFERRED_TAX_LIABILITIES_NON_CURRENT: ["递延所得税负债(非流动)"],
        USStockMarketFields.DEFERRED_TAX_ASSETS_CURRENT: ["递延所得税资产(流动)"],
        USStockMarketFields.DEFERRED_REVENUE_CURRENT: ["递延收入(流动)"],
        USStockMarketFields.DEFERRED_REVENUE_NON_CURRENT: ["递延收入(非流动)"],
        USStockMarketFields.ADVANCE_PAYMENTS_ACCRUED_EXPENSES: ["预收及预提费用"],
        USStockMarketFields.ATTRIBUTABLE_TO_PARENT_EQUITY_OTHER_ITEMS: ["归属于母公司股东权益其他项目"],
        USStockMarketFields.PREFERRED_STOCK: ["优先股"],

        # 利润表特有字段
        USStockMarketFields.MAIN_OPERATING_REVENUE: ["主营收入"],
        USStockMarketFields.MAIN_OPERATING_COST: ["主营成本"],
        USStockMarketFields.OPERATING_EXPENSES_US: ["营业费用"],
        USStockMarketFields.MARKETING_EXPENSES: ["营销费用"],
        USStockMarketFields.RESTRUCTURING_EXPENSES: ["重组费用"],
        USStockMarketFields.OTHER_OPERATING_EXPENSES: ["其他营业费用"],
        USStockMarketFields.CONTINUING_OPERATIONS_INCOME_BEFORE_TAX: ["持续经营税前利润"],
        USStockMarketFields.CONTINUING_OPERATIONS_NET_INCOME: ["持续经营净利润"],
        USStockMarketFields.ATTRIBUTABLE_TO_COMMON_SHAREHOLDERS: ["归属于普通股股东净利润"],
        USStockMarketFields.NET_INCOME_OTHER_ITEMS: ["税后利润其他项目"],
        USStockMarketFields.EQUITY_INVESTMENT_GAIN_LOSS: ["权益性投资损益"],
        USStockMarketFields.OTHER_INCOME_EXPENSE: ["其他收入(支出)"],
        USStockMarketFields.BASIC_WEIGHTED_SHARES_COMMON: ["基本加权平均股数-普通股"],
        USStockMarketFields.BASIC_EPS_COMMON: ["基本每股收益-普通股"],
        USStockMarketFields.DILUTED_WEIGHTED_SHARES_COMMON: ["摊薄加权平均股数-普通股"],
        USStockMarketFields.DILUTED_EPS_COMMON: ["摊薄每股收益-普通股"],
        USStockMarketFields.DIVIDENDS_PER_SHARE_COMMON: ["每股股息-普通股"],
        USStockMarketFields.ATTRIBUTABLE_TO_COMPANY_COMPREHENSIVE_INCOME: ["本公司拥有人占全面收益总额"],
        USStockMarketFields.OTHER_COMPREHENSIVE_INCOME_OTHER_ITEMS: ["其他全面收益其他项目"],
        USStockMarketFields.OTHER_COMPREHENSIVE_INCOME_TOTAL: ["其他全面收益合计项"],
        USStockMarketFields.NON_CONTROLLING_COMPREHENSIVE_INCOME: ["非控股权益占全面收益总额"],

        # 现金流量表特有字段
        USStockMarketFields.DEPRECIATION_AMORTIZATION_US: ["折旧及摊销"],
        USStockMarketFields.IMPAIRMENT_PROVISIONS: ["减值及拨备"],
        USStockMarketFields.STOCK_BASED_COMPENSATION: ["基于股票的补偿费"],
        USStockMarketFields.DEFERRED_TAX_US: ["递延所得税"],
        USStockMarketFields.EXCESS_TAX_BENEFIT: ["超额税收优惠"],
        USStockMarketFields.ASSET_DISPOSAL_GAIN_LOSS: ["资产处置损益"],
        USStockMarketFields.ACCOUNTS_RECEIVABLE_NOTES: ["应收账款及票据"],
        USStockMarketFields.ACCOUNTS_PAYABLE_NOTES: ["应付账款及票据"],
        USStockMarketFields.OPERATING_ADJUSTMENT_OTHER_ITEMS: ["经营业务调整其他项目"],
        USStockMarketFields.OPERATING_OTHER_ITEMS: ["经营业务其他项目"],
        USStockMarketFields.INVESTMENT_GAIN_LOSS_CF: ["投资损益"],
        USStockMarketFields.PURCHASE_FIXED_ASSETS: ["购买固定资产"],
        USStockMarketFields.PURCHASE_INTANGIBLE_OTHER_ASSETS: ["购建无形资产及其他资产"],
        USStockMarketFields.LOAN_INCOME: ["贷款收益"],
        USStockMarketFields.INVESTING_OTHER_ITEMS: ["投资业务其他项目"],
        USStockMarketFields.OTHER_INVESTING_CASH_FLOW: ["其他投资活动产生的现金流量净额"],
        USStockMarketFields.DIVIDEND_PAYMENT: ["股息支付"],
        USStockMarketFields.FINANCING_OTHER_ITEMS: ["筹资业务其他项目"],
        USStockMarketFields.OTHER_FINANCING_CASH_FLOW: ["其他筹资活动产生的现金流量净额"],
        USStockMarketFields.CASH_EQUIVALENTS_INCREASE_DECREASE: ["现金及现金等价物增加(减少)额"],
        USStockMarketFields.REVALUATION_SURPLUS: ["重估盈余"],

        # 财务指标字段
        USStockMarketFields.OPERATE_INCOME_US: ["OPERATE_INCOME", "营业收入"],
        USStockMarketFields.OPERATE_INCOME_YOY_US: ["OPERATE_INCOME_YOY", "营业收入同比增长(%)"],
        USStockMarketFields.GROSS_PROFIT_US: ["GROSS_PROFIT", "毛利润"],
        USStockMarketFields.GROSS_PROFIT_YOY_US: ["GROSS_PROFIT_YOY", "毛利润同比增长(%)"],
        USStockMarketFields.PARENT_HOLDER_NETPROFIT: ["PARENT_HOLDER_NETPROFIT", "归属于母公司股东净利润"],
        USStockMarketFields.PARENT_HOLDER_NETPROFIT_YOY: ["PARENT_HOLDER_NETPROFIT_YOY", "归属于母公司股东净利润同比增长(%)"],
        USStockMarketFields.GROSS_PROFIT_RATIO_US: ["GROSS_PROFIT_RATIO", "毛利率(%)"],
        USStockMarketFields.NET_PROFIT_RATIO_US: ["NET_PROFIT_RATIO", "净利率(%)"],
        USStockMarketFields.ROE_AVG_US: ["ROE_AVG", "平均净资产收益率(%)"],
        USStockMarketFields.ROA_US: ["ROA", "总资产收益率(%)"],
        USStockMarketFields.ACCOUNTS_RECEIVABLE_TURNOVER: ["ACCOUNTS_RECE_TR", "应收账款周转率"],
        USStockMarketFields.INVENTORY_TURNOVER_US: ["INVENTORY_TR", "存货周转率"],
        USStockMarketFields.TOTAL_ASSETS_TURNOVER: ["TOTAL_ASSETS_TR", "总资产周转率"],
        USStockMarketFields.ACCOUNTS_RECEIVABLE_DAYS: ["ACCOUNTS_RECE_TDAYS", "应收账款周转天数"],
        USStockMarketFields.INVENTORY_DAYS: ["INVENTORY_TDAYS", "存货周转天数"],
        USStockMarketFields.TOTAL_ASSETS_DAYS: ["TOTAL_ASSETS_TDAYS", "总资产周转天数"],
        USStockMarketFields.CURRENT_RATIO_US: ["CURRENT_RATIO", "流动比率"],
        USStockMarketFields.SPEED_RATIO: ["SPEED_RATIO", "速动比率"],
        USStockMarketFields.OCF_TO_CURRENT_DEBT: ["OCF_LIQDEBT", "经营现金流/流动负债"],
        USStockMarketFields.DEBT_ASSET_RATIO_US: ["DEBT_ASSET_RATIO", "资产负债率(%)"],
        USStockMarketFields.EQUITY_RATIO: ["EQUITY_RATIO", "权益乘数"],
        USStockMarketFields.BASIC_EPS_YOY: ["BASIC_EPS_YOY", "基本每股收益同比增长(%)"],
        USStockMarketFields.GROSS_PROFIT_RATIO_YOY: ["GROSS_PROFIT_RATIO_YOY", "毛利率同比增长(%)"],
        USStockMarketFields.NET_PROFIT_RATIO_YOY: ["NET_PROFIT_RATIO_YOY", "净利率同比增长(%)"],
        USStockMarketFields.ROE_AVG_YOY: ["ROE_AVG_YOY", "平均净资产收益率同比增长(%)"],
        USStockMarketFields.ROA_YOY: ["ROA_YOY", "总资产收益率同比增长(%)"],
        USStockMarketFields.DEBT_ASSET_RATIO_YOY: ["DEBT_ASSET_RATIO_YOY", "资产负债率同比增长(%)"],
        USStockMarketFields.CURRENT_RATIO_YOY: ["CURRENT_RATIO_YOY", "流动比率同比增长(%)"],
        USStockMarketFields.SPEED_RATIO_YOY: ["SPEED_RATIO_YOY", "速动比率同比增长(%)"],
    }


def load_market_specific_mappings() -> Dict[str, Dict[str, List[str]]]:
    """
    加载所有市场的特有字段映射配置

    Returns:
        Dict[市场名称, Dict[市场特有字段, 原始字段列表]]

    Example:
        >>> config = load_market_specific_mappings()
        >>> config['a_stock'][AStockMarketFields.SPLIT_OUT_CAPITAL]
        ['拆出资金']
    """
    return {
        'a_stock': get_a_stock_specific_mappings(),
        'hk_stock': get_hk_stock_specific_mappings(),
        'us_stock': get_us_stock_specific_mappings(),
    }
