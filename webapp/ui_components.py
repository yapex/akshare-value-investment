"""
UI组件模块

处理Streamlit界面的各种组件渲染
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from data_formatter import format_financial_data, create_styler, display_metrics_section
from chart_utils import create_financial_chart


def render_sidebar() -> tuple[str, str, str, bool]:
    """
    渲染侧边栏

    Returns:
        tuple: (symbol, start_date, end_date, query_button)
    """
    st.sidebar.title("📊 A股财务报表分析")

    # 股票代码输入
    symbol = st.sidebar.text_input(
        "股票代码",
        value="600519",
        help="请输入6位A股代码，如600519（贵州茅台）"
    )

    # 时间范围选择
    st.sidebar.subheader("查询时间范围")

    time_option = st.sidebar.selectbox(
        "选择时间范围",
        ["最近10年", "最近5年", "全部", "自定义"],
        index=0
    )

    start_date = None
    end_date = None

    if time_option == "全部":
        start_date = None
        end_date = None
    elif time_option == "最近10年":
        end_date = datetime.now().strftime("%Y-12-31")
        start_date = f"{datetime.now().year - 10}-01-01"
    elif time_option == "最近5年":
        end_date = datetime.now().strftime("%Y-12-31")
        start_date = f"{datetime.now().year - 5}-01-01"
    elif time_option == "自定义":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("开始日期", value=datetime(2020, 1, 1)).strftime("%Y-%m-%d")
        with col2:
            end_date = st.date_input("结束日期", value=datetime.now()).strftime("%Y-%m-%d")

    # 查询按钮
    query_button = st.sidebar.button("🔍 查询财务数据", type="primary", use_container_width=True)

    return symbol, start_date, end_date, query_button


def render_report(title: str, df: pd.DataFrame, report_type: str) -> None:
    """
    渲染单个报表

    Args:
        title: 报表标题
        df: 报表数据
        report_type: 报表类型
    """
    if df.empty:
        st.warning(f"⚠️ {title}暂无数据")
        return

    st.subheader(f"📋 {title}")

    # 显示数据概览
    display_metrics_section(df)

    # 格式化数据
    formatted_df = format_financial_data(df, report_type)

    # 首先显示数据表格（原始数据展示）
    st.subheader("📊 财务数据表格")

    if not formatted_df.empty and '指标名称' in formatted_df.columns:
        # 创建样式化的表格（带可点击的指标名称）
        styler = create_styler(formatted_df)
        st.dataframe(styler, use_container_width=True, hide_index=True)

        # 深度分析部分
        st.markdown("---")
        st.subheader("📈 财务指标深度分析")
        st.info("💡 **点击下方任意指标名称进行深度图表分析**")

        # 过滤掉空值或0值的指标
        valid_indicators = []
        year_columns = [col for col in formatted_df.columns if col not in ['指标名称', '单位']]

        for _, row in formatted_df.iterrows():
            indicator = row['指标名称']
            # 检查该指标是否有有效数据（非空且非0）
            has_valid_data = False
            for year_col in year_columns:
                value = row[year_col]
                if pd.notna(value) and float(value) != 0:
                    has_valid_data = True
                    break

            if has_valid_data:
                valid_indicators.append(indicator)

        # 显示有效指标或提示信息
        if not valid_indicators:
            st.warning("⚠️ 该报表暂无有效的财务指标数据进行分析")
        else:
            # 使用按钮创建可点击的指标列表
            cols = st.columns(4)  # 四列布局，更紧凑
            for i, indicator in enumerate(valid_indicators):
                with cols[i % 4]:
                    button_style = "primary" if indicator == st.session_state.get(f"selected_indicator_{report_type}", "") else "secondary"

                    if st.button(
                        indicator,
                        key=f"indicator_{report_type}_{i}",
                        type=button_style,
                        use_container_width=True,
                        help=f"点击分析 {indicator}"
                    ):
                        st.session_state[f"selected_indicator_{report_type}"] = indicator
                        st.rerun()

            # 显示选中指标的图表
            selected_indicator = st.session_state.get(f"selected_indicator_{report_type}", None)
            if selected_indicator:
                st.markdown("---")
                st.success(f"📊 **{selected_indicator}** - 财务指标分析")
                try:
                    create_financial_chart(selected_indicator, formatted_df, report_type)
                except Exception as e:
                    st.error(f"生成图表时发生错误: {str(e)}")
                    st.write("请尝试选择其他指标或检查数据质量。")
    else:
        # 创建样式化的表格（无数据情况）
        styler = create_styler(formatted_df)
        st.dataframe(styler, use_container_width=True, hide_index=True)

    st.markdown("---")


def render_main_content() -> None:
    """渲染主要内容区域"""
    st.info("👈 请在左侧输入股票代码开始查询")


def display_query_results(data: dict[str, pd.DataFrame]) -> None:
    """
    显示查询结果

    Args:
        data: 包含四大报表数据的字典
    """
    if not data:
        st.error("❌ 未能获取到任何财务数据，请检查股票代码或稍后重试")
        return

    # 创建选项卡
    tab_titles = [
        "📈 财务指标",
        "🏦 资产负债表",
        "💰 利润表",
        "💳 现金流量表"
    ]

    tabs = st.tabs(tab_titles)

    # 定义报表映射
    report_mapping = [
        (tabs[0], "财务指标", data.get('indicators'), "indicators"),
        (tabs[1], "资产负债表", data.get('balance_sheet'), "balance_sheet"),
        (tabs[2], "利润表", data.get('income_statement'), "income_statement"),
        (tabs[3], "现金流量表", data.get('cash_flow'), "cash_flow")
    ]

    # 渲染各个报表
    for tab, title, df_data, report_type in report_mapping:
        with tab:
            render_report(title, df_data, report_type)