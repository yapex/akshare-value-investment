"""
数据格式化模块

处理财务数据的格式化和转换
"""

import pandas as pd
import streamlit as st
from typing import Dict, List


def format_financial_data(df: pd.DataFrame, report_type: str, market: str = "A股") -> pd.DataFrame:
    """
    格式化财务数据为窄表格式

    Args:
        df: 原始数据DataFrame
        report_type: 报表类型

    Returns:
        格式化后的DataFrame（窄表格式：年份为列，字段为行）
    """
    if df.empty:
        return df

    df_formatted = df.copy()

    # 识别日期列
    date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
    date_col = None
    for col in date_columns:
        if col in df_formatted.columns:
            date_col = col
            break

    if date_col is None:
        return df_formatted

    # 确保日期列为datetime类型
    df_formatted[date_col] = pd.to_datetime(df_formatted[date_col])

    # 提取年份作为列名
    df_formatted['年份'] = df_formatted[date_col].dt.year

    # 按年份降序排列（最新的年份在前）
    df_formatted = df_formatted.sort_values('年份', ascending=False)

    # 获取唯一的年份，按降序排列
    years = sorted(df_formatted['年份'].unique(), reverse=True)

    # 获取指标字段映射
    indicator_mapping = get_indicator_mapping(report_type)

    # 移除日期列和年份列，获取指标列
    indicator_cols = [col for col in df_formatted.columns
                     if col not in [date_col, '年份'] and col not in date_columns]

    # 创建窄表格式
    result_data = []

    for indicator in indicator_cols:
        # 获取友好的指标名称
        indicator_name = indicator_mapping.get(indicator, indicator)

        # 跳过说明性行，只处理实际数据
        if indicator == '报表核心指标' or indicator == 'SECURITY_CODE' or indicator == 'SECURITY_NAME_ABBR':
            continue

        row_data = {'指标名称': indicator_name}
        for year in years:
            year_data = df_formatted[df_formatted['年份'] == year]
            if not year_data.empty:
                value = year_data[indicator].iloc[0] if len(year_data) > 0 else None
                # 智能数据处理：根据指标类型和市场类型进行相应转换
                if value is not None and not pd.isna(value):
                    # 判断指标类型
                    indicator_type = get_financial_indicator_type(indicator_name)

                    # 美股特殊处理：美元转换为亿美元
                    if 'us_stock_indicators' in report_type:
                        # 美股的绝对金额类指标需要转换为亿美元
                        if indicator_type == 'amount':
                            if isinstance(value, str):
                                clean_value = value.replace(',', '').replace('，', '').strip()
                                try:
                                    float_val = float(clean_value)
                                except ValueError:
                                    row_data[str(year)] = None
                                    continue
                            elif isinstance(value, (int, float)):
                                float_val = float(value)
                            else:
                                row_data[str(year)] = None
                                continue

                            # 转换为亿美元
                            billions_val = float_val / 100_000_000
                            row_data[str(year)] = f"{billions_val:.2f}"
                        else:
                            # 美股非金额类指标：使用通用格式化，但移除百分比符号
                            formatted_value = format_financial_value_by_type(value, indicator_type, indicator_name, market)
                            if formatted_value and '%' in formatted_value:
                                formatted_value = formatted_value.replace('%', '')
                            row_data[str(year)] = formatted_value
                    else:
                        # A股和港股：使用智能格式化函数
                        formatted_value = format_financial_value_by_type(value, indicator_type, indicator_name, market)
                        row_data[str(year)] = formatted_value
                else:
                    # 非数值数据保持None，避免类型混合
                    row_data[str(year)] = None
            else:
                row_data[str(year)] = None
        result_data.append(row_data)

    # 创建新的DataFrame
    narrow_df = pd.DataFrame(result_data)

    # 重新排列列：指标名称 + 年份列
    year_columns = [str(year) for year in years]
    column_order = ['指标名称'] + year_columns

    # 确保列存在
    available_cols = [col for col in column_order if col in narrow_df.columns]
    narrow_df = narrow_df[available_cols]

    return narrow_df


