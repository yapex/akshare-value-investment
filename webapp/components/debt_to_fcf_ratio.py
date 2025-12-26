"""
有息债务与自由现金流比率分析组件
"""

import traceback


class DebtToFcfRatioComponent:
    """有息债务与自由现金流比率分析组件"""

    title = "💰 有息债务与自由现金流比率"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染有息债务与自由现金流比率分析组件

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

        from services.calculators.debt_to_fcf_ratio import calculate as calculate_dtf
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                DebtToFcfRatioComponent.title,
                help="""
                **有息债务与自由现金流比率（有息债务 ÷ 自由现金流）**

                **核心问题**：公司需要多少年才能用自由现金流还清债务？

                **什么是有息债务与自由现金流比率？**
                - 有息债务：需要支付利息的债务（借款、债券等）
                - 自由现金流：公司真正可自由支配的现金
                - 该比率衡量"用自由现金流偿还债务的能力"

                **计算公式：**
                - 有息债务与自由现金流比率 = 有息债务 ÷ 自由现金流

                **指标解读：**
                - **< 3倍**：优秀！用3年以内FCF可还清债务，偿债能力极强
                - **3-5倍**：良好，用5年以内FCF可还清债务
                - **5-10倍**：一般，需要较长时间才能还清债务
                - **> 10倍**：警惕！按当前FCF水平，还清债务需要10年以上

                **为什么这个指标很重要？**
                - 自由现金流是"真实可支配现金"，比利润更真实
                - 衡量公司"实际还债能力"，而非账面能力
                - 结合"有息债务权益比"更全面评估财务风险

                **特殊情况处理：**
                - 自由现金流为负：比率显示为空白，说明公司"烧钱"模式
                - 自由现金流波动大：关注FCF的稳定性

                **投资意义：**
                巴菲特强调：自由现金流是衡量公司"真实赚钱能力"的试金石。
                该比率告诉你：公司赚到的"真金白银"能否覆盖债务负担。
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的有息债务与自由现金流比率数据..."):
                try:
                    result = calculate_dtf(symbol, market, years)
                    ratio_data, display_cols, metrics = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建折线图
            fig = go.Figure()

            # 添加有息债务与自由现金流比率折线图
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=ratio_data['有息债务与自由现金流比率'],
                    name='有息债务与自由现金流比率',
                    mode='lines+markers',
                    line=dict(color='purple', width=3),
                    marker=dict(size=10),
                    hovertemplate='%{x}年<br/>比率: %{y:.2f}倍<extra></extra>'
                )
            )

            # 添加参考线（3倍健康线）
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=[3] * len(ratio_data['年份']),
                    mode='lines',
                    name='健康线 (3倍)',
                    line=dict(color='green', width=2, dash='dash'),
                    hoverinfo='skip'
                )
            )

            # 添加参考线（5倍警戒线）
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=[5] * len(ratio_data['年份']),
                    mode='lines',
                    name='警戒线 (5倍)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                )
            )

            # 添加参考线（10倍危险线）
            fig.add_trace(
                go.Scatter(
                    x=ratio_data['年份'],
                    y=[10] * len(ratio_data['年份']),
                    mode='lines',
                    name='危险线 (10倍)',
                    line=dict(color='red', width=2, dash='dash'),
                    hoverinfo='skip'
                )
            )

            # 设置布局
            fig.update_layout(
                title=f"{symbol} - 有息债务与自由现金流比率分析",
                xaxis_title="年份",
                yaxis_title="有息债务与自由现金流比率 (倍数)",
                hovermode="x unified",
                height=500,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )

            # 显示图表
            st.plotly_chart(fig, width='stretch')

            # 关键指标
            st.markdown("##### 📊 有息债务与自由现金流比率关键指标")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if metrics['avg_ratio'] is not None:
                    st.metric(
                        label=f"{years}年平均比率",
                        value=f"{metrics['avg_ratio']:.2f}倍",
                        delta=None,
                        help=f"最近{years}年平均有息债务与自由现金流比率"
                    )
                else:
                    st.metric(label=f"{years}年平均比率", value="N/A", delta=None)

            with col2:
                if metrics['latest_ratio'] is not None:
                    latest_ratio = metrics['latest_ratio']
                    delta_color = "normal" if latest_ratio <= 5 else "inverse"
                    st.metric(
                        label="最新比率",
                        value=f"{latest_ratio:.2f}倍",
                        delta=None,
                        help="最新年度的有息债务与自由现金流比率"
                    )
                else:
                    st.metric(label="最新比率", value="N/A", delta=None)

            with col3:
                if metrics['min_ratio'] is not None:
                    st.metric(
                        label="最低比率",
                        value=f"{metrics['min_ratio']:.2f}倍",
                        delta=None,
                        help=f"{years}年内最低有息债务与自由现金流比率"
                    )
                else:
                    st.metric(label="最低比率", value="N/A", delta=None)

            with col4:
                if metrics['max_ratio'] is not None:
                    st.metric(
                        label="最高比率",
                        value=f"{metrics['max_ratio']:.2f}倍",
                        delta=None,
                        help=f"{years}年内最高有息债务与自由现金流比率"
                    )
                else:
                    st.metric(label="最高比率", value="N/A", delta=None)

            # 绝对值指标
            st.markdown("##### 💰 债务与自由现金流规模")
            col5, col6, col7 = st.columns(3)

            with col5:
                if metrics['latest_debt'] is not None:
                    st.metric(
                        label="最新有息债务",
                        value=f"{metrics['latest_debt']:.2f}",
                        delta=None,
                        help="最新年度的有息债务总额"
                    )
                else:
                    st.metric(label="最新有息债务", value="N/A", delta=None)

            with col6:
                if metrics['latest_fcf'] is not None:
                    st.metric(
                        label="最新自由现金流",
                        value=f"{metrics['latest_fcf']:.2f}",
                        delta=None,
                        help="最新年度的自由现金流"
                    )
                else:
                    st.metric(label="最新自由现金流", value="N/A", delta=None)

            with col7:
                st.metric(
                    label="正FCF年数",
                    value=f"{metrics['positive_fcf_years']}/{metrics['total_years']}年",
                    delta=None,
                    help=f"最近{years}年内自由现金流为正的年份数"
                )

            # 折叠的原始数据表格
            st.markdown("---")
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(ratio_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"有息债务与自由现金流比率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
