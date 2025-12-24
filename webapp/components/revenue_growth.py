"""
营业收入增长分析组件
"""

import traceback


class RevenueGrowthComponent:
    """营业收入增长分析组件"""

    title = "📈 营业收入增长趋势分析"

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
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        import sys
        from pathlib import Path

        # 添加 src 目录到 Python 路径
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from services.calculator import Calculator

        try:
            st.markdown("---")
            st.subheader(RevenueGrowthComponent.title)

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的营业收入数据..."):
                result = Calculator.calculate_revenue_growth(symbol, market, years)

                if result is None:
                    st.error(f"无法获取股票 {symbol} 的营业收入数据")
                    return False

                revenue_data, metrics = result

            # 获取收入字段名称（用于显示）
            if market == "A股":
                revenue_col = "其中：营业收入"
            elif market == "港股":
                revenue_col = "营业额"
            else:  # 美股
                revenue_col = "营业收入"

            # 创建双Y轴图表
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 营业收入趋势及增长率"]
            )

            # 添加柱状图（营业收入）
            fig.add_trace(
                go.Bar(
                    x=revenue_data['年份'],
                    y=revenue_data[revenue_col],
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
            st.plotly_chart(fig, use_container_width=True)

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
                display_data['增长率'] = display_data['增长率'].round(2)
                display_data.loc[display_data['增长率'].isna(), '增长率'] = '-'
                st.dataframe(display_data, use_container_width=True, hide_index=True)

            return True

        except Exception as e:
            st.error(f"营业收入增长分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
