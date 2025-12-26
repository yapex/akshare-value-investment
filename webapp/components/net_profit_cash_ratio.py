"""
净利润现金比分析组件
"""

import traceback


class NetProfitCashRatioComponent:
    """净利润现金比分析组件"""

    title = "💰 利润是否为真（净现比）"

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

        from services.calculator import Calculator
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                NetProfitCashRatioComponent.title,
                help="""
                **净利润现金比（累计经营现金流 / 累计净利润）**

                **核心问题**：公司赚的利润，有没有真金白银到账？

                **计算公式：**
                - 净现比 = 累计经营性现金流量净额 ÷ 累计净利润

                **指标解读：**
                - **> 1.0**：优秀！利润质量高，全部利润都转化为现金，甚至更多
                - **0.8-1.0**：良好，大部分利润能转化为现金
                - **< 0.8**：警惕！大量利润被应收账款或存货占用，可能是"纸面富贵"

                **为什么用累计值？**
                单年波动大，累计能更真实反映长期盈利质量。

                **典型场景：**
                - 净现比持续 > 1：优质公司，如茅台、腾讯
                - 净现比持续 < 0.8：可能存在激进确认收入、大量赊销等问题
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的净利润现金比数据..."):
                try:
                    result = Calculator.calculate_net_profit_cash_ratio(symbol, market, years)
                    ratio_data, display_cols = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False
                ratio_data = ratio_data.sort_values("年份").reset_index(drop=True)

            # 创建双Y轴图表：净利润和经营现金流的对比
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 净利润现金比分析"]
            )

            # 添加净利润柱状图
            fig.add_trace(
                go.Bar(
                    x=ratio_data['年份'],
                    y=ratio_data['净利润'],
                    name='净利润',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加经营现金流柱状图
            fig.add_trace(
                go.Bar(
                    x=ratio_data['年份'],
                    y=ratio_data['经营性现金流量净额'],
                    name='经营现金流',
                    marker_color='lightgreen',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加净现比折线图（副Y轴）
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=ratio_data['净现比'],
                    name='净现比',
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )

            # 添加参考线（比率为0.8的合格线位置）- 使用Scatter确保在副Y轴
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=[0.8] * len(ratio_data['年份']),
                    mode='lines',
                    name='合格线 (0.8)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig.update_yaxes(title_text="金额", secondary_y=False)
            fig.update_yaxes(title_text="净现比", secondary_y=True)

            # 设置布局
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=500,
                barmode='group'
            )

            # 显示图表（使用动态key避免重复渲染时的冲突）
            chart_key = f"net_profit_cash_ratio_{symbol}_{market}"
            st.plotly_chart(fig, width='stretch', key=chart_key)

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            latest_ratio = ratio_data['净现比'].iloc[-1]
            latest_cumulative_net_profit = ratio_data['累计净利润'].iloc[-1]
            latest_cumulative_cashflow = ratio_data['累计经营性现金流量净额'].iloc[-1]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(label=f"{years}年累计净现比", value=f"{latest_ratio:.2f}", delta=None)

            with col2:
                st.metric(label="累计净利润", value=f"{latest_cumulative_net_profit:.2f}", delta=None)

            with col3:
                st.metric(label="累计经营现金流", value=f"{latest_cumulative_cashflow:.2f}", delta=None)

            # 折叠的原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(ratio_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"净利润现金比分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
