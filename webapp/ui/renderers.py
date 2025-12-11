"""
专门的渲染器 - 各种表格的渲染
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.data_accessor import format_financial_number, parse_amount, get_field_value


def render_cash_safety_table(calculation_details: Dict):
    """显示货币资金安全计算表格"""
    raw_data = calculation_details.get("raw_data", [])
    calculated_data = calculation_details.get("calculated_data", [])

    if not raw_data or not calculated_data:
        st.warning("暂无数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    raw_data_sorted = sorted(raw_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in raw_data_sorted]

    def format_ratio(value):
        """格式化比率：小数点后两位，分母为0时显示100%"""
        try:
            if pd.isna(value):
                return "100.00"
            num_value = float(value)
            # 如果分母为0导致的无限大值，显示为100%
            if num_value == float('inf') or num_value > 999999:
                return "100.00"
            return f"{num_value:.2f}"
        except (ValueError, TypeError):
            return "100.00"

    # 第1行：货币资金
    cash_row = {"指标": "货币资金(百万元)"}
    for item in raw_data_sorted:
        cash_row[item["报告期"]] = format_financial_number(item["货币资金(百万元)"])
    table_data.append(cash_row)

    # 第2行：交易性金融资产
    financial_assets_row = {"指标": "交易性金融资产(百万元)"}
    for item in raw_data_sorted:
        financial_assets_row[item["报告期"]] = format_financial_number(item["交易性金融资产(百万元)"])
    table_data.append(financial_assets_row)

    # 第3行：短期借款
    short_debt_row = {"指标": "短期借款(百万元)"}
    for item in raw_data_sorted:
        short_debt_row[item["报告期"]] = format_financial_number(item["短期借款(百万元)"])
    table_data.append(short_debt_row)

    # 第4行：长期借款
    long_debt_row = {"指标": "长期借款(百万元)"}
    for item in raw_data_sorted:
        long_debt_row[item["报告期"]] = format_financial_number(item["长期借款(百万元)"])
    table_data.append(long_debt_row)

    # 第5行：有息负债总额
    interest_debt_map = {item["报告期"]: item["有息负债(百万元)"] for item in calculated_data}
    interest_debt_row = {"指标": "有息负债(百万元)"}
    for year in years:
        interest_debt_row[year] = format_financial_number(interest_debt_map.get(year, 0))
    table_data.append(interest_debt_row)

    # 第6行：货币资金安全比率
    safety_ratio_map = {item["报告期"]: item["货币资金安全比率"] for item in calculated_data}
    safety_ratio_row = {"指标": "货币资金安全比率(%)"}
    for year in years:
        safety_ratio_row[year] = format_ratio(safety_ratio_map.get(year, "N/A"))
    table_data.append(safety_ratio_row)

    # 第7行：总覆盖率
    coverage_ratio_map = {item["报告期"]: item["总覆盖率"] for item in calculated_data}
    coverage_ratio_row = {"指标": "总覆盖率(%)"}
    for year in years:
        coverage_ratio_row[year] = format_ratio(coverage_ratio_map.get(year, "N/A"))
    table_data.append(coverage_ratio_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, width='stretch')


def render_cash_anomaly_table(calculation_details: Dict):
    """显示货币资金异常计算表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    def format_ratio(value):
        """格式化比率：小数点后两位，分母为0时显示100%"""
        try:
            if pd.isna(value):
                return "100.00"
            num_value = float(value)
            # 如果分母为0导致的无限大值，显示为100%
            if num_value == float('inf') or num_value > 999999:
                return "100.00"
            return f"{num_value:.2f}"
        except (ValueError, TypeError):
            return "100.00"

    # 第1行：货币资金
    cash_row = {"指标": "货币资金(百万元)"}
    for item in detailed_data_sorted:
        cash_row[item["报告期"]] = format_financial_number(item["货币资金(百万元)"])
    table_data.append(cash_row)

    # 第2行：短期借款
    short_debt_row = {"指标": "短期借款(百万元)"}
    for item in detailed_data_sorted:
        short_debt_row[item["报告期"]] = format_financial_number(item["短期借款(百万元)"])
    table_data.append(short_debt_row)

    # 第3行：利息收入
    interest_income_row = {"指标": "利息收入(百万元)"}
    for item in detailed_data_sorted:
        interest_income_row[item["报告期"]] = format_financial_number(item["利息收入(百万元)"])
    table_data.append(interest_income_row)

    # 第4行：资金覆盖度
    coverage_row = {"指标": "资金覆盖度(%)"}
    for item in detailed_data_sorted:
        coverage_row[item["报告期"]] = format_ratio(item["资金覆盖度"])
    table_data.append(coverage_row)

    # 第5行：估算利率
    rate_row = {"指标": "估算利率(%)"}
    for item in detailed_data_sorted:
        rate = item.get("估算利率", 0)
        try:
            if rate == "N/A" or pd.isna(rate):
                rate_row[item["报告期"]] = "N/A"
            else:
                rate_row[item["报告期"]] = f"{float(rate):.2f}%"
        except (ValueError, TypeError):
            rate_row[item["报告期"]] = "N/A"
    table_data.append(rate_row)

    # 第6行：异常程度
    anomaly_row = {"指标": "异常程度"}
    for item in detailed_data_sorted:
        anomaly_row[item["报告期"]] = item["异常程度"]
    table_data.append(anomaly_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, width='stretch')


