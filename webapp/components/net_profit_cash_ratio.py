"""
净利润现金比分析组件
"""

from typing import Tuple, List
import traceback


class NetProfitCashRatioComponent:
    """净利润现金比分析组件"""

    title = "💰 净利润现金比分析（利润质量）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染净利润现金比分析组件

        Args:
            symbol: 股票代码
            market: 市场类型（A股/港股/美股）
            years: 查询年数

        Returns:
            bool: 是否成功渲染
        """
        # 延迟导入，优化启动性能
        import streamlit as st
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        import sys
        from pathlib import Path

        # 添加 src 目录到 Python 路径
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from services.calculator import Calculator

        try:
            st.markdown("---")
            st.subheader(NetProfitCashRatioComponent.title)

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的净利润现金比数据..."):
                result = Calculator.calculate_net_profit_cash_ratio(symbol, market, years)

                if result is None:
                    st.error(f"无法获取股票 {symbol} 的净利润现金比数据")
                    return False

                ratio_data, display_cols = result
                ratio_data = ratio_data.sort_values("年份").reset_index(drop=True)

            # 创建双Y轴图表：两条折线分别展示累计净利润和累计经营现金流
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 累计净利润 vs 累计经营现金流"]
            )

            # 添加折线图（累计净利润）
            fig.add_trace(
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
            fig.add_trace(
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
            fig.update_yaxes(title_text="累计净利润", secondary_y=False)
            fig.update_yaxes(title_text="累计经营现金流", secondary_y=True)

            # 设置布局
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=500
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)

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

            return True

        except Exception as e:
            st.error(f"净利润现金比分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
