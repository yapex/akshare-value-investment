"""
数据获取服务

为Streamlit应用提供简化的数据查询接口，通过FastAPI Web服务获取数据
"""

import requests
import pandas as pd


# API配置
API_BASE_URL = "http://localhost:8000"


def get_financial_statements(symbol: str, market: str, years: int = 10):
    """获取财务三表原始数据（保持分离的字典结构）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        Dict[str, pd.DataFrame]: 包含利润表和现金流量表的字典
            {
                "income_statement": DataFrame,
                "cash_flow": DataFrame
            }
            如果查询失败返回None
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

        # 提取利润表和现金流量表数据
        data_dict = result.get("data", {})
        income_statement = data_dict.get("income_statement")
        cash_flow = data_dict.get("cash_flow")

        if not income_statement or not cash_flow:
            return None

        # 转换为DataFrame（保持分离，避免合并带来的列名重复问题）
        income_df = pd.DataFrame(income_statement["data"])
        cashflow_df = pd.DataFrame(cash_flow["data"])

        if income_df.empty or cashflow_df.empty:
            return None

        # 提取年份并排序
        date_col = "报告期" if "报告期" in income_df.columns else "date"

        income_df = income_df.copy()
        cashflow_df = cashflow_df.copy()

        income_df["年份"] = pd.to_datetime(income_df[date_col]).dt.year
        cashflow_df["年份"] = pd.to_datetime(cashflow_df[date_col]).dt.year

        # 排序并限制年数
        income_df = income_df.sort_values("年份").tail(years).reset_index(drop=True)
        cashflow_df = cashflow_df.sort_values("年份").tail(years).reset_index(drop=True)

        # 返回分离的字典结构（避免合并带来的列名重复问题）
        return {
            "income_statement": income_df,
            "cash_flow": cashflow_df
        }

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None
