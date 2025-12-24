"""
股票质量分析应用

基于Streamlit的股票财务分析工具，支持A股、港股、美股
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入计算器（所有数据获取和计算都在这里）
from services.calculator import Calculator

st.set_page_config(
    page_title="股票质量分析",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 股票质量分析")
st.markdown("---")

# 侧边栏：选择股票
st.sidebar.header("📈 股票选择")

market = st.sidebar.selectbox(
    "选择市场",
    ["A股", "港股", "美股"],
    index=0
)

symbol = st.sidebar.text_input(
    "股票代码",
    value="600519" if market == "A股" else ("00700" if market == "港股" else "AAPL"),
    help="A股：如600519或SH600519\n港股：如00700\n美股：如AAPL"
)

years = st.sidebar.slider(
    "查询年数",
    min_value=1,
    max_value=20,
    value=10,
    step=1
)

st.sidebar.markdown("---")
st.sidebar.write(f"**当前设置**")
st.sidebar.write(f"- 市场：{market}")
st.sidebar.write(f"- 代码：{symbol}")
st.sidebar.write(f"- 年数：{years}")

# 主内容区
# 检查参数是否变化，如果变化则自动重新分析
current_params = f"{market}_{symbol}_{years}"

if 'last_params' not in st.session_state:
    st.session_state.last_params = current_params

params_changed = st.session_state.last_params != current_params

# 自动开始分析（首次加载或参数变化时）
if params_changed or st.button("🔄 刷新分析", type="secondary"):
    st.session_state.last_params = current_params
    st.session_state.initialized = True

    # ==================== 1. 净利润现金比分析 ====================
    st.markdown("---")
    st.subheader("💰 净利润现金比分析（利润质量）")

    with st.spinner(f"正在获取 {market} 股票 {symbol} 的净利润现金比数据..."):
        result = Calculator.calculate_net_profit_cash_ratio(symbol, market, years)

        if result is not None:
            ratio_data, display_cols = result
            ratio_data = ratio_data.sort_values("年份").reset_index(drop=True)

            # 创建双Y轴图表：两条折线分别展示累计净利润和累计经营现金流
            fig1 = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 累计净利润 vs 累计经营现金流"]
            )

            # 添加折线图（累计净利润）
            fig1.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=ratio_data['累计净利润'],
                    name='累计净利润',
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=False
            )

            # 添加折线图（累计经营现金流）
            fig1.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=ratio_data['累计经营性现金流量净额'],
                    name='累计经营现金流',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig1.update_yaxes(title_text="累计净利润", secondary_y=False)
            fig1.update_yaxes(title_text="累计经营现金流", secondary_y=True)

            # 设置布局
            fig1.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=500
            )

            # 显示图表
            st.plotly_chart(fig1, use_container_width=True)

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            avg_ratio = ratio_data['净现比'].mean()
            latest_ratio = ratio_data['净现比'].iloc[-1]
            latest_cumulative_net_profit = ratio_data['累计净利润'].iloc[-1]
            latest_cumulative_cashflow = ratio_data['累计经营性现金流量净额'].iloc[-1]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="平均净现比", value=f"{avg_ratio:.2f}", delta=None)

            with col2:
                st.metric(label="最新净现比", value=f"{latest_ratio:.2f}", delta=None)

            with col3:
                st.metric(label="累计净利润", value=f"{latest_cumulative_net_profit:.2f}", delta=None)

            with col4:
                st.metric(label="累计经营现金流", value=f"{latest_cumulative_cashflow:.2f}", delta=None)

            # 折叠的原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(ratio_data[display_cols], use_container_width=True, hide_index=True)
        else:
            st.error(f"无法获取股票 {symbol} 的净利润现金比数据")

    # ==================== 2. 营业收入增长趋势分析 ====================
    st.markdown("---")
    st.subheader("📈 营业收入增长趋势分析")

    with st.spinner(f"正在获取 {market} 股票 {symbol} 的营业收入数据..."):
        result = Calculator.calculate_revenue_growth(symbol, market, years)

        if result is not None:
            revenue_data, metrics = result

            # 获取收入字段名称（用于显示）
            if market == "A股":
                revenue_col = "其中：营业收入"
            elif market == "港股":
                revenue_col = "营业额"
            else:  # 美股
                revenue_col = "营业收入"

            # 创建双Y轴图表
            fig2 = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 营业收入趋势及增长率"]
            )

            # 添加柱状图（营业收入）
            fig2.add_trace(
                go.Bar(
                    x=revenue_data['年份'],
                    y=revenue_data[revenue_col],
                    name="营业收入",
                    marker_color='green',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加折线图（增长率）
            fig2.add_trace(
                go.Scatter(
                    x=revenue_data['年份'],
                    y=revenue_data['增长率'],
                    name='增长率',
                    mode='lines+markers',
                    line=dict(color='orange', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig2.update_yaxes(title_text="营业收入", secondary_y=False)
            fig2.update_yaxes(title_text="增长率 (%)", secondary_y=True)

            # 设置布局
            fig2.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                barmode='group',
                height=500
            )

            # 显示图表
            st.plotly_chart(fig2, use_container_width=True)

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="年复合增长率 (CAGR)", value=f"{metrics['cagr']:.2f}%", delta=None)

            with col2:
                st.metric(label="平均增长率", value=f"{metrics['avg_growth_rate']:.2f}%", delta=None)

            with col3:
                st.metric(label="最新营业收入", value=f"{metrics['latest_revenue']:.2f}", delta=None)

            with col4:
                st.metric(label=f"{metrics['years_count']}年平均", value=f"{metrics['avg_revenue']:.2f}", delta=None)

            # 折叠的原始数据表格
            with st.expander("📊 查看原始数据"):
                display_data = revenue_data.copy()
                display_data['增长率'] = display_data['增长率'].round(2)
                display_data.loc[display_data['增长率'].isna(), '增长率'] = '-'
                st.dataframe(display_data, use_container_width=True, hide_index=True)
        else:
            st.error(f"无法获取股票 {symbol} 的营业收入数据")

    # ==================== 3. EBIT利润率分析 ====================
    st.markdown("---")
    st.subheader("💰 EBIT利润率分析")

    with st.spinner(f"正在获取 {market} 股票 {symbol} 的EBIT利润率数据..."):
        result = Calculator.calculate_ebit_margin(symbol, market, years)

        if result is not None:
            ebit_data, display_cols, metrics = result

            # 创建双Y轴图表
            fig3 = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - EBIT利润率趋势"]
            )

            # 添加柱状图（EBIT利润率）
            fig3.add_trace(
                go.Bar(
                    x=ebit_data['年份'],
                    y=ebit_data['EBIT利润率'],
                    name="EBIT利润率 (%)",
                    marker_color='purple',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加折线图（增长率）
            fig3.add_trace(
                go.Scatter(
                    x=ebit_data['年份'],
                    y=ebit_data['利润率增长率'],
                    name='增长率',
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig3.update_yaxes(title_text="EBIT利润率 (%)", secondary_y=False)
            fig3.update_yaxes(title_text="增长率 (%)", secondary_y=True)

            # 设置布局
            fig3.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                barmode='group',
                height=500
            )

            # 显示图表
            st.plotly_chart(fig3, use_container_width=True)

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="平均利润率", value=f"{metrics['avg_margin']:.2f}%", delta=None)

            with col2:
                st.metric(label="最新利润率", value=f"{metrics['latest_margin']:.2f}%", delta=None)

            with col3:
                st.metric(label=f"{years}年最高", value=f"{metrics['max_margin']:.2f}%", delta=None)

            with col4:
                st.metric(label=f"{years}年最低", value=f"{metrics['min_margin']:.2f}%", delta=None)

            # 折叠的计算用原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(ebit_data[display_cols], use_container_width=True, hide_index=True)
        else:
            st.warning(f"无法获取股票 {symbol} 的EBIT利润率数据，可能该市场不支持此指标")
