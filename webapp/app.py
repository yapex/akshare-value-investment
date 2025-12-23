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

# 导入数据服务
from services.data_service import get_revenue_data, get_ebit_margin_data

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

    with st.spinner(f"正在获取 {market} 股票 {symbol} 的数据..."):
        data = get_revenue_data(symbol, market, years)

        if data is not None and not data.empty:
            # 获取收入字段名称
            revenue_col = [col for col in data.columns if col != "年份"][0]

            # 计算增长率
            data = data.sort_values("年份").reset_index(drop=True)
            data['增长率'] = data[revenue_col].pct_change() * 100
            data['增长率'] = data['增长率'].round(2)

            # 创建双Y轴图表
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - {revenue_col}趋势及增长率"]
            )

            # 添加柱状图（营业收入）
            fig.add_trace(
                go.Bar(
                    x=data['年份'],
                    y=data[revenue_col],
                    name=revenue_col,
                    marker_color='steelblue',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加折线图（增长率）
            fig.add_trace(
                go.Scatter(
                    x=data['年份'],
                    y=data['增长率'],
                    name='增长率',
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig.update_yaxes(title_text=revenue_col, secondary_y=False)
            fig.update_yaxes(title_text="增长率 (%)", secondary_y=True)

            # 设置布局
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                barmode='group',
                height=500
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

            # 计算并显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            # 计算指标
            avg_revenue = data[revenue_col].mean()
            max_revenue = data[revenue_col].max()
            min_revenue = data[revenue_col].min()
            latest_revenue = data[revenue_col].iloc[-1]
            first_revenue = data[revenue_col].iloc[0]

            # 计算年复合增长率 (CAGR)
            years_count = len(data)
            if years_count > 1 and first_revenue > 0:
                cagr = ((latest_revenue / first_revenue) ** (1 / (years_count - 1)) - 1) * 100
            else:
                cagr = 0

            # 计算平均增长率
            avg_growth_rate = data['增长率'].mean()

            # 使用四列布局显示指标
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="年复合增长率 (CAGR)",
                    value=f"{cagr:.2f}%",
                    delta=None
                )

            with col2:
                st.metric(
                    label="平均增长率",
                    value=f"{avg_growth_rate:.2f}%",
                    delta=None
                )

            with col3:
                st.metric(
                    label="最新营业收入",
                    value=f"{latest_revenue:.2f}",
                    delta=None
                )

            with col4:
                st.metric(
                    label=f"{years_count}年平均",
                    value=f"{avg_revenue:.2f}",
                    delta=None
                )

            # 折叠的原始数据表格
            with st.expander("📊 查看原始数据"):
                # 格式化显示：保留两位小数
                display_data = data.copy()
                display_data['增长率'] = display_data['增长率'].round(2)
                display_data.loc[display_data['增长率'].isna(), '增长率'] = '-'
                st.dataframe(display_data, use_container_width=True, hide_index=True)

# EBIT利润率分析
st.markdown("---")
st.subheader("💰 EBIT利润率分析")

with st.spinner(f"正在获取 {market} 股票 {symbol} 的EBIT利润率数据..."):
    ebit_data = get_ebit_margin_data(symbol, market, years)

    if ebit_data is not None and not ebit_data.empty:
        # 计算增长率
        ebit_data = ebit_data.sort_values("年份").reset_index(drop=True)
        ebit_data['利润率增长率'] = ebit_data['EBIT利润率'].pct_change() * 100
        ebit_data['利润率增长率'] = ebit_data['利润率增长率'].round(2)

        # 创建双Y轴图表
        fig2 = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=[f"{symbol} - EBIT利润率趋势"]
        )

        # 添加柱状图（EBIT利润率）
        fig2.add_trace(
            go.Bar(
                x=ebit_data['年份'],
                y=ebit_data['EBIT利润率'],
                name="EBIT利润率 (%)",
                marker_color='green',
                opacity=0.7
            ),
            secondary_y=False
        )

        # 添加折线图（增长率）
        fig2.add_trace(
            go.Scatter(
                x=ebit_data['年份'],
                y=ebit_data['利润率增长率'],
                name='增长率',
                mode='lines+markers',
                line=dict(color='orange', width=2),
                marker=dict(size=8)
            ),
            secondary_y=True
        )

        # 设置Y轴标题
        fig2.update_yaxes(title_text="EBIT利润率 (%)", secondary_y=False)
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

        # 计算并显示关键指标
        st.markdown("---")
        st.subheader("📊 关键指标")

        # 计算指标
        avg_margin = ebit_data['EBIT利润率'].mean()
        max_margin = ebit_data['EBIT利润率'].max()
        min_margin = ebit_data['EBIT利润率'].min()
        latest_margin = ebit_data['EBIT利润率'].iloc[-1]

        # 计算平均增长率
        avg_growth_rate = ebit_data['利润率增长率'].mean()

        # 使用四列布局显示指标
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="平均利润率",
                value=f"{avg_margin:.2f}%",
                delta=None
            )

        with col2:
            st.metric(
                label="最新利润率",
                value=f"{latest_margin:.2f}%",
                delta=None
            )

        with col3:
            st.metric(
                label=f"{years}年最高",
                value=f"{max_margin:.2f}%",
                delta=None
            )

        with col4:
            st.metric(
                label=f"{years}年最低",
                value=f"{min_margin:.2f}%",
                delta=None
            )

        # 折叠的计算用原始数据表格
        with st.expander("📊 查看计算用原始数据"):
            # 格式化显示
            display_ebit_data = ebit_data.copy()
            # 显示所有列（根据不同市场显示不同字段）
            display_cols = list(ebit_data.columns)
            st.dataframe(display_ebit_data[display_cols], use_container_width=True, hide_index=True)
    else:
        st.warning(f"无法获取股票 {symbol} 的EBIT利润率数据，可能该市场不支持此指标")
