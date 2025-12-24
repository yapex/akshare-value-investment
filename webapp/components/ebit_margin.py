"""
EBIT利润率分析组件
"""

import traceback


class EBITMarginComponent:
    """EBIT利润率分析组件"""

    title = "💰 EBIT利润率分析"

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

        import sys
        from pathlib import Path

        # 添加 src 目录到 Python 路径
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from services.calculator import Calculator

        try:
            st.markdown("---")
            st.subheader(EBITMarginComponent.title)

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的EBIT利润率数据..."):
                result = Calculator.calculate_ebit_margin(symbol, market, years)

                if result is None:
                    st.warning(f"无法获取股票 {symbol} 的EBIT利润率数据，可能该市场不支持此指标")
                    return False

                ebit_data, display_cols, metrics = result

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
            st.plotly_chart(fig, use_container_width=True)

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
                st.dataframe(ebit_data[display_cols], use_container_width=True, hide_index=True)

            return True

        except Exception as e:
            st.error(f"EBIT利润率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
