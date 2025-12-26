"""
流动性比率计算器（港股速动比率）

对应 components/liquidity_ratio.py
"""

from typing import Dict, Tuple, List
import pandas as pd
import requests

from .. import data_service


def calculate(
    symbol: str,
    years: int
) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算港股速动比率（港股财务指标API未提供）

    计算公式：速动比率 = (流动资产 - 存货) ÷ 流动负债

    Args:
        symbol: 股票代码
        years: 查询年数

    Returns:
        (速动比率DataFrame, 显示列名列表, 关键指标字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    # 获取港股资产负债表
    response = requests.get(
        f"{data_service.API_BASE_URL}{data_service.FINANCIAL_STATEMENTS_ENDPOINT}",
        params={
            "symbol": symbol,
            "query_type": "hk_financial_statements",
            "frequency": "annual"
        },
        timeout=30
    )

    if response.status_code != 200:
        raise data_service.APIServiceUnavailableError(f"API服务返回错误状态码: {response.status_code}")

    result = response.json()
    data_dict = result.get("data", {})
    balance_sheet = data_dict.get("balance_sheet")

    if not balance_sheet:
        raise data_service.DataServiceError(f"港股股票 {symbol} 没有资产负债表数据")

    # 转换为DataFrame并提取年份
    balance_df = pd.DataFrame(balance_sheet["data"])
    balance_df = data_service.extract_year_column(balance_df, "港股", symbol, "资产负债表")

    # 计算速动比率
    balance_df["速动比率"] = (
        (balance_df["流动资产合计"] - balance_df["存货"]) /
        balance_df["流动负债合计"].replace(0, pd.NA)
    ).replace([float('inf'), -float('inf')], pd.NA).round(2)

    # 限制年数
    result_df = balance_df[["年份", "流动资产合计", "存货", "流动负债合计", "速动比率"]]
    result_df = result_df.sort_values("年份").tail(years).reset_index(drop=True)

    # 计算关键指标
    valid_ratios = result_df["速动比率"].dropna()
    metrics = {
        "avg_ratio": valid_ratios.mean() if len(valid_ratios) > 0 else None,
        "latest_ratio": result_df["速动比率"].iloc[-1] if len(result_df) > 0 else None,
        "min_ratio": valid_ratios.min() if len(valid_ratios) > 0 else None,
        "max_ratio": valid_ratios.max() if len(valid_ratios) > 0 else None,
        "healthy_years": (valid_ratios >= 1).sum() if len(valid_ratios) > 0 else 0,
        "total_years": len(valid_ratios)
    }

    display_cols = ["年份", "流动资产合计", "存货", "流动负债合计", "速动比率"]

    return result_df, display_cols, metrics


def calculate_interest_coverage_ratio(
    symbol: str,
    market: str,
    years: int
) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算利息覆盖比率分析（包含数据获取）

    计算公式：利息覆盖比率 = (息税前利润 + 利息收入) ÷ 利息费用

    各市场特殊处理：
    - A股：EBIT = 净利润 + 所得税 + 利息费用（标准公式）
    - 港股：EBIT = 除税前溢利（已减去融资成本，需加回）
    - 美股：利息支出为负数，需取绝对值

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (结果DataFrame, 显示列名列表, 指标字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    from .common import calculate_ebit

    financial_data = data_service.get_financial_statements(symbol, market, years)
    income_df = financial_data["income_statement"]

    if market == "A股":
        # A股标准计算
        ebit_df, _ = calculate_ebit(financial_data, market)

        result_df = pd.merge(
            ebit_df[["年份", "EBIT"]],
            income_df[["年份", "利息收入", "其中：利息费用"]],
            on="年份"
        )

        # 转换为数值类型
        result_df["利息收入"] = pd.to_numeric(result_df["利息收入"], errors="coerce")
        result_df["其中：利息费用"] = pd.to_numeric(result_df["其中：利息费用"], errors="coerce")

        # 计算利息覆盖比率
        ratio = (
            (result_df["EBIT"] + result_df["利息收入"]) /
            result_df["其中：利息费用"].replace(0, pd.NA)
        )
        # 处理无穷值
        ratio = ratio.replace([float('inf'), -float('inf')], pd.NA)
        # 确保是数值类型后再round
        result_df["利息覆盖比率"] = pd.to_numeric(ratio, errors="coerce").round(2)

        display_cols = ["年份", "EBIT", "利息收入", "其中：利息费用", "利息覆盖比率"]

    elif market == "港股":
        # 港股特殊处理：EBIT需要加回融资成本
        result_df = pd.DataFrame({
            "年份": income_df["年份"],
            "EBIT": income_df["除税前溢利"],
            "融资成本": income_df["融资成本"],
            "利息收入": income_df["利息收入"]
        })

        # 转换为数值类型
        result_df["EBIT"] = pd.to_numeric(result_df["EBIT"], errors="coerce")
        result_df["融资成本"] = pd.to_numeric(result_df["融资成本"], errors="coerce")
        result_df["利息收入"] = pd.to_numeric(result_df["利息收入"], errors="coerce")

        # 港股的EBIT已经减去了融资成本，所以计算时要加回
        # 利息覆盖比率 = (除税前溢利 + 融资成本 + 利息收入) ÷ 融资成本
        ratio = (
            (result_df["EBIT"] + result_df["融资成本"] + result_df["利息收入"]) /
            result_df["融资成本"].replace(0, pd.NA)
        )
        # 处理无穷值
        ratio = ratio.replace([float('inf'), -float('inf')], pd.NA)
        # 确保是数值类型后再round
        result_df["利息覆盖比率"] = pd.to_numeric(ratio, errors="coerce").round(2)

        display_cols = ["年份", "EBIT", "融资成本", "利息收入", "利息覆盖比率"]

    else:  # 美股
        # 美股需要检查是否有利息支出数据
        if "利息支出" not in income_df.columns:
            raise data_service.DataServiceError(f"美股股票 {symbol} 没有利息支出数据")

        ebit_df, _ = calculate_ebit(financial_data, market)

        result_df = pd.merge(
            ebit_df[["年份", "EBIT"]],
            income_df[["年份", "利息收入", "利息支出"]],
            on="年份"
        )

        # 转换为数值类型
        result_df["利息收入"] = pd.to_numeric(result_df["利息收入"], errors="coerce")
        result_df["利息支出"] = pd.to_numeric(result_df["利息支出"], errors="coerce")

        # 过滤掉利息支出为N/A的行
        result_df = result_df[result_df["利息支出"].notna()].copy()

        # 利息支出是负数，取绝对值
        result_df["利息支出"] = result_df["利息支出"].abs()

        # 计算利息覆盖比率
        ratio = (
            (result_df["EBIT"] + result_df["利息收入"]) /
            result_df["利息支出"].replace(0, pd.NA)
        )
        # 处理无穷值
        ratio = ratio.replace([float('inf'), -float('inf')], pd.NA)
        # 确保是数值类型后再round
        result_df["利息覆盖比率"] = pd.to_numeric(ratio, errors="coerce").round(2)

        display_cols = ["年份", "EBIT", "利息收入", "利息支出", "利息覆盖比率"]

    # 限制年数并排序
    result_df = result_df.sort_values("年份").tail(years).reset_index(drop=True)

    # 计算关键指标
    valid_ratios = result_df["利息覆盖比率"].dropna()
    metrics = {
        "avg_ratio": valid_ratios.mean() if len(valid_ratios) > 0 else None,
        "latest_ratio": result_df["利息覆盖比率"].iloc[-1] if len(result_df) > 0 else None,
        "min_ratio": valid_ratios.min() if len(valid_ratios) > 0 else None,
        "max_ratio": valid_ratios.max() if len(valid_ratios) > 0 else None,
        "safe_years": (valid_ratios >= 3).sum() if len(valid_ratios) > 0 else 0,
        "warning_years": ((valid_ratios >= 1.5) & (valid_ratios < 3)).sum() if len(valid_ratios) > 0 else 0,
        "danger_years": (valid_ratios < 1.5).sum() if len(valid_ratios) > 0 else 0,
        "total_years": len(valid_ratios)
    }

    return result_df, display_cols, metrics
