"""
净资产收益率（ROE）分析组件
"""

import traceback


class ROEComponent:
    """净资产收益率分析组件"""

    title = "💰 净资产收益率（ROE）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染净资产收益率分析组件

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
        import pandas as pd

        from services.calculators.roe import calculate as calculate_roe
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                ROEComponent.title,
                help="""
                **净资产收益率（ROE = Return on Equity）**

                **核心问题**：公司每使用一元钱股东权益能创造多少净利润？

                **什么是ROE？**
                ROE = 净利润 ÷ 股东权益 × 100%
                - 衡量公司**股东资金回报率**的核心指标
                - 巴菲特最看重的指标之一
                - 直接反映公司为股东创造价值的能力

                **杜邦分析三要素：**
                ROE = 净利润率 × 总资产周转率 × 权益乘数
                - **净利润率**：每单位收入的盈利能力（盈利能力）
                - **总资产周转率**：资产利用效率（营运能力）
                - **权益乘数**：财务杠杆水平（偿债能力）

                **指标解读：**
                - **> 20%**：卓越！公司股东回报率极高，护城河深厚
                - **15%-20%**：优秀，公司股东回报率很高
                - **10%-15%**：良好，公司股东回报率较好
                - **< 10%**：一般，股东回报率较低

                **ROE vs ROIC：**
                - ROE：看股东能拿到的回报（受杠杆影响）
                - ROIC：看公司业务的回报能力（排除资本结构影响）
                - 优秀公司通常ROE > ROIC（正杠杆效应）

                **典型场景：**
                - 超高ROE（>30%）：高端白酒、奢侈品、软件SaaS
                - 高ROE（20-30%）：消费品牌、优质制造
                - 中等ROE（10-20%）：一般制造业、服务业
                - 低ROE（<10%）：竞争激烈行业、重资产行业

                **投资意义：**
                ROE持续 > 15% 的公司，往往是长期投资的好标的！
                但要警惕高ROE背后的高风险（高杠杆、周期性等）。
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的ROE和杜邦分析数据..."):
                try:
                    # 获取ROE和杜邦分析数据
                    roe_data, dupont_data = calculate_roe(symbol, market, years)
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建2行1列的子图布局
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(
                    f"{symbol} - 净资产收益率分析",
                    f"{symbol} - 杜邦分析三要素"
                ),
                specs=[[{"secondary_y": False}], [{"secondary_y": True}]],
                vertical_spacing=0.12,
                shared_xaxes=True
            )

            # ========== 第1行：ROE柱状图 ==========

            # 添加ROE柱状图
            fig.add_trace(
                go.Bar(
                    x=roe_data['年份'],
                    y=roe_data['ROE'],
                    name='ROE',
                    marker_color='steelblue',
                    opacity=0.7,
                    text=roe_data['ROE'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else ""),
                    textposition='outside'
                ),
                row=1, col=1
            )

            # 添加15%优秀线
            fig.add_trace(
                go.Scatter(
                    x=roe_data['年份'],
                    y=[15] * len(roe_data['年份']),
                    mode='lines',
                    name='优秀线 (15%)',
                    line=dict(color='green', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                row=1, col=1
            )

            # 添加20%卓越线
            fig.add_trace(
                go.Scatter(
                    x=roe_data['年份'],
                    y=[20] * len(roe_data['年份']),
                    mode='lines',
                    name='卓越线 (20%)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                row=1, col=1
            )

            # 设置第1行Y轴标题
            fig.update_yaxes(title_text="ROE (%)", row=1, col=1)

            # ========== 第2行：杜邦分析三要素 ==========

            # 添加净利润率折线图（左Y轴）
            fig.add_trace(
                go.Scatter(
                    x=dupont_data['年份'],
                    y=dupont_data['净利润率'],
                    name='净利润率',
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ),
                row=2, col=1, secondary_y=False
            )

            # 添加总资产周转率折线图（右Y轴）
            fig.add_trace(
                go.Scatter(
                    x=dupont_data['年份'],
                    y=dupont_data['总资产周转率'],
                    name='总资产周转率',
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8)
                ),
                row=2, col=1, secondary_y=True
            )

            # 添加权益乘数折线图（右Y轴）
            fig.add_trace(
                go.Scatter(
                    x=dupont_data['年份'],
                    y=dupont_data['权益乘数'],
                    name='权益乘数',
                    mode='lines+markers',
                    line=dict(color='green', width=2),
                    marker=dict(size=8)
                ),
                row=2, col=1, secondary_y=True
            )

            # 设置第2行Y轴标题
            fig.update_yaxes(title_text="净利润率 (%)", row=2, col=1, secondary_y=False)
            fig.update_yaxes(title_text="周转率 / 权益乘数", row=2, col=1, secondary_y=True)

            # ========== 设置整体布局 ==========
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=900,
                showlegend=True
            )

            # 显示图表
            st.plotly_chart(fig, width='stretch')

            # 显示ROE关键指标
            st.markdown("---")
            st.subheader("📊 ROE关键指标")

            avg_roe = roe_data['ROE'].mean()
            latest_roe = roe_data['ROE'].iloc[-1]
            min_roe = roe_data['ROE'].min()
            max_roe = roe_data['ROE'].max()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label=f"{years}年平均ROE", value=f"{avg_roe:.2f}%", delta=None)

            with col2:
                st.metric(label="最新ROE", value=f"{latest_roe:.2f}%", delta=None)

            with col3:
                st.metric(label="最低ROE", value=f"{min_roe:.2f}%", delta=None)

            with col4:
                st.metric(label="最高ROE", value=f"{max_roe:.2f}%", delta=None)

            # 显示杜邦分析关键指标
            st.markdown("---")
            st.subheader("🔍 杜邦分析三要素")

            avg_npm = dupont_data['净利润率'].mean()
            avg_at = dupont_data['总资产周转率'].mean()
            avg_em = dupont_data['权益乘数'].mean()

            col5, col6, col7 = st.columns(3)

            with col5:
                st.metric(
                    label="平均净利润率",
                    value=f"{avg_npm:.2f}%",
                    delta=None,
                    help="盈利能力：每单位收入的盈利水平"
                )

            with col6:
                st.metric(
                    label="平均资产周转率",
                    value=f"{avg_at:.2f}",
                    delta=None,
                    help="营运能力：资产利用效率"
                )

            with col7:
                st.metric(
                    label="平均权益乘数",
                    value=f"{avg_em:.2f}",
                    delta=None,
                    help="财务杠杆：权益乘数越高，杠杆越大"
                )

            # ROE评价
            st.markdown("---")
            st.subheader("🎯 综合评价")

            if avg_roe >= 20:
                level = "卓越"
                color = "🟢"
                comment = "公司股东回报率极高，具有深厚护城河"
            elif avg_roe >= 15:
                level = "优秀"
                color = "🟢"
                comment = "公司股东回报率很高，为股东创造良好回报"
            elif avg_roe >= 10:
                level = "良好"
                color = "🟡"
                comment = "公司股东回报率较好，但仍有提升空间"
            else:
                level = "一般"
                color = "🔴"
                comment = "公司股东回报率较低，需要关注盈利能力"

            st.info(f"{color} **{level}**：{comment}")

            # 杜邦分析驱动因素
            st.markdown("---")
            st.subheader("📈 杜邦驱动因素分析")

            latest_npm = dupont_data['净利润率'].iloc[-1]
            latest_at = dupont_data['总资产周转率'].iloc[-1]
            latest_em = dupont_data['权益乘数'].iloc[-1]

            # 判断主要驱动因素
            drivers = []
            if latest_npm > avg_npm * 1.1:
                drivers.append("✅ 净利润率提升（盈利能力改善）")
            elif latest_npm < avg_npm * 0.9:
                drivers.append("⚠️ 净利润率下降（盈利能力恶化）")

            if latest_at > avg_at * 1.1:
                drivers.append("✅ 资产周转率提升（营运效率改善）")
            elif latest_at < avg_at * 0.9:
                drivers.append("⚠️ 资产周转率下降（营运效率恶化）")

            if latest_em > avg_em * 1.1:
                drivers.append("⚠️ 权益乘数上升（杠杆增加）")
            elif latest_em < avg_em * 0.9:
                drivers.append("✅ 权益乘数下降（杠杆降低）")

            if drivers:
                for driver in drivers:
                    st.markdown(f"- {driver}")
            else:
                st.markdown("- 各项指标保持稳定")

            # 折叠的原始数据表格
            st.markdown("---")
            with st.expander("📊 查看ROE计算用原始数据"):
                display_df = roe_data[['年份', 'ROE']].copy()
                display_df['ROE'] = display_df['ROE'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
                st.dataframe(display_df, width='stretch', hide_index=True)

            with st.expander("📊 查看杜邦分析原始数据"):
                display_dupont = dupont_data[['年份', '净利润率', '总资产周转率', '权益乘数']].copy()
                display_dupont['净利润率'] = display_dupont['净利润率'].apply(lambda x: f"{x:.2f}%")
                display_dupont['总资产周转率'] = display_dupont['总资产周转率'].apply(lambda x: f"{x:.2f}")
                display_dupont['权益乘数'] = display_dupont['权益乘数'].apply(lambda x: f"{x:.2f}")
                st.dataframe(display_dupont, width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"净资产收益率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
