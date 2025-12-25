"""
有息债务权益比分析组件
"""

import traceback


class DebtToEquityComponent:
    """有息债务权益比分析组件"""

    title = "💳 有息债务权益比"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染有息债务权益比分析组件

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

        from services.calculator import Calculator
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                DebtToEquityComponent.title,
                help="""
                **有息债务权益比（有息债务 ÷ 股东权益 × 100%）**

                **核心问题**：公司的债务水平是否过高？偿债能力如何？

                **什么是有息债务？**
                有息债务 = 短期借款 + 长期借款 + 应付债券 + 一年内到期的非流动负债
                - 这些债务都需要支付利息
                - 是公司真正的"负债负担"

                **计算公式：**
                - 有息债务权益比 = 有息债务 ÷ 股东权益 × 100%

                **指标解读：**
                - **< 50%**：优秀！债务水平低，财务风险小
                - **50%-100%**：良好，债务水平适中
                - **> 100%**：警惕！债务总额超过股东权益，财务风险较高

                **为什么这个指标很重要？**
                - 衡量公司财务杠杆和偿债能力
                - 债务权益比过高意味着公司依赖借钱经营
                - 当债务超过股东权益时，债权人承担的风险大于股东

                **投资意义：**
                - 优质公司通常债务权益比 < 50%
                - 债务权益比持续 > 100% 的公司需要仔细评估风险
                - 行业特性影响：公用事业、金融业可接受较高比例
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的有息债务权益比数据..."):
                try:
                    result = Calculator.calculate_debt_to_equity(symbol, market, years)
                    debt_data, display_cols, metrics = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建折线图
            fig = go.Figure()

            # 添加有息债务权益比折线图
            fig.add_trace(
                go.Scatter(
                    x=debt_data['年份'],
                    y=debt_data['有息债务权益比'],
                    name='有息债务权益比',
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=10),
                    hovertemplate='%{x}年<br/>有息债务权益比: %{y:.2f}%<extra></extra>'
                )
            )

            # 添加参考线（100%警戒线）
            fig.add_trace(
                go.Scatter(
                    x=debt_data['年份'],
                    y=[100] * len(debt_data['年份']),
                    mode='lines',
                    name='警戒线 (100%)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                )
            )

            # 添加参考线（50%优秀线）
            fig.add_trace(
                go.Scatter(
                    x=debt_data['年份'],
                    y=[50] * len(debt_data['年份']),
                    mode='lines',
                    name='优秀线 (50%)',
                    line=dict(color='green', width=2, dash='dash'),
                    hoverinfo='skip'
                )
            )

            # 设置布局
            fig.update_layout(
                title=f"{symbol} - 有息债务权益比分析",
                xaxis_title="年份",
                yaxis_title="有息债务权益比 (%)",
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
            st.markdown("##### 📊 有息债务权益比关键指标")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label=f"{years}年平均有息债务权益比",
                    value=f"{metrics['avg_debt_to_equity']:.2f}%",
                    delta=None,
                    help=f"最近{years}年平均有息债务权益比"
                )

            with col2:
                latest_ratio = metrics['latest_debt_to_equity']
                delta_color = "normal" if latest_ratio <= 100 else "inverse"
                st.metric(
                    label="最新有息债务权益比",
                    value=f"{latest_ratio:.2f}%",
                    delta=None,
                    help="最新年度的有息债务权益比"
                )

            with col3:
                st.metric(
                    label="最低有息债务权益比",
                    value=f"{metrics['min_debt_to_equity']:.2f}%",
                    delta=None,
                    help=f"{years}年内最低有息债务权益比"
                )

            with col4:
                st.metric(
                    label="最高有息债务权益比",
                    value=f"{metrics['max_debt_to_equity']:.2f}%",
                    delta=None,
                    help=f"{years}年内最高有息债务权益比"
                )

            # 绝对值指标
            st.markdown("##### 💰 债务与权益规模")
            col5, col6 = st.columns(2)

            with col5:
                st.metric(
                    label="最新有息债务",
                    value=f"{metrics['latest_debt']:.2f}",
                    delta=None,
                    help="最新年度的有息债务总额"
                )

            with col6:
                st.metric(
                    label="最新股东权益",
                    value=f"{metrics['latest_equity']:.2f}",
                    delta=None,
                    help="最新年度的股东权益总额"
                )

            # 折叠的原始数据表格
            st.markdown("---")
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(debt_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"有息债务权益比分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
