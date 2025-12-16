"""
A股财务报表Streamlit应用

四大财务报表（指标、资产负债、利润、现金流）合并展示
支持窄表形式，财务格式显示，小数点后2位，百万元单位
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import streamlit as st
import requests
from datetime import datetime

# 导入自定义模块
from ui_components import render_sidebar, render_main_content, display_query_results

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class FinancialReportApp:
    """财务报表应用主类"""

    def __init__(self):
        """初始化应用"""
        self.api_base_url = "http://localhost:8000"
        self.setup_page_config()

    def setup_page_config(self):
        """配置页面设置"""
        st.set_page_config(
            page_title="A股财务报表分析",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def query_financial_data_via_api(self, market: str, query_type: str, symbol: str,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        通过FastAPI查询财务数据

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame格式的财务数据
        """
        try:
            request_data = {
                "market": market,
                "query_type": query_type,
                "symbol": symbol,
                "frequency": "annual"
            }

            if start_date:
                request_data["start_date"] = start_date
            if end_date:
                request_data["end_date"] = end_date

            response = requests.post(
                f"{self.api_base_url}/api/v1/financial/query",
                json=request_data,
                timeout=30
            )

            if response.status_code == 200:
                api_response = response.json()
                if api_response.get("status") == "success":
                    data = api_response.get("data", {})
                    if isinstance(data, dict) and "records" in data:
                        return pd.DataFrame(data["records"])
                else:
                    st.error(f"API查询失败: {api_response.get('message', '未知错误')}")
            else:
                st.error(f"API请求失败: HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("无法连接到FastAPI服务，请确保API服务正在运行 (http://localhost:8000)")
        except Exception as e:
            st.error(f"查询数据失败: {str(e)}")

        return pd.DataFrame()

    def get_financial_data(self, symbol: str, start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        获取四大财务报表数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含四大报表的字典
        """
        try:
            data = {}

            with st.spinner("正在获取财务指标数据..."):
                data['indicators'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_indicators", symbol, start_date, end_date
                )

            with st.spinner("正在获取资产负债表数据..."):
                data['balance_sheet'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_balance_sheet", symbol, start_date, end_date
                )

            with st.spinner("正在获取利润表数据..."):
                data['income_statement'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_income_statement", symbol, start_date, end_date
                )

            with st.spinner("正在获取现金流量表数据..."):
                data['cash_flow'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_cash_flow", symbol, start_date, end_date
                )

            return data

        except Exception as e:
            st.error(f"获取数据失败: {str(e)}")
            return {}

    def run(self):
        """运行应用"""
        # 渲染侧边栏
        symbol, start_date, end_date, query_button = render_sidebar()

        # 主标题
        st.title("📊 A股财务报表分析系统")
        st.markdown("---")

        # 初始化会话状态
        if 'current_symbol' not in st.session_state:
            st.session_state.current_symbol = None
        if 'current_start_date' not in st.session_state:
            st.session_state.current_start_date = None
        if 'current_end_date' not in st.session_state:
            st.session_state.current_end_date = None

        # 检查是否需要重新查询数据
        should_query = query_button or (
            st.session_state.current_symbol != symbol or
            st.session_state.current_start_date != start_date or
            st.session_state.current_end_date != end_date
        )

        # 如果没有数据且没有查询，显示欢迎页面
        if not hasattr(st.session_state, 'data') or st.session_state.data is None:
            render_main_content()
            should_query = False

        # 执行查询
        if should_query:
            if not symbol:
                st.error("请输入股票代码")
                return

            # 更新会话状态
            st.session_state.current_symbol = symbol
            st.session_state.current_start_date = start_date
            st.session_state.current_end_date = end_date

            # 显示股票信息
            st.success(f"🔍 正在查询 **{symbol}** 的财务数据...")

            # 获取数据
            data = self.get_financial_data(symbol, start_date, end_date)
            st.session_state.data = data

            # 显示查询结果
            if data:
                st.success(f"✅ **{symbol}** 财务数据查询成功！")
                display_query_results(data)
            else:
                st.error("❌ 未能获取到财务数据，请检查股票代码或稍后重试")

        # 显示当前数据（如果存在）
        elif hasattr(st.session_state, 'data') and st.session_state.data is not None:
            current_symbol = st.session_state.current_symbol
            if current_symbol:
                st.info(f"当前显示: **{current_symbol}** 的财务数据")
            display_query_results(st.session_state.data)


def main():
    """主函数"""
    app = FinancialReportApp()
    app.run()


if __name__ == "__main__":
    main()