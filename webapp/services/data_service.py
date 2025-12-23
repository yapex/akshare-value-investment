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


def get_ebit_margin_data(symbol: str, market: str, years: int = 10):
    """获取EBIT利润率数据

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
    # 市场类型映射
    market_type_map = {
        "A股": "a_stock",
        "港股": "hk_stock",
        "美股": "us_stock"
    }

    # 查询类型映射
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }

    # 收入字段映射
    revenue_field_map = {
        "A股": "其中：营业收入",
        "港股": "营业额",
        "美股": "营业收入"
    }

    market_type = market_type_map.get(market)
    query_type = query_type_map.get(market)
    revenue_field = revenue_field_map.get(market)

    if not all([market_type, query_type, revenue_field]):
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

        # 提取年份和相关数据
        date_col = "报告期" if "报告期" in df.columns else "date"
        df = df.copy()
        df["年份"] = pd.to_datetime(df[date_col]).dt.year

        # 按市场分别处理
        if market == "A股":
            # A股: EBIT = 净利润 + 所得税费用 + 利息费用
            required_fields = ["五、净利润", "减：所得税费用", "其中：利息费用", revenue_field]
            for field in required_fields:
                if field not in df.columns:
                    print(f"A股缺少字段: {field}")
                    return None

            result_df = df[["年份", "五、净利润", "减：所得税费用", "其中：利息费用", revenue_field]].copy()
            result_df = result_df.sort_values("年份").tail(years)

            # 计算EBIT: 净利润 + 所得税费用 + 利息费用
            result_df["EBIT"] = result_df["五、净利润"] + result_df["减：所得税费用"] + result_df["其中：利息费用"]

            # 重命名列为通用名称
            result_df.rename(columns={
                "五、净利润": "净利润",
                "减：所得税费用": "所得税费用",
                "其中：利息费用": "利息费用",
                revenue_field: "收入"
            }, inplace=True)

            # 选择显示列
            final_columns = ["年份", "净利润", "所得税费用", "利息费用", "收入", "EBIT"]

        elif market == "港股":
            # 港股: EBIT = 除税前溢利
            required_fields = ["除税前溢利", revenue_field]
            for field in required_fields:
                if field not in df.columns:
                    print(f"港股缺少字段: {field}")
                    return None

            result_df = df[["年份", "除税前溢利", revenue_field]].copy()
            result_df = result_df.sort_values("年份").tail(years)

            # 直接使用除税前溢利作为EBIT
            result_df["EBIT"] = result_df["除税前溢利"]

            # 重命名列为通用名称
            result_df.rename(columns={
                "除税前溢利": "除税前溢利",
                revenue_field: "收入"
            }, inplace=True)

            # 选择显示列
            final_columns = ["年份", "除税前溢利", "收入", "EBIT"]

        else:  # 美股
            # 美股: EBIT = 持续经营税前利润
            required_fields = ["持续经营税前利润", revenue_field]
            for field in required_fields:
                if field not in df.columns:
                    print(f"美股缺少字段: {field}")
                    return None

            result_df = df[["年份", "持续经营税前利润", revenue_field]].copy()
            result_df = result_df.sort_values("年份").tail(years)

            # 直接使用持续经营税前利润作为EBIT
            result_df["EBIT"] = result_df["持续经营税前利润"]

            # 重命名列为通用名称
            result_df.rename(columns={
                "持续经营税前利润": "持续经营税前利润",
                revenue_field: "收入"
            }, inplace=True)

            # 选择显示列
            final_columns = ["年份", "持续经营税前利润", "收入", "EBIT"]

        # 计算EBIT利润率（百分比）
        result_df["EBIT利润率"] = (result_df["EBIT"] / result_df["收入"] * 100).round(2)

        # 添加EBIT利润率到显示列
        final_columns.append("EBIT利润率")

        return result_df[final_columns]

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None
