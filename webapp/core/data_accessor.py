"""
数据访问和字段管理
"""

import pandas as pd
import httpx
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.base_models import MarketType
from models.market_config import get_market_fields




def format_financial_number(value):
    """统一的财务数字格式化：小数点后两位，符合财务要求"""
    if pd.isna(value) or value == 0 or value == "0":
        return "0.00"

    try:
        # 转换为数字
        num_value = float(value)

        # 会计格式：负数用括号表示，千位分隔，保留两位小数
        if num_value < 0:
            return f"({abs(num_value):,.2f})"
        else:
            return f"{num_value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def parse_amount(value) -> float:
    """解析金额字符串，处理 '924.64亿' 这样的格式"""
    if pd.isna(value) or value == 0:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        if '亿' in value:
            return float(value.replace('亿', '')) * 100000000
        elif '万' in value:
            return float(value.replace('万', '')) * 10000
        else:
            return float(value)

    return 0.0


def get_field_value(row, field_name: str):
    """获取行中指定字段的值，字段不存在或为false时抛出异常

    Args:
        row: 数据行（pandas Series 或 dict）
        field_name: 字段名称

    Returns:
        字段值

    Raises:
        KeyError: 当字段不存在或为false时
    """
    if hasattr(row, 'get'):
        # pandas Series 或 dict
        if field_name in row:
            value = row[field_name]
            # 处理false值，表示数据缺失
            if value is False:
                raise KeyError(f"字段 '{field_name}' 数据缺失")
            return value
        else:
            raise KeyError(f"字段 '{field_name}' 不存在")
    else:
        # 其他类型，尝试通过属性访问
        try:
            value = getattr(row, field_name)
            # 处理false值，表示数据缺失
            if value is False:
                raise KeyError(f"字段 '{field_name}' 数据缺失")
            return value
        except AttributeError:
            raise KeyError(f"字段 '{field_name}' 不存在")


class StockAnalyzer:
    """增强版股票分析器，支持跨市场"""

    def __init__(self, symbol: str, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
        self.symbol = symbol
        # 自动识别市场类型
        self.market = self._detect_market_type(symbol)

    def _detect_market_type(self, symbol: str) -> MarketType:
        """根据股票代码自动检测市场类型"""
        symbol = symbol.upper().strip()

        if symbol.startswith(('SH', 'SZ')) or (len(symbol) == 6 and symbol.isdigit()):
            return MarketType.A_STOCK
        elif symbol.endswith('.HK') or (len(symbol) <= 5 and symbol.isdigit()):
            return MarketType.HK_STOCK
        else:
            return MarketType.US_STOCK

    def fetch_financial_data(self, query_type: str, fields: List[str],
                           start_date: str, end_date: str) -> Dict:
        """从FastAPI获取财务数据"""
        try:
            response = self.client.post(
                f"{self.api_base_url}/api/v1/financial/query",
                json={
                    "market": self.market.value,
                    "query_type": query_type,
                    "symbol": self.symbol,
                    "fields": fields,
                    "start_date": start_date,
                    "end_date": end_date,
                    "frequency": "annual"
                }
            )
            response.raise_for_status()
            data = response.json()
            # 检查API响应状态
            if data.get("status") == "success":
                return data
            else:
                st.error(f"API返回错误: {data}")
                return {}
        except Exception as e:
            st.error(f"数据获取失败: {e}")
            return {}

    def validate_fields_exist(self, query_type: str, required_fields: List[str]) -> None:
        """验证所需字段是否在API中存在"""
        # 获取所有可用字段
        try:
            # 根据API路由，正确的URL格式为 /api/v1/financial/fields/{market}/{query_type}
            # 其中query_type需要使用完整格式，如 a_stock_balance_sheet
            market = self.market.value

            # 映射查询类型到API的完整格式
            query_type_mapping = {
                "balance_sheet": "a_stock_balance_sheet",
                "income_statement": "a_stock_income_statement",
                "cash_flow": "a_stock_cash_flow"
            }
            api_query_type = query_type_mapping.get(query_type, query_type)

            response = self.client.get(
                f"{self.api_base_url}/api/v1/financial/fields/{market}/{api_query_type}"
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                available_fields = data.get("metadata", {}).get("available_fields", [])
                missing_fields = [field for field in required_fields if field not in available_fields]

                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    raise ValueError(f"以下字段不存在: {missing_fields_str}")
        except httpx.ReadTimeout:
            st.warning("API连接超时，跳过字段验证，直接尝试获取数据")
        except httpx.ConnectError:
            st.error("无法连接到API服务器，请检查服务是否正常运行")
            raise
        except Exception as e:
            # 对于其他错误，我们仅显示警告并继续，不中断程序
            st.warning(f"字段验证失败: {e}，继续尝试获取数据")

    def get_balance_sheet_data(self, years: int = 5) -> pd.DataFrame:
        """获取资产负债表数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")

        # 获取资产负债表分析所需的字段
        # 从市场配置中获取字段

        fields_config = get_market_fields(self.market, "balance_sheet")
        fields = list(fields_config.values()) if fields_config else []

        # 验证字段是否存在，但不中断程序执行
        try:
            self.validate_fields_exist("balance_sheet", fields)
        except:
            # 如果验证失败，仍继续尝试获取数据
            pass

        data = self.fetch_financial_data(
            "a_stock_balance_sheet", fields, start_date, end_date
        )

        if data.get("status") == "success":
            df = pd.DataFrame(data["data"]["records"])
            # 清理报告期格式，去掉时分秒
            if "报告期" in df.columns:
                df["报告期"] = df["报告期"].str.split("T").str[0]
            # 按报告期降序排列（最新的在前）
            df = df.sort_values("报告期", ascending=False)
            return df

        return pd.DataFrame()

    def get_income_statement_data(self, years: int = 5) -> pd.DataFrame:
        """获取利润表数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")

        # 获取利润表所需的字段

        fields_config = get_market_fields(self.market, "income_statement")
        fields = list(fields_config.values()) if fields_config else []

        # 验证字段是否存在，但不中断程序执行
        try:
            self.validate_fields_exist("income_statement", fields)
        except:
            # 如果验证失败，仍继续尝试获取数据
            pass

        data = self.fetch_financial_data(
            "a_stock_income_statement", fields, start_date, end_date
        )

        if data.get("status") == "success":
            df = pd.DataFrame(data["data"]["records"])
            # 清理报告期格式，去掉时分秒
            if "报告期" in df.columns:
                df["报告期"] = df["报告期"].str.split("T").str[0]
            # 按报告期降序排列（最新的在前）
            df = df.sort_values("报告期", ascending=False)
            return df

        return pd.DataFrame()