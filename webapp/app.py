"""
股票质量分析应用

基于Streamlit的股票财务分析工具，支持A股、港股、美股
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
from akshare_value_investment.container import create_container
from akshare_value_investment.core.models import MarketType

# 导入分析组件
from components.net_profit_cash_ratio import NetProfitCashRatioComponent
from components.revenue_growth import RevenueGrowthComponent
from components.ebit_margin import EBITMarginComponent
from components.free_cash_flow_ratio import FreeCashFlowRatioComponent
from components.roic import ROICComponent
from components.debt_to_equity import DebtToEquityComponent
from components.debt_to_fcf_ratio import DebtToFcfRatioComponent
from components.liquidity_ratio import LiquidityRatioComponent
# from components.roe import ROEComponent  # 暂时不用

# 配置：分析组件列表（按分组组织）
ANALYSIS_GROUPS = {
    "💰 盈利分析": [
        ROICComponent,
        EBITMarginComponent,
        RevenueGrowthComponent,
        NetProfitCashRatioComponent,
        FreeCashFlowRatioComponent,
    ],
    "💳 债务分析": [
        DebtToEquityComponent,
        DebtToFcfRatioComponent,
        LiquidityRatioComponent,
        # ROEComponent,  # 暂时不用
    ]
}

# 扁平化组件列表（用于快速导航）
ANALYSIS_COMPONENTS = []
for components in ANALYSIS_GROUPS.values():
    ANALYSIS_COMPONENTS.extend(components)

# 创建容器，获取股票识别器
container = create_container()
stock_identifier = container.stock_identifier()

# 页面配置
st.set_page_config(
    page_title="股票质量分析",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==================== 侧边栏：股票选择 ====================
st.sidebar.header("📈 股票选择")

# 股票代码输入（支持自动识别市场）
user_input_symbol = st.sidebar.text_input(
    "股票代码",
    value="600519",
    help="""
    **智能识别**：自动识别股票代码所属市场

    **A股格式**：
    - 纯数字：600519, 000001, 300015
    - 带前缀：SH600519, SZ000001

    **港股格式**：
    - 3-5位数字：700, 00700, 09988
    - 带前缀：HK.00700

    **美股格式**：
    - 字母代码：AAPL, MSFT, GOOGL
    - 带前缀：US.AAPL
    """
)

# 自动识别市场
identified_market, identified_symbol = stock_identifier.identify(user_input_symbol)

# 市场类型映射
MARKET_TYPE_MAP = {
    MarketType.A_STOCK: "A股",
    MarketType.HK_STOCK: "港股",
    MarketType.US_STOCK: "美股"
}

market = MARKET_TYPE_MAP[identified_market]
symbol = identified_symbol

# 显示识别结果
st.sidebar.info(f"🎯 识别结果：**{market}** - `{symbol}`")

# 标题（动态显示股票代码）
st.title(f"📊 股票质量分析 - {symbol}")
st.markdown("---")

years = st.sidebar.slider(
    "查询年数",
    min_value=1,
    max_value=20,
    value=10,
    step=1
)

# ==================== 侧边栏：快速导航 ====================
st.sidebar.markdown("---")
st.sidebar.header("📊 快速导航")

# 导航按钮：用于跳转到指定组件
selected_component = st.sidebar.radio(
    "跳转到分析模块",
    ["全部显示"] + [comp.title for comp in ANALYSIS_COMPONENTS],
    label_visibility="collapsed"
)

# ==================== 主内容区 ====================
# 检查参数是否变化，如果变化则自动重新分析
current_params = f"{market}_{symbol}_{years}"

if 'last_params' not in st.session_state:
    st.session_state.last_params = current_params
    st.session_state.initialized = False

params_changed = st.session_state.last_params != current_params

# 自动开始分析（首次加载或参数变化时）
should_analyze = params_changed or not st.session_state.get('initialized', False)

if should_analyze:
    st.session_state.last_params = current_params
    st.session_state.initialized = True

# 渲染组件
if selected_component == "全部显示":
    # 使用Tab标签页分组显示
    group_names = list(ANALYSIS_GROUPS.keys())
    tabs = st.tabs(group_names)

    for tab, group_name in zip(tabs, group_names):
        with tab:
            components = ANALYSIS_GROUPS[group_name]
            if not components:
                st.info("📭 该分类下暂无分析模块")
            else:
                for component in components:
                    component.render(symbol, market, years)
else:
    # 只显示选中的组件
    for component in ANALYSIS_COMPONENTS:
        if component.title == selected_component:
            # 添加返回按钮
            if st.button("⬆️ 返回全部显示", key="back_to_all"):
                st.rerun()
            st.markdown("---")

            # 渲染该组件
            component.render(symbol, market, years)
            break

