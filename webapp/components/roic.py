"""
投入资本回报率（ROIC）分析组件
"""

import traceback


class ROICComponent:
    """投入资本回报率分析组件"""

    title = "💎 投入资本回报率（ROIC）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染投入资本回报率分析组件

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
                ROICComponent.title,
                help="""
                **投入资本回报率（ROIC = Return on Invested Capital）**

                **核心问题**：公司每投入一元钱能创造多少回报？

                **什么是ROIC？**
                ROIC = NOPAT（税后净营业利润）÷ 投入资本
                - 衡量公司资本使用效率的**核心指标**
                - 巴菲特最看重的指标之一
                - 比ROE更真实，排除了资本结构的影响

                **计算公式：**
                - NOPAT = EBIT × (1 - 税率)
                - 投入资本 = 股东权益（简化版）
                - ROIC = NOPAT ÷ 投入资本 × 100%

                **指标解读：**
                - **> 20%**：卓越！公司资本利用效率极高，护城河深厚
                - **15%-20%**：优秀，公司资本利用效率很高
                - **10%-15%**：良好，公司资本利用效率较好
                - **< 10%**：一般，资本利用效率较低

                **为什么ROIC比ROE更重要？**
                - ROE受杠杆影响，债务高会让ROE虚高
                - ROIC衡量的是**业务本身**的回报能力
                - 真正的价值创造者，ROIC > WACC（加权平均资本成本）

                **典型场景：**
                - 超高ROIC（>30%）：茅台、高端奢侈品、软件SaaS
                - 高ROIC（20-30%）：消费品牌、优质制造
                - 中等ROIC（10-20%）：一般制造业、服务业
                - 低ROIC（<10%）：竞争激烈行业、重资产行业

                **投资意义：**
                ROIC持续 > 15% 的公司，往往是长期投资的好标的！
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的ROIC数据..."):
                try:
                    result = Calculator.calculate_roic(symbol, market, years)
                    roic_data, display_cols, metrics = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建双Y轴图表
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 投入资本回报率分析"]
            )

            # 添加投入资本柱状图（主Y轴）- 想要显示在左边，需要先添加
            fig.add_trace(
                go.Bar(
                    x=roic_data['年份'],
                    y=roic_data['投入资本'],
                    name='投入资本',
                    marker_color='lightgreen',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加NOPAT柱状图（主Y轴）- 后添加显示在右边
            fig.add_trace(
                go.Bar(
                    x=roic_data['年份'],
                    y=roic_data['NOPAT'],
                    name='NOPAT（税后净营业利润）',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加ROIC折线图（副Y轴）
            fig.add_trace(
                go.Scatter(
                    x=roic_data['年份'],
                    y=roic_data['ROIC'],
                    name='ROIC',
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )

            # 添加参考线（15%优秀线）
            fig.add_trace(
                go.Scatter(
                    x=roic_data['年份'],
                    y=[15] * len(roic_data['年份']),
                    mode='lines',
                    name='优秀线 (15%)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig.update_yaxes(title_text="金额", secondary_y=False)
            fig.update_yaxes(title_text="ROIC (%)", secondary_y=True)

            # 设置布局
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=500,
                barmode='group',
                legend={'traceorder': 'normal'}
            )

            # 交换前两个柱状图的位置，使投入资本显示在左边
            # 获取所有traces
            traces = list(fig.data)
            # 交换第1和第2个trace（索引0和1）
            traces[0], traces[1] = traces[1], traces[0]
            # 重新赋值
            fig.data = tuple(traces)

            # 显示图表
            st.plotly_chart(fig, width='stretch')

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label=f"{years}年平均ROIC", value=f"{metrics['avg_roic']:.2f}%", delta=None)

            with col2:
                st.metric(label="最新ROIC", value=f"{metrics['latest_roic']:.2f}%", delta=None)

            with col3:
                st.metric(label="最低ROIC", value=f"{metrics['min_roic']:.2f}%", delta=None)

            with col4:
                st.metric(label="最高ROIC", value=f"{metrics['max_roic']:.2f}%", delta=None)

            # 显示辅助指标
            st.markdown("---")
            st.subheader("💡 辅助指标")

            col5, col6 = st.columns(2)

            with col5:
                st.metric(label="平均NOPAT", value=f"{metrics['avg_nopat']:.2f}", delta=None)

            with col6:
                st.metric(label="平均投入资本", value=f"{metrics['avg_capital']:.2f}", delta=None)

            # 折叠的原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(roic_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"投入资本回报率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