def get_financial_indicator_type(indicator_name: str) -> str:
    """
    根据指标名称判断财务指标类型

    Returns:
        'amount': 绝对金额类（亿元、万元等）
        'percentage': 比率类（百分比）
        'multiplier': 倍数类（周转率、比率）
        'per_share': 每股类（元/股）
        'days': 时间类（天数）
        'other': 其他类型
    """
    # 绝对金额类 - 收入、利润、资产、负债等（排除增长率）
    amount_keywords = [
        # 英文指标
        '总收入', '收入', '净利润', '利润', '毛利', '营业利润', '息税前利润',
        '资产总计', '负债合计', '所有者权益', '未分配利润', '资本公积',
        'TOTAL_REVENUE', 'NET_INCOME', 'GROSS_PROFIT', 'OPERATING_INCOME',
        'TOTAL_ASSETS', 'TOTAL_LIABILITIES', 'TOTAL_EQUITY', 'CASH',
        'INVENTORY', 'ACCOUNTS_RECEIVABLE',
        # 中文港股指标
        '总资产', '总负债', '股东权益', '营业收入', '销售成本', '毛利', '税前利润',
        '年内溢利', '净利润', '存货', '应收账款', '应付账款', '固定资产', '无形资产',
        '现金及现金等价物', '银行存款', '保留溢利', '储备', '留存溢利', '投资物业',
        '中长期存款', '其他储备', '其他金融资产', '其他金融负债', '净资产', '净流动资产'
    ]

    # 排除增长率指标
    if any(keyword in indicator_name for keyword in amount_keywords) and '增长率' not in indicator_name and '同比' not in indicator_name and '环比' not in indicator_name:
        return 'amount'

    # 增长率类
    elif any(keyword in indicator_name for keyword in [
        '同比增长率', '增长率', '同比', '环比', 'YOY', 'QOQ', '_GROWTH'
    ]):
        return 'percentage'

    # 比率类 - 百分比形式
    elif any(keyword in indicator_name for keyword in [
        '净利率', '毛利率', 'ROE', 'ROA', '负债率', '权益乘数', '销售费用率',
        '管理费用率', '财务费用率', '研发费用率', '所得税', '税前利润税率',
        'RATIO', '_RATIO', 'RATE'
    ]):
        return 'percentage'

    # 倍数类 - 周转率、流动性比率
    elif any(keyword in indicator_name for keyword in [
        '周转率', '流动比率', '速动比率', '保守速动比率', '产权比率',
        '现金比率', '利息保障倍数', '倍数', 'TURNOVER', 'RATIO'
    ]):
        return 'multiplier'

    # 每股类
    elif any(keyword in indicator_name for keyword in [
        '每股', 'EPS', '每股市价', 'PER_', 'BPS', 'BASIC_EPS', 'DILUTED_EPS'
    ]):
        return 'per_share'

    # 时间类
    elif any(keyword in indicator_name for keyword in [
        '周转天数', '周期', '账龄', '回收期', '_DAYS', 'DAYS'
    ]):
        return 'days'

    # 其他类型
    else:
        return 'other'


