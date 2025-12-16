"""
图表工具模块

处理Plotly图表的生成和配置
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from typing import List, Optional


def create_financial_chart(indicator_name: str, formatted_df: pd.DataFrame, report_type: str) -> None:
    """
    为指定指标创建财务分析图表

    Args:
        indicator_name: 指标名称
        formatted_df: 格式化后的数据DataFrame
        report_type: 报表类型
    """
    # 查找指标数据
    indicator_row = formatted_df[formatted_df['指标名称'] == indicator_name]

    if indicator_row.empty:
        st.warning(f"未找到指标: {indicator_name}")
        return

    # 获取年份列（排除非数值列）
    year_columns = [col for col in formatted_df.columns if col not in ['指标名称', '单位']]

    if not year_columns:
        st.warning("没有找到年份数据")
        return

    # 按年份排序（从旧到新）
    year_columns_sorted = sorted(year_columns, key=lambda x: int(x.replace('-', '')))

    # 提取数值数据
    values = []
    years = []

    for year in year_columns_sorted:
        if len(indicator_row) > 0:
            value = indicator_row[year].iloc[0]

            # 数据解析逻辑
            if pd.notna(value):
                try:
                    if isinstance(value, str):
                        clean_value = str(value).replace(',', '').replace('，', '').replace('%', '').strip()
                        if clean_value in ['', '-', '--']:
                            raise ValueError("空字符串或占位符")
                        numeric_value = float(clean_value)
                    else:
                        numeric_value = float(value)

                    values.append(numeric_value)
                    years.append(year)
                except (ValueError, TypeError):
                    if isinstance(value, str):
                        try:
                            import re
                            numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', value)
                            if numbers:
                                numeric_value = float(numbers[0])
                                values.append(numeric_value)
                                years.append(year)
                        except:
                            pass

    if not values:
        st.warning(f"该指标 '{indicator_name}' 没有有效的数值数据")
        return

    # 创建图表
    _create_dual_axis_chart(indicator_name, years, values)

    # 显示数据表格
    _show_data_table(indicator_name, years, values)


def _create_dual_axis_chart(indicator_name: str, years: List[str], values: List[float]) -> None:
    """
    创建双Y轴图表（柱状图+折线图）

    Args:
        indicator_name: 指标名称
        years: 年份列表
        values: 数值列表
    """
    fig = go.Figure()

    # 柱状图 - 显示数值
    fig.add_trace(
        go.Bar(
            x=years,
            y=values,
            name='历史数值 (百万元)',
            marker=dict(
                color='lightblue',
                line=dict(color='darkblue', width=1)
            ),
            text=[f'{v:,.0f}' for v in values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>数值: %{y:,.2f} 百万元<extra></extra>',
            textfont=dict(size=12, color='#000000'),
            yaxis='y'
        )
    )

    # 折线图 - 显示增长率
    if len(values) > 1:
        growth_rates = [None]  # 第一年没有增长率
        growth_years = [years[0]]

        for i in range(1, len(values)):
            if values[i-1] != 0:
                growth_rate = ((values[i] - values[i-1]) / values[i-1]) * 100
                growth_rates.append(growth_rate)
                growth_years.append(years[i])
            else:
                growth_rates.append(None)
                growth_years.append(years[i])

        # 添加增长率折线到第二Y轴
        fig.add_trace(
            go.Scatter(
                x=growth_years,
                y=growth_rates,
                mode='lines+markers',
                name='同比增长率 (%)',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(
                    size=8,
                    color='#FF6B6B',
                    line=dict(color='darkred', width=1)
                ),
                text=[f'{gr:.1f}%' if gr is not None else 'N/A' for gr in growth_rates],
                textposition='top center',
                textfont=dict(size=12, color='#CC0000', weight='bold'),
                hovertemplate='<b>%{x}</b><br>增长率: %{y:.2f}%<extra></extra>',
                yaxis='y2'
            )
        )

    # 更新布局
    fig.update_layout(
        height=500,
        title=dict(
            text=f'<b>{indicator_name}</b> 财务指标分析',
            x=0.5,
            font=dict(size=16, color='#2c3e50')
        ),
        showlegend=True,
        hovermode='x unified',
        margin=dict(t=80, b=40, l=60, r=60),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            font=dict(size=12, color="black")
        ),
        yaxis=dict(
            title=dict(text="数值 (百万元)", font=dict(color='#003366', size=14)),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            linecolor='black',
            linewidth=1,
            tickformat=",.0f",
            tickfont=dict(color='black', size=12),
            side='left'
        ),
        yaxis2=dict(
            title=dict(text="增长率 (%)", font=dict(color='#CC0000', size=14)),
            showgrid=False,
            linecolor='black',
            linewidth=1,
            tickformat=".1f",
            tickfont=dict(color='black', size=12),
            overlaying='y',
            side='right',
            zeroline=True,
            zerolinecolor="gray",
            zerolinewidth=2
        ),
        xaxis=dict(
            title=dict(text="年份", font=dict(color='#003366', size=14)),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            linecolor='black',
            linewidth=1,
            tickfont=dict(color='black', size=12)
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})


def _show_data_table(indicator_name: str, years: List[str], values: List[float]) -> None:
    """
    显示数据明细表格

    Args:
        indicator_name: 指标名称
        years: 年份列表
        values: 数值列表
    """
    st.subheader(f"📊 {indicator_name} 数据明细")

    # 创建数据摘要表
    summary_data = []
    for i, (year, value) in enumerate(zip(years, values)):
        growth_rate = None
        if i > 0 and values[i-1] != 0:
            growth_rate = ((value - values[i-1]) / values[i-1]) * 100

        summary_data.append({
            '年份': year,
            '数值 (百万元)': f"{value:,.2f}",
            '同比增长率 (%)': f"{growth_rate:.2f}%" if growth_rate is not None else "N/A"
        })

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # 显示统计信息
    if len(values) > 1:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # 计算年化增长率 (CAGR)
            start_value = values[0]   # 最早的值
            end_value = values[-1]   # 最新的值
            years_count = len(values) - 1

            
            if start_value > 0 and years_count > 0:
                cagr = ((end_value / start_value) ** (1/years_count) - 1) * 100
                st.metric("年化增长率", f"{cagr:.2f}%")
            else:
                st.metric("年化增长率", "N/A")

        with col2:
            avg_value = sum(values) / len(values)
            st.metric("平均值", f"{avg_value:,.2f} 百万元")

        with col3:
            max_value = max(values)
            max_year = years[values.index(max_value)]
            st.metric("最高值", f"{max_value:,.2f} 百万元", f"年份: {max_year}")

        with col4:
            min_value = min(values)
            min_year = years[values.index(min_value)]
            st.metric("最低值", f"{min_value:,.2f} 百万元", f"年份: {min_year}")