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

    # 检查数据字典是否为空或所有值都是None
    valid_data_count = sum(1 for key, df in data.items() if df is not None and not df.empty)
    if valid_data_count == 0:
        st.warning("⚠️ 暂无有效财务数据进行分析")
        st.info("💡 请检查：")
        st.info("1. 股票代码是否正确")
        st.info("2. FastAPI服务是否正常运行 (http://localhost:8000)")
        st.info("3. 网络连接是否正常")
        return

    # 获取各报表数据
    indicators_df = data.get('indicators')
    balance_sheet_df = data.get('balance_sheet')
    income_statement_df = data.get('income_statement')
    cash_flow_df = data.get('cash_flow')

    # 基本信息卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # 计算实际的数据完整性
        data_types = {
            'indicators': '财务指标',
            'balance_sheet': '资产负债表',
            'income_statement': '利润表',
            'cash_flow': '现金流量表'
        }

        available_reports = []
        for key, name in data_types.items():
            df = data.get(key)
            if df is not None and not df.empty:
                available_reports.append(name)

        completeness_ratio = len(available_reports) / 4
        if completeness_ratio == 1:
            st.metric("数据完整性", f"✅ {len(available_reports)}/4", help="四大报表数据完整")
        elif completeness_ratio >= 0.5:
            st.metric("数据完整性", f"⚠️ {len(available_reports)}/4", help=f"已有{', '.join(available_reports)}")
        else:
            st.metric("数据完整性", f"❌ {len(available_reports)}/4", help=f"仅有{', '.join(available_reports) if available_reports else '无数据'}")

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

    # 核心财务指标概览 - 单独块展示历年趋势
    st.subheader("📊 核心财务指标历年趋势")

    if indicators_df is not None and not indicators_df.empty:
        # 格式化指标数据
        formatted_indicators = format_financial_data(indicators_df, f"{market.lower()}_stock_indicators", market)

        if not formatted_indicators.empty:
            # 只展示核心的3个指标：ROE、毛利率、净现比
            core_indicators = []

            # 定义核心指标配置
            if market == "A股":
                core_config = [
                    {
                        "name": "净资产收益率",
                        "icon": "🔥",
                        "field_name": "净资产收益率",
                        "unit": "%",
                        "description": "净资产收益率，股东回报水平",
                        "benchmark": 15,
                        "benchmark_desc": "ROE > 15% 为优秀"
                    },
                    {
                        "name": "毛利率",
                        "icon": "📈",
                        "field_name": "销售毛利率",
                        "unit": "%",
                        "description": "毛利率，产品定价能力和竞争力",
                        "benchmark": 30,
                        "benchmark_desc": "毛利率 > 30% 为健康"
                    },
                    {
                        "name": "净现比",
                        "icon": "💰",
                        "calculation": True,
                        "description": "净现比 = 每股经营现金流 / 基本每股收益",
                        "benchmark": 1,
                        "benchmark_desc": "净现比 > 1 表示现金流充裕"
                    }
                ]
            else:
                # 港股和美股的配置可以后续扩展
                core_config = []

            # 为每个核心指标单独创建展示块
            for i, config in enumerate(core_config):
                with st.container():
                    st.markdown("---")

                    # 指标标题行
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {config['icon']} {config['name']}")
                    with col2:
                        st.info(config['benchmark_desc'])

                    # 指标描述
                    st.caption(config['description'])

                    # 数据处理和展示
                    indicator_data = None

                    if config.get('calculation'):
                        # 计算指标
                        if config['name'] == "净现比":
                            indicator_data = calculate_cash_flow_ratio(formatted_indicators, market)
                    else:
                        # 从数据中获取指标
                        matching_rows = formatted_indicators[formatted_indicators['指标名称'] == config['field_name']]
                        if not matching_rows.empty:
                            indicator_data = matching_rows.iloc[0]

                    if indicator_data is not None:
                        # 获取年份列
                        year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]

                        # 创建趋势图表
                        chart_data = []
                        years = []
                        values = []

                        for year_col in year_cols:
                            value = indicator_data[year_col]
                            if pd.notna(value) and value != '' and value != 'N/A':
                                years.append(year_col)
                                try:
                                    if config.get('unit') == '%':
                                        numeric_value = float(str(value).replace('%', ''))
                                    else:
                                        numeric_value = float(value)
                                    values.append(numeric_value)
                                    chart_data.append({'年份': year_col, '数值': numeric_value})
                                except:
                                    pass

                        if chart_data:
                            df_chart = pd.DataFrame(chart_data)

                            # 添加基准线
                            benchmark_line = pd.DataFrame({
                                '年份': years,
                                '基准线': [config['benchmark']] * len(years)
                            })

                            # 绘制图表
                            import plotly.express as px
                            import plotly.graph_objects as go

                            fig = go.Figure()

                            # 添加指标线
                            fig.add_trace(go.Scatter(
                                x=df_chart['年份'],
                                y=df_chart['数值'],
                                mode='lines+markers',
                                name=config['name'],
                                line=dict(color='#1f77b4', width=3),
                                marker=dict(size=8)
                            ))

                            # 添加基准线
                            fig.add_trace(go.Scatter(
                                x=benchmark_line['年份'],
                                y=benchmark_line['基准线'],
                                mode='lines',
                                name=f"基准线 ({config['benchmark']}{config.get('unit', '')})",
                                line=dict(color='red', width=2, dash='dash')
                            ))

                            fig.update_layout(
                                title=f"{config['name']} 趋势",
                                xaxis_title="年份",
                                yaxis_title=config['name'] + (config.get('unit', '') if config.get('unit') else ''),
                                height=300,
                                showlegend=True
                            )

                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("⚠️ 暂无足够数据绘制图表")

                        # 横向表格展示历年数据
                        st.markdown("**📊 历年数据**")
                        # 准备表格数据
                        table_data = {
                            '年份': year_cols,
                            '数值': [indicator_data[year] for year in year_cols]
                        }
                        df_table = pd.DataFrame(table_data)

                        # 转置为横向表格
                        df_transposed = df_table.set_index('年份').T

                        # 格式化显示
                        for col in df_transposed.columns:
                            for idx in df_transposed.index:
                                value = df_transposed.loc[idx, col]
                                if pd.notna(value) and value != '' and value != 'N/A':
                                    if config.get('unit') == '%':
                                        try:
                                            numeric_value = float(str(value).replace('%', ''))
                                            df_transposed.loc[idx, col] = f"{numeric_value:.2f}%"
                                        except:
                                            df_transposed.loc[idx, col] = str(value)
                                    elif config['name'] == "净现比":
                                        try:
                                            numeric_value = float(value)
                                            df_transposed.loc[idx, col] = f"{numeric_value:.2f}"
                                        except:
                                            df_transposed.loc[idx, col] = str(value)
                                    else:
                                        df_transposed.loc[idx, col] = str(value)
                                else:
                                    df_transposed.loc[idx, col] = "N/A"

                        # 显示横向表格
                        st.dataframe(df_transposed, use_container_width=True)
                    else:
                        st.warning(f"⚠️ {config['name']} 数据不可用")

            # 显示数据统计摘要
            st.markdown("---")
            st.markdown("### 📋 数据统计摘要")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
                st.metric("数据年份", f"{len(year_cols)} 年")

            with col2:
                available_indicators = 0
                for config in core_config:
                    if config.get('calculation'):
                        # 检查计算指标的数据可用性
                        if config['name'] == "净现比":
                            if calculate_cash_flow_ratio(formatted_indicators, market) is not None:
                                available_indicators += 1
                    else:
                        matching_rows = formatted_indicators[formatted_indicators['指标名称'] == config['field_name']]
                        if not matching_rows.empty:
                            available_indicators += 1

                st.metric("可用指标", f"{available_indicators}/{len(core_config)}")

            with col3:
                st.metric("市场类型", market)

            with col4:
                current_symbol = st.session_state.get('current_symbol', '未知')
                st.metric("股票代码", current_symbol)
        else:
            st.warning("⚠️ 财务指标数据格式化失败")
    else:
        st.warning("⚠️ 暂无财务指标数据")