def format_financial_value_by_type(value, indicator_type: str, indicator_name: str, market: str = "A股") -> str:
    """
    根据指标类型格式化财务数值
    """
    # 处理布尔值
    if isinstance(value, bool):
        return None

    # 处理字符串类型
    if isinstance(value, str):
        clean_value = value.replace(',', '').replace('，', '').strip()

        # 处理百分比格式
        if '%' in clean_value:
            try:
                percentage_val = float(clean_value.replace('%', '').strip())
                return f"{percentage_val:.2f}"
            except ValueError:
                return None

        # 处理"亿"单位
        elif '亿' in clean_value:
            if indicator_type == 'amount':
                # 金额类：保持"亿"格式，但确保两位小数
                if '.' in value:
                    parts = value.split('亿')
                    number_part = parts[0]
                    try:
                        formatted_number = f"{float(number_part):.2f}"
                        return f"{formatted_number}亿"
                    except ValueError:
                        return value
                else:
                    try:
                        formatted_number = f"{float(value.replace('亿', '')):.2f}"
                        return f"{formatted_number}亿"
                    except ValueError:
                        return value
            else:
                # 非金额类的"亿"单位，转换为数值
                try:
                    float_val = float(clean_value.replace('亿', '').strip())
                    return f"{float_val:.2f}"
                except ValueError:
                    return None

        # 处理"万"单位
        elif '万' in clean_value:
            if indicator_type == 'amount':
                # 金额类："万"转换为"亿"
                try:
                    float_val = float(clean_value.replace('万', '').strip()) / 10000
                    return f"{float_val:.2f}亿"
                except ValueError:
                    return None
            else:
                # 非金额类的"万"单位，转换为数值
                try:
                    float_val = float(clean_value.replace('万', '').strip())
                    return f"{float_val:.2f}"
                except ValueError:
                    return None

        # 普通数字
        else:
            try:
                float_val = float(clean_value)

                # 根据指标类型进行格式化
                if indicator_type == 'amount':
                    # 金额类：如果是大数值，假设为元，转换为亿元
                    if float_val >= 1_000_000_000:  # 10亿以上
                        billions_val = float_val / 100_000_000
                        return f"{billions_val:.2f}亿"
                    else:
                        return f"{float_val:.2f}"
                elif indicator_type == 'percentage':
                    return f"{float_val:.2f}%"
                elif indicator_type == 'multiplier':
                    return f"{float_val:.2f}"
                elif indicator_type == 'per_share':
                    return f"{float_val:.2f}"
                elif indicator_type == 'days':
                    return f"{float_val:.2f}"
                else:
                    return f"{float_val:.2f}"
            except ValueError:
                return None

    # 处理数值类型（包括numpy数值类型）
    elif isinstance(value, (int, float)) or str(type(value)).startswith("<class 'numpy."):
        try:
            float_val = float(value)
        except (ValueError, TypeError):
            return None

        # 根据指标类型和市场进行格式化
        if indicator_type == 'amount':
            if market == "港股":
                # 港股金额：港元转换为亿港元，所有数据都转换为亿港元显示
                billions_val = float_val / 100_000_000
                return f"{billions_val:.2f}"
            elif market == "美股":
                # 美股金额：美元转换为亿美元，所有数据都转换为亿美元显示
                billions_val = float_val / 1_000_000_000
                return f"{billions_val:.2f}"
            else:  # A股
                # A股金额：元转换为亿元
                if float_val >= 1_000_000_000:  # 10亿以上
                    billions_val = float_val / 100_000_000
                    return f"{billions_val:.2f}"
                else:
                    return f"{float_val:.2f}"
        elif indicator_type == 'percentage':
            return f"{float_val:.2f}%"
        elif indicator_type == 'multiplier':
            return f"{float_val:.2f}"
        elif indicator_type == 'per_share':
            if market == "港股":
                return f"{float_val:.2f}"  # 港元
            elif market == "美股":
                return f"{float_val:.2f}"  # 美元
            else:
                return f"{float_val:.2f}"  # 人民币
        elif indicator_type == 'days':
            return f"{float_val:.2f}"
        else:
            return f"{float_val:.2f}"

    # 其他类型
    else:
        return None


