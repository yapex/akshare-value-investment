"""
股票质量分析应用

基于Streamlit的股票财务分析工具，支持A股、港股、美股
"""

import streamlit as st

# 导入分析组件
from components.net_profit_cash_ratio import NetProfitCashRatioComponent
from components.revenue_growth import RevenueGrowthComponent
from components.ebit_margin import EBITMarginComponent

# 配置：分析组件列表
ANALYSIS_COMPONENTS = [
    NetProfitCashRatioComponent,
    RevenueGrowthComponent,
    EBITMarginComponent,
]

# 页面配置
st.set_page_config(
    page_title="股票质量分析",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("📊 股票质量分析")
st.markdown("---")

# ==================== 侧边栏：股票选择 ====================
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

# ==================== 主内容区 ====================
# 检查参数是否变化，如果变化则自动重新分析
current_params = f"{market}_{symbol}_{years}"

if 'last_params' not in st.session_state:
    st.session_state.last_params = current_params

params_changed = st.session_state.last_params != current_params

# 自动开始分析（首次加载或参数变化时）
if params_changed or st.button("🔄 刷新分析", type="secondary"):
    st.session_state.last_params = current_params
    st.session_state.initialized = True

    # 渲染所有分析组件
    for component in ANALYSIS_COMPONENTS:
        component.render(symbol, market, years)
