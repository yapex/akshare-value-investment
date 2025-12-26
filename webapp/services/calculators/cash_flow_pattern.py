"""
现金流类型分析计算器

对应 components/cash_flow_pattern.py
"""

from typing import Dict, List, Tuple
import pandas as pd

from .. import data_service


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, any]]:
    """计算现金流类型分析（包含数据获取）

    根据经营、投资、筹资三种现金流的正负组合，判断企业类型：
    - 🐄 奶牛型（最佳）：经营为正，投资为负，筹资可正可负
    - 🐂 蛮牛型：经营为正，投资为负，筹资为正（需融资补血）
    - 🧚 妖精型：经营为负，投资为正
    - 🐄 病牛型：经营为负，投资为正，筹资为正
    - 🃏 骗吃型：经营为负，投资为负，筹资为正

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (现金流类型DataFrame, 显示列名列表, 统计信息字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    financial_data = data_service.get_financial_statements(symbol, market, years)
    cashflow_df = financial_data["cash_flow"].copy()

    # 根据市场提取三种现金流字段
    if market == "A股":
        operating_col = "经营活动产生的现金流量净额"
        investing_col = "投资活动产生的现金流量净额"
        financing_col = "筹资活动产生的现金流量净额"
    elif market == "港股":
        operating_col = "经营业务现金净额"
        investing_col = "投资业务现金净额"
        financing_col = "融资业务现金净额"
    else:  # 美股
        operating_col = "经营活动产生的现金流量净额"
        investing_col = "投资活动产生的现金流量净额"
        financing_col = "筹资活动产生的现金流量净额"

    # 检查字段是否存在
    for col in [operating_col, investing_col, financing_col]:
        if col not in cashflow_df.columns:
            raise ValueError(f"现金流量表字段 '{col}' 不存在")

    # 提取三种现金流数据
    result_df = cashflow_df[["年份", operating_col, investing_col, financing_col]].copy()
    result_df = result_df.sort_values("年份").reset_index(drop=True)

    # 计算累计值
    result_df['累计经营现金流'] = result_df[operating_col].cumsum()
    result_df['累计投资现金流'] = result_df[investing_col].cumsum()
    result_df['累计筹资现金流'] = result_df[financing_col].cumsum()

    # 重命名字段为通用名称
    result_df.rename(columns={
        operating_col: "经营现金流",
        investing_col: "投资现金流",
        financing_col: "筹资现金流"
    }, inplace=True)

    # 判断每年现金流类型
    def classify_pattern(row):
        """判断现金流类型"""
        operating = row['经营现金流']
        investing = row['投资现金流']
        financing = row['筹资现金流']

        # 奶牛型：经营为正，投资为负，筹资可正可负
        if operating > 0 and investing < 0:
            if financing < 0:
                return "🐄 奶牛型", "+ - -", "最佳模式：主业强劲造血，投资扩张+分红回购"
            else:
                # 需要进一步判断是奶牛型还是蛮牛型
                # 如果投资流出远大于经营流入，需要融资补血，则为蛮牛型
                if abs(investing) > operating * 1.5:
                    return "🐂 蛮牛型", "+ - +", "扩张激进：主业造血，但投资远超现金流需融资补血"
                else:
                    return "🐄 奶牛型", "+ -", "优质模式：主业强劲造血，适度投资扩张"

        # 蛮牛型：经营为正，投资为负，筹资为正
        elif operating > 0 and investing < 0 and financing > 0:
            return "🐂 蛮牛型", "+ - +", "扩张激进：主业造血，但投资远超现金流需融资补血"

        # 妖精型：经营为负，投资为正
        elif operating < 0 and investing > 0:
            return "🧚 妖精型", "- +", "主业不赚钱：靠变卖资产或投资收益维持"

        # 病牛型：经营为负，投资为正，筹资为正
        elif operating < 0 and investing > 0 and financing > 0:
            return "🐄 病牛型", "- + +", "经营困难：主业失血，靠卖资产+借款度日"

        # 骗吃型：经营为负，投资为负，筹资为正
        elif operating < 0 and investing < 0 and financing > 0:
            return "🃏 骗吃型", "- - +", "最危险：主业失血+疯狂投资，完全靠外部输血"

        # 其他情况
        elif operating > 0 and investing > 0:
            return "🧚 妖精型", "+ +", "投资收益型：经营和投资都为正"

        else:
            return "❓ 其他", str(int(operating > 0)) + " " + str(int(investing > 0)) + " " + str(int(financing > 0)), "特殊模式"

    # 应用分类函数
    pattern_info = result_df.apply(classify_pattern, axis=1, result_type='expand')
    result_df['类型名称'] = pattern_info[0]
    result_df['类型模式'] = pattern_info[1]
    result_df['类型说明'] = pattern_info[2]

    # 计算统计信息
    type_counts = result_df['类型名称'].value_counts()
    total_years = len(result_df)

    # 找出主导类型（出现最多的类型）
    dominant_type = type_counts.index[0] if len(type_counts) > 0 else "未知"
    dominant_ratio = (type_counts.iloc[0] / total_years * 100) if total_years > 0 else 0

    # 最新类型
    latest_type = result_df['类型名称'].iloc[-1] if len(result_df) > 0 else "未知"

    # 计算累计现金流净额
    cumulative_net_cashflow = (
        result_df['累计经营现金流'].iloc[-1] +
        result_df['累计投资现金流'].iloc[-1] +
        result_df['累计筹资现金流'].iloc[-1]
    ) if len(result_df) > 0 else 0

    # 基于累计现金流判断整体类型（更准确地反映公司长期状况）
    def classify_cumulative_pattern(cum_operating, cum_investing, cum_financing):
        """基于累计现金流判断整体类型"""
        # 奶牛型：累计经营为正，累计投资为负（主业造血+持续投资）
        if cum_operating > 0 and cum_investing < 0:
            if cum_financing < 0:
                return "🐄 奶牛型", "+ - -", "最佳模式：{years}年主业强劲造血，投资扩张+分红回购"
            else:
                # 判断投资强度
                if abs(cum_investing) > cum_operating * 1.5:
                    return "🐂 蛮牛型", "+ - +", "扩张激进：主业造血，但{years}年累计投资远超现金流需融资补血"
                else:
                    return "🐄 奶牛型", "+ -", "优质模式：{years}年主业强劲造血，适度投资扩张"

        # 蛮牛型：累计经营为正，累计投资为负，累计筹资为正
        elif cum_operating > 0 and cum_investing < 0 and cum_financing > 0:
            return "🐂 蛮牛型", "+ - +", "扩张激进：主业造血，但{years}年累计投资远超现金流需融资补血"

        # 妖精型：累计经营为负，累计投资为正
        elif cum_operating < 0 and cum_investing > 0:
            return "🧚 妖精型", "- +", "主业不赚钱：{years}年累计靠变卖资产或投资收益维持"

        # 病牛型：累计经营为负，累计投资为正，累计筹资为正
        elif cum_operating < 0 and cum_investing > 0 and cum_financing > 0:
            return "🐄 病牛型", "- + +", "经营困难：{years}年主业失血，靠卖资产+借款度日"

        # 骗吃型：累计经营为负，累计投资为负，累计筹资为正
        elif cum_operating < 0 and cum_investing < 0 and cum_financing > 0:
            return "🃏 骗吃型", "- - +", "最危险：{years}年主业失血+疯狂投资，完全靠外部输血"

        # 其他情况
        elif cum_operating > 0 and cum_investing > 0:
            return "🧚 妖精型", "+ +", "投资收益型：{years}年累计经营和投资都为正"

        else:
            return "❓ 其他", f"{int(cum_operating > 0)} {int(cum_investing > 0)} {int(cum_financing > 0)}", "特殊模式"

    # 获取最后一行的累计值
    if len(result_df) > 0:
        cum_operating = result_df['累计经营现金流'].iloc[-1]
        cum_investing = result_df['累计投资现金流'].iloc[-1]
        cum_financing = result_df['累计筹资现金流'].iloc[-1]

        # 判断累计类型
        cumulative_type_info = classify_cumulative_pattern(cum_operating, cum_investing, cum_financing)
        cumulative_type = cumulative_type_info[0]
        cumulative_pattern = cumulative_type_info[1]
        cumulative_description = cumulative_type_info[2].format(years=total_years)
    else:
        cumulative_type = "未知"
        cumulative_pattern = ""
        cumulative_description = "数据不足"

    stats = {
        'latest_type': latest_type,
        'latest_pattern': result_df['类型模式'].iloc[-1] if len(result_df) > 0 else "",
        'latest_description': result_df['类型说明'].iloc[-1] if len(result_df) > 0 else "",
        'dominant_type': dominant_type,
        'dominant_count': type_counts.iloc[0] if len(type_counts) > 0 else 0,
        'dominant_ratio': dominant_ratio,
        'cumulative_operating': result_df['累计经营现金流'].iloc[-1] if len(result_df) > 0 else 0,
        'cumulative_investing': result_df['累计投资现金流'].iloc[-1] if len(result_df) > 0 else 0,
        'cumulative_financing': result_df['累计筹资现金流'].iloc[-1] if len(result_df) > 0 else 0,
        'cumulative_net': cumulative_net_cashflow,
        'total_years': total_years,
        'type_distribution': type_counts.to_dict(),
        # 新增：基于累计值的整体类型判断
        'cumulative_type': cumulative_type,
        'cumulative_pattern': cumulative_pattern,
        'cumulative_description': cumulative_description,
    }

    display_cols = [
        "年份",
        "经营现金流",
        "投资现金流",
        "筹资现金流",
        "累计经营现金流",
        "累计投资现金流",
        "累计筹资现金流",
        "类型名称",
        "类型模式",
        "类型说明"
    ]

    return result_df, display_cols, stats