def get_indicator_mapping(report_type: str) -> Dict[str, str]:
    """
    获取指标字段映射，将技术字段名转换为友好的中文名称

    Args:
        report_type: 报表类型

    Returns:
        字段映射字典
    """
    # 美股财务指标映射（完整版本）
    us_indicators_mapping = {
        'OPERATE_INCOME': '营业收入(亿美元)',
        'OPERATE_INCOME_YOY': '营业收入同比增长(%)',
        'GROSS_PROFIT': '毛利润(亿美元)',
        'GROSS_PROFIT_YOY': '毛利润同比增长(%)',
        'PARENT_HOLDER_NETPROFIT': '归母净利润(亿美元)',
        'PARENT_HOLDER_NETPROFIT_YOY': '归母净利润同比增长(%)',
        'BASIC_EPS': '基本每股收益(美元)',
        'DILUTED_EPS': '稀释每股收益(美元)',
        'GROSS_PROFIT_RATIO': '毛利率(%)',
        'NET_PROFIT_RATIO': '净利率(%)',
        'ACCOUNTS_RECE_TR': '应收账款周转率',
        'INVENTORY_TR': '存货周转率',
        'TOTAL_ASSETS_TR': '总资产周转率',
        'ACCOUNTS_RECE_TDAYS': '应收账款周转天数',
        'INVENTORY_TDAYS': '存货周转天数',
        'TOTAL_ASSETS_TDAYS': '总资产周转天数',
        'ROE_AVG': '净资产收益率(%)',
        'ROA': '总资产收益率(%)',
        'CURRENT_RATIO': '流动比率',
        'SPEED_RATIO': '速动比率',
        'OCF_LIQDEBT': '经营现金流/流动负债',
        'DEBT_ASSET_RATIO': '资产负债率(%)',
        'EQUITY_RATIO': '权益乘数',
        'BASIC_EPS_YOY': '基本每股收益同比增长(%)',
        'GROSS_PROFIT_RATIO_YOY': '毛利率同比增长(%)',
        'NET_PROFIT_RATIO_YOY': '净利率同比增长(%)',
        'ROE_AVG_YOY': '净资产收益率同比增长(%)',
        'ROA_YOY': '总资产收益率同比增长(%)',
        'DEBT_ASSET_RATIO_YOY': '资产负债率同比增长(%)',
        'CURRENT_RATIO_YOY': '流动比率同比增长(%)',
        'SPEED_RATIO_YOY': '速动比率同比增长(%)',
    }

    # 美股资产负债表映射
    us_balance_mapping = {
        'TOTAL_ASSETS': '总资产',
        'TOTAL_LIABILITIES': '总负债',
        'TOTAL_EQUITY': '股东权益',
        'CURRENT_ASSETS': '流动资产',
        'CURRENT_LIABILITIES': '流动负债',
        'CASH_AND_CASH_EQUIVALENTS': '现金及现金等价物',
        'SHORT_TERM_INVESTMENTS': '短期投资',
        'INVENTORY': '存货',
        'ACCOUNTS_RECEIVABLE': '应收账款'
    }

    # 美股利润表映射
    us_income_mapping = {
        'TOTAL_REVENUE': '总收入',
        'GROSS_PROFIT': '毛利润',
        'OPERATING_INCOME': '营业利润',
        'NET_INCOME': '净利润',
        'RESEARCH_AND_DEVELOPMENT': '研发费用',
        'SELLING_GENERAL_AND_ADMINISTRATIVE': '销售费用',
        'INTEREST_EXPENSE': '利息费用'
    }

    # 美股现金流量表映射
    us_cashflow_mapping = {
        'OPERATING_CASH_FLOW': '经营活动现金流',
        'INVESTING_CASH_FLOW': '投资活动现金流',
        'FINANCING_CASH_FLOW': '筹资活动现金流',
        'FREE_CASH_FLOW': '自由现金流',
        'CAPITAL_EXPENDITURE': '资本支出',
        'DEPRECIATION_AMORTIZATION': '折旧摊销'
    }

    # 港股财务指标映射（基于实际akshare港股字段）
    hk_indicators_mapping = {
        'SECUCODE': '股票代码',
        'SECURITY_CODE': '证券代码',
        'SECURITY_NAME_ABBR': '证券名称',
        'ORG_CODE': '机构代码',
        'REPORT_DATE': '报告日期',
        'DATE_TYPE_CODE': '日期类型代码',
        'PER_NETCASH_OPERATE': '每股经营现金流(港元)',
        'PER_OI': '每股营业收入(港元)',
        'BPS': '每股净资产(港元)',
        'BASIC_EPS': '基本每股收益(港元)',
        'DILUTED_EPS': '稀释每股收益(港元)',
        'OPERATE_INCOME': '营业收入(亿港元)',
        'OPERATE_INCOME_YOY': '营业收入同比增长(%)',
        'GROSS_PROFIT': '毛利润(亿港元)',
        'GROSS_PROFIT_YOY': '毛利润同比增长(%)',
        'HOLDER_PROFIT': '股东净利润(亿港元)',
        'HOLDER_PROFIT_YOY': '股东净利润同比增长(%)',
        'GROSS_PROFIT_RATIO': '毛利率(%)',
        'EPS_TTM': '滚动市盈率',
        'OPERATE_INCOME_QOQ': '营业收入环比增长(%)',
        'NET_PROFIT_RATIO': '净利率(%)',
        'ROE_AVG': '平均净资产收益率(%)',
        'GROSS_PROFIT_QOQ': '毛利润环比增长(%)',
        'ROA': '总资产收益率(%)',
        'HOLDER_PROFIT_QOQ': '股东净利润环比增长(%)',
        'ROE_YEARLY': '年度净资产收益率(%)',
        'ROIC_YEARLY': '年度投入资本回报率(%)',
        'TAX_EBT': '税前利润税率(%)',
        'OCF_SALES': '经营活动现金流/营业收入(%)',
        'DEBT_ASSET_RATIO': '资产负债率(%)',
        'CURRENT_RATIO': '流动比率',
        'CURRENTDEBT_DEBT': '流动负债/总负债(%)',
        'START_DATE': '开始日期',
        'FISCAL_YEAR': '财年截止日',
        'CURRENCY': '货币单位',
        'IS_CNY_CODE': '是否人民币代码'
    }

    # 港股财务三表映射（简化版，主要字段友好化）
    hk_statements_mapping = {
        'date': '报告日期',
        'SECURITY_CODE': '股票代码',
        'SECURITY_NAME_ABBR': '股票名称',
        '现金及现金等价物': '现金及现金等价物',
        '存款': '银行存款',
        '受限制存款及现金': '受限制现金',
        '交易性金融资产(流动)': '交易性金融资产',
        '交易性金融资产(非流动)': '非流动交易性资产',
        '应收账款': '应收账款',
        '存货': '存货',
        '固定资产': '固定资产',
        '投资物业': '投资性房地产',
        '无形资产': '无形资产',
        '总资产': '总资产',
        '银行借款': '银行借款',
        '应付账款': '应付账款',
        '其他应付款及应计费用': '其他应付款',
        '计息借款及其他借款': '计息借款',
        '总负债': '总负债',
        '储备': '储备',
        '留存溢利': '留存收益',
        '股东权益': '股东权益',
        '营业收入': '营业收入',
        '销售成本': '营业成本',
        '毛利': '毛利润',
        '其他收益及亏损': '其他收益',
        '销售及分销费用': '销售费用',
        '行政费用': '管理费用',
        '研发费用': '研发费用',
        '财务费用': '财务费用',
        '除税前溢利': '税前利润',
        '所得税': '所得税费用',
        '年内溢利': '年度净利润',
        '经营活动现金流': '经营活动现金流',
        '投资活动现金流': '投资活动现金流',
        '融资活动现金流': '融资活动现金流',
        '现金净增加额': '现金净增加额',
    }

    # 港股资产负债表映射
    hk_balance_sheet_mapping = {
        'date': '报告日期',
        'SECURITY_CODE': '股票代码',
        'SECURITY_NAME_ABBR': '股票名称',
        '现金及现金等价物': '现金及现金等价物',
        '存款': '银行存款',
        '受限制存款及现金': '受限制现金',
        '交易性金融资产(流动)': '交易性金融资产',
        '交易性金融资产(非流动)': '非流动交易性资产',
        '应收账款': '应收账款',
        '存货': '存货',
        '固定资产': '固定资产',
        '投资物业': '投资性房地产',
        '无形资产': '无形资产',
        '总资产': '总资产',
        '银行借款': '银行借款',
        '应付账款': '应付账款',
        '其他应付款及应计费用': '其他应付款',
        '计息借款及其他借款': '计息借款',
        '总负债': '总负债',
        '储备': '储备',
        '留存溢利': '留存收益',
        '股东权益': '股东权益',
    }

    # 港股利润表映射
    hk_income_mapping = {
        'date': '报告日期',
        'SECURITY_CODE': '股票代码',
        'SECURITY_NAME_ABBR': '股票名称',
        '营业收入': '营业收入',
        '其他收入': '其他收入',
        '其他收益': '其他收益',
        '销售成本': '营业成本',
        '毛利': '毛利润',
        '其他全面收益': '其他全面收益',
        '全面收益总额': '全面收益总额',
        '除税前溢利': '税前利润',
        '所得税': '所得税费用',
        '年内溢利': '年度净利润',
    }

    # 港股现金流量表映射
    hk_cashflow_mapping = {
        'date': '报告日期',
        'SECURITY_CODE': '股票代码',
        'SECURITY_NAME_ABBR': '股票名称',
        '经营活动现金流': '经营活动现金流',
        '投资活动现金流': '投资活动现金流',
        '融资活动现金流': '融资活动现金流',
        '现金净增加额': '现金净增加额',
        '期初现金及现金等价物': '期初现金及现金等价物',
        '期末现金及现金等价物': '期末现金及现金等价物',
        '已付利息(经营)': '已付利息(经营)',
        '已收利息(经营)': '已收利息(经营)',
        '吸收投资所得': '吸收投资所得',
        '偿还融资租赁': '偿还融资租赁',
        '减:投资收益': '减:投资收益',
        '加:经营调整其他项目': '加:经营调整其他项目',
    }

    # 根据报告类型选择对应的映射
    if report_type == 'us_stock_indicators':
        return us_indicators_mapping
    elif report_type == 'us_stock_balance_sheet':
        return us_balance_mapping
    elif report_type == 'us_stock_income_statement':
        return us_income_mapping
    elif report_type == 'us_stock_cash_flow':
        return us_cashflow_mapping
    elif report_type == 'hk_stock_indicators':
        return hk_indicators_mapping
    elif report_type == 'hk_stock_balance_sheet':
        return hk_balance_sheet_mapping
    elif report_type == 'hk_stock_income_statement':
        return hk_income_mapping
    elif report_type == 'hk_stock_cash_flow':
        return hk_cashflow_mapping
    elif report_type == 'hk_stock_statements':
        return hk_statements_mapping  # 备用
    else:
        # 默认返回空映射（使用原始字段名）
        return {}


