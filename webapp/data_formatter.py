"""
数据格式化模块

处理财务数据的格式化和转换
"""

import pandas as pd
import streamlit as st
from typing import Dict, List


def format_financial_data(df: pd.DataFrame, report_type: str) -> pd.DataFrame:
    """
    格式化财务数据为窄表格式

    Args:
        df: 原始数据DataFrame
        report_type: 报表类型

    Returns:
        格式化后的DataFrame（窄表格式：年份为列，字段为行）
    """
    if df.empty:
        return df

    df_formatted = df.copy()

    # 识别日期列
    date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
    date_col = None
    for col in date_columns:
        if col in df_formatted.columns:
            date_col = col
            break

    if date_col is None:
        return df_formatted

    # 确保日期列为datetime类型
    df_formatted[date_col] = pd.to_datetime(df_formatted[date_col])

    # 提取年份作为列名
    df_formatted['年份'] = df_formatted[date_col].dt.year

    # 按年份降序排列（最新的年份在前）
    df_formatted = df_formatted.sort_values('年份', ascending=False)

    # 获取唯一的年份，按降序排列
    years = sorted(df_formatted['年份'].unique(), reverse=True)

    # 移除日期列和年份列，获取指标列
    indicator_cols = [col for col in df_formatted.columns
                     if col not in [date_col, '年份'] and col not in date_columns]

    # 创建窄表格式
    result_data = []

    for indicator in indicator_cols:
        # 跳过说明性行，只处理实际数据
        if indicator == '报表核心指标':
            continue

        row_data = {'指标名称': indicator}
        for year in years:
            year_data = df_formatted[df_formatted['年份'] == year]
            if not year_data.empty:
                value = year_data[indicator].iloc[0] if len(year_data) > 0 else None
                # 转换为百万元
                if pd.notna(value) and isinstance(value, (int, float)):
                    value = value / 1_000_000
                row_data[str(year)] = value
            else:
                row_data[str(year)] = None
        result_data.append(row_data)

    # 创建新的DataFrame
    narrow_df = pd.DataFrame(result_data)

    # 重新排列列：指标名称 + 年份列
    year_columns = [str(year) for year in years]
    column_order = ['指标名称'] + year_columns
    narrow_df = narrow_df[column_order]

    return narrow_df


def create_styler(df: pd.DataFrame) -> pd.DataFrame.style:
    """
    创建样式化的DataFrame

    Args:
        df: 要样式化的DataFrame

    Returns:
        样式化的DataFrame
    """
    def _format_values(x):
        if pd.isna(x):
            return "N/A"
        elif isinstance(x, (int, float)):
            return f"{x:,.2f}"
        else:
            return x

    def _highlight_row(row):
        if row.name % 2 == 0:
            return ['background-color: #f8f9fa'] * len(row)
        else:
            return ['background-color: white'] * len(row)

    # 创建样式化对象
    styler = df.style

    # 应用数值格式化
    for col in df.columns:
        if col not in ['指标名称', '单位']:
            styler = styler.format({col: _format_values})

    # 应用行样式
    styler = styler.apply(_highlight_row, axis=1)

    # 设置表格样式
    styler = styler.set_properties(**{
        'text-align': 'right',
        'padding': '8px',
        'border': '1px solid #dddddd',
        'color': '#000000',
        'font-size': '14px'
    })

    # 设置指标名称列左对齐
    styler = styler.set_properties(subset=['指标名称'], **{
        'text-align': 'left',
        'font-weight': 'bold',
        'color': '#1f77b4'
    })

    # 设置表格样式
    styler = styler.set_table_styles([
        {
            'selector': 'thead th',
            'props': [
                ('background-color', '#f0f2f6'),
                ('font-weight', 'bold'),
                ('text-align', 'center'),
                ('padding', '8px'),
                ('border', '1px solid #dddddd'),
                ('color', '#333333'),
                ('font-size', '14px')
            ]
        },
        {
            'selector': 'tbody tr:hover',
            'props': [
                ('background-color', '#f5f5f5'),
                ('color', '#000000')
            ]
        },
        {
            'selector': 'td',
            'props': [
                ('border-bottom', '1px solid #eeeeee')
            ]
        }
    ])

    return styler


def display_metrics_section(df: pd.DataFrame) -> None:
    """
    显示指标摘要部分

    Args:
        df: 数据DataFrame
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        data_points = len(df)
        st.metric("数据点数", data_points)

    with col2:
        if not df.empty:
            # 尝试获取最新的报告期
            date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
            latest_date = "N/A"
            for date_col in date_columns:
                if date_col in df.columns:
                    try:
                        latest_date_raw = df[date_col].iloc[0]
                        if pd.notna(latest_date_raw):
                            if pd.api.types.is_datetime64_any_dtype(df[date_col]):
                                latest_date = pd.to_datetime(latest_date_raw).strftime('%Y-%m-%d')
                            else:
                                latest_date = str(latest_date_raw)
                        break
                    except:
                        latest_date = latest_date_raw
                        break
            st.metric("最新报告期", latest_date)

    with col3:
        if not df.empty:
            # 计算数据完整性
            total_cells = len(df) * len(df.columns)
            non_null_cells = df.count().sum()
            completeness = (non_null_cells / total_cells) * 100
            st.metric("数据完整性", f"{completeness:.1f}%")