def render_notes_receivable_table(calculation_details: Dict):
    """显示应收票据健康度计算表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无应收票据数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    # 第1行：应收票据及应收账款
    notes_receivable_row = {"指标": "应收票据及应收账款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("应收票据及应收账款(百万元)", 0)
        notes_receivable_row[item["报告期"]] = format_financial_number(value)
    table_data.append(notes_receivable_row)

    # 第2行：总资产
    total_assets_row = {"指标": "总资产(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("总资产(百万元)", 0)
        total_assets_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_assets_row)

    # 第3行：占总资产比例
    ratio_row = {"指标": "占总资产比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("占总资产比例(%)", 0)
        ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(ratio_row)

    # 第4行：评估结果
    assessment_row = {"指标": "评估结果"}
    for item in detailed_data_sorted:
        assessment = item.get("评估结果", "需要关注")
        assessment_row[item["报告期"]] = assessment
    table_data.append(assessment_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 📊 应收票据历史数据分析")
    st.dataframe(df, width='stretch')


def render_receivables_table(calculation_details: Dict):
    """显示应收账款健康度计算表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无应收账款数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    # 第1行：应收账款
    receivables_row = {"指标": "应收账款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("应收账款(百万元)", 0)
        receivables_row[item["报告期"]] = format_financial_number(value)
    table_data.append(receivables_row)

    # 第2行：总资产
    total_assets_row = {"指标": "总资产(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("总资产(百万元)", 0)
        total_assets_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_assets_row)

    # 第3行：营业收入
    revenue_row = {"指标": "营业收入(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("营业收入(百万元)", 0)
        revenue_row[item["报告期"]] = format_financial_number(value)
    table_data.append(revenue_row)

    # 第4行：应收账款占总资产比例
    assets_ratio_row = {"指标": "应收账款占总资产比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("应收账款占总资产比例(%)", 0)
        assets_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(assets_ratio_row)

    # 第5行：应收账款周转率
    turnover_row = {"指标": "应收账款周转率(次)"}
    for item in detailed_data_sorted:
        turnover = item.get("应收账款周转率(次)", "N/A")
        turnover_row[item["报告期"]] = turnover
    table_data.append(turnover_row)

    # 第6行：评估结果
    assessment_row = {"指标": "评估结果"}
    for item in detailed_data_sorted:
        assessment = item.get("评估结果", "需要关注")
        assessment_row[item["报告期"]] = assessment
    table_data.append(assessment_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 📊 应收账款健康度分析")
    st.dataframe(df, width='stretch')


def render_other_receivables_table(calculation_details: Dict):
    """渲染其他应收款的详细分析表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无其他应收款数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]


    # 第1行：其他应收款
    other_receivables_row = {"指标": "其他应收款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("其他应收款(百万元)", 0)
        other_receivables_row[item["报告期"]] = format_financial_number(value)
    table_data.append(other_receivables_row)

    # 第2行：其中：应收利息
    interest_receivable_row = {"指标": "其中：应收利息(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("其中：应收利息(百万元)", 0)
        interest_receivable_row[item["报告期"]] = format_financial_number(value)
    table_data.append(interest_receivable_row)

    # 第3行：剔除应收利息后的其他应收款
    other_receivables_exclude_interest_row = {"指标": "剔除应收利息后的其他应收款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("剔除应收利息后的其他应收款(百万元)", 0)
        other_receivables_exclude_interest_row[item["报告期"]] = format_financial_number(value)
    table_data.append(other_receivables_exclude_interest_row)

    # 第4行：营业收入
    revenue_row = {"指标": "营业收入(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("营业收入(百万元)", 0)
        revenue_row[item["报告期"]] = format_financial_number(value)
    table_data.append(revenue_row)

    # 第5行：其他应收款占营业收入比例
    ratio_row = {"指标": "其他应收款占营业收入比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get('其他应收款占营业收入比例', 0)
        ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(ratio_row)

    # 第6行：风险评估
    risk_row = {"指标": "风险评估"}
    for item in detailed_data_sorted:
        risk_ratio = item.get('其他应收款占营业收入比例', 0)
        risk_amount = item.get("剔除应收利息后的其他应收款(百万元)", 0)
        if risk_ratio > 5 or risk_amount > 10000:  # 5%或100亿元
            risk_row[item["报告期"]] = "⚠️ 异常"
        else:
            risk_row[item["报告期"]] = "✅ 正常"
    table_data.append(risk_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 📊 其他应收款历史数据分析")
    st.dataframe(df, width='stretch')


def render_bad_debt_provision_table(calculation_details: Dict):
    """渲染坏账准备计提合理性分析表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无坏账准备数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    def format_ratio(value):
        """格式化比率：小数点后两位，百分号显示"""
        try:
            if pd.isna(value):
                return "0.00%"
            num_value = float(value)
            return f"{num_value:.2f}%"
        except (ValueError, TypeError):
            return "0.00%"

    # 第1行：应收账款
    receivables_row = {"指标": "应收账款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("应收账款(百万元)", 0)
        receivables_row[item["报告期"]] = format_financial_number(value)
    table_data.append(receivables_row)

    # 第2行：其他应收款
    other_receivables_row = {"指标": "其他应收款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("其他应收款(百万元)", 0)
        other_receivables_row[item["报告期"]] = format_financial_number(value)
    table_data.append(other_receivables_row)

    # 第3行：应收款项合计
    total_receivables_row = {"指标": "应收款项合计(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("应收款项合计(百万元)", 0)
        total_receivables_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_receivables_row)

    # 第4行：资产减值损失
    asset_impairment_row = {"指标": "资产减值损失(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("资产减值损失(百万元)", 0)
        asset_impairment_row[item["报告期"]] = format_financial_number(value)
    table_data.append(asset_impairment_row)

    # 第5行：信用减值损失
    credit_impairment_row = {"指标": "信用减值损失(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("信用减值损失(百万元)", 0)
        credit_impairment_row[item["报告期"]] = format_financial_number(value)
    table_data.append(credit_impairment_row)

    # 第6行：总减值损失
    total_impairment_row = {"指标": "总减值损失(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("总减值损失(百万元)", 0)
        total_impairment_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_impairment_row)

    # 第7行：坏账准备计提比例
    provision_rate_row = {"指标": "坏账准备计提比例(%)"}
    for item in detailed_data_sorted:
        rate = item.get("坏账准备计提比例", 0)
        provision_rate_row[item["报告期"]] = format_ratio(rate)
    table_data.append(provision_rate_row)

    # 第8行：计提合理性评估
    assessment_row = {"指标": "计提合理性评估"}
    for item in detailed_data_sorted:
        assessment = item.get("计提合理性评估", "需要关注")
        # 添加表情符号增强可读性
        if assessment == "异常偏高":
            assessment_row[item["报告期"]] = "🔴 " + assessment
        elif assessment == "计提不足":
            assessment_row[item["报告期"]] = "⚠️ " + assessment
        elif assessment == "需要关注":
            assessment_row[item["报告期"]] = "🟡 " + assessment
        else:  # 正常
            assessment_row[item["报告期"]] = "✅ " + assessment
    table_data.append(assessment_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 🔍 坏账准备计提合理性分析")
    st.dataframe(df, width='stretch')

    # 显示分析说明
    with st.expander("📖 分析说明", expanded=False):
        st.markdown("""
        **坏账准备计提合理性分析说明：**

        1. **计算逻辑**：
           - 应收款项合计 = 应收账款 + 其他应收款
           - 总减值损失 = 资产减值损失 + 信用减值损失
           - 坏账准备计提比例 = 总减值损失 / 应收款项合计

        2. **合理性评估标准**：
           - **✅ 正常**：计提比例在 1%~5% 之间
           - **🟡 需要关注**：计提比例在 0.5%~1% 或 5%~8% 之间
           - **⚠️ 计提不足**：计提比例 < 0.5%（可能风险准备不足）
           - **🔴 异常偏高**：计提比例 > 8%（可能存在利润调节）

        3. **分析要点**：
           - 计提比例应与业务特性和经济环境相匹配
           - 连续观察多年趋势，分析计提政策的一致性
           - 结合行业特点和公司历史经验进行综合判断
        """)


def render_prepaid_expenses_table(calculation_details: Dict):
    """渲染预付账款的详细分析表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无预付账款数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    # 第1行：预付账款
    prepaid_row = {"指标": "预付账款(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("预付账款(百万元)", 0)
        prepaid_row[item["报告期"]] = format_financial_number(value)
    table_data.append(prepaid_row)

    # 第2行：总资产
    total_assets_row = {"指标": "总资产(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("总资产(百万元)", 0)
        total_assets_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_assets_row)

    # 第3行：营业收入
    revenue_row = {"指标": "营业收入(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("营业收入(百万元)", 0)
        revenue_row[item["报告期"]] = format_financial_number(value)
    table_data.append(revenue_row)

    # 第4行：营业成本
    cost_row = {"指标": "营业成本(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("营业成本(百万元)", 0)
        cost_row[item["报告期"]] = format_financial_number(value)
    table_data.append(cost_row)

    # 第5行：预付账款占总资产比例
    assets_ratio_row = {"指标": "预付账款占总资产比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("预付账款占总资产比例(%)", 0)
        assets_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(assets_ratio_row)

    # 第6行：预付账款占收入比例
    revenue_ratio_row = {"指标": "预付账款占收入比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("预付账款占收入比例(%)", 0)
        revenue_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(revenue_ratio_row)

    # 第7行：预付账款占成本比例
    cost_ratio_row = {"指标": "预付账款占成本比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("预付账款占成本比例(%)", 0)
        cost_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(cost_ratio_row)

    # 第8行：评估结果
    assessment_row = {"指标": "评估结果"}
    for item in detailed_data_sorted:
        assessment = item.get("评估结果", "需要关注")
        assessment_row[item["报告期"]] = assessment
    table_data.append(assessment_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 📊 预付账款异常分析")
    st.dataframe(df, width='stretch')


def render_inventory_risk_table(calculation_details: Dict):
    """渲染存货风险分析表格"""
    detailed_data = calculation_details.get("detailed_data", [])

    if not detailed_data:
        st.warning("暂无存货数据")
        return

    # 构建统一表格
    table_data = []

    # 按年份排序（最新在前）
    detailed_data_sorted = sorted(detailed_data, key=lambda x: x["报告期"], reverse=True)

    # 提取年份列
    years = [item["报告期"] for item in detailed_data_sorted]

    # 第1行：存货
    inventory_row = {"指标": "存货(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("存货(百万元)", 0)
        inventory_row[item["报告期"]] = format_financial_number(value)
    table_data.append(inventory_row)

    # 第2行：总资产
    total_assets_row = {"指标": "总资产(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("总资产(百万元)", 0)
        total_assets_row[item["报告期"]] = format_financial_number(value)
    table_data.append(total_assets_row)

    # 第3行：营业成本
    operating_cost_row = {"指标": "营业成本(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("营业成本(百万元)", 0)
        operating_cost_row[item["报告期"]] = format_financial_number(value)
    table_data.append(operating_cost_row)

    # 第4行：资产减值损失
    impairment_row = {"指标": "资产减值损失(百万元)"}
    for item in detailed_data_sorted:
        value = item.get("资产减值损失(百万元)", 0)
        impairment_row[item["报告期"]] = format_financial_number(value)
    table_data.append(impairment_row)

    # 第5行：存货占总资产比例
    assets_ratio_row = {"指标": "存货占总资产比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("存货占总资产比例(%)", 0)
        assets_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(assets_ratio_row)

    # 第6行：存货减值计提比例
    provision_ratio_row = {"指标": "存货减值计提比例(%)"}
    for item in detailed_data_sorted:
        ratio = item.get("存货减值计提比例(%)", 0)
        provision_ratio_row[item["报告期"]] = f"{ratio:.2f}%"
    table_data.append(provision_ratio_row)

    # 第7行：存货周转率
    turnover_row = {"指标": "存货周转率(次)"}
    for item in detailed_data_sorted:
        turnover = item.get("存货周转率(次)", 0)
        turnover_row[item["报告期"]] = f"{turnover:.2f}"
    table_data.append(turnover_row)

    # 第8行：风险评估
    risk_row = {"指标": "风险评估"}
    for item in detailed_data_sorted:
        risk_level = item.get("评估结果", "需要关注")
        risk_row[item["报告期"]] = risk_level
    table_data.append(risk_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.markdown("#### 📊 存货风险分析")
    st.dataframe(df, width='stretch')

    # 显示分析说明
    with st.expander("📖 分析说明", expanded=False):
        st.markdown("""
        **存货风险分析说明：**

        1. **关键指标计算**：
           - 存货占总资产比例 = 存货 ÷ 总资产 × 100%
           - 存货减值计提比例 = 资产减值损失 ÷ 存货 × 100%
           - 存货周转率 = 营业成本 ÷ 存货

        2. **风险评估标准**：
           - **✅ 正常**：各项指标处于合理范围
           - **🟡 需要关注**：存货占比>20%或周转率<2次或未计提减值
           - **⚠️ 异常**：存货占比>30%或周转率<1次

        3. **风险关注点**：
           - 存货占总资产比例过高可能表示滞销风险
           - 存货周转率低说明库存管理效率低下
           - 未计提存货减值准备可能存在资产虚高风险
        """)


def generate_financial_summary(balance_df: pd.DataFrame, stock_code: str) -> str:
    """生成财报数据汇总（markdown格式）"""
    if balance_df.empty:
        return "# 财报数据汇总\n\n暂无数据"

    # 提取关键数据
    summary_data = []
    for _, row in balance_df.iterrows():
        report_period = row["报告期"]
        # 使用新的数据访问方式
        try:
            # 获取原始数值并转换为百万元
            cash = parse_amount(get_field_value(row, "货币资金")) / 1000000
            financial_assets = parse_amount(get_field_value(row, "交易性金融资产")) / 1000000
            short_debt = parse_amount(get_field_value(row, "短期借款")) / 1000000
            long_debt = parse_amount(get_field_value(row, "长期借款")) / 1000000
            # 应付债券字段不存在，设为0
            bonds = 0
            total_assets = parse_amount(get_field_value(row, "*资产合计")) / 1000000
            total_liabilities = parse_amount(get_field_value(row, "*负债合计")) / 1000000
        except:
            # 如果字段不存在，使用0值
            cash = financial_assets = short_debt = long_debt = bonds = 0.0
            total_assets = total_liabilities = 0.0

        summary_data.append({
            "报告期": report_period,
            "货币资金": format_financial_number(cash),
            "交易性金融资产": format_financial_number(financial_assets),
            "短期借款": format_financial_number(short_debt),
            "长期借款": format_financial_number(long_debt),
            "应付债券": format_financial_number(bonds),
            "资产总计": format_financial_number(total_assets),
            "负债总计": format_financial_number(total_liabilities)
        })

    # 生成markdown表格
    markdown = f"""# {stock_code} 财报数据汇总

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 资产负债表关键数据
| 项目 | {" | ".join([item['报告期'] for item in summary_data])} |
|------|{"-".join(['|'] * (len(summary_data) + 1))}|
| 货币资金 | {" | ".join([item['货币资金'] for item in summary_data])} |
| 交易性金融资产 | {" | ".join([item['交易性金融资产'] for item in summary_data])} |
| 短期借款 | {" | ".join([item['短期借款'] for item in summary_data])} |
| 长期借款 | {" | ".join([item['长期借款'] for item in summary_data])} |
| 应付债券 | {" | ".join([item['应付债券'] for item in summary_data])} |
| 资产总计 | {" | ".join([item['资产总计'] for item in summary_data])} |
| 负债总计 | {" | ".join([item['负债总计'] for item in summary_data])} |

*数据单位：百万元人民币*
"""

    return markdown