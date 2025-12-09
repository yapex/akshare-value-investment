"""
市场配置 - 不同市场的字段映射
"""

from typing import Dict, List
from .base_models import MarketType


# A股字段配置（基于FastAPI字段发现API验证）
A_STOCK_FIELDS = {
    "balance_sheet": {
        "报告期": "报告期",
        "货币资金": "货币资金",
        "交易性金融资产": "交易性金融资产",
        "短期借款": "短期借款",
        "长期借款": "长期借款",
        "应收票据及应收账款": "应收票据及应收账款",
        "应收账款": "应收账款",
        "其他应收款": "其他应收款",
        "预付款项": "预付款项",
        "存货": "存货",
        "其中：固定资产": "其中：固定资产",
        "其中：在建工程": "其中：在建工程",
        "应付账款": "应付账款",
        "预收款项": "预收款项",
        "应付职工薪酬": "应付职工薪酬",
        "*资产合计": "*资产合计",
        "*负债合计": "*负债合计",
        "归属于母公司所有者权益合计": "归属于母公司所有者权益合计",
        "所有者权益（或股东权益）合计": "所有者权益（或股东权益）合计"
    },
    "income_statement": {
        "报告期": "报告期",
        "其中：营业收入": "其中：营业收入",
        "其中：营业成本": "其中：营业成本",
        "利息收入": "利息收入",
        "销售费用": "销售费用",
        "管理费用": "管理费用",
        "财务费用": "财务费用",
        "研发费用": "研发费用",
        "三、营业利润": "三、营业利润",
        "利润总额": "四、利润总额",
        "净利润": "五、净利润",
        "归属于母公司所有者的净利润": "归属于母公司所有者的净利润"
    },
    "cash_flow": {
        "报告期": "报告期",
        "经营活动产生的现金流量净额": "经营活动产生的现金流量净额",
        "投资活动产生的现金流量净额": "投资活动产生的现金流量净额",
        "筹资活动产生的现金流量净额": "筹资活动产生的现金流量净额"
    }
}

# 港股字段配置（TODO: 待完善）
HK_STOCK_FIELDS = {
    "balance_sheet": {
        # TODO: 港股字段映射
    },
    "income_statement": {
        # TODO: 港股字段映射
    },
    "cash_flow": {
        # TODO: 港股字段映射
    }
}

# 美股字段配置（TODO: 待完善）
US_STOCK_FIELDS = {
    "balance_sheet": {
        # TODO: 美股字段映射
    },
    "income_statement": {
        # TODO: 美股字段映射
    },
    "cash_flow": {
        # TODO: 美股字段映射
    }
}

# 市场配置映射
MARKET_CONFIGS = {
    MarketType.A_STOCK: A_STOCK_FIELDS,
    MarketType.HK_STOCK: HK_STOCK_FIELDS,
    MarketType.US_STOCK: US_STOCK_FIELDS
}


def get_market_fields(market: MarketType, query_type: str) -> Dict[str, str]:
    """获取指定市场和查询类型的字段映射

    Args:
        market: 市场类型
        query_type: 查询类型 (balance_sheet, income_statement, cash_flow)

    Returns:
        字段映射字典
    """
    config = MARKET_CONFIGS.get(market, {})
    return config.get(query_type, {})


def get_all_market_configs() -> Dict[MarketType, Dict[str, Dict[str, str]]]:
    """获取所有市场的配置

    Returns:
        所有市场配置字典
    """
    return MARKET_CONFIGS.copy()


def get_required_fields_for_market(market: MarketType, query_type: str) -> List[str]:
    """获取指定市场和查询类型的所有字段列表

    Args:
        market: 市场类型
        query_type: 查询类型

    Returns:
        字段列表
    """
    fields_config = get_market_fields(market, query_type)
    return list(fields_config.values()) if fields_config else []