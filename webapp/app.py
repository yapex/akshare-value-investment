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

# 导入搜索相关组件
from streamlit_searchbox import st_searchbox
from services.stock_search_service import StockSearchService
from utils.stock_history_manager import StockHistoryManager

# 导入分析组件
from components.net_profit_cash_ratio import NetProfitCashRatioComponent
from components.revenue_growth import RevenueGrowthComponent
from components.ebit_margin import EBITMarginComponent
from components.free_cash_flow_ratio import FreeCashFlowRatioComponent
from components.roic import ROICComponent
from components.debt_to_equity import DebtToEquityComponent
from components.debt_to_fcf_ratio import DebtToFcfRatioComponent
from components.liquidity_ratio import LiquidityRatioComponent
from components.cash_flow_pattern import CashFlowPatternComponent
from components.dcf_valuation import DCFValuationComponent
from components.net_income_valuation import NetIncomeValuationComponent
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
    ],
    "💵 现金流分析": [
        CashFlowPatternComponent,
    ],
    "📈 估值(DCF)": [
        DCFValuationComponent,
    ],
    "📊 估值(净利润)": [
        NetIncomeValuationComponent,
    ]
}

# 扁平化组件列表（用于快速导航）
ANALYSIS_COMPONENTS = []
for components in ANALYSIS_GROUPS.values():
    ANALYSIS_COMPONENTS.extend(components)

# 创建容器，获取股票识别器
container = create_container()
stock_identifier = container.stock_identifier()

# 市场类型映射（统一定义在这里，避免重复）
MARKET_TYPE_MAP = {
    MarketType.A_STOCK: "A股",
    MarketType.HK_STOCK: "港股",
    MarketType.US_STOCK: "美股"
}

# 初始化搜索服务
history_manager = StockHistoryManager()
search_service = StockSearchService(stock_identifier, history_manager)

# 页面配置
st.set_page_config(
    page_title="股票质量分析",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==================== 侧边栏：设置 ====================
st.sidebar.header("⚙️ 设置")

# 初始化 session state
if 'confirmed_symbol' not in st.session_state:
    st.session_state.confirmed_symbol = "600519"

if 'pending_symbol' not in st.session_state:
    st.session_state.pending_symbol = None

# 股票搜索函数
def search_stocks(searchterm: str, **kwargs) -> list:
    """搜索股票（用于 searchbox）

    Args:
        searchterm: 搜索词
        **kwargs: searchbox 传递的额外参数（如 rerun_delay），忽略即可
    """
    if not searchterm:
        # 返回最近查询的股票
        return history_manager.search("", limit=8)
    return search_service.search(searchterm)

# 股票代码搜索框
selected_result = st_searchbox(
    search_stocks,
    key="stock_searchbox",
    placeholder="输入股票代码...",
    label="股票代码",
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
    """,
    rerun_delay=200,  # 延迟 200ms，减少请求
    default_options=history_manager.search("", limit=8)  # 默认显示历史记录
)

# 如果用户选择了新的股票
if selected_result and selected_result != st.session_state.pending_symbol:
    st.session_state.pending_symbol = selected_result

    # 识别股票信息
    identified_market, identified_symbol = stock_identifier.identify(selected_result)

    # 使用 format_symbol 获得真正标准化的代码（用于去重）
    standardized_symbol = stock_identifier.format_symbol(identified_market, identified_symbol)

    # 更新确认的股票代码
    st.session_state.confirmed_symbol = standardized_symbol

    # 注意：历史记录将在数据查询成功后记录
    # 这里暂存待记录的信息（使用标准化代码作为键）
    st.session_state.pending_record = {
        'symbol': standardized_symbol,
        'market': MARKET_TYPE_MAP.get(identified_market, str(identified_market)),
        'original_input': selected_result
    }

# 使用确认的股票代码
user_input_symbol = st.session_state.confirmed_symbol

# 自动识别市场
identified_market, identified_symbol = stock_identifier.identify(user_input_symbol)

market = MARKET_TYPE_MAP[identified_market]
symbol = identified_symbol

# 标题（动态显示股票代码）
st.title(f"📊 股票质量分析 - {symbol}")
st.markdown("---")

# 查询年数选项：5、10、20、全部（None表示不限制）
years_options = {
    "5年": 5,
    "10年": 10,
    "20年": 20,
    "全部": None
}
years = st.sidebar.selectbox(
    "查询年数",
    options=list(years_options.keys()),
    index=1  # 默认选择"10年"
)
years = years_options[years]

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

    # 记录是否有组件成功渲染
    any_component_success = False

    for tab, group_name in zip(tabs, group_names):
        with tab:
            components = ANALYSIS_GROUPS[group_name]
            if not components:
                st.info("📭 该分类下暂无分析模块")
            else:
                for component in components:
                    success = component.render(symbol, market, years)
                    if success:
                        any_component_success = True

    # 如果有组件成功渲染，记录历史
    if any_component_success and 'pending_record' in st.session_state:
        record = st.session_state.pending_record
        search_service.record_query(
            symbol=record['symbol'],
            market=record['market'],
            original_input=record['original_input']
        )
        # 清除待记录信息
        del st.session_state.pending_record
else:
    # 只显示选中的组件
    for component in ANALYSIS_COMPONENTS:
        if component.title == selected_component:
            # 添加返回按钮
            if st.button("⬆️ 返回全部显示", key="back_to_all"):
                st.rerun()
            st.markdown("---")

            # 渲染该组件
            success = component.render(symbol, market, years)

            # 如果渲染成功，记录历史
            if success and 'pending_record' in st.session_state:
                record = st.session_state.pending_record
                search_service.record_query(
                    symbol=record['symbol'],
                    market=record['market'],
                    original_input=record['original_input']
                )
                # 清除待记录信息
                del st.session_state.pending_record

            break

