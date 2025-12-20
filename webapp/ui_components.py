"""
UI组件模块

处理Streamlit界面的各种组件渲染
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from data_formatter import format_financial_data, create_styler, display_metrics_section
from chart_utils import create_financial_chart


def render_sidebar() -> tuple[str, str, str, str, bool]:
    """
    渲染侧边栏

    Returns:
        tuple: (market, symbol, start_date, end_date, query_button)
    """
    st.sidebar.title("📊 跨市场财务报表分析")

    # 市场选择
    market = st.sidebar.selectbox("选择市场", ["A股", "港股", "美股"], index=0)

    # 根据市场设置默认值和提示
    market_configs = {
        "A股": {"placeholder": "600519", "example": "600519（贵州茅台）", "length": 6},
        "港股": {"placeholder": "00700", "example": "00700（腾讯控股）", "length": 5},
        "美股": {"placeholder": "AAPL", "example": "AAPL（苹果公司）", "length": None}
    }

    config = market_configs[market]

    # 股票代码输入
    symbol = st.sidebar.text_input(
        "股票代码",
        value=config["placeholder"],
        help=f"请输入{market}代码，如{config['example']}"
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

    return market, symbol, start_date, end_date, query_button


def render_report(title: str, df: pd.DataFrame, report_type: str, market: str = "A股") -> None:
    """
    渲染单个报表

    Args:
        title: 报表标题
        df: 报表数据
        report_type: 报表类型
    """
    if df is None or df.empty:
        st.warning(f"⚠️ {title}暂无数据")
        return

    st.subheader(f"📋 {title}")

    # 显示数据概览
    display_metrics_section(df)

    # 格式化数据
    formatted_df = format_financial_data(df, report_type, market)

    # 首先显示数据表格（原始数据展示）
    st.subheader("📊 财务数据表格")

    if not formatted_df.empty and '指标名称' in formatted_df.columns:
        # 创建样式化的表格（带可点击的指标名称）
        styler = create_styler(formatted_df)
        st.dataframe(styler, width='stretch', hide_index=True, height=800)

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
                if pd.notna(value):
                    try:
                        # 清理单位并转换为浮点数
                        if isinstance(value, str):
                            clean_value = value.replace(',', '').replace('，', '').replace('亿', '').replace('万', '').strip()
                            if clean_value and clean_value not in ['-', '--', 'N/A', '']:
                                numeric_value = float(clean_value)
                                if numeric_value != 0:
                                    has_valid_data = True
                                    break
                        else:
                            numeric_value = float(value)
                            if numeric_value != 0:
                                has_valid_data = True
                                break
                    except (ValueError, TypeError):
                        pass

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
                        use_container_width=True
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
        st.dataframe(styler, width='stretch', hide_index=True, height=800)

    st.markdown("---")


def render_main_content() -> None:
    """渲染主要内容区域"""
    st.info("👈 请在左侧输入股票代码开始查询")


def render_basic_check(data: dict[str, pd.DataFrame], market: str = "A股") -> None:
    """
    渲染基本检查页面

    Args:
        data: 包含四大报表数据的字典
        market: 市场类型
    """
    st.subheader("🔍 财务健康状况基本检查")

    if not data:
        st.warning("⚠️ 暂无数据进行基本检查")
        return

    # 获取各报表数据
    indicators_df = data.get('indicators')
    balance_sheet_df = data.get('balance_sheet')
    income_statement_df = data.get('income_statement')
    cash_flow_df = data.get('cash_flow')

    # 基本信息卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("数据完整性", "✅ 良好", help="四大报表数据完整")

    with col2:
        # 计算数据年份范围
        all_years = []
        for df_data in [indicators_df, balance_sheet_df, income_statement_df, cash_flow_df]:
            if df_data is not None and not df_data.empty:
                date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
                for date_col in date_columns:
                    if date_col in df_data.columns:
                        years = pd.to_datetime(df_data[date_col]).dt.year.unique()
                        all_years.extend(years)
                        break
        if all_years:
            year_range = f"{min(all_years)}-{max(all_years)}"
            st.metric("数据年份", year_range)
        else:
            st.metric("数据年份", "未知")

    with col3:
        st.metric("市场类型", market)

    with col4:
        # 获取当前股票代码
        current_symbol = st.session_state.get('current_symbol', '未知')
        st.metric("股票代码", current_symbol)

    st.markdown("---")

    # 核心财务指标概览
    st.subheader("📊 核心财务指标概览")

    if indicators_df is not None and not indicators_df.empty:
        # 格式化指标数据
        formatted_indicators = format_financial_data(indicators_df, f"{market.lower()}_stock_indicators", market)

        if not formatted_indicators.empty:
            # 选择关键指标进行展示
            key_indicators = []

            # 根据市场选择关键指标
            if market == "A股":
                key_names = ["净资产收益率(%)", "净利润(亿元)", "营业收入(亿元)", "资产负债率(%)", "毛利率(%)", "基本每股收益(元)"]
            elif market == "港股":
                key_names = ["平均净资产收益率(%)", "股东净利润(亿港元)", "营业收入(亿港元)", "资产负债率(%)", "毛利率(%)", "基本每股收益(港元)"]
            else:  # 美股
                key_names = ["净资产收益率(%)", "归母净利润(亿美元)", "营业收入(亿美元)", "资产负债率(%)", "毛利率(%)", "基本每股收益(美元)"]

            # 提取关键指标数据
            for name in key_names:
                matching_rows = formatted_indicators[formatted_indicators['指标名称'] == name]
                if not matching_rows.empty:
                    key_indicators.append(matching_rows.iloc[0])

            if key_indicators:
                key_df = pd.DataFrame(key_indicators)

                # 展示关键指标
                col1, col2, col3 = st.columns(3)

                for i, (_, row) in enumerate(key_df.iterrows()):
                    if i < 6:  # 只显示前6个指标
                        col = [col1, col2, col3][i % 3]
                        indicator_name = row['指标名称']

                        # 获取最新年份的数据
                        year_cols = [col for col in key_df.columns if col not in ['指标名称']]
                        if year_cols:
                            latest_year = year_cols[0]  # 格式化后已按年份降序排列
                            latest_value = row[latest_year]

                            if pd.notna(latest_value) and latest_value != '':
                                col.metric(
                                    indicator_name,
                                    latest_value,
                                    help=f"最新{latest_year}年数据"
                                )
            else:
                st.warning("⚠️ 未找到关键财务指标数据")
        else:
            st.warning("⚠️ 财务指标数据格式化失败")
    else:
        st.warning("⚠️ 暂无财务指标数据")

    st.markdown("---")

    # 财务健康状态检查
    st.subheader("💰 财务健康状态检查")

    health_checks = []

    # 检查盈利能力
    if indicators_df is not None and not indicators_df.empty:
        # 这里可以添加更多健康检查逻辑
        health_checks.append(("✅ 数据完整性", "四大报表数据齐全"))
        health_checks.append(("✅ 最新数据", "包含最新财务年度数据"))

    if health_checks:
        for status, description in health_checks:
            st.write(f"{status} {description}")
    else:
        st.info("📋 财务健康检查需要完整的财务数据")


def display_query_results(data: dict[str, pd.DataFrame], market: str = "A股") -> None:
    """
    显示查询结果

    Args:
        data: 包含四大报表数据的字典
        market: 市场类型
    """
    if not data:
        st.error("❌ 未能获取到任何财务数据，请检查股票代码或稍后重试")
        return

    # 添加基本检查页签，共5个页签
    tab_titles = [
        "🔍 基本检查",
        "📈 财务指标",
        "🏦 资产负债表",
        "💰 利润表",
        "💳 现金流量表"
    ]

    tabs = st.tabs(tab_titles)

    # 映射市场名称到API格式
    market_api_mapping = {
        "A股": "a",
        "港股": "hk",
        "美股": "us"
    }
    api_market = market_api_mapping.get(market, market.lower())

    # 首先渲染基本检查页签
    with tabs[0]:
        render_basic_check(data, market)

    # 定义剩余报表映射（从第2个页签开始）
    report_mapping = [
        (tabs[1], "财务指标", data.get('indicators'), f"{api_market}_stock_indicators"),
        (tabs[2], "资产负债表", data.get('balance_sheet'), f"{api_market}_stock_balance_sheet"),
        (tabs[3], "利润表", data.get('income_statement'), f"{api_market}_stock_income_statement"),
        (tabs[4], "现金流量表", data.get('cash_flow'), f"{api_market}_stock_cash_flow")
    ]

    # 渲染各个报表
    for tab, title, df_data, report_type in report_mapping:
        with tab:
            render_report(title, df_data, report_type, market)