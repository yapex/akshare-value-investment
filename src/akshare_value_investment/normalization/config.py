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
