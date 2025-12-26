"""
投入资本回报率（ROIC）分析组件
"""

import traceback


class ROICComponent:
    """投入资本回报率分析组件"""

    title = "💎 投入资本回报率（ROIC）"

    @staticmethod
    def render(symbol: str, market: str, years: int) -> bool:
        """渲染投入资本回报率分析组件

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

        from services.calculator import Calculator
        from services import data_service

        try:
            st.subheader(
                ROICComponent.title,
                help="""
                **投入资本回报率（ROIC = Return on Invested Capital）**

                **核心问题**：公司每投入一元钱能创造多少回报？

                **什么是ROIC？**
                ROIC = NOPAT（税后净营业利润）÷ 投入资本
                - 衡量公司资本使用效率的**核心指标**
                - 巴菲特最看重的指标之一
                - 比ROE更真实，排除了资本结构的影响

                **计算公式：**
                - NOPAT = EBIT × (1 - 税率)
                - 投入资本 = 股东权益 + 有息负债
                - ROIC = NOPAT ÷ 投入资本 × 100%

                **运营ROIC（剔除非经营性资产）：**
                - 剔除了不直接参与业务运营的资产（商誉、现金等）
                - 运营投入资本 = 投入资本 - 非经营性资产
                - 运营ROIC = NOPAT ÷ 运营投入资本 × 100%
                - 能更准确地反映企业核心业务的投资回报率

                **指标解读：**
                - **> 20%**：卓越！公司资本利用效率极高，护城河深厚
                - **15%-20%**：优秀，公司资本利用效率很高
                - **10%-15%**：良好，公司资本利用效率较好
                - **< 10%**：一般，资本利用效率较低

                **为什么ROIC比ROE更重要？**
                - ROE受杠杆影响，债务高会让ROE虚高
                - ROIC衡量的是**业务本身**的回报能力
                - 真正的价值创造者，ROIC > WACC（加权平均资本成本）

                **投资意义：**
                ROIC持续 > 15% 的公司，往往是长期投资的好标的！
                运营ROIC通常高于ROIC，因为剔除了非经营性资产。
                """
            )

            with st.spinner(f"正在获取 {market} 股票 {symbol} 的ROIC数据..."):
                try:
                    result = Calculator.calculate_roic(symbol, market, years)
                    (
                        roic_data,
                        operating_roic_data,
                        dupont_data,
                        roic_display_cols,
                        operating_display_cols,
                        dupont_display_cols,
                        roic_metrics,
                        operating_roic_metrics,
                        exclusion_info
                    ) = result
                except data_service.DataServiceError as e:
                    data_service.handle_data_service_error(e)
                    return False

            # ========== 第1行：ROIC图表 ==========
            st.markdown("#### 📈 ROIC（全投入资本）")

            fig1 = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 投入资本回报率分析"]
            )

            # 添加投入资本柱状图（主Y轴）
            fig1.add_trace(
                go.Bar(
                    x=roic_data['年份'],
                    y=roic_data['投入资本'],
                    name='投入资本',
                    marker_color='lightgreen',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加NOPAT柱状图（主Y轴）
            fig1.add_trace(
                go.Bar(
                    x=roic_data['年份'],
                    y=roic_data['NOPAT'],
                    name='NOPAT（税后净营业利润）',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加ROIC折线图（副Y轴）
            fig1.add_trace(
                go.Scatter(
                    x=roic_data['年份'],
                    y=roic_data['ROIC'],
                    name='ROIC',
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )

            # 添加参考线（15%优秀线）
            fig1.add_trace(
                go.Scatter(
                    x=roic_data['年份'],
                    y=[15] * len(roic_data['年份']),
                    mode='lines',
                    name='优秀线 (15%)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig1.update_yaxes(title_text="金额", secondary_y=False)
            fig1.update_yaxes(title_text="ROIC (%)", secondary_y=True)

            # 设置布局
            fig1.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=450,
                barmode='group',
                legend={'traceorder': 'normal'},
                showlegend=True
            )

            # 交换前两个柱状图的位置，使投入资本显示在左边
            traces1 = list(fig1.data)
            traces1[0], traces1[1] = traces1[1], traces1[0]
            fig1.data = tuple(traces1)

            # 显示第1行图表
            st.plotly_chart(fig1, width='stretch')

            # ROIC关键指标
            st.markdown("##### 📊 ROIC关键指标")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label=f"{years}年平均ROIC",
                    value=f"{roic_metrics['avg_roic']:.2f}%",
                    delta=None,
                    help="ROIC = NOPAT ÷ 投入资本 × 100%"
                )

            with col2:
                st.metric(
                    label="最新ROIC",
                    value=f"{roic_metrics['latest_roic']:.2f}%",
                    delta=None,
                    help="最新年度的ROIC值"
                )

            with col3:
                st.metric(
                    label="最低ROIC",
                    value=f"{roic_metrics['min_roic']:.2f}%",
                    delta=None,
                    help=f"{years}年内最低ROIC"
                )

            with col4:
                st.metric(
                    label="最高ROIC",
                    value=f"{roic_metrics['max_roic']:.2f}%",
                    delta=None,
                    help=f"{years}年内最高ROIC"
                )

            st.markdown("---")

            # ========== 第2行：ROIC拆解分析 ==========
            help_text = """
            **杜邦分析法拆解ROIC**：ROIC = NOPAT利润率 × 资本周转率

            **NOPAT利润率（盈利能力）**：
            - 公式：NOPAT利润率 = NOPAT ÷ 收入 × 100%
            - 含义：每单位收入创造的税后净营业利润
            - 反映：公司的定价权和成本控制能力

            **资本周转率（营运效率）**：
            - 公式：资本周转率 = 收入 ÷ 投入资本
            - 含义：每单位投入资本产生的收入
            - 反映：公司的资产使用效率和营运能力

            **投资意义**：
            - 高利润率 + 高周转率 = 卓越企业（具有定价权和高效运营）
            - 高利润率 + 低周转率 = 品牌溢价型企业（奢侈品、高端制造）
            - 低利润率 + 高周转率 = 薄利多销型企业（零售、快消品）
            - 低利润率 + 低周转率 = 需要警惕的企业
            """

            st.markdown("#### 🔍 ROIC拆解分析（杜邦分析法）", help=help_text)

            # 创建拆解图表
            fig_dupont = make_subplots(
                specs=[[{"secondary_y": False}]],
                subplot_titles=[f"{symbol} - ROIC杜邦拆解：利润率 vs 周转率"]
            )

            # 添加NOPAT利润率折线图
            fig_dupont.add_trace(
                go.Scatter(
                    x=dupont_data['年份'],
                    y=dupont_data['NOPAT利润率'],
                    name='NOPAT利润率',
                    mode='lines+markers',
                    line=dict(color='blue', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=False
            )

            # 添加资本周转率折线图（转换为百分比以便对比）
            fig_dupont.add_trace(
                go.Scatter(
                    x=dupont_data['年份'],
                    y=dupont_data['资本周转率'] * 100,
                    name='资本周转率 (×100)',
                    mode='lines+markers',
                    line=dict(color='green', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=False
            )

            # 设置Y轴标题
            fig_dupont.update_yaxes(title_text="%")

            # 设置布局
            fig_dupont.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=450,
                legend={'traceorder': 'normal'},
                showlegend=True
            )

            # 显示拆解图表
            st.plotly_chart(fig_dupont, width='stretch')

            # ROIC拆解关键指标
            st.markdown("##### 📊 ROIC拆解关键指标")
            col9, col10, col11, col12 = st.columns(4)

            with col9:
                st.metric(
                    label=f"{years}年平均NOPAT利润率",
                    value=f"{roic_metrics['avg_nopat_margin']:.2f}%",
                    delta=None,
                    help="盈利能力：每单位收入创造的税后净营业利润"
                )

            with col10:
                st.metric(
                    label="最新NOPAT利润率",
                    value=f"{roic_metrics['latest_nopat_margin']:.2f}%",
                    delta=None,
                    help="最新年度的NOPAT利润率"
                )

            st.markdown("---")

            # ========== 第3行：运营ROIC图表 ==========
            st.markdown("#### 🚀 运营ROIC（剔除非经营性资产）")

            # 显示非经营性资产剔除说明
            st.info(f"💡 **{exclusion_info['exclusion_note']}**")

            fig2 = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=[f"{symbol} - 运营投入资本回报率分析"]
            )

            # 添加运营投入资本柱状图（主Y轴）
            fig2.add_trace(
                go.Bar(
                    x=operating_roic_data['年份'],
                    y=operating_roic_data['运营投入资本'],
                    name='运营投入资本',
                    marker_color='lightgreen',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加NOPAT柱状图（主Y轴）
            fig2.add_trace(
                go.Bar(
                    x=operating_roic_data['年份'],
                    y=operating_roic_data['NOPAT'],
                    name='NOPAT（税后净营业利润）',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                secondary_y=False
            )

            # 添加非经营性资产柱状图（主Y轴）
            fig2.add_trace(
                go.Bar(
                    x=operating_roic_data['年份'],
                    y=operating_roic_data['非经营性资产'],
                    name='非经营性资产（已剔除）',
                    marker_color='lightgray',
                    opacity=0.5
                ),
                secondary_y=False
            )

            # 添加运营ROIC折线图（副Y轴）
            fig2.add_trace(
                go.Scatter(
                    x=operating_roic_data['年份'],
                    y=operating_roic_data['运营ROIC'],
                    name='运营ROIC',
                    mode='lines+markers',
                    line=dict(color='darkgreen', width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )

            # 添加参考线（15%优秀线）
            fig2.add_trace(
                go.Scatter(
                    x=operating_roic_data['年份'],
                    y=[15] * len(operating_roic_data['年份']),
                    mode='lines',
                    name='优秀线 (15%)',
                    line=dict(color='orange', width=2, dash='dash'),
                    hoverinfo='skip'
                ),
                secondary_y=True
            )

            # 设置Y轴标题
            fig2.update_yaxes(title_text="金额", secondary_y=False)
            fig2.update_yaxes(title_text="运营ROIC (%)", secondary_y=True)

            # 设置布局
            fig2.update_layout(
                xaxis_title="年份",
                hovermode="x unified",
                height=450,
                barmode='group',
                legend={'traceorder': 'normal'},
                showlegend=True
            )

            # 交换柱状图的位置，使运营投入资本显示在最左边
            traces2 = list(fig2.data)
            # 顺序调整为：运营投入资本, NOPAT, 非经营性资产
            traces2[0], traces2[1], traces2[2] = traces2[1], traces2[0], traces2[2]
            fig2.data = tuple(traces2)

            # 显示第2行图表
            st.plotly_chart(fig2, width='stretch')

            # 运营ROIC关键指标
            st.markdown("##### 📊 运营ROIC关键指标")
            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.metric(
                    label=f"{years}年平均运营ROIC",
                    value=f"{operating_roic_metrics['avg_operating_roic']:.2f}%",
                    delta=None
                )

            with col6:
                st.metric(
                    label="最新运营ROIC",
                    value=f"{operating_roic_metrics['latest_operating_roic']:.2f}%",
                    delta=None
                )

            with col7:
                st.metric(
                    label="最低运营ROIC",
                    value=f"{operating_roic_metrics['min_operating_roic']:.2f}%",
                    delta=None
                )

            with col8:
                st.metric(
                    label="最高运营ROIC",
                    value=f"{operating_roic_metrics['max_operating_roic']:.2f}%",
                    delta=None
                )

            # 运营ROIC辅助指标
            st.markdown("##### 💡 运营ROIC辅助指标")
            col9, col10 = st.columns(2)

            with col9:
                st.metric(
                    label="平均运营投入资本",
                    value=f"{operating_roic_metrics['avg_operating_capital']:.2f}",
                    delta=None,
                    help="剔除非经营性资产后的投入资本"
                )

            with col10:
                avg_capital = roic_metrics['avg_capital']
                avg_operating_capital = operating_roic_metrics['avg_operating_capital']
                avg_exclusion = avg_capital - avg_operating_capital
                exclusion_ratio = (avg_exclusion / avg_capital * 100) if avg_capital != 0 else 0
                st.metric(
                    label="平均非经营性资产占比",
                    value=f"{exclusion_ratio:.2f}%",
                    delta=None,
                    help="非经营性资产占总投入资本的比例"
                )

            # ========== 折叠的原始数据表格 ==========
            st.markdown("---")
            with st.expander("📊 查看普通ROIC计算用原始数据"):
                st.dataframe(roic_data[roic_display_cols], width='stretch', hide_index=True)

            with st.expander("📊 查看ROIC拆解分析数据"):
                st.dataframe(dupont_data[dupont_display_cols], width='stretch', hide_index=True)

            with st.expander("📊 查看运营ROIC计算用原始数据"):
                st.dataframe(operating_roic_data[operating_display_cols], width='stretch', hide_index=True)

            return True

        except Exception as e:
            st.error(f"投入资本回报率分析失败：{str(e)}")
            st.error(traceback.format_exc())
            return False