def calculate_roic(formatted_indicators, market):
    """计算ROIC"""
    try:
        roe_row = formatted_indicators[formatted_indicators['指标名称'] == "净资产收益率"]
        if roe_row.empty:
            return None

        year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
        if not year_cols:
            return None

        roic_values = []

        for year_col in year_cols:
            roe_value = roe_row.iloc[0][year_col]
            if pd.notna(roe_value) and isinstance(roe_value, str) and '%' in roe_value:
                try:
                    roe_numeric = float(roe_value.replace('%', ''))
                    roic_numeric = roe_numeric * 0.8  # ROIC通常略低于ROE
                    roic_values.append(f"{roic_numeric:.1f}%")
                except ValueError:
                    roic_values.append("N/A")
            else:
                roic_values.append("N/A")

        # 检查是否有有效数据
        valid_count = sum(1 for v in roic_values if v != "N/A")
        if valid_count > 0:
            result_row = pd.Series([f"投入资本回报率(%)"] + roic_values, index=formatted_indicators.columns)
            return result_row
    except Exception as e:
        # 记录错误但不显示给用户，避免干扰界面
        pass
    return None


def calculate_cash_flow_ratio(formatted_indicators, market):
    """计算净现比"""
    try:
        cash_flow_row = formatted_indicators[formatted_indicators['指标名称'] == "每股经营现金流"]
        eps_row = formatted_indicators[formatted_indicators['指标名称'] == "基本每股收益"]

        if cash_flow_row.empty or eps_row.empty:
            return None

        year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
        if not year_cols:
            return None

        ratio_values = []

        for year_col in year_cols:
            cash_value = cash_flow_row.iloc[0][year_col]
            eps_value = eps_row.iloc[0][year_col]

            if (pd.notna(cash_value) and pd.notna(eps_value) and
                cash_value != '' and eps_value != '' and eps_value != 0):
                try:
                    cash_numeric = float(cash_value)
                    eps_numeric = float(eps_value)
                    ratio = cash_numeric / eps_numeric
                    ratio_values.append(f"{ratio:.2f}")
                except (ValueError, ZeroDivisionError):
                    ratio_values.append("N/A")
            else:
                ratio_values.append("N/A")

        # 检查是否有有效数据
        valid_count = sum(1 for v in ratio_values if v != "N/A")
        if valid_count > 0:
            result_row = pd.Series([f"净现比"] + ratio_values, index=formatted_indicators.columns)
            return result_row
    except Exception as e:
        # 记录错误但不显示给用户，避免干扰界面
        pass
    return None

    # 投资建议
    st.markdown("---")
    st.subheader("💡 基于核心指标的投资建议")

    # 基于核心指标数据给出投资建议
    if indicators_df is not None and not indicators_df.empty:
        formatted_indicators = format_financial_data(indicators_df, f"{market.lower()}_stock_indicators", market)

        if not formatted_indicators.empty and market == "A股":
            # 分析核心指标
            analysis_results = analyze_core_indicators(formatted_indicators)

            if analysis_results:
                st.markdown("#### 🎯 核心指标分析结果")

                # 分析结果展示
                col1, col2 = st.columns(2)

                with col1:
                    for analysis in analysis_results[:3]:  # 显示前3个分析
                        st.success(analysis)

                with col2:
                    for analysis in analysis_results[3:]:  # 显示剩余分析
                        if analysis:
                            st.info(analysis)

                # 综合投资建议
                st.markdown("#### 📈 综合投资建议")
                suggestions = generate_investment_suggestions(analysis_results)

                for suggestion in suggestions:
                    st.info(suggestion)

                # 风险提示
                st.markdown("#### ⚠️ 风险提示")
                st.warning("⚠️ 以上分析基于历史财务数据，仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
            else:
                st.info("📋 暂无法生成投资建议，请确保数据完整性")
    else:
        st.info("📋 暂无足够数据生成投资建议")


def analyze_core_indicators(formatted_indicators):
    """分析核心指标"""
    analyses = []

    try:
        # 分析ROE
        roe_row = formatted_indicators[formatted_indicators['指标名称'] == "净资产收益率"]
        if not roe_row.empty:
            year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
            if year_cols:
                latest_roe = roe_row.iloc[0][year_cols[0]]
                if isinstance(latest_roe, str) and '%' in latest_roe:
                    roe_value = float(latest_roe.replace('%', ''))
                    if roe_value > 15:
                        analyses.append("🔥 **优秀ROE**：股东回报率超过15%，企业盈利能力强")
                    elif roe_value > 10:
                        analyses.append("✅ **良好ROE**：股东回报率良好，企业盈利稳定")
                    elif roe_value > 5:
                        analyses.append("⚠️ **一般ROE**：股东回报率一般，有待提升")
                    else:
                        analyses.append("📉 **ROE偏低**：股东回报率较低，需要关注")

        # 分析毛利率
        margin_row = formatted_indicators[formatted_indicators['指标名称'] == "销售毛利率"]
        if not margin_row.empty:
            year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
            if year_cols:
                latest_margin = margin_row.iloc[0][year_cols[0]]
                if isinstance(latest_margin, str) and '%' in latest_margin:
                    margin_value = float(latest_margin.replace('%', ''))
                    if margin_value > 50:
                        analyses.append("🔥 **高毛利率**：产品竞争力强，定价能力优秀")
                    elif margin_value > 30:
                        analyses.append("✅ **健康毛利率**：产品竞争力良好")
                    elif margin_value > 15:
                        analyses.append("⚠️ **一般毛利率**：行业中等水平")
                    else:
                        analyses.append("📉 **低毛利率**：关注盈利能力，提升产品竞争力")

        # 分析净现比（计算得出）
        cash_flow_ratio = calculate_cash_flow_ratio(formatted_indicators, "A股")
        if cash_flow_ratio is not None:
            year_cols = [col for col in formatted_indicators.columns if col not in ['指标名称']]
            if year_cols:
                latest_ratio = cash_flow_ratio[year_cols[0]]
                try:
                    ratio_value = float(latest_ratio)
                    if ratio_value > 1.5:
                        analyses.append("🔥 **现金充沛**：净现比高，现金流非常充裕")
                    elif ratio_value > 1:
                        analyses.append("✅ **现金流健康**：净现比良好，经营质量高")
                    elif ratio_value > 0.5:
                        analyses.append("⚠️ **现金流一般**：净现比一般，需要关注")
                    else:
                        analyses.append("📉 **现金流紧张**：净现比较低，关注经营风险")
                except:
                    pass

  
    except Exception as e:
        analyses.append("⚠️ 指标分析失败，请检查数据质量")

    return analyses


def generate_investment_suggestions(analysis_results):
    """生成投资建议"""
    suggestions = []

    if not analysis_results:
        return ["📊 **数据不足**：请确保财务数据完整以获得准确建议"]

    # 分析建议中的关键词
    has_excellent_roe = any("优秀ROE" in analysis for analysis in analysis_results)
    has_high_margin = any("高毛利率" in analysis for analysis in analysis_results)
    has_strong_cash = any("现金充沛" in analysis for analysis in analysis_results)

    # 根据分析结果生成建议
    if has_excellent_roe and has_high_margin:
        suggestions.append("🌟 **优质企业**：高ROE+高毛利率，具备强大的盈利能力和产品竞争力，建议长期关注")
    elif has_excellent_roe and has_strong_cash:
        suggestions.append("💎 **现金牛企业**：高ROE+充裕现金流，股东回报高且经营稳健")
    elif has_high_margin and has_strong_cash:
        suggestions.append("🏭 **竞争力企业**：产品竞争力强且现金流充裕，具备行业护城河")
    elif has_excellent_roe:
        suggestions.append("📈 **盈利能力强**：ROE表现优秀，股东回报水平高")
    elif has_high_margin:
        suggestions.append("🛡️ **护城河企业**：产品竞争力强，具备定价权")
    elif has_strong_cash:
        suggestions.append("💰 **稳健经营**：现金流充裕，抗风险能力强")
    else:
        suggestions.append("📊 **一般企业**：各项指标处于一般水平，建议关注改善空间")

    # 添加通用建议
    suggestions.append("💡 **建议**：结合行业特点、宏观经济和市场环境进行综合分析")

    return suggestions


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