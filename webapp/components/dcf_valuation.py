"""
DCF估值组件
"""

import traceback


class DCFValuationComponent:
    """DCF估值组件"""

    title = "📈 DCF估值分析"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染DCF估值组件

        Args:
            symbol: 股票代码
            market: 市场类型（A股/港股/美股）
            years: 查询年数

        Returns:
            bool: 是否成功渲染
        """
        # 延迟导入，优化启动性能
        import streamlit as st

        from services.calculators.dcf_valuation import calculate as calculate_dcf
        from services import data_service

        try:
            st.subheader(
                DCFValuationComponent.title,
                help="""
                **DCF（折现现金流）估值模型**

                **核心原理**：企业的内在价值等于其未来产生的所有自由现金流的现值之和。

                **什么是DCF估值？**
                DCF估值是一种绝对估值方法，通过预测企业未来的自由现金流，并按照适当的折现率将其折现到现值，从而得出企业的内在价值。

                **DCF估值的核心步骤**：
                1. **计算自由现金流**：FCF = 经营活动现金流 - 资本支出
                2. **预测未来现金流**：基于历史数据和增长率假设
                3. **折现到现值**：使用WACC（加权平均资本成本）作为折现率
                4. **计算终值**：永续增长期价值的现值
                5. **得出企业价值**：预测期现值 + 终值现值
                6. **计算股权价值**：企业价值 - 净债务

                **关键参数说明**：
                - **现金流增长率**：预测期内自由现金流的预期增长率
                - **折现率（WACC）**：加权平均资本成本，反映投资风险
                - **永续增长率**：预测期后的长期稳定增长率（通常2-3%）

                **投资意义**：
                - DCF估值提供企业的内在价值参考
                - 通过对比DCF股权价值和账面股权价值，判断估值水平
                - 适合现金流稳定可预测的成熟企业

                **注意事项**：
                - DCF估值对参数假设非常敏感
                - 适合现金流稳定可预测的成熟企业
                - 对于高增长或周期性企业，预测难度较大
                - 建议结合其他估值方法综合判断
                """
            )

            # 参数设置区域
            st.markdown("##### ⚙️ 估值参数设置")
            col1, col2, col3 = st.columns(3)

            with col1:
                growth_rate = st.number_input(
                    "现金流增长率 (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=9.0,
                    step=0.5,
                    format="%.1f",
                    help="预测期内自由现金流的预期年增长率",
                    key="dcf_growth_rate"
                ) / 100

            with col2:
                discount_rate = st.number_input(
                    "折现率/WACC (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=10.0,
                    step=0.5,
                    format="%.1f",
                    help="加权平均资本成本，反映投资风险",
                    key="dcf_discount_rate"
                ) / 100

            with col3:
                terminal_growth = st.number_input(
                    "永续增长率 (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=2.0,
                    step=0.1,
                    format="%.1f",
                    help="预测期后的长期稳定增长率（通常2-3%）",
                    key="dcf_terminal_growth"
                ) / 100

            projection_years = st.slider(
                "预测年数",
                min_value=3,
                max_value=10,
                value=5,
                help="现金流预测的年数"
            )

            with st.spinner(f"正在计算 {market} 股票 {symbol} 的DCF估值..."):
                try:
                    result = calculate_dcf(
                        symbol, market,
                        years=projection_years,
                        growth_rate=growth_rate,
                        discount_rate=discount_rate,
                        terminal_growth=terminal_growth
                    )
                    prediction_df, display_cols, stats = result
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
                    key="dcf_market_cap"
                )

            # 如果输入了市值，显示对比分析
            if market_cap_input > 0:
                dcf_value = stats['equity_value_dcf']
                market_cap = market_cap_input

                # 计算对比指标
                premium_rate = (market_cap / dcf_value - 1) * 100
                premium_ratio = market_cap / dcf_value

                # 计算市场隐含增长率
                implied_growth = stats['implied_growth_rate'](market_cap) if stats['implied_growth_rate'] else 0.0
                assumed_growth = stats['growth_rate']

                # 综合判断
                if premium_rate > 50:
                    overall_status = "⚠️ 显著高估"
                    status_color = "🔴"
                    advice = "市值远超DCF内在价值，风险较高。建议谨慎投资或等待更好的买入时机。"
                elif premium_rate > 20:
                    overall_status = "⚠️ 可能高估"
                    status_color = "🟠"
                    advice = "市值明显高于DCF内在价值，安全边际较小。建议深入分析品牌溢价是否合理，或等待回调。"
                elif premium_rate > -20:
                    overall_status = "✅ 相对合理"
                    status_color = "🟢"
                    advice = "市值与DCF内在价值基本匹配。对于具有强大品牌的企业，这个估值水平相对合理，可以考虑配置。"
                else:
                    overall_status = "✅✅ 可能低估"
                    status_color = "🟢"
                    advice = "市值低于DCF内在价值，可能存在低估机会。建议深入分析公司基本面，考虑适当配置。"

                # 显示对比结果
                st.markdown("##### 📊 市值对比结果")

                # 第一行：核心对比数据
                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    st.metric(
                        label="当前市值",
                        value=f"{market_cap:.2f} 亿元",
                        help="市场给出的总市值"
                    )

                with col_m2:
                    st.metric(
                        label="DCF内在价值",
                        value=f"{dcf_value:.2f} 亿元",
                        help="基于DCF模型计算的内在价值"
                    )

                with col_m3:
                    st.metric(
                        label="市值溢价率",
                        value=f"{premium_rate:+.1f}%",
                        delta=f"{premium_ratio:.2f}倍",
                        help="市值相对DCF价值的溢价程度"
                    )

                # 第二行：增长率对比
                st.markdown("##### 📈 增长率对比")

                col_g1, col_g2 = st.columns(2)

                with col_g1:
                    # 判断市场预期vs我们假设
                    growth_diff = implied_growth - assumed_growth
                    if abs(growth_diff) < 0.01:  # 差异小于1%
                        growth_comparison = "🟢 基本一致"
                        growth_color = "green"
                    elif growth_diff > 0:
                        growth_comparison = "🔴 市场更乐观"
                        growth_color = "red"
                    else:
                        growth_comparison = "🟢 市场更保守"
                        growth_color = "green"

                    st.metric(
                        label="市场隐含增长率",
                        value=f"{implied_growth*100:.1f}%",
                        delta=growth_comparison,
                        help=f"从当前市值反推的市场预期增长率\n我们的假设：{assumed_growth*100:.1f}%\n差异：{growth_diff*100:+.1f}个百分点"
                    )

                with col_g2:
                    st.metric(
                        label="我们的增长率假设",
                        value=f"{assumed_growth*100:.1f}%",
                        help="我们设置的现金流增长率假设（可调整上方参数）"
                    )

                # 显示综合判断
                st.info(f"""
                **综合判断：{status_color} {overall_status}**

                **市值 / DCF价值** = {premium_ratio:.2f}倍

                **增长率分析：**
                - 📊 **市场隐含增长率**：{implied_growth*100:.1f}%（市场预期的增长率）
                - 🎯 **我们的假设**：{assumed_growth*100:.1f}%（可调整参数测试）
                - 📉 **差异**：{growth_diff*100:+.1f}个百分点 ({'市场更乐观' if growth_diff > 0 else '市场更保守' if growth_diff < 0 else '基本一致'})

                **其他要点：**
                - 当前自由现金流：{stats['current_fcf']:.2f} 亿元
                - 市值溢价率：{premium_rate:+.1f}%

                **投资建议：**
                {advice}

                **注意事项：**
                - DCF估值适合现金流稳定的成熟企业
                - 对于品牌型企业，DCF可能低估品牌价值
                - 建议结合市盈率、市销率等其他指标综合判断
                """)

            # 显示估值结果
            st.markdown("##### 📊 估值结果")

            # 核心估值指标
            col_v1, col_v2, col_v3 = st.columns(3)

            with col_v1:
                st.metric(
                    label="企业价值",
                    value=f"{stats['enterprise_value']:.2f} 亿元",
                    help="预测期现值 + 终值现值"
                )

            with col_v2:
                st.metric(
                    label="DCF股权价值",
                    value=f"{stats['equity_value_dcf']:.2f} 亿元",
                    help="企业价值 - 净债务"
                )

            with col_v3:
                valuation_premium = stats['valuation_premium']
                st.metric(
                    label="估值溢价/折价",
                    value=f"{valuation_premium:+.1f}%",
                    help=f"DCF股权价值 vs 账面股权价值（{stats['equity_value_bs']:.2f}亿元）"
                )

            # 显示详细估值说明
            with st.expander("📋 估值说明", expanded=False):
                st.markdown(stats['valuation_summary'])

            # 显示现金流预测表
            st.markdown("##### 🔮 现金流预测")
            st.dataframe(
                prediction_df[display_cols].style.format({
                    "预测现金流": "{:.2f}",
                    "折现因子": "{:.4f}",
                    "折现现金流": "{:.2f}"
                }),
                width='stretch',
                hide_index=True
            )

            # 显示计算公式说明
            with st.expander("📖 计算公式说明", expanded=False):
                st.markdown("""
                ### DCF估值核心公式

                **1. 自由现金流（FCF）**
                ```
                FCF = 经营活动现金流 - 资本支出
                ```
                单位：亿元

                **2. 预测期现金流现值**
                ```
                PV_预测期 = Σ(FCF_t × (1 + g)^t) / (1 + WACC)^t
                ```
                其中：
                - FCF_t: 第t年的自由现金流
                - g: 现金流增长率
                - WACC: 加权平均资本成本（折现率）
                - t: 预测年份

                **3. 终值（Terminal Value）**
                ```
                终值 = [FCF_预测期最后一年 × (1 + g_永续)] / (WACC - g_永续)
                PV_终值 = 终值 / (1 + WACC)^预测年数
                ```

                **4. 企业价值**
                ```
                企业价值 = PV_预测期 + PV_终值
                ```

                **5. 股权价值**
                ```
                股权价值 = 企业价值 - 净债务
                净债务 = 有息债务 - 现金及等价物
                ```

                **6. 估值溢价/折价**
                ```
                估值溢价 = (DCF股权价值 - 账面股权价值) / 账面股权价值 × 100%
                ```

                ### 参数设置建议

                **现金流增长率（g）**
                - 成熟企业：3-8%
                - 成长企业：8-15%
                - 周期性企业：使用历史平均水平

                **折现率（WACC）**
                - 稳健企业：8-10%
                - 风险较高企业：10-15%
                - 可使用CAPM模型计算

                **永续增长率（g_永续）**
                - 通常设置为2-3%（接近长期GDP增长率）
                - 不应超过经济增长率

                ### 投资建议

                **估值溢价 > 20%（可能高估）**
                - DCF估值显著高于账面价值
                - 股价可能已经充分反映未来增长预期
                - 建议谨慎投资或等待更好时机

                **估值溢价 ±20%（相对合理）**
                - DCF估值与账面价值基本一致
                - 股价相对合理
                - 可以继续持有或适当配置

                **估值溢价 < -20%（可能低估）**
                - DCF估值显著低于账面价值
                - 股价可能被市场低估
                - 值得深入研究和关注
                """)

            return True

        except Exception as e:
            st.error(f"DCF估值分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
