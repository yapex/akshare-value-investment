"""
A股财务报表Streamlit应用

四大财务报表（指标、资产负债、利润、现金流）合并展示
支持窄表形式，财务格式显示，小数点后2位，百万元单位
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import streamlit as st
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class FinancialReportApp:
    """财务报表应用主类"""

    def __init__(self):
        """初始化应用"""
        self.api_base_url = "http://localhost:8000"
        self.setup_page_config()

    def setup_page_config(self):
        """配置页面设置"""
        st.set_page_config(
            page_title="A股财务报表分析",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def query_financial_data_via_api(self, market: str, query_type: str, symbol: str,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> pd.DataFrame:
        """
        通过FastAPI查询财务数据

        Args:
            market: 市场类型
            query_type: 查询类型
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame格式的财务数据
        """
        try:
            request_data = {
                "market": market,
                "query_type": query_type,
                "symbol": symbol,
                "frequency": "annual"
            }

            if start_date:
                request_data["start_date"] = start_date
            if end_date:
                request_data["end_date"] = end_date

            response = requests.post(
                f"{self.api_base_url}/api/v1/financial/query",
                json=request_data,
                timeout=30
            )

            if response.status_code == 200:
                api_response = response.json()
                if api_response.get("status") == "success":
                    data = api_response.get("data", {})
                    if isinstance(data, dict) and "records" in data:
                        return pd.DataFrame(data["records"])
                else:
                    st.error(f"API查询失败: {api_response.get('message', '未知错误')}")
            else:
                st.error(f"API请求失败: HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("无法连接到FastAPI服务，请确保API服务正在运行 (http://localhost:8000)")
        except Exception as e:
            st.error(f"查询数据失败: {str(e)}")

        return pd.DataFrame()

    def get_financial_data(self, symbol: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        获取四大财务报表数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含四大报表的字典
        """
        try:
            data = {}

            with st.spinner("正在获取财务指标数据..."):
                data['indicators'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_indicators", symbol, start_date, end_date
                )

            with st.spinner("正在获取资产负债表数据..."):
                data['balance_sheet'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_balance_sheet", symbol, start_date, end_date
                )

            with st.spinner("正在获取利润表数据..."):
                data['income_statement'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_income_statement", symbol, start_date, end_date
                )

            with st.spinner("正在获取现金流量表数据..."):
                data['cash_flow'] = self.query_financial_data_via_api(
                    "a_stock", "a_stock_cash_flow", symbol, start_date, end_date
                )

            return data

        except Exception as e:
            st.error(f"获取数据失败: {str(e)}")
            return {}

    def format_financial_data(self, df: pd.DataFrame, report_type: str) -> pd.DataFrame:
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

    def create_charts_for_indicator(self, indicator_name: str, formatted_df: pd.DataFrame, report_type: str):
        """
        为选定的指标创建图表

        Args:
            indicator_name: 指标名称
            formatted_df: 格式化后的DataFrame
            report_type: 报表类型
        """
        try:
            if formatted_df.empty:
                st.warning("没有数据可用于生成图表")
                return

            # 提取该指标的数据行
            indicator_row = formatted_df[formatted_df['指标名称'] == indicator_name]

            if indicator_row.empty:
                st.warning(f"未找到指标 '{indicator_name}' 的数据")
                return

            # 获取年份列（排除指标名称列）
            year_columns = [col for col in formatted_df.columns
                           if col != '指标名称' and col.replace('-', '').isdigit()]

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

                    # 更宽松的数值检查
                    if pd.notna(value):
                        try:
                            # 处理各种格式的数据
                            if isinstance(value, str):
                                # 移除常见的格式字符
                                clean_value = str(value).replace(',', '').replace('，', '').replace('%', '').strip()
                                if clean_value == '' or clean_value == '-' or clean_value == '--':
                                    raise ValueError("空字符串或占位符")
                                numeric_value = float(clean_value)
                            else:
                                numeric_value = float(value)

                            values.append(numeric_value)
                            years.append(year)
                        except (ValueError, TypeError):
                            # 如果是字符串，尝试更复杂的解析
                            if isinstance(value, str):
                                try:
                                    import re
                                    # 尝试提取数字部分
                                    numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', value)
                                    if numbers:
                                        numeric_value = float(numbers[0])
                                        values.append(numeric_value)
                                        years.append(year)
                                except:
                                    pass  # 静默失败，继续处理下一年份

            if not values:
                st.warning(f"该指标 '{indicator_name}' 没有有效的数值数据")
                return

            # 创建单一图表，柱状图和折线图叠加
            fig = go.Figure()

            # 1. 柱状图 - 显示数值
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
                    textfont=dict(size=10),
                    yaxis='y'  # 主Y轴
                )
            )

            # 2. 折线图 - 显示增长率（叠加在同一图表上）
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
                        textfont=dict(size=10, color='#FF6B6B'),
                        hovertemplate='<b>%{x}</b><br>增长率: %{y:.2f}%<extra></extra>',
                        yaxis='y2'  # 第二Y轴
                    )
                )

            # 更新布局，创建双Y轴
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
                # 设置两个Y轴
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
                    showgrid=False,  # 第二Y轴不显示网格
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

            # 显示图表
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

            # 添加数据表格
            st.subheader(f"📊 {indicator_name} 数据明细")

            # 创建数据摘要表
            summary_data = []
            for i, (year, value) in enumerate(zip(years, values)):
                if i > 0:
                    growth_rate = ((value - values[i-1]) / values[i-1]) * 100 if values[i-1] != 0 else None
                    growth_color = "🔺" if growth_rate and growth_rate > 0 else "🔻" if growth_rate and growth_rate < 0 else "➡️"
                    growth_display = f"{growth_color} {growth_rate:.2f}%" if growth_rate is not None else "基期"
                else:
                    growth_rate = None
                    growth_display = "📍 基期"

                summary_data.append({
                    '年份': year,
                    '数值(百万元)': f"{value:,.2f}",
                    '同比增长率': growth_display,
                    '变化额(百万元)': f"{value - values[i-1]:+,.2f}" if i > 0 else "—"
                })

            summary_df = pd.DataFrame(summary_data)

            # 添加统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_value = sum(values) / len(values)
                st.metric("平均值", f"{avg_value:,.2f} 百万元")
            with col2:
                if len(values) > 1:
                    cagr = ((values[-1] / values[0]) ** (1/len(years)) - 1) * 100
                    st.metric("复合增长率", f"{cagr:.2f}%")
                else:
                    st.metric("复合增长率", "—")
            with col3:
                volatility = (max(values) - min(values)) / avg_value * 100 if avg_value > 0 else 0
                st.metric("波动率", f"{volatility:.2f}%")

            # 显示数据表格
            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "年份": st.column_config.TextColumn("年份", width="small"),
                    "数值(百万元)": st.column_config.TextColumn("数值", width="medium"),
                    "同比增长率": st.column_config.TextColumn("同比增长率", width="medium"),
                    "变化额(百万元)": st.column_config.TextColumn("年度变化额", width="medium")
                }
            )

        except Exception as e:
            st.error(f"生成图表时发生错误: {str(e)}")
            st.write("请尝试选择其他指标或检查数据质量。")

    def create_styler(self, df: pd.DataFrame):
        """
        创建财务格式的样式器

        Args:
            df: 格式化后的DataFrame

        Returns:
            带样式的Styler对象
        """
        if df.empty:
            return df.style

        # 定义格式化函数
        def format_currency(value):
            if pd.isna(value):
                return ""
            try:
                return f"{float(value):,.2f}"
            except (ValueError, TypeError):
                return str(value)

        def format_percentage(value):
            if pd.isna(value):
                return ""
            if isinstance(value, str) and '%' in value:
                return value
            try:
                return f"{float(value):.2f}%"
            except (ValueError, TypeError):
                return str(value)

        # 识别需要格式化的列（窄表格式）
        first_column = df.columns[0] if len(df.columns) > 0 else None  # 指标名称列
        year_columns = [col for col in df.columns if col != first_column and (col.isdigit() or '-' in col)]

        # 创建自定义格式化函数，根据指标类型选择格式
        def format_cell(value):
            if pd.isna(value):
                return ""
            try:
                float_val = float(value)
                return f"{float_val:,.2f}"
            except (ValueError, TypeError):
                return str(value)

        # 应用格式化
        styler = df.style

        # 对数值列应用格式化
        if year_columns:
            styler = styler.format({col: format_cell for col in year_columns})

        # 添加样式
        styler = styler.set_properties(**{
            'text-align': 'right'
        })

        # 第一列（指标名称）左对齐，添加可点击样式
        if first_column:
            styler = styler.set_properties(subset=[first_column], **{
                'text-align': 'left',
                'font-weight': 'bold',
                'color': '#1f77b4',
                'cursor': 'pointer',
                'text-decoration': 'underline'
            })

        # 添加表格样式
        styler = styler.set_table_styles([
            {'selector': 'thead th', 'props': [
                ('background-color', '#f0f2f6'),
                ('font-weight', 'bold'),
                ('text-align', 'center'),
                ('border-bottom', '2px solid #ddd')
            ]},
            {'selector': 'tbody tr:hover', 'props': [
                ('background-color', '#f5f5f5')
            ]},
            {'selector': 'td', 'props': [
                ('border-bottom', '1px solid #eee'),
                ('padding', '8px')
            ]},
            {'selector': f'td:nth-child(1)', 'props': [
                ('color', '#1f77b4'),
                ('cursor', 'pointer'),
                ('font-weight', 'bold')
            ]}
        ])

        return styler

    def render_sidebar(self):
        """渲染侧边栏"""
        st.sidebar.title("📊 A股财务报表分析")

        # 股票代码输入
        symbol = st.sidebar.text_input(
            "股票代码",
            value="600519",
            help="请输入6位A股代码，如600519（贵州茅台）"
        )

        # 时间范围选择
        st.sidebar.subheader("查询时间范围")

        time_option = st.sidebar.selectbox(
            "选择时间范围",
            ["最近10年", "最近5年", "全部", "自定义"],
            index=0
        )

        start_date = None
        end_date = None

        if time_option == "全部":
            # 不设置时间限制，获取所有可用数据
            start_date = None
            end_date = None
        elif time_option == "最近10年":
            end_date = datetime.now().strftime("%Y-12-31")
            start_date = f"{datetime.now().year - 10}-01-01"
        elif time_option == "最近5年":
            end_date = datetime.now().strftime("%Y-12-31")
            start_date = f"{datetime.now().year - 5}-01-01"
        elif time_option == "自定义":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("开始日期", value=datetime(2020, 1, 1)).strftime("%Y-%m-%d")
            with col2:
                end_date = st.date_input("结束日期", value=datetime.now()).strftime("%Y-%m-%d")

        # 查询按钮
        query_button = st.sidebar.button("🔍 查询财务数据", type="primary", use_container_width=True)

        return symbol, start_date, end_date, query_button

    def render_report(self, title: str, df: pd.DataFrame, report_type: str):
        """
        渲染单个报表

        Args:
            title: 报表标题
            df: 报表数据
            report_type: 报表类型
        """
        if df.empty:
            st.warning(f"⚠️ {title}暂无数据")
            return

        st.subheader(f"📋 {title}")

        # 显示数据概览
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("报告期数", len(df))
        with col2:
            st.metric("字段数", len(df.columns))
        with col3:
            # 识别日期列并获取最新日期
            date_columns = ['报告期', 'date', 'DATE', 'report_date', 'REPORT_DATE']
            latest_date = "N/A"
            for col in date_columns:
                if col in df.columns and not df.empty:
                    # 确保日期列是datetime类型并找到最大日期
                    df_temp = df.copy()
                    df_temp[col] = pd.to_datetime(df_temp[col])
                    latest_date_raw = df_temp[col].max()
                    if isinstance(latest_date_raw, pd.Timestamp):
                        latest_date = latest_date_raw.strftime('%Y-%m-%d')
                    elif isinstance(latest_date_raw, str):
                        # 如果是字符串，尝试解析为日期
                        try:
                            latest_date = pd.to_datetime(latest_date_raw).strftime('%Y-%m-%d')
                        except:
                            latest_date = latest_date_raw
                    break
            st.metric("最新报告期", latest_date)

        # 格式化数据
        formatted_df = self.format_financial_data(df, report_type)

        # 首先显示数据表格（原始数据展示）
        st.subheader("📊 财务数据表格")

        if not formatted_df.empty and '指标名称' in formatted_df.columns:
            # 创建样式化的表格（带可点击的指标名称）
            styler = self.create_styler(formatted_df)
            st.dataframe(styler, use_container_width=True, hide_index=True)

            # 深度分析部分
            st.markdown("---")
            st.subheader("📈 财务指标深度分析")
            st.info("💡 **点击下方任意指标名称进行深度图表分析**")

            indicators = formatted_df['指标名称'].tolist()

            # 使用按钮创建可点击的指标列表
            cols = st.columns(4)  # 四列布局，更紧凑
            for i, indicator in enumerate(indicators):
                with cols[i % 4]:
                    button_style = "primary" if indicator == st.session_state.get(f"selected_indicator_{report_type}", "") else "secondary"

                    if st.button(
                        indicator,
                        key=f"indicator_{report_type}_{i}",
                        type=button_style,
                        use_container_width=True,
                        help=f"点击分析 {indicator}"
                    ):
                        st.session_state[f"selected_indicator_{report_type}"] = indicator
                        st.rerun()

            # 显示选中指标的图表
            selected_indicator = st.session_state.get(f"selected_indicator_{report_type}", None)
            if selected_indicator:
                st.markdown("---")
                st.success(f"📊 **{selected_indicator}** - 财务指标分析")
                try:
                    self.create_charts_for_indicator(selected_indicator, formatted_df, report_type)
                except Exception as e:
                    st.error(f"生成图表时发生错误: {str(e)}")
                    st.write("请尝试选择其他指标或检查数据质量。")
        else:
            # 创建样式化的表格（无数据情况）
            styler = self.create_styler(formatted_df)
            st.dataframe(styler, use_container_width=True, hide_index=True)

        st.markdown("---")

    def run(self):
        """运行应用"""
        # 渲染侧边栏
        symbol, start_date, end_date, query_button = self.render_sidebar()

        # 主标题
        st.title("📈 A股财务报表综合分析（窄表格式）")
        st.markdown("*数据单位：百万元 | 数值保留2位小数 | 年份为列，指标为行，时间从左到右由近到远*")

        # 检查是否需要重新查询
        should_query = query_button

        # 检查时间范围或股票代码是否发生变化
        if not should_query and 'financial_data' in st.session_state:
            current_symbol = st.session_state.current_symbol
            current_start_date = st.session_state.get('start_date', None)
            current_end_date = st.session_state.get('end_date', None)

            # 如果股票代码或时间范围发生变化，需要重新查询
            if (current_symbol != symbol or
                current_start_date != start_date or
                current_end_date != end_date):
                should_query = True

        # 查询数据
        if should_query:
            with st.spinner("正在获取财务数据..."):
                financial_data = self.get_financial_data(symbol, start_date, end_date)
                st.session_state.financial_data = financial_data
                st.session_state.current_symbol = symbol
                st.session_state.start_date = start_date
                st.session_state.end_date = end_date
        elif 'financial_data' not in st.session_state:
            financial_data = {}
        else:
            financial_data = st.session_state.financial_data
            symbol = st.session_state.current_symbol

        if financial_data:
            # 显示当前查询的股票
            st.success(f"✅ 已获取 {symbol} 的财务数据")

            # 使用tabs展示四大报表
            tab_names = [
                "📊 财务指标",
                "💰 资产负债表",
                "📈 利润表",
                "💳 现金流量表"
            ]

            tabs = st.tabs(tab_names)

            with tabs[0]:
                self.render_report("财务指标", financial_data.get('indicators', pd.DataFrame()), "indicators")

            with tabs[1]:
                self.render_report("资产负债表", financial_data.get('balance_sheet', pd.DataFrame()), "balance_sheet")

            with tabs[2]:
                self.render_report("利润表", financial_data.get('income_statement', pd.DataFrame()), "income_statement")

            with tabs[3]:
                self.render_report("现金流量表", financial_data.get('cash_flow', pd.DataFrame()), "cash_flow")

            # 数据下载按钮
            st.subheader("📥 数据下载")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if not financial_data.get('indicators', pd.DataFrame()).empty:
                    csv_data = self.format_financial_data(financial_data['indicators'], "indicators").to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载财务指标",
                        data=csv_data,
                        file_name=f"{symbol}_财务指标_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col2:
                if not financial_data.get('balance_sheet', pd.DataFrame()).empty:
                    csv_data = self.format_financial_data(financial_data['balance_sheet'], "balance_sheet").to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载资产负债表",
                        data=csv_data,
                        file_name=f"{symbol}_资产负债表_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col3:
                if not financial_data.get('income_statement', pd.DataFrame()).empty:
                    csv_data = self.format_financial_data(financial_data['income_statement'], "income_statement").to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载利润表",
                        data=csv_data,
                        file_name=f"{symbol}_利润表_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col4:
                if not financial_data.get('cash_flow', pd.DataFrame()).empty:
                    csv_data = self.format_financial_data(financial_data['cash_flow'], "cash_flow").to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="下载现金流量表",
                        data=csv_data,
                        file_name=f"{symbol}_现金流量表_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        else:
            st.error("❌ 未能获取到财务数据，请检查股票代码是否正确")

        # 页脚信息
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 12px;'>"
            "数据来源：akshare | 仅供参考，不构成投资建议"
            "</div>",
            unsafe_allow_html=True
        )


def main():
    """主函数"""
    app = FinancialReportApp()
    app.run()


if __name__ == "__main__":
    main()