"""
营业收入增长分析组件
"""

import traceback


class RevenueGrowthComponent:
    """营业收入增长分析组件"""

    title = "📈 营收是否增长（成长性）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染营业收入增长分析组件

        Args:
            symbol: 股票代码
            market: 市场类型（A股/港股/美股）
            years: 查询年数

        Returns:
            bool: 是否成功渲染
        """
        # 延迟导入，优化启动性能
        import streamlit as st
        import pandas as pd
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        from services.calculators.revenue_growth import calculate as calculate_revenue_growth
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                RevenueGrowthComponent.title,
                help="""
                **营业收入增长趋势**

                **核心问题**：公司业务是否在持续扩张？

                **关键指标：**
                - **CAGR（复合年增长率）**：多年平均增长率，比单年增长率更稳定
                - **平均增长率**：各年增长率的算术平均
                - **最新增长率**：最近一年的增长情况

                **指标解读：**
                - **CAGR > 20%**：高成长！可能是优质成长股
                - **CAGR 10%-20%**：稳健增长，可持续性强
                - **CAGR < 10%**：增长缓慢，成熟期或遭遇瓶颈
                - **CAGR < 0%**：业务萎缩，需要警惕

                **重要提示：**
                - 关注增长的**可持续性**：连续多年增长 > 偶尔爆发
                - 对比**同行水平**：行业平均增长率很重要
                - 剔除**异常因素**：并购、一次性收益等

                **典型场景：**
                - 成长期公司：CAGR 持续 > 20%
                - 成熟期公司：CAGR 稳定在 5%-15%
                - 衰退期公司：CAGR 持续为负
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的营业收入数据..."):
                try:
                    revenue_data, metrics = calculate_revenue_growth(symbol, market, years)
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建双Y轴图表
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 营业收入趋势及增长率"]
            )

            # 添加柱状图（营业收入）- 计算器已统一返回"收入"字段
            fig.add_trace(
                go.Bar(
                    x=revenue_data['年份'],
                    y=revenue_data['收入'],
                    name="营业收入",
                    marker_color='green',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加折线图（增长率）
            fig.add_trace(
                go.Scatter(
                    x=revenue_data['年份'],
                    y=revenue_data['增长率'],
                    name='增长率',
                    mode='lines+markers',
                    line=dict(color='orange', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig.update_yaxes(title_text="营业收入", secondary_y=False)
            fig.update_yaxes(title_text="增长率 (%)", secondary_y=True)

            # 设置布局
            fig.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                barmode='group',
                height=500
            )

            # 显示图表
            st.plotly_chart(fig, width='stretch')

            # 显示关键指标
            st.markdown("---")
            st.subheader("📊 关键指标")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="年复合增长率 (CAGR)", value=f"{metrics['cagr']:.2f}%", delta=None)

            with col2:
                st.metric(label="平均增长率", value=f"{metrics['avg_growth_rate']:.2f}%", delta=None)

            with col3:
                st.metric(label="最新营业收入", value=f"{metrics['latest_revenue']:.2f}", delta=None)

            with col4:
                st.metric(label=f"{metrics['years_count']}年平均", value=f"{metrics['avg_revenue']:.2f}", delta=None)

            # 折叠的原始数据表格
            with st.expander("📊 查看原始数据"):
                display_data = revenue_data.copy()
                # 创建用于显示的副本，避免修改原始数据类型
                display_data = display_data.astype({
                    '增长率': 'str'
                })
                # 格式化增长率显示
                for idx in display_data.index:
                    growth_val = revenue_data.loc[idx, '增长率']
                    if pd.isna(growth_val):
                        display_data.loc[idx, '增长率'] = '-'
                    else:
                        display_data.loc[idx, '增长率'] = f"{growth_val:.2f}%"
                st.dataframe(display_data, width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"营业收入增长分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
