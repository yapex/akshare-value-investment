"""
EBIT利润率分析组件
"""

import traceback


class EBITMarginComponent:
    """EBIT利润率分析组件"""

    title = "💰 盈利能力如何（EBIT利润率）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染EBIT利润率分析组件

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
                EBITMarginComponent.title,
                help="""
                **EBIT利润率（息税前利润率）**

                **核心问题**：公司的核心业务赚钱能力如何？

                **什么是EBIT？**
                EBIT = Earnings Before Interest and Taxes（息税前利润）
                - 排除了财务杠杆（利息）和税收政策的影响
                - 更纯粹地反映**核心业务**的盈利能力

                **计算公式：**
                - A股：EBIT = 净利润 + 所得税费用 + 利息费用
                - 港股：EBIT = 除税前溢利
                - 美股：EBIT = 持续经营税前利润
                - EBIT利润率 = EIT ÷ 营业收入 × 100%

                **指标解读：**
                - **> 25%**：优秀！拥有极强的定价权和垄断优势（如茅台）
                - **15%-25%**：良好，竞争力较强
                - **10%-15%**：一般，竞争激烈或成本压力大
                - **< 10%**：较低，可能处于红海竞争

                **为什么看EBIT而非净利润？**
                - 净利润受资本结构影响（杠杆高的公司净利润低）
                - EBIT更真实反映**商业模式**的盈利能力
                - 便于跨公司、跨行业比较

                **典型场景：**
                - 高利润率（>25%）：茅台、奢侈品、软件SaaS
                - 中等利润率（15-20%）：消费品牌、高端制造
                - 低利润率（<10%）：零售、餐饮、传统制造

                **注意：**利润率不是越高越好，要结合**周转率**看ROE
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的EBIT利润率数据..."):
                try:
                    result = Calculator.calculate_ebit_margin(symbol, market, years)
                    ebit_data, display_cols, metrics = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建双Y轴图表
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - EBIT利润率趋势"]
            )

            # 添加柱状图（EBIT利润率）
            fig.add_trace(
                go.Bar(
                    x=ebit_data['年份'],
                    y=ebit_data['EBIT利润率'],
                    name="EBIT利润率 (%)",
                    marker_color='purple',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加折线图（增长率）
            fig.add_trace(
                go.Scatter(
                    x=ebit_data['年份'],
                    y=ebit_data['利润率增长率'],
                    name='增长率',
                    mode='lines+markers',
                    line=dict(color='red', width=2),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )

            # 添加25%优秀线
            fig.add_hline(
                y=25, line_dash="dash", line_color="green",
                annotation_text="优秀 (25%)", annotation_position="right",
                secondary_y=False
            )

            # 设置Y轴标题
            fig.update_yaxes(title_text="EBIT利润率 (%)", secondary_y=False)
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
                st.metric(label="平均利润率", value=f"{metrics['avg_margin']:.2f}%", delta=None)

            with col2:
                st.metric(label="最新利润率", value=f"{metrics['latest_margin']:.2f}%", delta=None)

            with col3:
                st.metric(label=f"{years}年最高", value=f"{metrics['max_margin']:.2f}%", delta=None)

            with col4:
                st.metric(label=f"{years}年最低", value=f"{metrics['min_margin']:.2f}%", delta=None)

            # 折叠的计算用原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(ebit_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"EBIT利润率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
