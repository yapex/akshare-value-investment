"""
流动性分析组件（流动比率、速动比率、利息覆盖率）
"""

import traceback


class LiquidityRatioComponent:
    """流动性分析组件（整合三个流动性指标）"""

    title = "💧 流动性分析"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染流动性分析组件

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
        import pandas as pd
        import requests

        from services.calculators.liquidity_ratio import (
            calculate as calculate_liquidity,
            calculate_interest_coverage_ratio
        )
        from services import data_service

        try:
            st.markdown("---")
            st.subheader(
                LiquidityRatioComponent.title,
                help="""
                **流动性分析：流动比率、速动比率、利息覆盖比率**

                **核心问题**：公司的短期偿债能力和利息支付能力如何？

                **📊 三个流动性指标：**

                **1. 流动比率（Current Ratio）**
                - 公式：流动比率 = 流动资产 ÷ 流动负债
                - 含义：每1元流动负债，有多少流动资产可以偿还
                - 标准：≥ 2 为优秀，1.5-2 为良好，< 1.5 需警惕

                **2. 速动比率（Quick Ratio）**
                - 公式：速动比率 = (流动资产 - 存货) ÷ 流动负债
                - 含义：剔除存货后，每1元流动负债有多少快速变现资产可偿还
                - 标准：≥ 1 为优秀，0.5-1 为一般，< 0.5 需警惕

                **3. 利息覆盖比率（Interest Coverage Ratio）**
                - 公式：利息覆盖比率 = (息税前利润 + 利息收入) ÷ 利息费用
                - 含义：公司利润是利息支出的多少倍
                - 标准：≥ 3 倍为安全，1.5-3 倍为一般，< 1.5 倍为危险

                **🎯 为什么这三个指标重要？**
                - 流动比率：衡量短期偿债能力（传统指标）
                - 速动比率：衡量"快速变现"能力（更严格）
                - 利息覆盖比率：衡量利息支付能力（关注债务成本）

                **💡 投资启示：**
                - 优质公司：流动比率 > 1.5，速动比率 > 1，利息覆盖率 > 3
                - 警惕信号：任一指标持续恶化
                - 行业差异：零售业、公用事业可接受较低比率

                **📌 数据来源说明：**
                - A股：流动比率、速动比率来自财务指标API
                - 港股：流动比率来自财务指标API，速动比率从资产负债表计算
                - 美股：流动比率、速动比率来自财务指标API
                - 利息覆盖率：三地市场均从利润表计算
                """
            )

            # ========== 1. 获取流动比率和速动比率数据 ==========
            with st.spinner(f"正在获取 {market} 股票 {symbol} 的流动性数据..."):
                try:
                    # 获取财务指标数据（包含流动比率和速动比率）
                    market_type_map = {
                        "A股": "a_stock",
                        "港股": "hk_stock",
                        "美股": "us_stock"
                    }
                    market_type = market_type_map.get(market)

                    indicators_response = requests.get(
                        f"{data_service.API_BASE_URL}/api/v1/financial/indicators",
                        params={
                            "symbol": symbol,
                            "market": market_type,
                            "frequency": "annual"
                        },
                        timeout=30
                    )

                    if indicators_response.status_code != 200:
                        raise data_service.APIServiceUnavailableError(
                            f"API服务返回错误状态码: {indicators_response.status_code}"
                        )

                    indicators_result = indicators_response.json()
                    data_wrapper = indicators_result.get("data", {})
                    records = data_wrapper.get("records", [])

                    if not records:
                        raise data_service.SymbolNotFoundError(f"{market}股票 {symbol} 没有财务指标数据")

                    # 转换为DataFrame
                    import pandas as pd
                    indicators_df = pd.DataFrame(records)

                    # 提取年份
                    if "报告期" in indicators_df.columns:
                        date_col = "报告期"
                    elif "REPORT_DATE" in indicators_df.columns:
                        date_col = "REPORT_DATE"
                    elif "date" in indicators_df.columns:
                        date_col = "date"
                    else:
                        raise data_service.DataServiceError(f"{market}股票 {symbol} 数据中缺少日期字段")

                    indicators_df = indicators_df.copy()
                    indicators_df["年份"] = pd.to_datetime(indicators_df[date_col]).dt.year

                    # 根据市场选择字段
                    if market == "A股":
                        current_ratio_col = "流动比率"
                        quick_ratio_col = "速动比率"
                    elif market == "港股":
                        current_ratio_col = "CURRENT_RATIO"
                        quick_ratio_col = None  # 港股API没有速动比率，需要单独计算
                    else:  # 美股
                        current_ratio_col = "CURRENT_RATIO"
                        quick_ratio_col = "SPEED_RATIO"

                    # 提取流动比率数据并转换为数值类型
                    liquidity_data = indicators_df[["年份", current_ratio_col]].copy()
                    liquidity_data.columns = ["年份", "流动比率"]
                    liquidity_data["流动比率"] = pd.to_numeric(liquidity_data["流动比率"], errors="coerce")

                    # 提取或计算速动比率
                    if quick_ratio_col and quick_ratio_col in indicators_df.columns:
                        liquidity_data["速动比率"] = pd.to_numeric(indicators_df[quick_ratio_col], errors="coerce").values
                    elif market == "港股":
                        # 港股需要单独计算速动比率
                        try:
                            from services.calculators.liquidity_ratio import calculate as calculate_quick_ratio
                            quick_ratio_df, _, _ = calculate_quick_ratio(symbol, years + 5)
                            liquidity_data = pd.merge(
                                liquidity_data,
                                quick_ratio_df[["年份", "速动比率"]],
                                on="年份",
                                how="left"
                            )
                        except Exception as e:
                            st.warning(f"港股速动比率计算失败：{str(e)}")
                            liquidity_data["速动比率"] = None

                    # 限制年数并排序
                    liquidity_data = liquidity_data.sort_values("年份").tail(years).reset_index(drop=True)

                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # ========== 2. 获取利息覆盖比率数据 ==========
            try:
                interest_coverage_df, _, interest_metrics = calculate_interest_coverage_ratio(
                    symbol, market, years
                )

                # 合并数据
                liquidity_data = pd.merge(
                    liquidity_data,
                    interest_coverage_df[["年份", "利息覆盖比率"]],
                    on="年份",
                    how="left"
                )

            except data_service.DataServiceError as e:
                st.warning(f"利息覆盖比率获取失败：{str(e)}")
                liquidity_data["利息覆盖比率"] = None

            # ========== 3. 显示流动比率和速动比率图表 ==========
            st.markdown("##### 📊 流动比率 & 速动比率趋势")

            fig1 = go.Figure()

            # 添加流动比率折线
            if "流动比率" in liquidity_data.columns:
                fig1.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=liquidity_data['流动比率'],
                        name='流动比率',
                        mode='lines+markers',
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=10),
                        hovertemplate='%{x}年<br/>流动比率: %{y:.2f}<extra></extra>'
                    )
                )

            # 添加速动比率折线
            if "速动比率" in liquidity_data.columns and liquidity_data["速动比率"].notna().any():
                fig1.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=liquidity_data['速动比率'],
                        name='速动比率',
                        mode='lines+markers',
                        line=dict(color='#2ecc71', width=3),
                        marker=dict(size=10),
                        hovertemplate='%{x}年<br/>速动比率: %{y:.2f}<extra></extra>'
                    )
                )

            # 添加参考线
            if "流动比率" in liquidity_data.columns:
                fig1.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=[1.5] * len(liquidity_data['年份']),
                        mode='lines',
                        name='流动比率警戒线 (1.5)',
                        line=dict(color='orange', width=2, dash='dash'),
                        hoverinfo='skip'
                    )
                )

            if "速动比率" in liquidity_data.columns and liquidity_data["速动比率"].notna().any():
                fig1.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=[1] * len(liquidity_data['年份']),
                        mode='lines',
                        name='速动比率健康线 (1.0)',
                        line=dict(color='green', width=2, dash='dash'),
                        hoverinfo='skip'
                    )
                )

            fig1.update_layout(
                title=f"{symbol} - 流动比率与速动比率趋势",
                xaxis_title="年份",
                yaxis_title="比率",
                hovermode="x unified",
                height=450,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )

            st.plotly_chart(fig1, width='stretch')

            # ========== 4. 显示利息覆盖比率图表 ==========
            if "利息覆盖比率" in liquidity_data.columns and liquidity_data["利息覆盖比率"].notna().any():
                st.markdown("##### 📊 利息覆盖比率趋势")

                fig2 = go.Figure()

                fig2.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=liquidity_data['利息覆盖比率'],
                        name='利息覆盖比率',
                        mode='lines+markers',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=10),
                        hovertemplate='%{x}年<br/>利息覆盖比率: %{y:.2f}倍<extra></extra>'
                    )
                )

                # 添加参考线
                fig2.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=[3] * len(liquidity_data['年份']),
                        mode='lines',
                        name='安全线 (3倍)',
                        line=dict(color='green', width=2, dash='dash'),
                        hoverinfo='skip'
                    )
                )

                fig2.add_trace(
                    go.Scatter(
                        x=liquidity_data['年份'],
                        y=[1.5] * len(liquidity_data['年份']),
                        mode='lines',
                        name='警戒线 (1.5倍)',
                        line=dict(color='orange', width=2, dash='dash'),
                        hoverinfo='skip'
                    )
                )

                fig2.update_layout(
                    title=f"{symbol} - 利息覆盖比率趋势",
                    xaxis_title="年份",
                    yaxis_title="利息覆盖比率 (倍数)",
                    hovermode="x unified",
                    height=450,
                    showlegend=True,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )

                st.plotly_chart(fig2, width='stretch')

            # ========== 5. 显示关键指标 ==========
            st.markdown("##### 📈 最新年度关键指标")

            latest_data = liquidity_data.iloc[-1]

            col1, col2, col3 = st.columns(3)

            with col1:
                if pd.notna(latest_data["流动比率"]):
                    current_ratio = latest_data["流动比率"]
                    delta_color = "normal" if current_ratio >= 1.5 else "inverse"
                    st.metric(
                        label="流动比率",
                        value=f"{current_ratio:.2f}",
                        delta="健康" if current_ratio >= 1.5 else "需警惕",
                        delta_color=delta_color,
                        help="流动比率 ≥ 1.5 为健康"
                    )
                else:
                    st.metric(label="流动比率", value="N/A")

            with col2:
                if "速动比率" in latest_data and pd.notna(latest_data["速动比率"]):
                    quick_ratio = latest_data["速动比率"]
                    delta_color = "normal" if quick_ratio >= 1 else "inverse"
                    st.metric(
                        label="速动比率",
                        value=f"{quick_ratio:.2f}",
                        delta="健康" if quick_ratio >= 1 else "需警惕",
                        delta_color=delta_color,
                        help="速动比率 ≥ 1 为健康"
                    )
                else:
                    st.metric(label="速动比率", value="N/A")

            with col3:
                if "利息覆盖比率" in latest_data and pd.notna(latest_data["利息覆盖比率"]):
                    coverage_ratio = latest_data["利息覆盖比率"]
                    if coverage_ratio >= 3:
                        status = "安全"
                        delta_color = "normal"
                    elif coverage_ratio >= 1.5:
                        status = "一般"
                        delta_color = "normal"
                    else:
                        status = "危险"
                        delta_color = "inverse"
                    st.metric(
                        label="利息覆盖比率",
                        value=f"{coverage_ratio:.2f}倍",
                        delta=status,
                        delta_color=delta_color,
                        help="利息覆盖率 ≥ 3倍为安全"
                    )
                else:
                    st.metric(label="利息覆盖比率", value="N/A")

            # ========== 6. 原始数据表格 ==========
            st.markdown("---")
            with st.expander("📊 查看原始数据"):
                # 选择要显示的列
                display_cols = ["年份", "流动比率"]
                if "速动比率" in liquidity_data.columns:
                    display_cols.append("速动比率")
                if "利息覆盖比率" in liquidity_data.columns:
                    display_cols.append("利息覆盖比率")

                st.dataframe(
                    liquidity_data[display_cols],
                    width='stretch',
                    hide_index=True
                )

            return True

        except Exception as e:
            st.error(f"流动性分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
