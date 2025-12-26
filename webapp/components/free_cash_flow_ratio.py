"""
自由现金流净利润比分析组件
"""

import traceback


class FreeCashFlowRatioComponent:
    """自由现金流净利润比分析组件"""

    title = "💵 现金转化能力（自由现金流）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染自由现金流净利润比分析组件

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
                FreeCashFlowRatioComponent.title,
                help="""
                **自由现金流净利润比**

                **核心问题**：公司赚到钱后，还有多少可以自由支配？

                **什么是自由现金流？**
                自由现金流（FCF）= 经营性现金流量净额 - 资本支出
                - 这是公司**真正可以自由支配**的现金
                - 可用于分红、回购股票、偿还债务、投资扩张

                **计算公式：**
                - 自由现金流净利润比 = 自由现金流 ÷ 净利润

                **指标解读：**
                - **> 1.0**：优秀！公司不仅能将利润全部转化为现金，还有额外现金用于扩张、分红或回购
                - **0.8-1.0**：良好，利润质量较高，大部分利润能转化为真实现金
                - **< 0.8**：利润质量较差，大量利润被应收账款、存货占用，或资本支出过大

                **为什么比经营现金流更严格？**
                - 经营现金流：看"赚了多少现金"
                - 自由现金流：还要扣除"维持和扩张业务必须花的钱"
                - 更真实反映**股东能分到的钱**

                **典型场景：**
                - FCF比率 > 1：成熟优质公司（茅台、可口可乐）
                - FCF比率 0.5-1：快速扩张期公司（需要大量资本支出）
                - FCF比率持续 < 0.5：警惕！可能是"烧钱"模式

                **投资意义：**
                巴菲特最爱指标！自由现金流是公司"真实赚钱能力"的试金石。
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的自由现金流和投资强度数据..."):
                try:
                    # 获取自由现金流数据
                    fcf_result = Calculator.calculate_free_cash_flow_to_net_income_ratio(symbol, market, years)
                    fcf_data, fcf_display_cols, fcf_metrics = fcf_result
                    # 获取投资强度数据
                    inv_result = Calculator.calculate_investment_intensity_ratio(symbol, market, years)
                    inv_data, inv_display_cols, inv_metrics = inv_result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建2行1列的子图布局
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(
                    f"{symbol} - 自由现金流净利润比分析",
                    f"{symbol} - 投资强度比率分析"
                ),
                specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                vertical_spacing=0.12,
                shared_xaxes=True
            )

            # ========== 第一行：自由现金流净利润比图表 ==========

            # 添加净利润柱状图
            fig.add_trace(
                go.Bar(
                    x=fcf_data['年份'],
                    y=fcf_data['净利润'],
                    name='净利润',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                row=1, col=1, secondary_y=False
            )

            # 添加自由现金流柱状图
            fig.add_trace(
                go.Bar(
                    x=fcf_data['年份'],
                    y=fcf_data['自由现金流'],
                    name='自由现金流',
                    marker_color='lightgreen',
                    opacity=0.7
                ),
                row=1, col=1, secondary_y=False
            )

            # 添加自由现金流净利润比折线图（副Y轴）
            fig.add_trace(
                go.Scatter(
                    x=fcf_data['年份'],
                    y=fcf_data['自由现金流净利润比'],
                    name='自由现金流净利润比',
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=10)
                ),
                row=1, col=1, secondary_y=True
            )

            # 添加参考线（比率为0.8的合格线位置）
            fig.add_trace(
                go.Scatter(
                    x=fcf_data['年份'],
                    y=[0.8] * len(fcf_data['年份']),
                    mode='lines',
                    name='FCF合格线 (0.8)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                row=1, col=1, secondary_y=True
            )

            # 设置第一行Y轴标题
            fig.update_yaxes(title_text="金额", row=1, col=1, secondary_y=False)
            fig.update_yaxes(title_text="FCF净利润比", row=1, col=1, secondary_y=True)

            # ========== 第二行：投资强度比率图表 ==========

            # 添加资本支出柱状图
            fig.add_trace(
                go.Bar(
                    x=inv_data['年份'],
                    y=inv_data['资本支出'],
                    name='资本支出',
                    marker_color='lightcoral',
                    opacity=0.7
                ),
                row=2, col=1, secondary_y=False
            )

            # 添加折旧柱状图
            fig.add_trace(
                go.Bar(
                    x=inv_data['年份'],
                    y=inv_data['折旧'],
                    name='折旧',
                    marker_color='gold',
                    opacity=0.8
                ),
                row=2, col=1, secondary_y=False
            )

            # 添加投资强度比率折线图（副Y轴）
            fig.add_trace(
                go.Scatter(
                    x=inv_data['年份'],
                    y=inv_data['投资强度比率'],
                    name='投资强度比率',
                    mode='lines+markers',
                    line=dict(color='purple', width=3),
                    marker=dict(size=10)
                ),
                row=2, col=1, secondary_y=True
            )

            # 添加参考线（比率为100%的维护线位置）
            fig.add_trace(
                go.Scatter(
                    x=inv_data['年份'],
                    y=[100] * len(inv_data['年份']),
                    mode='lines',
                    name='维护线 (100%)',
                    line=dict(color='gray', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                row=2, col=1, secondary_y=True
            )

            # 设置第二行Y轴标题
            fig.update_yaxes(title_text="金额", row=2, col=1, secondary_y=False)
            fig.update_yaxes(title_text="投资强度比率(%)", row=2, col=1, secondary_y=True)

            # ========== 设置整体布局 ==========
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=900,
                barmode='group',
                showlegend=True
            )

            # 显示图表（使用动态key避免重复渲染时的冲突）
            chart_key = f"free_cash_flow_ratio_{symbol}_{market}"
            st.plotly_chart(fig, width='stretch', key=chart_key)

            # 显示自由现金流关键指标
            st.markdown("---")
            st.subheader("📊 自由现金流关键指标")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label=f"{years}年平均比率", value=f"{fcf_metrics['avg_ratio']:.2f}", delta=None)

            with col2:
                st.metric(label="最新比率", value=f"{fcf_metrics['latest_ratio']:.2f}", delta=None)

            with col3:
                st.metric(label="最低比率", value=f"{fcf_metrics['min_ratio']:.2f}", delta=None)

            with col4:
                st.metric(label="最高比率", value=f"{fcf_metrics['max_ratio']:.2f}", delta=None)

            # 显示投资强度关键指标
            st.markdown("---")
            st.subheader("🏗️ 投资强度关键指标")

            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.metric(label=f"{years}年平均比率", value=f"{inv_metrics['avg_ratio']:.2f}%", delta=None)

            with col6:
                st.metric(label="最新比率", value=f"{inv_metrics['latest_ratio']:.2f}%", delta=None)

            with col7:
                st.metric(label="累计资本支出", value=f"{inv_metrics['cumulative_capex']:.2f}", delta=None)

            with col8:
                st.metric(label="累计折旧", value=f"{inv_metrics['cumulative_depreciation']:.2f}", delta=None)

            # 显示辅助指标
            st.markdown("---")
            st.subheader("💡 自由现金流辅助指标")

            col9, col10, col11 = st.columns(3)

            with col9:
                st.metric(label="累计自由现金流", value=f"{fcf_metrics['cumulative_fcf']:.2f}", delta=None)

            with col10:
                st.metric(label="累计净利润", value=f"{fcf_metrics['cumulative_net_income']:.2f}", delta=None)

            with col11:
                cumulative_ratio = fcf_metrics['cumulative_fcf'] / fcf_metrics['cumulative_net_income'] if fcf_metrics['cumulative_net_income'] != 0 else 0
                st.metric(label="累计比率", value=f"{cumulative_ratio:.2f}", delta=None)

            # 折叠的原始数据表格
            st.markdown("---")
            with st.expander("📊 查看自由现金流计算用原始数据"):
                st.dataframe(fcf_data[fcf_display_cols], width='stretch', hide_index=True)

            with st.expander("📊 查看投资强度计算用原始数据"):
                st.dataframe(inv_data[inv_display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"自由现金流和投资强度分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
