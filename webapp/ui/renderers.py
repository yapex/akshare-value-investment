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

from core.data_accessor import format_accounting, parse_amount, get_field_value


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

    # 第1行：货币资金
    cash_row = {"指标": "货币资金(百万元)"}
    for item in raw_data_sorted:
        cash_row[item["报告期"]] = format_accounting(item["货币资金(百万元)"])
    table_data.append(cash_row)

    # 第2行：交易性金融资产
    financial_assets_row = {"指标": "交易性金融资产(百万元)"}
    for item in raw_data_sorted:
        financial_assets_row[item["报告期"]] = format_accounting(item["交易性金融资产(百万元)"])
    table_data.append(financial_assets_row)

    # 第3行：短期借款
    short_debt_row = {"指标": "短期借款(百万元)"}
    for item in raw_data_sorted:
        short_debt_row[item["报告期"]] = format_accounting(item["短期借款(百万元)"])
    table_data.append(short_debt_row)

    # 第4行：长期借款
    long_debt_row = {"指标": "长期借款(百万元)"}
    for item in raw_data_sorted:
        long_debt_row[item["报告期"]] = format_accounting(item["长期借款(百万元)"])
    table_data.append(long_debt_row)

    # 第5行：有息负债总额
    interest_debt_map = {item["报告期"]: item["有息负债(百万元)"] for item in calculated_data}
    interest_debt_row = {"指标": "有息负债(百万元)"}
    for year in years:
        interest_debt_row[year] = format_accounting(interest_debt_map.get(year, 0))
    table_data.append(interest_debt_row)

    # 第6行：货币资金安全比率
    safety_ratio_map = {item["报告期"]: item["货币资金安全比率"] for item in calculated_data}
    safety_ratio_row = {"指标": "货币资金安全比率"}
    for year in years:
        safety_ratio_row[year] = safety_ratio_map.get(year, "N/A")
    table_data.append(safety_ratio_row)

    # 第7行：总覆盖率
    coverage_ratio_map = {item["报告期"]: item["总覆盖率"] for item in calculated_data}
    coverage_ratio_row = {"指标": "总覆盖率"}
    for year in years:
        coverage_ratio_row[year] = coverage_ratio_map.get(year, "N/A")
    table_data.append(coverage_ratio_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)


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

    # 第1行：货币资金
    cash_row = {"指标": "货币资金(百万元)"}
    for item in detailed_data_sorted:
        cash_row[item["报告期"]] = item["货币资金(百万元)"]
    table_data.append(cash_row)

    # 第2行：短期借款
    short_debt_row = {"指标": "短期借款(百万元)"}
    for item in detailed_data_sorted:
        short_debt_row[item["报告期"]] = item["短期借款(百万元)"]
    table_data.append(short_debt_row)

    # 第3行：利息收入
    interest_income_row = {"指标": "利息收入(百万元)"}
    for item in detailed_data_sorted:
        interest_income_row[item["报告期"]] = item["利息收入(百万元)"]
    table_data.append(interest_income_row)

    # 第4行：资金覆盖度
    coverage_row = {"指标": "资金覆盖度"}
    for item in detailed_data_sorted:
        coverage_row[item["报告期"]] = item["资金覆盖度"]
    table_data.append(coverage_row)

    # 第5行：估算利率
    rate_row = {"指标": "估算利率"}
    for item in detailed_data_sorted:
        rate_row[item["报告期"]] = item["估算利率"]
    table_data.append(rate_row)

    # 第6行：异常程度
    anomaly_row = {"指标": "异常程度"}
    for item in detailed_data_sorted:
        anomaly_row[item["报告期"]] = item["异常程度"]
    table_data.append(anomaly_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)


def render_notes_receivable_table(calculation_details: Dict):
    """显示应收票据健康度计算表格"""
    # 简化版本，实际实现可以根据需要扩展
    st.markdown("**应收票据分析数据**:")
    for key, value in calculation_details.items():
        if key != "raw_data" and key != "calculated_data":
            st.write(f"- {key}: {value}")


def render_receivables_table(calculation_details: Dict):
    """显示应收账款健康度计算表格"""
    # 简化版本，实际实现可以根据需要扩展
    st.markdown("**应收账款分析数据**:")
    for key, value in calculation_details.items():
        if key != "detailed_data":
            st.write(f"- {key}: {value}")


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

            cash = format_accounting(parse_amount(get_field_value(row, "货币资金")))
            financial_assets = format_accounting(parse_amount(get_field_value(row, "交易性金融资产")))
            short_debt = format_accounting(parse_amount(get_field_value(row, "短期借款")))
            long_debt = format_accounting(parse_amount(get_field_value(row, "长期借款")))
            # 应付债券字段不存在，设为0
            bonds = format_accounting(0)
            total_assets = format_accounting(parse_amount(get_field_value(row, "*资产合计")))
            total_liabilities = format_accounting(parse_amount(get_field_value(row, "*负债合计")))
        except:
            # 如果字段不存在，使用0值
            cash = financial_assets = short_debt = long_debt = bonds = "0.00"
            total_assets = total_liabilities = "0.00"

        summary_data.append({
            "报告期": report_period,
            "货币资金": cash,
            "交易性金融资产": financial_assets,
            "短期借款": short_debt,
            "长期借款": long_debt,
            "应付债券": bonds,
            "资产总计": total_assets,
            "负债总计": total_liabilities
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