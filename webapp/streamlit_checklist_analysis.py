#!/usr/bin/env python3
"""
A股股票财报检查清单分析工具 - 重构版

基于财报检查清单的逐项检查分析
专注于问题导向的财务健康状况评估

架构说明：
- 采用模块化设计，UI和计算逻辑分离
- 使用插件式检查项架构，便于扩展
- 支持跨市场（A股、港股、美股）
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入新的模块化组件
from models.base_models import ChecklistCategory
from core.data_accessor import StockAnalyzer
from calculators import get_all_calculators, get_calculators_by_category
from ui.components import render_checklist_item, create_category_header, create_summary_section
from ui.renderers import generate_financial_summary


def preprocess_stock_code(stock_code: str) -> str:
    """预处理股票代码，确保格式正确"""
    stock_code = stock_code.strip()

    if stock_code.isdigit() and len(stock_code) == 6:
        # 如果是6位数字，自动添加市场前缀
        if stock_code.startswith("6"):
            return f"SH{stock_code}"
        elif stock_code.startswith("0") or stock_code.startswith("2"):
            return f"SZ{stock_code}"
        else:
            return f"SH{stock_code}"  # 默认为SH
    else:
        return stock_code.upper()


def get_financial_data(analyzer: StockAnalyzer, years: int = 5) -> Dict[str, pd.DataFrame]:
    """获取财务数据"""
    balance_sheet = analyzer.get_balance_sheet_data(years)
    income_statement = analyzer.get_income_statement_data(years)

    return {
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cash_flow": pd.DataFrame()  # 暂时为空，后续可扩展
    }


def run_checklist_analysis(data: Dict[str, pd.DataFrame]) -> List:
    """执行检查清单分析"""
    # 获取所有已注册的计算器
    calculators = get_all_calculators()

    results = []
    for calculator in calculators.values():
        try:
            # 执行计算
            result = calculator.calculate(data)
            results.append(result)
        except Exception as e:
            st.error(f"检查项 {calculator.question_id} 执行失败: {e}")
            # 创建错误状态的检查项
            error_result = calculator.handle_data_error(data)
            results.append(error_result)

    return results


def display_results(checklist_items: List, stock_code: str, balance_df: pd.DataFrame):
    """显示分析结果"""
    # 显示汇总信息
    st.header(f"📊 {stock_code} 财报分析结果")
    create_summary_section(checklist_items)

    # 按分类显示检查结果
    categories = [
        (ChecklistCategory.ASSETS, "一、\"资产负债表\"及相关附注", "#### 1.1 资产类项目"),
    ]

    for category, main_title, sub_title in categories:
        category_items = [item for item in checklist_items if item.category == category]

        if category_items:
            st.markdown(f"### {main_title}")
            st.markdown(sub_title)

            for item in category_items:
                render_checklist_item(item)
                st.markdown("---")

    # 财报数据汇总
    st.header("📄 财报原始数据汇总")

    # 生成并提供下载功能
    financial_summary = generate_financial_summary(balance_df, stock_code)
    st.download_button(
        label="📥 下载财报汇总 (Markdown)",
        data=financial_summary,
        file_name=f"{stock_code}_财报汇总_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
        key="financial_summary_download"
    )


def main():
    """主应用入口"""
    st.set_page_config(
        page_title="A股财报检查清单",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📋 A股财报检查清单")
    st.markdown("基于财报检查清单的逐项财务健康状况评估")

    # 顶部输入区域 - 用更精确的方式对齐
    col1, col2 = st.columns([4, 1])

    # 创建一个容器来对齐输入框和按钮
    with col1:
        stock_code = st.text_input("股票代码", placeholder="请输入股票代码，如：SH600519 或 000001", value="")
    with col2:
        # 在按钮上方添加一些空间，让按钮和输入框底部对齐
        st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
        analyze_button = st.button("开始分析", type="primary", use_container_width=True)

    # 分析结果显示区域
    if analyze_button:
        if not stock_code.strip():
            st.error("请输入股票代码")
        else:
            # 预处理股票代码
            full_code = preprocess_stock_code(stock_code)

            with st.spinner(f"正在分析 {full_code} 的财务数据..."):
                # 初始化分析器
                analyzer = StockAnalyzer(full_code)

                # 获取财务数据
                financial_data = get_financial_data(analyzer, 5)

                # 检查是否有数据
                if financial_data["balance_sheet"].empty:
                    st.error("未能获取到财务数据，请检查API服务是否正常运行或股票代码是否正确")
                else:
                    # 执行检查清单分析
                    checklist_items = run_checklist_analysis(financial_data)

                    # 显示结果
                    display_results(checklist_items, full_code, financial_data["balance_sheet"])


if __name__ == "__main__":
    main()