"""
现金流类型分析组件
"""

import traceback


class CashFlowPatternComponent:
    """现金流类型分析组件"""

    title = "💵 现金流类型分析"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染现金流类型分析组件

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

        from services.calculators.cash_flow_pattern import calculate as calculate_cfp
        from services import data_service

        try:
            st.subheader(
                CashFlowPatternComponent.title,
                help="""
                **公司整体现金流类型分析**

                **核心问题**：公司现金流的流入流出模式是什么？

                **什么是现金流类型？**
                根据经营、投资、筹资三种现金流的正负组合，可以判断企业所处的生命周期和经营状况：

                **🐄 奶牛型（最佳模式）**
                - 经营现金流为正（+），投资现金流为负（-）
                - 主业强劲造血，投资扩张+分红回购
                - 典型公司：贵州茅台、成熟的消费品牌

                **🐂 蛮牛型（扩张激进型）**
                - 经营现金流为正（+），投资现金流为负（-），筹资现金流为正（+）
                - 主业造血，但投资远超现金流需融资补血
                - 典型公司：高速扩张期的成长型公司

                **🧚 妖精型（不依赖主业型）**
                - 经营现金流为负（-），投资现金流为正（+）
                - 主业不赚钱，靠变卖资产或投资收益维持
                - 典型公司：投资控股型公司

                **🐄 病牛型（经营困难型）**
                - 经营现金流为负（-），投资现金流为正（+），筹资现金流为正（+）
                - 主业失血，靠卖资产+借款度日
                - 典型公司：主营业务陷入困境的公司

                **🃏 骗吃型（庞氏骗局型）**
                - 经营现金流为负（-），投资现金流为负（-），筹资现金流为正（+）
                - 主业失血+疯狂投资，完全靠外部输血
                - 典型公司：商业模式未跑通的公司

                **投资意义：**
                - 现金流类型稳定且优质的公司，往往是长期投资的好标的
                - 关注现金流类型的演变，判断公司所处生命周期的变化
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的现金流类型数据..."):
                try:
                    result = calculate_cfp(symbol, market, years)
                    pattern_data, display_cols, stats = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # 创建分组柱状图
            fig = go.Figure()

            # 添加经营现金流柱状图
            fig.add_trace(
                go.Bar(
                    x=pattern_data['年份'],
                    y=pattern_data['经营现金流'],
                    name='经营现金流',
                    marker_color='lightblue',
                    opacity=0.8,
                    text=pattern_data['类型名称'],
                    textposition='outside',
                    textfont=dict(size=10)
                )
            )

            # 添加投资现金流柱状图
            fig.add_trace(
                go.Bar(
                    x=pattern_data['年份'],
                    y=pattern_data['投资现金流'],
                    name='投资现金流',
                    marker_color='lightcoral',
                    opacity=0.8
                )
            )

            # 添加筹资现金流柱状图
            fig.add_trace(
                go.Bar(
                    x=pattern_data['年份'],
                    y=pattern_data['筹资现金流'],
                    name='筹资现金流',
                    marker_color='lightgreen',
                    opacity=0.8
                )
            )

            # 设置布局
            fig.update_layout(
                title=f"{symbol} - 现金流类型分析",
                xaxis_title="年份",
                yaxis_title="现金流金额",
                hovermode="x unified",
                height=500,
                barmode='group',
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )

            # 显示图表（使用动态key避免重复渲染时的冲突）
            chart_key = f"cash_flow_pattern_{symbol}_{market}"
            st.plotly_chart(fig, width='stretch', key=chart_key)

            # 显示关键指标
            st.markdown("##### 📊 当前类型")
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="最新现金流类型",
                    value=stats['latest_type'],
                    help=f"模式：{stats['latest_pattern']}"
                )

            with col2:
                st.markdown(f"**类型说明**：{stats['latest_description']}")

            # 显示类型稳定性
            st.markdown("##### 📈 类型稳定性")
            col3, col4, col5 = st.columns(3)

            with col3:
                st.metric(
                    label="主导类型",
                    value=stats['dominant_type'],
                    help=f"{years}年内出现最多的类型"
                )

            with col4:
                st.metric(
                    label="主导类型年数",
                    value=f"{stats['dominant_count']} 年",
                    help=f"占 {stats['dominant_ratio']:.1f}%"
                )

            with col5:
                stability_score = "高" if stats['dominant_ratio'] >= 70 else "中" if stats['dominant_ratio'] >= 50 else "低"
                st.metric(
                    label="类型稳定性",
                    value=stability_score,
                    help=f"主导类型占比：{stats['dominant_ratio']:.1f}%"
                )

            # 显示累计现金流
            st.markdown("##### 💰 累计现金流与整体类型")

            # 第一行：整体类型结论（突出显示）
            st.info(f"""
            **📊 {stats['total_years']}年累计现金流整体类型：{stats['cumulative_type']}**

            模式：`{stats['cumulative_pattern']}`

            {stats['cumulative_description']}
            """)

            # 第二行：累计现金流数据
            col6, col7, col8, col9 = st.columns(4)

            with col6:
                st.metric(
                    label="累计经营现金流",
                    value=f"{stats['cumulative_operating']:.2f}",
                    delta=None,
                    help=f"{stats['total_years']}年累计经营活动现金流"
                )

            with col7:
                st.metric(
                    label="累计投资现金流",
                    value=f"{stats['cumulative_investing']:.2f}",
                    delta=None,
                    help=f"{stats['total_years']}年累计投资活动现金流"
                )

            with col8:
                st.metric(
                    label="累计筹资现金流",
                    value=f"{stats['cumulative_financing']:.2f}",
                    delta=None,
                    help=f"{stats['total_years']}年累计筹资活动现金流"
                )

            with col9:
                delta_value = "增加" if stats['cumulative_net'] > 0 else "减少"
                st.metric(
                    label="累计现金净额",
                    value=f"{stats['cumulative_net']:.2f}",
                    delta=delta_value,
                    help=f"{stats['total_years']}年三种现金流累计之和"
                )

            # 显示类型分布
            st.markdown("##### 📊 类型分布")
            distribution_df = pattern_data['类型名称'].value_counts().reset_index()
            distribution_df.columns = ['类型名称', '年数']
            distribution_df['占比'] = (distribution_df['年数'] / stats['total_years'] * 100).round(1)
            distribution_df = distribution_df.sort_values('年数', ascending=False)
            st.dataframe(distribution_df, width='stretch', hide_index=True)

            # 折叠的原始数据表格
            with st.expander("📊 查看计算用原始数据"):
                st.dataframe(pattern_data[display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"现金流类型分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