def create_styler(df: pd.DataFrame) -> pd.DataFrame.style:
    """
    创建样式化的DataFrame

    Args:
        df: 要样式化的DataFrame

    Returns:
        样式化的DataFrame
    """
    def _format_values(x):
        if pd.isna(x):
            return "N/A"
        elif isinstance(x, str):
            # 如果是字符串格式（如"6.28亿"），直接返回
            return x
        elif isinstance(x, (int, float)):
            return f"{x:,.2f}"
        else:
            return str(x)

    def _highlight_row(row):
        if row.name % 2 == 0:
            return ['background-color: #f8f9fa'] * len(row)
        else:
            return ['background-color: white'] * len(row)

    # 创建样式化对象
    styler = df.style

    # 应用数值格式化
    for col in df.columns:
        if col not in ['指标名称', '单位']:
            styler = styler.format({col: _format_values})

    # 应用行样式
    styler = styler.apply(_highlight_row, axis=1)

    # 设置表格样式
    styler = styler.set_properties(**{
        'text-align': 'right',
        'padding': '8px',
        'border': '1px solid #dddddd',
        'color': '#000000',
        'font-size': '14px'
    })

    # 设置指标名称列左对齐
    styler = styler.set_properties(subset=['指标名称'], **{
        'text-align': 'left',
        'font-weight': 'bold',
        'color': '#1f77b4'
    })

    # 设置表格样式
    styler = styler.set_table_styles([
        {
            'selector': 'thead th',
            'props': [
                ('background-color', '#f0f2f6'),
                ('font-weight', 'bold'),
                ('text-align', 'center'),
                ('padding', '8px'),
                ('border', '1px solid #dddddd'),
                ('color', '#333333'),
                ('font-size', '14px')
            ]
        },
        {
            'selector': 'tbody tr:hover',
            'props': [
                ('background-color', '#f5f5f5'),
                ('color', '#000000')
            ]
        },
        {
            'selector': 'td',
            'props': [
                ('border-bottom', '1px solid #eeeeee')
            ]
        }
    ])

    return styler


def display_metrics_section(df: pd.DataFrame) -> None:
    """
    显示指标摘要部分

    Args:
        df: 数据DataFrame
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        data_points = len(df)
        st.metric("数据点数", data_points)

    with col2:
        if not df.empty:
            # 尝试获取最新的报告期
            date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
            latest_date = "N/A"
            for date_col in date_columns:
                if date_col in df.columns:
                    try:
                        latest_date_raw = df[date_col].iloc[0]
                        if pd.notna(latest_date_raw):
                            # 统一转换为YYYY-MM-DD格式
                            latest_date = pd.to_datetime(latest_date_raw).strftime('%Y-%m-%d')
                        break
                    except:
                        # 转换失败时尝试其他格式或显示原始值
                        try:
                            latest_date = str(latest_date_raw)
                        except:
                            latest_date = "N/A"
                        break
            st.metric("最新报告期", latest_date)

    with col3:
        if not df.empty:
            # 计算数据完整性
            total_cells = len(df) * len(df.columns)
            non_null_cells = df.count().sum()
            completeness = (non_null_cells / total_cells) * 100
            st.metric("数据完整性", f"{completeness:.1f}%")