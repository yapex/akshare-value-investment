"""
净利润估值组件
"""

import traceback


class NetIncomeValuationComponent:
    """净利润估值组件（PE倍数法）"""

    title = "📊 估值（净利润）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染净利润估值组件

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

        from services.calculators.net_income_valuation import calculate as calculate_net_income_valuation
        from services import data_service

        try:
            st.subheader(
                NetIncomeValuationComponent.title,
                help="""
                **PE倍数估值法（三年后净利润）**

                **核心原理**：企业的价值等于其未来三年后预估净利润乘以合理的PE倍数。

                **什么是PE倍数估值法？**
                PE倍数估值法是一种相对估值方法，通过预测企业未来的净利润，并乘以合理的市盈率（PE）倍数，从而得出企业的估值。

                **估值公式**：
                ```
                企业价值 = 三年后预估净利润 × PE倍数
                三年后预估净利润 = 当前净利润 × (1 + 增长率)^3
                ```

                **核心步骤**：
                1. **获取当前净利润**：从最新的利润表获取
                2. **预测未来净利润**：基于增长率假设预测三年后净利润
                3. **应用PE倍数**：使用合理的PE倍数计算企业价值
                4. **对比当前市值**：判断估值水平

                **关键参数说明**：
                - **净利润增长率**：预测期内净利润的预期增长率
                - **PE倍数**：合理的市盈率倍数，通常参考行业平均或历史水平

                **投资意义**：
                - PE倍数法简单直观，易于理解和应用
                - 适合盈利稳定、增长可预测的成熟企业
                - 常用的PE倍数：15-25倍（根据行业和成长性调整）

                **注意事项**：
                - PE倍数法对增长率和PE倍数假设非常敏感
                - 不适合亏损企业或高增长但盈利不稳定的企业
                - 建议结合DCF、市销率等其他估值方法综合判断
                """
            )

            # 参数设置区域
            st.markdown("##### ⚙️ 估值参数设置")
            col1, col2 = st.columns(2)

            with col1:
                growth_rate = st.number_input(
                    "净利润增长率 (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    format="%.1f",
                    help="预测期内净利润的预期年增长率",
                    key="net_income_growth_rate"
                ) / 100

            with col2:
                pe_multiple = st.number_input(
                    "PE倍数",
                    min_value=5.0,
                    max_value=100.0,
                    value=25.0,
                    step=1.0,
                    format="%.0f",
                    help="合理的市盈率倍数，通常参考行业平均或历史水平",
                    key="net_income_pe_multiple"
                )

            with st.spinner(f"正在计算 {market} 股票 {symbol} 的净利润估值..."):
                try:
                    result = calculate_net_income_valuation(
                        symbol, market,
                        years=years,
                        growth_rate=growth_rate,
                        pe_multiple=pe_multiple
                    )
                    history_df, prediction_df, display_cols_history, display_cols_prediction, stats = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 市值对比与综合判断（在估值结果之前）
            st.markdown("##### 💰 市值对比与综合判断")

            col_market, col_empty = st.columns([2, 1])

            with col_market:
                market_cap_input = st.number_input(
                    "当前市值（亿元）",
                    min_value=0.0,
                    max_value=100000.0,
                    value=0.0,
                    step=100.0,
                    format="%.2f",
                    help="请输入当前市值，单位：亿元。例如：茅台1.77万亿 = 17700亿元",
                    key="net_income_market_cap"
                )

            # 如果输入了市值，显示对比分析
            if market_cap_input > 0:
                enterprise_value = stats['enterprise_value']
                market_cap = market_cap_input

                # 计算对比指标
                premium_rate = (market_cap / enterprise_value - 1) * 100
                premium_ratio = market_cap / enterprise_value

                # 综合判断
                if premium_rate > 50:
                    overall_status = "⚠️ 显著高估"
                    status_color = "🔴"
                    advice = "市值远超估值，风险较高。建议谨慎投资或等待更好的买入时机。"
                elif premium_rate > 20:
                    overall_status = "⚠️ 可能高估"
                    status_color = "🟠"
                    advice = "市值明显高于估值，安全边际较小。建议深入分析品牌溢价是否合理，或等待回调。"
                elif premium_rate > -20:
                    overall_status = "✅ 相对合理"
                    status_color = "🟢"
                    advice = "市值与估值基本匹配。对于具有强大品牌的企业，这个估值水平相对合理，可以考虑配置。"
                else:
                    overall_status = "✅✅ 可能低估"
                    status_color = "🟢"
                    advice = "市值低于估值，可能存在低估机会。建议深入分析公司基本面，考虑适当配置。"

                # 显示对比结果
                st.markdown("##### 📊 市值对比结果")

                # 核心对比数据
                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    st.metric(
                        label="当前市值",
                        value=f"{market_cap:.2f} 亿元",
                        help="市场给出的总市值"
                    )

                with col_m2:
                    st.metric(
                        label="估值结果",
                        value=f"{enterprise_value:.2f} 亿元",
                        help=f"基于{pe_multiple:.0f}倍PE计算的估值"
                    )

                with col_m3:
                    st.metric(
                        label="市值溢价率",
                        value=f"{premium_rate:+.1f}%",
                        delta=f"{premium_ratio:.2f}倍",
                        help="市值相对估值的溢价程度"
                    )

                # 显示综合判断
                st.info(f"""
                **综合判断：{status_color} {overall_status}**

                **市值 / 估值** = {premium_ratio:.2f}倍

                **其他要点：**
                - 当前净利润：{stats['current_net_income']:.2f} 亿元
                - 三年后预测净利润：{stats['year3_net_income']:.2f} 亿元
                - 市值溢价率：{premium_rate:+.1f}%

                **投资建议：**
                {advice}

                **注意事项：**
                - 估值适合盈利稳定的成熟企业
                - 对于品牌型企业，估值可能低估品牌价值
                - 建议结合DCF、市销率等其他指标综合判断
                """)

            # 显示估值结果
            st.markdown("##### 📊 估值结果")

            # 核心估值指标
            col_v1, col_v2, col_v3 = st.columns(3)

            with col_v1:
                st.metric(
                    label="当前净利润",
                    value=f"{stats['current_net_income']:.2f} 亿元",
                    help="最新年度的净利润"
                )

            with col_v2:
                st.metric(
                    label="三年后预测净利润",
                    value=f"{stats['year3_net_income']:.2f} 亿元",
                    help=f"基于 {growth_rate * 100:.1f}% 增长率预测"
                )

            with col_v3:
                st.metric(
                    label="PE估值",
                    value=f"{stats['enterprise_value']:.2f} 亿元",
                    help=f"三年后预测净利润 × {pe_multiple:.0f}倍PE"
                )

            # 显示详细估值说明
            with st.expander("📋 估值说明", expanded=False):
                st.markdown(stats['valuation_summary'])

            # 显示历史净利润图表
            if len(history_df) > 0:
                st.markdown("##### 📈 历史净利润趋势")

                # 创建历史净利润图表
                fig_history = go.Figure()

                fig_history.add_trace(go.Scatter(
                    x=history_df["年份"],
                    y=history_df["历史净利润"],
                    mode='lines+markers',
                    name='历史净利润',
                    line=dict(color='#3498db', width=2),
                    marker=dict(size=8)
                ))

                fig_history.update_layout(
                    title=f"{symbol} - 历史净利润趋势",
                    xaxis_title="年份",
                    yaxis_title="净利润（亿元）",
                    hovermode='x unified',
                    template='plotly_white',
                    height=400
                )

                st.plotly_chart(fig_history, use_container_width=True, key=f"net_income_history_{symbol}_{market}_{years}")

            # 显示预测数据表
            st.markdown("##### 🔮 净利润预测")
            data_df = prediction_df[display_cols_prediction].copy()
            data_df["预测净利润"] = data_df["预测净利润"].apply(lambda x: f"{x:.2f}")
            st.dataframe(
                data_df,
                width='stretch',
                hide_index=True
            )

            # 显示计算公式说明
            with st.expander("📖 计算公式说明", expanded=False):
                st.markdown(f"""
                ### PE倍数估值法核心公式

                **1. 预测净利润**
                ```
                第n年净利润 = 当前净利润 × (1 + 增长率)^n
                ```

                **2. 三年后净利润**
                ```
                三年后净利润 = 当前净利润 × (1 + 增长率)^3
                ```

                **3. 企业价值（PE估值）**
                ```
                企业价值 = 三年后净利润 × PE倍数
                ```

                **4. 市值对比**
                ```
                溢价率 = (当前市值 / 估值 - 1) × 100%
                ```

                **5. 市场隐含增长率**
                ```
                市值 = 当前净利润 × (1 + g)^3 × PE倍数
                g = (市值 / (当前净利润 × PE倍数))^(1/3) - 1
                ```

                ### 参数设置建议

                **净利润增长率**
                - 成熟企业：5-10%
                - 成长企业：10-20%
                - 周期性企业：使用历史平均水平
                - 本企业历史增长率：{stats['historical_growth_rate'] * 100:.1f}%

                **PE倍数**
                - 传统行业：10-15倍
                - 稳健成长行业：15-25倍
                - 高成长行业：25-40倍
                - 可参考行业平均或历史水平

                ### 投资建议

                **市值溢价 > 50%（显著高估）**
                - 市值远超估值
                - 风险较高，建议谨慎
                - 等待更好的买入时机

                **市值溢价 20%-50%（可能高估）**
                - 市值明显高于估值
                - 安全边际较小
                - 建议深入分析或等待回调

                **市值溢价 -20%-20%（相对合理）**
                - 市值与估值基本一致
                - 估值相对合理
                - 可以考虑配置

                **市值溢价 < -20%（可能低估）**
                - 市值低于估值
                - 可能存在低估机会
                - 值得深入研究

                ### 注意事项

                - PE倍数法适合盈利稳定的成熟企业
                - 不适合亏损企业或盈利波动大的企业
                - 建议结合DCF、市销率等多种估值方法
                - 对于具有强大品牌的企业，估值可能偏保守
                """)

            return True

        except Exception as e:
            st.error(f"净利润估值分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
