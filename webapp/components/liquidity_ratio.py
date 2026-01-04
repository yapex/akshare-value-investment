"""
流动性分析组件（流动比率、速动比率、利息覆盖率）
"""

import traceback
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from services.calculators.liquidity_ratio import calculate, calculate_interest_coverage_ratio, INF_VALUE
from services import data_service


class LiquidityRatioComponent:
    """流动性分析组件（整合三个流动性指标）"""

    title = "💧 流动性分析"

    @staticmethod
    def render(symbol: str, market: str, years: int = 5) -> bool:
        """渲染流动性分析组件

        Args:
            symbol: 股票代码
            market: 市场类型（A股/港股/美股）
            years: 查询年数

        Returns:
            bool: 是否成功渲染
        """
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
                - 标准：≥ 2 为优秀，1.5-2 为良好，< 1.5 需警惕

                **2. 速动比率（Quick Ratio）**
                - 公式：速动比率 = (流动资产 - 存货) ÷ 流动负债
                - 标准：≥ 1 为优秀，0.5-1 为一般，< 0.5 需警惕

                **3. 利息覆盖比率（Interest Coverage Ratio）**
                - 公式：利息覆盖比率 = (息税前利润 + 利息收入) ÷ 利息费用
                - 标准：≥ 3 倍为安全，1.5-3 倍为一般，< 1.5 倍为危险
                """
            )

            # ========== 1. 获取基础流动性数据（流动比率和速动比率） ==========
            with st.spinner(f"正在获取 {market} 股票 {symbol} 的流动性数据..."):
                try:
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

                    indicators_df = pd.DataFrame(records)

                    # 提取年份
                    date_col = next((c for c in ["报告期", "REPORT_DATE", "date"] if c in indicators_df.columns), None)
                    if not date_col:
                        raise data_service.DataServiceError(f"{market}股票 {symbol} 数据中缺少日期字段")

                    indicators_df["年份"] = pd.to_datetime(indicators_df[date_col]).dt.year

                    # 根据市场选择字段
                    if market == "A股":
                        current_ratio_col = "流动比率"
                        quick_ratio_col = "速动比率"
                    elif market == "港股":
                        current_ratio_col = "CURRENT_RATIO"
                        quick_ratio_col = None
                    else:  # 美股
                        current_ratio_col = "CURRENT_RATIO" if "CURRENT_RATIO" in indicators_df.columns else None
                        quick_ratio_col = "SPEED_RATIO" if "SPEED_RATIO" in indicators_df.columns else None

                    if not current_ratio_col:
                        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有流动比率数据")

                    liquidity_data = indicators_df[["年份", current_ratio_col]].copy()
                    liquidity_data.columns = ["年份", "流动比率"]
                    liquidity_data["流动比率"] = pd.to_numeric(liquidity_data["流动比率"], errors="coerce")

                    if quick_ratio_col and quick_ratio_col in indicators_df.columns:
                        liquidity_data["速动比率"] = pd.to_numeric(indicators_df[quick_ratio_col], errors="coerce").values
                    elif market == "港股":
                        try:
                            quick_ratio_df, _, _ = calculate(symbol, years + 5)
                            liquidity_data = pd.merge(liquidity_data, quick_ratio_df[["年份", "速动比率"]], on="年份", how="left")
                        except Exception as e:
                            st.warning(f"港股速动比率计算失败：{str(e)}")
                            liquidity_data["速动比率"] = None

                    liquidity_data = liquidity_data.sort_values("年份")
                    if years is not None:
                        liquidity_data = liquidity_data.tail(years)
                    liquidity_data = liquidity_data.reset_index(drop=True)

                except Exception as e:
                    st.error(f"流动性基础数据获取失败: {str(e)}")
                    return False

            # ========== 2. 获取利息覆盖比率数据 ==========
            try:
                interest_coverage_df, _, coverage_metrics = calculate_interest_coverage_ratio(
                    symbol, market, years
                )
                liquidity_data = pd.merge(
                    liquidity_data,
                    interest_coverage_df[["年份", "利息覆盖比率"]],
                    on="年份",
                    how="left"
                )
            except Exception as e:
                st.warning(f"利息覆盖比率获取失败：{str(e)}")
                liquidity_data["利息覆盖比率"] = None
                coverage_metrics = {}

            # ========== 3. 显示流动比率和速动比率图表 ==========
            st.markdown("##### 📊 流动比率 & 速动比率趋势")
            fig1 = go.Figure()
            if "流动比率" in liquidity_data.columns:
                fig1.add_trace(go.Scatter(x=liquidity_data['年份'], y=liquidity_data['流动比率'], name='流动比率', mode='lines+markers', line=dict(color='#3498db', width=3), marker=dict(size=10)))
            if "速动比率" in liquidity_data.columns and liquidity_data["速动比率"].notna().any():
                fig1.add_trace(go.Scatter(x=liquidity_data['年份'], y=liquidity_data['速动比率'], name='速动比率', mode='lines+markers', line=dict(color='#2ecc71', width=3), marker=dict(size=10)))
            
            fig1.add_trace(go.Scatter(x=liquidity_data['年份'], y=[1.5] * len(liquidity_data), mode='lines', name='流动比率警戒线 (1.5)', line=dict(color='orange', width=2, dash='dash')))
            fig1.add_trace(go.Scatter(x=liquidity_data['年份'], y=[1] * len(liquidity_data), mode='lines', name='速动比率健康线 (1.0)', line=dict(color='green', width=2, dash='dash')))
            
            fig1.update_layout(xaxis_title="年份", yaxis_title="比率", hovermode="x unified", height=400)
            st.plotly_chart(fig1, use_container_width=True)

            # ========== 4. 显示利息覆盖比率图表（含无穷大处理） ==========
            if "利息覆盖比率" in liquidity_data.columns and liquidity_data["利息覆盖比率"].notna().any():
                st.markdown("##### 📊 利息覆盖比率趋势")
                
                chart_data = liquidity_data.copy()
                chart_data["display_value"] = chart_data["利息覆盖比率"]
                chart_data["hover_label"] = chart_data["利息覆盖比率"].apply(lambda x: f"{x:.2f}倍" if pd.notna(x) else "N/A")
                
                max_display_val = 50.0
                valid_vals = chart_data[chart_data["利息覆盖比率"] < INF_VALUE]["利息覆盖比率"]
                if not valid_vals.empty:
                    max_display_val = max(50.0, valid_vals.max() * 1.2)
                
                mask_inf = chart_data["利息覆盖比率"] >= INF_VALUE
                if mask_inf.any():
                    chart_data.loc[mask_inf, "display_value"] = max_display_val
                    chart_data.loc[mask_inf, "hover_label"] = "无偿债压力 (无利息支出)"

                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=chart_data['年份'], y=chart_data['display_value'], text=chart_data['hover_label'],
                    name='利息覆盖比率', mode='lines+markers', line=dict(color='#e74c3c', width=3),
                    hovertemplate='%{x}年<br/>利息覆盖比率: %{text}<extra></extra>'
                ))
                fig2.add_trace(go.Scatter(x=chart_data['年份'], y=[3] * len(chart_data), mode='lines', name='安全线 (3倍)', line=dict(color='green', width=2, dash='dash')))
                fig2.update_layout(xaxis_title="年份", yaxis_title="利息覆盖比率 (倍数)", height=400)
                st.plotly_chart(fig2, use_container_width=True)

            # ========== 5. 显示最新年度关键指标 ==========
            st.markdown("##### 📈 最新年度关键指标")
            latest_data = liquidity_data.iloc[-1]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                val = latest_data.get("流动比率")
                st.metric(label="流动比率", value=f"{val:.2f}" if pd.notna(val) else "N/A", delta="健康" if pd.notna(val) and val >= 1.5 else "需警惕")
            
            with col2:
                val = latest_data.get("速动比率")
                st.metric(label="速动比率", value=f"{val:.2f}" if pd.notna(val) else "N/A", delta="健康" if pd.notna(val) and val >= 1 else "需警惕")
                
            with col3:
                val = latest_data.get("利息覆盖比率")
                display_val = "N/A"
                delta_status = None
                if pd.notna(val):
                    if val >= INF_VALUE:
                        display_val = "无偿债压力"
                        delta_status = "极安全"
                    else:
                        display_val = f"{val:.2f}倍"
                        delta_status = "安全" if val >= 3 else "危险"
                st.metric(label="利息覆盖比率", value=display_val, delta=delta_status)

            # ========== 6. 原始数据表格 ==========
            with st.expander("📊 查看原始数据"):
                show_df = liquidity_data.copy()
                if "利息覆盖比率" in show_df.columns:
                    mask = show_df["利息覆盖比率"] >= INF_VALUE
                    show_df["利息覆盖比率"] = show_df["利息覆盖比率"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                    show_df.loc[mask, "利息覆盖比率"] = "无偿债压力"
                st.dataframe(show_df, width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"流动性分析渲染失败：{str(e)}")
            st.error(traceback.format_exc())
            return False