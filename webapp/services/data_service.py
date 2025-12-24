"""
数据获取服务

为Streamlit应用提供简化的数据查询接口，通过FastAPI Web服务获取数据
"""

import requests
import pandas as pd


# API配置
API_BASE_URL = "http://localhost:8000"


class DataServiceError(Exception):
    """数据服务错误基类"""
    def __init__(self, message: str, suggestions: list = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.message)


class SymbolNotFoundError(DataServiceError):
    """股票代码未找到错误"""
    pass


class APIServiceUnavailableError(DataServiceError):
    """API服务不可用错误"""
    pass


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

    Raises:
        SymbolNotFoundError: 股票代码未找到或无效
        APIServiceUnavailableError: API服务不可用
        DataServiceError: 其他数据处理错误
    """
    # 查询类型映射
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }

    query_type = query_type_map.get(market)
    if not query_type:
        raise DataServiceError(f"不支持的市场类型: {market}")

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
        if response.status_code == 404:
            # 股票代码未找到
            suggestions = _get_common_mistakes(symbol, market)
            raise SymbolNotFoundError(
                f"未找到{market}股票代码: {symbol}",
                suggestions
            )
        elif response.status_code != 200:
            raise APIServiceUnavailableError(
                f"API服务返回错误状态码: {response.status_code}",
                ["请检查API服务是否正常运行", "请稍后重试"]
            )

        result = response.json()

        # 检查业务响应状态
        if result.get("status") == "error":
            error_msg = result.get("message", "未知错误")
            suggestions = _get_common_mistakes(symbol, market)
            raise SymbolNotFoundError(
                f"查询{market}股票 {symbol} 失败: {error_msg}",
                suggestions
            )

        # 提取利润表和现金流量表数据
        data_dict = result.get("data", {})
        income_statement = data_dict.get("income_statement")
        cash_flow = data_dict.get("cash_flow")

        if not income_statement or not cash_flow:
            raise SymbolNotFoundError(
                f"{market}股票 {symbol} 没有财务数据",
                ["请检查股票代码是否正确", "该股票可能已退市或数据不完整"]
            )

        # 转换为DataFrame（保持分离，避免合并带来的列名重复问题）
        income_df = pd.DataFrame(income_statement["data"])
        cashflow_df = pd.DataFrame(cash_flow["data"])

        if income_df.empty or cashflow_df.empty:
            raise SymbolNotFoundError(
                f"{market}股票 {symbol} 没有可用的财务数据",
                ["该股票可能是新上市，数据不足", "请尝试减少查询年数"]
            )

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

    except requests.exceptions.ConnectionError:
        raise APIServiceUnavailableError(
            "无法连接到API服务",
            [
                "请确保FastAPI服务已启动 (poe api)",
                "检查服务地址: http://localhost:8000",
                "查看文档启动API服务"
            ]
        )
    except requests.exceptions.Timeout:
        raise APIServiceUnavailableError(
            "API服务请求超时",
            ["网络连接较慢，请稍后重试", "API服务可能负载过高"]
        )
    except requests.exceptions.RequestException as e:
        raise APIServiceUnavailableError(
            f"API请求失败: {str(e)}",
            ["请检查网络连接", "请稍后重试"]
        )
    except (SymbolNotFoundError, APIServiceUnavailableError):
        # 重新抛出业务异常
        raise
    except Exception as e:
        raise DataServiceError(
            f"数据处理失败: {str(e)}",
            ["请稍后重试", "如果问题持续，请联系技术支持"]
        )


def _get_common_mistakes(symbol: str, market: str) -> list:
    """获取常见错误和更正建议

    Args:
        symbol: 用户输入的股票代码
        market: 识别的市场类型

    Returns:
        建议列表
    """
    suggestions = []

    if market == "美股":
        # 常见美股代码错误
        common_mistakes = {
            "APPL": "AAPL (苹果)",
            "MSF": "MSFT (微软)",
            "GOOG": "GOOGL 或 GOOG (谷歌)",
            "AMZ": "AMZN (亚马逊)",
            "TSL": "TSLA (特斯拉)",
            "META": "META (Facebook)",
            "FB": "META (Facebook已更名)",
        }

        # 检查是否是常见错误
        for wrong, correct in common_mistakes.items():
            if symbol.upper() == wrong:
                suggestions.append(f"您是否想输入: {correct}")
                break

        if not suggestions:
            suggestions.extend([
                f"请检查{symbol}是否为正确的美股代码",
                "常见美股代码: AAPL, MSFT, GOOGL, AMZN, TSLA",
                "区分大小写，建议使用大写字母"
            ])

    elif market == "A股":
        # A股常见错误
        if not symbol.isdigit():
            suggestions.append("A股代码应为6位数字，如: 600519 (茅台)")

        if len(symbol) != 6:
            suggestions.append(f"当前代码长度: {len(symbol)}位，A股代码应为6位")

        suggestions.extend([
            "上海交易所: 600xxx, 601xxx, 603xxx, 688xxx",
            "深圳交易所: 000xxx, 001xxx, 002xxx, 300xxx",
            "可使用前缀: SH600519 或 SZ000001"
        ])

    elif market == "港股":
        # 港股常见错误
        if not symbol.isdigit():
            suggestions.append("港股代码应为数字，如: 00700 (腾讯)")

        suggestions.extend([
            "港股代码通常为5位数字 (如00700)",
            "支持简写 (如700 → 00700)",
            "可使用前缀: HK.00700"
        ])

    return suggestions


def handle_data_service_error(e: DataServiceError):
    """在Streamlit UI中处理数据服务错误

    Args:
        e: 数据服务异常
    """
    import streamlit as st

    st.error(f"❌ {e.message}")
    if e.suggestions:
        st.info("💡 **建议：**")
        for suggestion in e.suggestions:
            st.markdown(f"- {suggestion}")
