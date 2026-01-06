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
