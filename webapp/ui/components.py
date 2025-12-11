"""
UI组件 - 通用展示组件
"""

import streamlit as st
import pandas as pd
from typing import Dict, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.base_models import ChecklistItem, SubQuestion
from core.data_accessor import format_financial_number
from .renderers import (
    render_cash_safety_table,
    render_cash_anomaly_table,
    render_notes_receivable_table,
    render_receivables_table,
    render_other_receivables_table,
    render_bad_debt_provision_table,
    render_prepaid_expenses_table,
    render_inventory_risk_table
)


def render_checklist_item(item: ChecklistItem):
    """渲染检查清单项目"""
    status = "✅" if item.passed else "❌"

    st.markdown(f"#### {status} {item.question_id} {item.question}")
    st.markdown(f"**总结**: {item.summary}")

    with st.expander("📊 查看详细计算过程", expanded=False):
        # 根据不同的检查项显示不同的表格
        if item.question_id == "1.1.1":
            render_cash_safety_table(item.calculation_details)
        elif item.question_id == "1.1.2":
            render_cash_anomaly_table(item.calculation_details)
        elif item.question_id == "1.1.3":
            render_notes_receivable_table(item.calculation_details)
        elif item.question_id == "1.1.4":
            render_receivables_table(item.calculation_details)
        elif item.question_id == "1.1.6":
            render_other_receivables_table(item.calculation_details)
        elif item.question_id == "1.1.5":
            render_prepaid_expenses_table(item.calculation_details)
        elif item.question_id == "1.1.7":
            render_bad_debt_provision_table(item.calculation_details)
        elif item.question_id == "1.1.8":
            render_inventory_risk_table(item.calculation_details)

        # 显示子问题
        for sub_question in item.sub_questions:
            render_sub_question(sub_question, item.calculation_details.get("detailed_data"))
            st.markdown("")  # 添加空行分隔


def render_sub_question(sub_question: SubQuestion, detailed_data: List[Dict] = None):
    """渲染子问题/追问"""
    status = "✅" if sub_question.passed else "❌"

    st.markdown(f"  - 🔍 **{sub_question.question}** {status}")

    # 如果提供了详细数据，直接展示表格
    if detailed_data:
        create_checklist_table(detailed_data, "")
    else:
        # 使用原有的详细数据展示方式，直接展示
        st.markdown("    **详细数据**:")
        for key, value in sub_question.details.items():
            if key != "报告期":
                st.markdown(f"    - {key}: {value}")

        st.markdown(f"    **财报指引**: {sub_question.report_guide}")



def create_checklist_table(data: List[Dict], title: str = "") -> None:
    """创建检查清单表格 - 年份横向排列，指标纵向排列"""
    if not data:
        if title:
            st.warning(f"{title}暂无数据")
        return

    df = pd.DataFrame(data)

    if "报告期" not in df.columns:
        if title:
            st.warning(f"{title}数据格式错误，缺少报告期列")
        return

    # 按年份降序排列（最新年份在左边）
    df = df.sort_values("报告期", ascending=False)

    # 格式化所有数值列
    for col in df.columns:
        if col != "报告期":
            df[col] = df[col].apply(format_financial_number)

    # 设置报告期为索引并转置
    df_transposed = df.set_index("报告期").T

    # 清理列名（去掉索引名称）
    df_transposed = df_transposed.rename_axis(None, axis=1).rename_axis("指标", axis=0)

    # 只有在提供标题时才显示
    if title:
        st.subheader(title)

    st.dataframe(df_transposed, width='stretch')


def create_category_header(category_name: str):
    """创建分类标题"""
    st.markdown(f"### {category_name}")


def create_summary_section(checklist_items: List[ChecklistItem]):
    """创建汇总部分"""
    if not checklist_items:
        return

    total_count = len(checklist_items)
    passed_count = sum(1 for item in checklist_items if item.passed)
    failed_count = total_count - passed_count

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总检查项", total_count)
    with col2:
        st.metric("通过项", passed_count, delta=f"{passed_count/total_count:.1%}" if total_count > 0 else "0%")
    with col3:
        st.metric("失败项", failed_count, delta=f"{failed_count/total_count:.1%}" if total_count > 0 else "0%", delta_color="inverse")

    # 按分类统计
    categories = {}
    for item in checklist_items:
        category = item.category.value
        if category not in categories:
            categories[category] = {"total": 0, "passed": 0}
        categories[category]["total"] += 1
        if item.passed:
            categories[category]["passed"] += 1

    if categories:
        st.markdown("#### 各分类通过情况")
        for category, stats in categories.items():
            ratio = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            st.write(f"- **{category}**: {stats['passed']}/{stats['total']} ({ratio:.1%})")