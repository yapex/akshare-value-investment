"""
数据获取服务

为Streamlit应用提供简化的数据查询接口，通过FastAPI Web服务获取数据
"""

import requests
import pandas as pd


# API配置
API_BASE_URL = "http://localhost:8000"


def get_revenue_data(symbol: str, market: str, years: int = 10):
    """获取营业收入数据

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        DataFrame: 包含年份和营业收入的数据，如果查询失败返回None
    """
    # 市场类型映射
    market_type_map = {
        "A股": "a_stock",
        "港股": "hk_stock",
        "美股": "us_stock"
    }

    # 查询类型映射 - 财务三表
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }

    # 字段名映射
    field_name_map = {
        "A股": "其中：营业收入",
        "港股": "营业额",
        "美股": "营业收入"
    }

    market_type = market_type_map.get(market)
    query_type = query_type_map.get(market)
    field_name = field_name_map.get(market)

    if not all([market_type, query_type, field_name]):
        return None

    # 调用FastAPI的财务三表查询端点
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/financial/statements",
            params={
                "symbol": symbol,
                "query_type": query_type,
                "frequency": "annual"
            },
            timeout=30
        )

        # 检查HTTP状态码
        if response.status_code != 200:
            return None

        result = response.json()

        # 检查业务响应状态
        if result.get("status") == "error":
            return None

        # 提取利润表数据
        data_dict = result.get("data", {})
        income_statement = data_dict.get("income_statement")

        if not income_statement:
            return None

        # 转换为DataFrame
        df = pd.DataFrame(income_statement["data"])

        if df.empty:
            return None

        # 提取年份和营业收入
        date_col = "报告期" if "报告期" in df.columns else "date"
        df = df.copy()
        df["年份"] = pd.to_datetime(df[date_col]).dt.year

        # 保留最近N年
        result_df = df[["年份", field_name]].copy()
        result_df = result_df.sort_values("年份").tail(years)

        return result_df

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None


def get_financial_statements(symbol: str, market: str, years: int = 10):
    """获取财务三表原始数据（仅数据获取，不进行计算）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        DataFrame: 原始财务数据（包含年份列），如果查询失败返回None
    """
    # 查询类型映射
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }

    query_type = query_type_map.get(market)
    if not query_type:
        return None

    # 调用FastAPI的财务三表查询端点
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/financial/statements",
            params={
                "symbol": symbol,
                "query_type": query_type,
                "frequency": "annual"
            },
            timeout=30
        )

        # 检查HTTP状态码
        if response.status_code != 200:
            return None

        result = response.json()

        # 检查业务响应状态
        if result.get("status") == "error":
            return None

        # 提取利润表数据
        data_dict = result.get("data", {})
        income_statement = data_dict.get("income_statement")

        if not income_statement:
            return None

        # 转换为DataFrame
        df = pd.DataFrame(income_statement["data"])

        if df.empty:
            return None

        # 提取年份
        date_col = "报告期" if "报告期" in df.columns else "date"
        df = df.copy()
        df["年份"] = pd.to_datetime(df[date_col]).dt.year

        # 排序并限制年数
        df = df.sort_values("年份").tail(years)

        return df

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None


def get_ebit_margin_data(symbol: str, market: str, years: int = 10):
    """获取EBIT利润率数据（保留向后兼容）

    计算公式：
    - A股: EBIT = 净利润 + 所得税费用 + 利息费用
    - 港股: EBIT = 除税前溢利（已包含所得税和融资成本）
    - 美股: EBIT = 持续经营税前利润（已包含所得税）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        DataFrame: 包含年份、EBIT、收入和EBIT利润率的数据，如果查询失败返回None
    """
    from .calculator import Calculator

    # 获取原始数据
    df = get_financial_statements(symbol, market, years)
    if df is None:
        return None

    # 调用Calculator计算EBIT
    result_df, display_columns = Calculator.ebit(df, market)

    return result_df[display_columns]
