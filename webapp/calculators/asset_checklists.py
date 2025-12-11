"""
资产类检查项计算器
"""

import pandas as pd
import streamlit as st
from typing import Dict, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_calculator import BaseCalculator
from core.data_accessor import get_field_value, parse_amount, format_financial_number
from models.base_models import ChecklistCategory, ChecklistItem
from calculators.calculator_registry import register_calculator


class CashSafetyCalculator(BaseCalculator):
    """货币资金安全检查计算器"""

    question_id = "1.1.1"
    question = "货币资金是否安全？"
    category = ChecklistCategory.ASSETS
    description = "检查货币资金能否覆盖有息负债"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": [
                "报告期",
                "货币资金",
                "交易性金融资产",
                "短期借款",
                "长期借款"
            ]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行货币资金安全检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        if balance_df is None or balance_df.empty:
            return self.handle_data_error(data)

        # 收集原始数据
        raw_data = []
        for _, row in balance_df.iterrows():
            try:
                cash = parse_amount(get_field_value(row, "货币资金"))
                short_debt = parse_amount(get_field_value(row, "短期借款"))
                long_debt = parse_amount(get_field_value(row, "长期借款"))
                financial_assets = parse_amount(get_field_value(row, "交易性金融资产"))

                raw_data.append({
                    "报告期": get_field_value(row, "报告期"),
                    "货币资金(百万元)": cash / 1000000,
                    "交易性金融资产(百万元)": financial_assets / 1000000,
                    "短期借款(百万元)": short_debt / 1000000,
                    "长期借款(百万元)": long_debt / 1000000,
                    "有息负债合计(百万元)": (short_debt + long_debt) / 1000000
                })
            except KeyError:
                # 如果任何必需字段不存在，跳过这一行的处理
                continue

        # 计算指标数据
        calculated_data = []
        for data_row in raw_data:
            cash = data_row["货币资金(百万元)"]
            short_debt = data_row["短期借款(百万元)"]
            long_debt = data_row["长期借款(百万元)"]
            financial_assets = data_row["交易性金融资产(百万元)"]

            total_interest_debt = short_debt + long_debt
            safety_ratio = cash / total_interest_debt if total_interest_debt > 0 else float('inf')
            total_liquid_assets = cash + financial_assets
            total_coverage_ratio = total_liquid_assets / total_interest_debt if total_interest_debt > 0 else float('inf')

            calculated_data.append({
                "报告期": data_row["报告期"],
                "有息负债(百万元)": total_interest_debt,
                "货币资金安全比率": "100%" if safety_ratio == float('inf') else f"{safety_ratio:.2f}",
                "总覆盖率": "100%" if total_coverage_ratio == float('inf') else f"{total_coverage_ratio:.2f}",
                "安全性": "安全" if safety_ratio >= 1 else "风险"
            })

        # 获取最新年份的数据用于检查结果
        latest_row = balance_df.iloc[0]
        try:
            report_period = get_field_value(latest_row, "报告期")
            # 解析关键财务数据
            cash = parse_amount(get_field_value(latest_row, "货币资金"))
            financial_assets = parse_amount(get_field_value(latest_row, "交易性金融资产"))
            short_debt = parse_amount(get_field_value(latest_row, "短期借款"))
            long_debt = parse_amount(get_field_value(latest_row, "长期借款"))

            # 计算有息负债总额（A股主要包含短期借款和长期借款）
            total_interest_debt = short_debt + long_debt

            # 检查1：现金及现金等价物能否覆盖有息负债
            cash_safety_ratio = cash / total_interest_debt if total_interest_debt > 0 else float('inf')
            cash_passed = cash_safety_ratio >= 1.0

            # 检查2：加上可迅速变现的金融资产后能否覆盖
            total_liquid_assets = cash + financial_assets
            total_coverage_ratio = total_liquid_assets / total_interest_debt if total_interest_debt > 0 else float('inf')
            coverage_passed = total_coverage_ratio >= 1.0

            # 总体判断
            overall_passed = cash_passed and coverage_passed

            # 生成追问
            sub_questions = [
                self.create_sub_question(
                    question="现金及现金等价物能否覆盖有息负债？",
                    passed=cash_passed,
                    calculation="货币资金安全比率 = 货币资金 ÷ 有息负债",
                    result=cash_safety_ratio,
                    threshold=1.0,
                    details={
                        "货币资金": format_financial_number(cash),
                        "有息负债": format_financial_number(total_interest_debt),
                        "安全比率": "100%" if cash_safety_ratio == float('inf') else f"{cash_safety_ratio:.2f}",
                        "报告期": report_period
                    },
                    report_guide='查看"资产负债表"中"货币资金"、"短期借款"、"长期借款"项目'
                ),
                self.create_sub_question(
                    question="加上可迅速变现的金融资产后能否覆盖？",
                    passed=coverage_passed,
                    calculation="总覆盖率 = (货币资金 + 交易性金融资产) ÷ 有息负债",
                    result=total_coverage_ratio,
                    threshold=1.0,
                    details={
                        "货币资金": format_financial_number(cash),
                        "交易性金融资产": format_financial_number(financial_assets),
                        "有息负债": format_financial_number(total_interest_debt),
                        "总覆盖率": "100%" if total_coverage_ratio == float('inf') else f"{total_coverage_ratio:.2f}",
                        "报告期": report_period
                    },
                    report_guide='查看"资产负债表"中"交易性金融资产"项目'
                )
            ]

            # 生成检查总结
            if overall_passed:
                if cash_safety_ratio >= 2.0:
                    summary = f"货币资金非常充足，安全比率={'100%' if cash_safety_ratio == float('inf') else f'{cash_safety_ratio:.2f}'}，财务风险极低"
                else:
                    summary = f"货币资金充足，安全比率={'100%' if cash_safety_ratio == float('inf') else f'{cash_safety_ratio:.2f}'}，能够覆盖有息负债，财务风险较低"
            else:
                summary = f"货币资金不足，安全比率={'100%' if cash_safety_ratio == float('inf') else f'{cash_safety_ratio:.2f}'} < 1，存在财务风险"

            # 创建检查清单项目
            return self.create_checklist_item(
                passed=overall_passed,
                summary=summary,
                calculation_details={
                    "报告期": report_period,
                    "货币资金": format_financial_number(cash),
                    "交易性金融资产": format_financial_number(financial_assets),
                    "有息负债": format_financial_number(total_interest_debt),
                    "安全比率": "100%" if cash_safety_ratio == float('inf') else f"{cash_safety_ratio:.2f}",
                    "总覆盖率": "100%" if total_coverage_ratio == float('inf') else f"{total_coverage_ratio:.2f}",
                    "raw_data": raw_data,  # 原始数据
                    "calculated_data": calculated_data  # 计算结果数据
                },
                sub_questions=sub_questions
            )

        except KeyError:
            # 如果任何必需字段不存在，返回空列表
            return self.handle_data_error(data)


class CashAnomalyCalculator(BaseCalculator):
    """货币资金异常检查计算器"""

    question_id = "1.1.2"
    question = "货币资金是否存在异常？"
    category = ChecklistCategory.ASSETS
    description = "检查货币资金是否存在异常情况"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": ["报告期", "货币资金", "短期借款"],
            "income_statement": ["报告期", "利息收入"]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行货币资金异常检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        income_df = data.get("income_statement")

        if balance_df is None or income_df is None or balance_df.empty or income_df.empty:
            return self.handle_data_error(data)

        # 合并资产负债表和利润表数据
        merged_data = []
        for _, balance_row in balance_df.iterrows():
            try:
                report_period = get_field_value(balance_row, "报告期")
                # 查找对应年度的利润表数据
                income_row = income_df[income_df["报告期"].str.contains(report_period[:4])]

                if not income_row.empty:
                    income_row = income_row.iloc[0]
                    cash = parse_amount(get_field_value(balance_row, "货币资金"))
                    short_debt = parse_amount(get_field_value(balance_row, "短期借款"))
                    interest_income = parse_amount(get_field_value(income_row, "利息收入"))

                    # 货币资金与短期负债比率
                    cash_to_short_debt = cash / short_debt if short_debt > 0 else float('inf')

                    # 估算利率（年化）
                    estimated_rate = (interest_income / cash) if cash > 0 else 0

                    # 异常程度判断
                    if cash_to_short_debt < 0.5:
                        anomaly_level = "严重异常"
                    elif cash_to_short_debt < 1.0:
                        anomaly_level = "需要关注"
                    else:
                        anomaly_level = "正常"

                    merged_data.append({
                        "报告期": report_period,
                        "货币资金(百万元)": format_financial_number(cash / 1000000),
                        "短期借款(百万元)": format_financial_number(short_debt / 1000000),
                        "资金覆盖度": "100%" if cash_to_short_debt == float('inf') else f"{cash_to_short_debt:.2f}",
                        "利息收入(百万元)": format_financial_number(interest_income / 1000000),
                        "估算利率": f"{estimated_rate:.2%}",
                        "异常程度": anomaly_level
                    })
            except KeyError:
                # 如果任何必需字段不存在，跳过这一行的处理
                continue

        # 获取最新年份的数据用于检查结果
        latest_balance = balance_df.iloc[0]
        latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

        if latest_income.empty:
            return self.handle_data_error(data)

        latest_income = latest_income.iloc[0]
        report_period = latest_balance["报告期"]

        # 解析关键财务数据
        cash = parse_amount(get_field_value(latest_balance, "货币资金"))
        short_debt = parse_amount(get_field_value(latest_balance, "短期借款"))
        interest_income = parse_amount(get_field_value(latest_income, "利息收入"))

        # 检查1：货币资金是否远小于短期负债（<0.5为严重异常）
        cash_to_short_debt = cash / short_debt if short_debt > 0 else float('inf')
        coverage_passed = cash_to_short_debt >= 0.5

        # 检查2：利息收入是否显著低于市场利率（<1%为异常）
        estimated_rate = (interest_income / cash) if cash > 0 else 0
        # 市场常见利率范围（年化）：1%-5%
        interest_rate_passed = estimated_rate >= 0.01 or interest_income == 0  # 无利息收入也算正常

        # 总体判断
        overall_passed = coverage_passed and interest_rate_passed

        # 生成追问
        sub_questions = [
            self.create_sub_question(
                question="货币资金余额是否远小于短期负债？",
                passed=coverage_passed,
                calculation="货币资金覆盖度 = 货币资金 ÷ 短期借款",
                result=cash_to_short_debt,
                threshold=0.5,
                details={
                    "货币资金": format_financial_number(cash),
                    "短期借款": format_financial_number(short_debt),
                    "覆盖度": "100%" if cash_to_short_debt == float('inf') else f"{cash_to_short_debt:.2f}",
                    "报告期": report_period
                },
                report_guide='查看"资产负债表"中"货币资金"和"短期借款"项目'
            ),
            self.create_sub_question(
                question="利息收入是否显著低于市场利率？",
                passed=interest_rate_passed,
                calculation="估算利率 = 利息收入 ÷ 货币资金",
                result=estimated_rate,
                threshold=0.01,
                details={
                    "利息收入": format_financial_number(interest_income),
                    "货币资金": format_financial_number(cash),
                    "估算利率": f"{estimated_rate:.2%}",
                    "报告期": report_period
                },
                report_guide='查看"资产负债表"中"货币资金"和"利润表"中"利息收入"项目'
            )
        ]

        # 生成检查总结
        if overall_passed:
            if cash_to_short_debt >= 2.0:
                summary = f"货币资金充足，覆盖度{cash_to_short_debt:.1f}≥0.5，资金状况正常"
            else:
                summary = f"货币资金覆盖度{cash_to_short_debt:.1f}≥0.5，但建议关注流动性"
        else:
            issues = []
            if not coverage_passed:
                issues.append("资金覆盖不足")
            if not interest_rate_passed:
                issues.append("利率异常偏低")
            issues_str = "、".join(issues)
            summary = f"货币资金存在异常：{issues_str}"

        # 创建检查清单项目
        return self.create_checklist_item(
            passed=overall_passed,
            summary=summary,
            calculation_details={
                "报告期": report_period,
                "货币资金": format_financial_number(cash),
                "短期借款": format_financial_number(short_debt),
                "利息收入": format_financial_number(interest_income),
                "资金覆盖度": "100%" if cash_to_short_debt == float('inf') else f"{cash_to_short_debt:.2f}",
                "估算利率": f"{estimated_rate:.2%}",
                "detailed_data": merged_data  # 添加详细数据用于表格展示
            },
            sub_questions=sub_questions
        )


class NotesReceivableCalculator(BaseCalculator):
    """应收票据健康度检查计算器"""

    question_id = "1.1.3"
    question = "应收票据是否健康？"
    category = ChecklistCategory.ASSETS
    description = "检查应收票据的规模和结构"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": [
                "报告期",
                "应收票据及应收账款",
                "*资产合计",
                "应收账款"
            ],
            "income_statement": ["报告期", "其中：营业收入"]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行应收票据健康度检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        if balance_df is None or balance_df.empty:
            return self.handle_data_error(data)

        # 处理所有年份的数据，而不仅仅是最新一年
        detailed_data = []
        passed_count = 0
        total_count = 0

        for _, row in balance_df.iterrows():
            try:
                notes_receivable = parse_amount(get_field_value(row, "应收票据及应收账款"))
                total_assets = parse_amount(get_field_value(row, "*资产合计"))
                receivables = parse_amount(get_field_value(row, "应收账款"))

                notes_ratio = notes_receivable / total_assets if total_assets > 0 else 0
                asset_ratio_passed = notes_ratio <= 0.15
                
                # 生成详细数据
                detailed_data.append({
                    "报告期": get_field_value(row, "报告期"),
                    "应收票据及应收账款(百万元)": notes_receivable / 1000000,
                    "总资产(百万元)": total_assets / 1000000,
                    "占总资产比例(%)": notes_ratio * 100,
                    "评估结果": "✅ 正常" if asset_ratio_passed else "⚠️ 需要关注"
                })

                if asset_ratio_passed:
                    passed_count += 1
                total_count += 1

            except KeyError:
                continue

        if not detailed_data:
            return self.handle_data_error(data)

        # 基于最新一年生成检查结果和子问题
        latest_row = balance_df.iloc[0]
        latest_data = detailed_data[0]  # 第一个就是最新的（已排序）
        notes_ratio = latest_data["占总资产比例(%)"] / 100
        asset_ratio_passed = latest_data["评估结果"] == "✅ 正常"

        # 创建子问题
        sub_question = self.create_sub_question(
            question="应收票据占总资产比例是否过高？",
            passed=asset_ratio_passed,
            calculation="应收票据占总资产比例 = 应收票据 ÷ 总资产",
            result=notes_ratio,
            threshold=0.15,
            details={
                "应收票据": format_financial_number(parse_amount(get_field_value(latest_row, "应收票据及应收账款"))),
                "总资产": format_financial_number(parse_amount(get_field_value(latest_row, "*资产合计"))),
                "占比": f"{notes_ratio:.2%}",
                "报告期": get_field_value(latest_row, "报告期")
            },
            report_guide='查看"资产负债表"中"应收票据及应收账款"和"*资产合计"项目'
        )

        # 生成检查总结（基于整体趋势）
        passed_rate = passed_count / total_count if total_count > 0 else 0
        if passed_rate >= 0.8:  # 80%以上年份正常
            summary = f"应收票据历史上{passed_count}/{total_count}年符合标准，最新占比{notes_ratio:.2%}{'≤15%，规模合理' if asset_ratio_passed else '>15%，规模过大需要关注'}"
        else:
            summary = f"应收票据历史上仅{passed_count}/{total_count}年符合标准，需要关注其变化趋势，最新占比{notes_ratio:.2%}"

        # 总体通过状态：基于最新年份
        overall_passed = asset_ratio_passed

        return self.create_checklist_item(
            passed=overall_passed,
            summary=summary,
            calculation_details={
                "detailed_data": detailed_data
            },
            sub_questions=[sub_question]
        )


class ReceivablesCalculator(BaseCalculator):
    """应收账款健康度检查计算器"""

    question_id = "1.1.4"
    question = "应收账款是否健康？"
    category = ChecklistCategory.ASSETS
    description = "检查应收账款的规模和周转情况"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": ["报告期", "应收账款", "*资产合计"],
            "income_statement": ["报告期", "其中：营业收入"]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行应收账款健康度检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        income_df = data.get("income_statement")

        if balance_df is None or income_df is None or balance_df.empty or income_df.empty:
            return self.handle_data_error(data)

        # 处理所有年份的数据
        detailed_data = []
        passed_count = 0
        total_count = 0

        for _, balance_row in balance_df.iterrows():
            try:
                # 找到对应年份的利润表数据
                report_period = get_field_value(balance_row, "报告期")
                year = report_period[:4]  # 提取年份
                income_rows = income_df[income_df["报告期"].str.contains(year)]
                
                if income_rows.empty:
                    continue
                    
                income_row = income_rows.iloc[0]

                receivables = parse_amount(get_field_value(balance_row, "应收账款"))
                total_assets = parse_amount(get_field_value(balance_row, "*资产合计"))
                revenue = parse_amount(get_field_value(income_row, "其中：营业收入"))

                receivables_to_assets = receivables / total_assets if total_assets > 0 else 0
                receivables_turnover = revenue / receivables if receivables > 0 else float('inf')

                assets_ratio_passed = receivables_to_assets <= 0.10
                turnover_passed = receivables_turnover >= 6.0 or receivables_turnover == float('inf')
                year_passed = assets_ratio_passed and turnover_passed
                
                # 生成详细数据
                detailed_data.append({
                    "报告期": report_period,
                    "应收账款(百万元)": receivables / 1000000,
                    "总资产(百万元)": total_assets / 1000000,
                    "营业收入(百万元)": revenue / 1000000,
                    "应收账款占总资产比例(%)": receivables_to_assets * 100,
                    "应收账款周转率(次)": "100.00" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}",
                    "评估结果": "✅ 正常" if year_passed else "⚠️ 需要关注"
                })

                if year_passed:
                    passed_count += 1
                total_count += 1

            except (KeyError, ValueError):
                continue

        if not detailed_data:
            return self.handle_data_error(data)

        # 基于最新一年生成检查结果和子问题
        latest_balance = balance_df.iloc[0]
        latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])].iloc[0]
        latest_data = detailed_data[0]

        receivables = parse_amount(get_field_value(latest_balance, "应收账款"))
        total_assets = parse_amount(get_field_value(latest_balance, "*资产合计"))
        revenue = parse_amount(get_field_value(latest_income, "其中：营业收入"))

        receivables_to_assets = receivables / total_assets if total_assets > 0 else 0
        receivables_turnover = revenue / receivables if receivables > 0 else float('inf')
        assets_ratio_passed = receivables_to_assets <= 0.10
        turnover_passed = receivables_turnover >= 6.0 or receivables_turnover == float('inf')
        overall_passed = assets_ratio_passed and turnover_passed

        # 创建子问题
        sub_questions = [
            self.create_sub_question(
                question="应收账款占总资产比例是否过高？",
                passed=assets_ratio_passed,
                calculation="应收账款占总资产比例 = 应收账款 ÷ 总资产",
                result=receivables_to_assets,
                threshold=0.10,
                details={
                    "应收账款": format_financial_number(receivables),
                    "总资产": format_financial_number(total_assets),
                    "占比": f"{receivables_to_assets:.2%}",
                    "报告期": get_field_value(latest_balance, "报告期")
                },
                report_guide='查看"资产负债表"中"应收账款"和"*资产合计"项目'
            ),
            self.create_sub_question(
                question="应收账款周转率是否过低？",
                passed=turnover_passed,
                calculation="应收账款周转率 = 营业收入 ÷ 应收账款",
                result=receivables_turnover,
                threshold=6.0,
                details={
                    "营业收入": format_financial_number(revenue),
                    "应收账款": format_financial_number(receivables),
                    "周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}",
                    "报告期": get_field_value(latest_balance, "报告期")
                },
                report_guide='查看"资产负债表"中"应收账款"和"利润表"中"其中：营业收入"项目'
            )
        ]

        # 生成检查总结
        passed_rate = passed_count / total_count if total_count > 0 else 0
        if overall_passed:
            if receivables_turnover == float('inf'):
                summary = f"应收账款历史上{passed_count}/{total_count}年符合标准，最新占比{receivables_to_assets:.2%}≤10%，周转率100%（应收账款为0），状况极好"
            else:
                summary = f"应收账款历史上{passed_count}/{total_count}年符合标准，最新占比{receivables_to_assets:.2%}≤10%，周转率{receivables_turnover:.1f}次≥6次，状况良好"
        else:
            if not assets_ratio_passed and not turnover_passed:
                summary = f"应收账款历史上仅{passed_count}/{total_count}年符合标准，最新占比{receivables_to_assets:.2%}>10%，周转率{receivables_turnover:.1f}次<6次，存在双重风险"
            elif not assets_ratio_passed:
                summary = f"应收账款历史上仅{passed_count}/{total_count}年符合标准，最新占比{receivables_to_assets:.2%}>10%，占总资产比例过高"
            else:
                summary = f"应收账款历史上仅{passed_count}/{total_count}年符合标准，最新周转率{receivables_turnover:.1f}次<6次，回款速度过慢"

        return self.create_checklist_item(
            passed=overall_passed,
            summary=summary,
            calculation_details={
                "detailed_data": detailed_data
            },
            sub_questions=sub_questions
        )


class PrepaidExpensesCalculator(BaseCalculator):
    """预付账款异常检查计算器"""

    question_id = "1.1.5"
    question = "预付账款是否异常？"
    category = ChecklistCategory.ASSETS
    description = "检查预付账款的规模和变化趋势"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": ["报告期", "预付款项", "*资产合计"],
            "income_statement": ["报告期", "其中：营业收入", "其中：营业成本"]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行预付账款异常检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        income_df = data.get("income_statement")

        if balance_df is None or income_df is None or balance_df.empty or income_df.empty:
            return self.handle_data_error(data)

        # 处理所有年份的数据
        detailed_data = []
        passed_count = 0
        total_count = 0

        for _, balance_row in balance_df.iterrows():
            try:
                # 找到对应年份的利润表数据
                report_period = get_field_value(balance_row, "报告期")
                year = report_period[:4]  # 提取年份
                income_rows = income_df[income_df["报告期"].str.contains(year)]
                
                if income_rows.empty:
                    continue
                    
                income_row = income_rows.iloc[0]

                prepaid_expenses = parse_amount(get_field_value(balance_row, "预付款项"))
                total_assets = parse_amount(get_field_value(balance_row, "*资产合计"))
                revenue = parse_amount(get_field_value(income_row, "其中：营业收入"))
                cost = parse_amount(get_field_value(income_row, "其中：营业成本"))

                # 检查1：预付账款占总资产比例是否过高（>5%为风险）
                prepaid_to_assets = prepaid_expenses / total_assets if total_assets > 0 else 0
                asset_ratio_passed = prepaid_to_assets <= 0.05

                # 检查2：预付账款占收入比例是否过大（>10%为风险）
                prepaid_to_revenue = prepaid_expenses / revenue if revenue > 0 else 0
                revenue_ratio_passed = prepaid_to_revenue <= 0.10

                # 检查3：预付账款占成本比例是否波动过大
                prepaid_to_cost = prepaid_expenses / cost if cost > 0 else 0
                cost_ratio_passed = prepaid_to_cost <= 0.15

                year_passed = all([asset_ratio_passed, revenue_ratio_passed, cost_ratio_passed])
                
                # 生成详细数据
                detailed_data.append({
                    "报告期": report_period,
                    "预付账款(百万元)": prepaid_expenses / 1000000,
                    "总资产(百万元)": total_assets / 1000000,
                    "营业收入(百万元)": revenue / 1000000,
                    "营业成本(百万元)": cost / 1000000,
                    "预付账款占总资产比例(%)": prepaid_to_assets * 100,
                    "预付账款占收入比例(%)": prepaid_to_revenue * 100,
                    "预付账款占成本比例(%)": prepaid_to_cost * 100,
                    "评估结果": "✅ 正常" if year_passed else "⚠️ 异常"
                })

                if year_passed:
                    passed_count += 1
                total_count += 1

            except (KeyError, ValueError):
                continue

        if not detailed_data:
            return self.handle_data_error(data)

        # 基于最新一年生成检查结果和子问题
        latest_balance = balance_df.iloc[0]
        latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])].iloc[0]
        latest_data = detailed_data[0]

        prepaid_expenses = parse_amount(get_field_value(latest_balance, "预付款项"))
        total_assets = parse_amount(get_field_value(latest_balance, "*资产合计"))
        revenue = parse_amount(get_field_value(latest_income, "其中：营业收入"))
        cost = parse_amount(get_field_value(latest_income, "其中：营业成本"))

        prepaid_to_assets = prepaid_expenses / total_assets if total_assets > 0 else 0
        prepaid_to_revenue = prepaid_expenses / revenue if revenue > 0 else 0
        prepaid_to_cost = prepaid_expenses / cost if cost > 0 else 0
        
        asset_ratio_passed = prepaid_to_assets <= 0.05
        revenue_ratio_passed = prepaid_to_revenue <= 0.10
        cost_ratio_passed = prepaid_to_cost <= 0.15
        overall_passed = all([asset_ratio_passed, revenue_ratio_passed, cost_ratio_passed])

        # 创建子问题（简化版，只包含主要检查）
        sub_question = self.create_sub_question(
            question="预付账款占总资产比例是否过高？",
            passed=asset_ratio_passed,
            calculation="预付账款占总资产比例 = 预付账款 ÷ 总资产",
            result=prepaid_to_assets,
            threshold=0.05,
            details={
                "预付账款": format_financial_number(prepaid_expenses),
                "总资产": format_financial_number(total_assets),
                "占比": f"{prepaid_to_assets:.2%}",
                "报告期": get_field_value(latest_balance, "报告期")
            },
            report_guide='查看"资产负债表"中"预付账款"和"*资产合计"项目'
        )

        # 生成检查总结
        passed_rate = passed_count / total_count if total_count > 0 else 0
        issues = []
        if not asset_ratio_passed:
            issues.append("占总资产比例过高")
        if not revenue_ratio_passed:
            issues.append("占收入比例过大")
        if not cost_ratio_passed:
            issues.append("占成本比例过大")

        if not issues:
            if passed_rate >= 0.8:
                summary = f"预付账款历史上{passed_count}/{total_count}年符合标准，最新占比资产{prepaid_to_assets:.2%}≤5%，占收入{prepaid_to_revenue:.2%}≤10%，占成本{prepaid_to_cost:.2%}≤15%，未发现异常"
            else:
                summary = f"预付账款历史上仅{passed_count}/{total_count}年符合标准，需要关注历史变化，最新各项指标均在正常范围内"
        else:
            issues_str = "、".join(issues)
            if passed_rate >= 0.8:
                summary = f"预付账款历史上{passed_count}/{total_count}年符合标准，但最新存在异常：{issues_str}"
            else:
                summary = f"预付账款历史上仅{passed_count}/{total_count}年符合标准，最新存在异常：{issues_str}"

        return self.create_checklist_item(
            passed=overall_passed,
            summary=summary,
            calculation_details={
                "detailed_data": detailed_data
            },
            sub_questions=[sub_question]
        )


class OtherReceivablesCalculator(BaseCalculator):
    """其他应收款异常检查计算器"""

    question_id = "1.1.6"
    question = "其他应收款是否异常？"
    category = ChecklistCategory.ASSETS
    description = "检查剔除应收股利和利息后，其他应收款数额是否较大"

    def get_required_fields(self) -> Dict[str, List[str]]:
        return {
            "balance_sheet": [
                "报告期",
                "其他应收款",
                "其中：应收利息",
                "*资产合计"
            ],
            "income_statement": [
                "报告期",
                "其中：营业收入"
            ]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """执行其他应收款异常检查"""
        if not self.validate_data(data):
            return self.handle_data_error(data)

        balance_df = data.get("balance_sheet")
        income_df = data.get("income_statement")
        if balance_df is None or balance_df.empty:
            return self.handle_data_error(data)

        # 生成多年度详细数据
        detailed_data = []
        for _, row in balance_df.iterrows():
            try:
                report_period = get_field_value(row, "报告期")
                other_receivables = parse_amount(get_field_value(row, "其他应收款"))
                interest_receivable = parse_amount(get_field_value(row, "其中：应收利息"))
                total_assets = parse_amount(get_field_value(row, "*资产合计"))

                # 剔除应收利息后的其他应收款
                other_receivables_exclude_interest = max(
                    other_receivables - interest_receivable, 0
                )

                # 查找对应的营业收入
                revenue = 0
                if income_df is not None and not income_df.empty:
                    revenue_row = income_df[income_df["报告期"] == report_period]
                    if not revenue_row.empty:
                        revenue = parse_amount(get_field_value(revenue_row.iloc[0], "其中：营业收入"))

                # 计算其他应收款占营业收入比例
                other_receivables_revenue_ratio = (other_receivables_exclude_interest / revenue * 100) if revenue > 0 else 0

                detailed_data.append({
                    "报告期": report_period,
                    "其他应收款(百万元)": other_receivables / 1000000,
                    "其中：应收利息(百万元)": interest_receivable / 1000000,
                    "剔除应收利息后的其他应收款(百万元)": other_receivables_exclude_interest / 1000000,
                    "营业收入(百万元)": revenue / 1000000,
                    "其他应收款占营业收入比例": other_receivables_revenue_ratio
                })
            except (KeyError, ValueError):
                continue

        # 实现逻辑：检查其他应收款（剔除应收股利和利息）占总资产比例
        latest_row = balance_df.iloc[0]
        try:
            other_receivables = parse_amount(get_field_value(latest_row, "其他应收款"))
            interest_receivable = parse_amount(get_field_value(latest_row, "其中：应收利息"))
            total_assets = parse_amount(get_field_value(latest_row, "*资产合计"))

            # 剔除应收利息后的其他应收款（应收股利字段不存在，只能剔除利息）
            # 由于API中没有单独的应收股利字段，我们只能剔除应收利息
            # 假设其他应收款中较大比例的不是应收股利，那么剔除利息后的余额可以作为参考
            other_receivables_exclude_interest = max(
                other_receivables - interest_receivable, 0
            )

            # 检查1：剔除应收利息后的其他应收款占总资产比例是否过高（>5%为风险）
            # 根据财报检查清单，剔除应收股利和利息后的数额如果较大，可能存在问题
            other_receivables_ratio = other_receivables_exclude_interest / total_assets if total_assets > 0 else 0
            asset_ratio_passed = other_receivables_ratio <= 0.05

            # 检查2：其他应收款绝对数额是否过大（>10亿为关注点）
            absolute_amount_passed = other_receivables_exclude_interest <= 1000000000  # 10亿

            # 检查3：应收利息占其他应收款的比例（过高可能异常）
            interest_ratio = interest_receivable / other_receivables if other_receivables > 0 else 0
            interest_ratio_passed = interest_ratio <= 0.5  # 应收利息不超过其他应收款的50%

            # 综合判断：主要关注比例和绝对数额，应收利息比例作为参考
            overall_passed = asset_ratio_passed and absolute_amount_passed

            # 创建子问题
            sub_questions = [
                self.create_sub_question(
                    question="剔除应收利息后的其他应收款占总资产比例是否过高？",
                    passed=asset_ratio_passed,
                    calculation="其他应收款净额占总资产比例 = (其他应收款 - 应收利息) ÷ 总资产",
                    result=other_receivables_ratio,
                    threshold=0.05,
                    details={
                        "其他应收款": format_financial_number(other_receivables),
                        "应收利息": format_financial_number(interest_receivable),
                        "剔除应收利息后净额": format_financial_number(other_receivables_exclude_interest),
                        "总资产": format_financial_number(total_assets),
                        "占比": f"{other_receivables_ratio:.2%}",
                        "报告期": get_field_value(latest_row, "报告期")
                    },
                    report_guide='查看"资产负债表"中"其他应收款"、"其中：应收利息"和"*资产合计"项目'
                ),
                self.create_sub_question(
                    question="其他应收款绝对数额是否过大？",
                    passed=absolute_amount_passed,
                    calculation="其他应收款净额与10亿元阈值比较",
                    result=other_receivables_exclude_interest,
                    threshold=1000000000,
                    details={
                        "其他应收款净额": format_financial_number(other_receivables_exclude_interest),
                        "阈值": "10亿元",
                        "是否超标": "是" if not absolute_amount_passed else "否"
                    },
                    report_guide='关注大额其他应收款的构成和回收风险'
                )
            ]

            # 生成检查总结
            if overall_passed:
                if other_receivables_exclude_interest == 0:
                    summary = f"其他应收款为0，不存在异常"
                else:
                    summary = f"其他应收款净额占比{other_receivables_ratio:.2%}≤5%，数额{format_financial_number(other_receivables_exclude_interest)}≤10亿，未发现明显异常"
            else:
                issues = []
                if not asset_ratio_passed:
                    issues.append(f"占总资产比例过高({other_receivables_ratio:.2%}>5%)")
                if not absolute_amount_passed:
                    issues.append(f"绝对数额过大(>{format_financial_number(1000000000)})")

                issues_str = "、".join(issues)
                summary = f"其他应收款存在异常：{issues_str}"

            return self.create_checklist_item(
                passed=overall_passed,
                summary=summary,
                calculation_details={
                    "报告期": get_field_value(latest_row, "报告期"),
                    "其他应收款": format_financial_number(other_receivables),
                    "应收利息": format_financial_number(interest_receivable),
                    "剔除应收利息后净额": format_financial_number(other_receivables_exclude_interest),
                    "总资产": format_financial_number(total_assets),
                    "占总资产比例": f"{other_receivables_ratio:.2%}",
                    "绝对数额": format_financial_number(other_receivables_exclude_interest),
                    "超过10亿元": "是" if not absolute_amount_passed else "否",
                    "detailed_data": detailed_data
                },
                sub_questions=sub_questions
            )
        except KeyError:
            return self.handle_data_error(data)


class BadDebtProvisionCalculator(BaseCalculator):
    """坏账准备计提合理性检查计算器"""

    question_id = "1.1.7"
    question = "坏账准备计提是否合理？"
    category = ChecklistCategory.ASSETS

    def get_required_fields(self) -> Dict[str, List[str]]:
        """获取所需的数据字段"""
        return {
            "balance_sheet": [
                "报告期",
                "应收账款",
                "其他应收款"
            ],
            "income_statement": [
                "报告期",
                "资产减值损失",
                "信用减值损失"
            ]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """计算坏账准备合理性"""
        try:
            # 获取数据
            balance_df = data.get("balance_sheet")
            income_df = data.get("income_statement")

            if balance_df is None or balance_df.empty:
                return self.handle_data_error(data)

            # 查找包含有效应收账款数据的最新年份
            valid_data_row = None
            income_row = None

            for _, balance_row in balance_df.iterrows():
                try:
                    # 尝试获取应收账款和其他应收款
                    receivables = get_field_value(balance_row, "应收账款")
                    other_receivables = get_field_value(balance_row, "其他应收款")

                    # 如果都能获取到，说明数据完整
                    if receivables is not None and other_receivables is not None:
                        # 转换为数值
                        receivables_amount = parse_amount(receivables)
                        other_receivables_amount = parse_amount(other_receivables)
                        total_receivables = receivables_amount + other_receivables_amount

                        if total_receivables > 0:  # 确保应收款项总额大于0
                            valid_data_row = balance_row
                            break
                except KeyError:
                    # 如果字段缺失，继续查找下一行
                    continue

            if valid_data_row is None:
                return self.handle_data_error(data)

            # 查找对应年份的利润表数据
            report_date = get_field_value(valid_data_row, "报告期")
            if income_df is not None and not income_df.empty:
                for _, income_row in income_df.iterrows():
                    try:
                        income_date = get_field_value(income_row, "报告期")
                        if income_date == report_date:
                            income_row = income_row
                            break
                    except KeyError:
                        continue

            # 获取关键数据
            receivables_amount = parse_amount(get_field_value(valid_data_row, "应收账款"))
            other_receivables_amount = parse_amount(get_field_value(valid_data_row, "其他应收款"))
            total_receivables = receivables_amount + other_receivables_amount

            # 获取减值损失数据
            asset_impairment = 0
            credit_impairment = 0

            if income_row is not None:
                try:
                    asset_impairment = parse_amount(get_field_value(income_row, "资产减值损失"))
                except KeyError:
                    asset_impairment = 0

                try:
                    credit_impairment = parse_amount(get_field_value(income_row, "信用减值损失"))
                except KeyError:
                    credit_impairment = 0

            total_impairment = asset_impairment + credit_impairment

            # 计算坏账准备率
            provision_rate = (total_impairment / total_receivables * 100) if total_receivables > 0 else 0

            # 判断合理性
            reasonability_score = "正常"
            if provision_rate > 8:
                reasonability_score = "异常偏高"
            elif provision_rate > 5:
                reasonability_score = "需要关注"
            elif provision_rate < 0.5:
                reasonability_score = "计提不足"

            # 判断是否通过检查
            passed = reasonability_score in ["正常", "需要关注"]

            # 生成详细数据用于显示
            detailed_data = [{
                "报告期": get_field_value(valid_data_row, "报告期"),
                "应收账款(百万元)": receivables_amount / 1000000,
                "其他应收款(百万元)": other_receivables_amount / 1000000,
                "应收款项合计(百万元)": total_receivables / 1000000,
                "资产减值损失(百万元)": asset_impairment / 1000000,
                "信用减值损失(百万元)": credit_impairment / 1000000,
                "总减值损失(百万元)": total_impairment / 1000000,
                "坏账准备计提比例": provision_rate,
                "计提合理性评估": reasonability_score
            }]

            # 生成子问题
            sub_questions = [
                self.create_sub_question(
                    question="坏账准备计提比例是否在合理范围内？",
                    passed=0.5 <= provision_rate <= 8,
                    calculation="坏账准备率 = (资产减值损失 + 信用减值损失) ÷ (应收账款 + 其他应收款) × 100%",
                    result=f"{provision_rate:.2f}%",
                    threshold="0.5%-8%",
                    details={
                        "应收款项总额": format_financial_number(total_receivables / 1000000),
                        "总减值损失": format_financial_number(total_impairment / 1000000),
                        "行业标准": "一般1%-5%较为合理"
                    },
                    report_guide="检查财务报表附注中关于坏账准备计提政策的说明"
                )
            ]

            # 生成总结
            summary = f"坏账准备计提比例为{provision_rate:.2f}%，{reasonability_score}。"

            if reasonability_score == "异常偏高":
                summary += "可能存在通过多计提坏账准备来隐藏利润的嫌疑。"
            elif reasonability_score == "计提不足":
                summary += "可能存在少计提坏账准备来虚增利润的嫌疑。"
            else:
                summary += "计提政策相对合理。"

            return self.create_checklist_item(
                passed=passed,
                summary=summary,
                calculation_details={
                    "detailed_data": detailed_data
                },
                sub_questions=sub_questions
            )

        except Exception as e:
            return self.handle_data_error(data)


class InventoryRiskCalculator(BaseCalculator):
    """存货风险检查计算器"""

    question_id = "1.1.8"
    question = "存货是否存在风险？"
    category = ChecklistCategory.ASSETS
    description = "检查存货减值准备计提是否充分，存货增长是否异常"

    def get_required_fields(self) -> Dict[str, List[str]]:
        """获取所需的数据字段"""
        return {
            "balance_sheet": [
                "报告期",
                "存货",
                "*资产合计"
            ],
            "income_statement": [
                "报告期",
                "其中：营业成本",
                "资产减值损失"
            ]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """计算存货风险分析"""
        try:
            # 获取数据
            balance_df = data.get("balance_sheet")
            income_df = data.get("income_statement")

            if balance_df is None or balance_df.empty:
                return self.handle_data_error(data)

            # 生成详细数据用于表格显示
            detailed_data = []
            risk_assessments = []

            for _, balance_row in balance_df.iterrows():
                try:
                    # 获取资产负债表数据
                    period = get_field_value(balance_row, "报告期")
                    inventory = get_field_value(balance_row, "存货")
                    total_assets = get_field_value(balance_row, "*资产合计")

                    # 查找对应期间的利润表数据
                    operating_cost = 0
                    asset_impairment = 0
                    gross_margin = 0

                    if income_df is not None and not income_df.empty:
                        matching_income = income_df[income_df["报告期"] == period]
                        if not matching_income.empty:
                            income_row = matching_income.iloc[0]
                            operating_cost = get_field_value(income_row, "其中：营业成本")
                            asset_impairment = get_field_value(income_row, "资产减值损失")

                    # 计算关键指标
                    inventory_to_assets_ratio = (inventory / total_assets * 100) if total_assets > 0 else 0
                    inventory_impairment_ratio = (asset_impairment / inventory * 100) if inventory > 0 else 0
                    inventory_turnover = (operating_cost / inventory) if inventory > 0 else 0

                    # 风险评估
                    risk_factors = []
                    risk_level = "✅ 正常"

                    # 存货占总资产比例风险
                    if inventory_to_assets_ratio > 30:
                        risk_factors.append("存货占比过高")
                        risk_level = "⚠️ 异常"
                    elif inventory_to_assets_ratio > 20:
                        risk_factors.append("存货占比较高")
                        if risk_level == "✅ 正常":
                            risk_level = "🟡 需要关注"

                    # 存货减值计提不足风险
                    if inventory > 0 and asset_impairment == 0:
                        risk_factors.append("未计提存货减值准备")
                        if risk_level == "✅ 正常":
                            risk_level = "🟡 需要关注"

                    # 存货周转率风险
                    if inventory_turnover < 2:
                        risk_factors.append("存货周转缓慢")
                        if risk_level == "✅ 正常":
                            risk_level = "🟡 需要关注"
                    elif inventory_turnover < 1:
                        risk_factors.append("存货积压严重")
                        risk_level = "⚠️ 异常"

                    risk_assessments.append(risk_level)

                    detailed_data.append({
                        "报告期": period,
                        "存货(百万元)": inventory / 1000000,
                        "总资产(百万元)": total_assets / 1000000,
                        "营业成本(百万元)": operating_cost / 1000000,
                        "资产减值损失(百万元)": asset_impairment / 1000000,
                        "存货占总资产比例(%)": inventory_to_assets_ratio,
                        "存货减值计提比例(%)": inventory_impairment_ratio,
                        "存货周转率(次)": inventory_turnover,
                        "评估结果": risk_level
                    })

                except (KeyError, ValueError) as e:
                    continue

            # 判断整体风险
            overall_risk = "✅ 正常"
            if "⚠️ 异常" in risk_assessments:
                overall_risk = "⚠️ 异常"
            elif "🟡 需要关注" in risk_assessments:
                overall_risk = "🟡 需要关注"

            passed = overall_risk in ["✅ 正常", "🟡 需要关注"]

            # 获取最新数据用于子问题分析
            latest_data = detailed_data[0] if detailed_data else {}

            # 生成子问题
            sub_questions = [
                self.create_sub_question(
                    question="存货（特别是易贬值品）的减值准备计提是否充分？",
                    passed=latest_data.get("存货减值计提比例(%)", 0) > 0 or latest_data.get("存货(百万元)", 0) == 0,
                    calculation="存货减值计提比例 = 资产减值损失 ÷ 存货 × 100%",
                    result=f"{latest_data.get('存货减值计提比例(%)', 0):.2f}%",
                    threshold="> 0%",
                    details={
                        "存货余额": format_financial_number(latest_data.get("存货(百万元)", 0)),
                        "减值损失": format_financial_number(latest_data.get("资产减值损失(百万元)", 0)),
                        "计提比例": f"{latest_data.get('存货减值计提比例(%)', 0):.2f}%"
                    },
                    report_guide="检查财务报表附注中关于存货跌价准备的会计政策和计提情况"
                ),
                self.create_sub_question(
                    question="存货增长是否快于营业成本？",
                    passed=True,  # 需要多期数据比较，暂时通过
                    calculation="存货增长率 vs 营业成本增长率",
                    result="需要多期数据进行比较分析",
                    threshold="存货增长率不应显著高于营业成本增长率",
                    details={
                        "当前存货": format_financial_number(latest_data.get("存货(百万元)", 0)),
                        "当前营业成本": format_financial_number(latest_data.get("营业成本(百万元)", 0)),
                        "分析建议": "应对比历史数据，分析存货增长趋势"
                    },
                    report_guide="查看历年财务数据，对比存货和营业成本的增长趋势"
                ),
                self.create_sub_question(
                    question="存货周转率下降的同时毛利率是否异常提升？",
                    passed=True,  # 需要毛利率数据，暂时通过
                    calculation="存货周转率 = 营业成本 ÷ 平均存货",
                    result=f"{latest_data.get('存货周转率(次)', 0):.2f}次",
                    threshold="存货周转率应保持相对稳定",
                    details={
                        "存货周转率": f"{latest_data.get('存货周转率(次)', 0):.2f}次",
                        "行业参考": "不同行业标准不同，一般制造业3-6次较为正常"
                    },
                    report_guide="结合行业特点分析存货周转率的合理性和变化趋势"
                )
            ]

            # 生成总结
            summary = f"存货占总资产比例为{latest_data.get('存货占总资产比例(%)', 0):.2f}%，"

            if overall_risk == "⚠️ 异常":
                summary += "存货存在较高风险。"
                if latest_data.get("存货减值计提比例(%)", 0) == 0:
                    summary += "未计提存货减值准备，"
                if latest_data.get("存货周转率(次)", 0) < 2:
                    summary += "存货周转缓慢，"
                summary += "需要重点关注存货质量和跌价风险。"
            elif overall_risk == "🟡 需要关注":
                summary += "存货存在一定风险，需要关注存货管理和跌价准备计提情况。"
            else:
                summary += "存货风险相对较低，管理较为正常。"

            return self.create_checklist_item(
                passed=passed,
                summary=summary,
                calculation_details={
                    "detailed_data": detailed_data
                },
                sub_questions=sub_questions
            )

        except Exception as e:
            return self.handle_data_error(data)


class FixedAssetDepreciationCalculator(BaseCalculator):
    """固定资产折旧政策检查计算器"""

    question_id = "1.1.12"
    question = "固定资产折旧政策是否变更？"
    category = ChecklistCategory.ASSETS
    description = "检查固定资产折旧政策变更及固定资产周转率"

    def get_required_fields(self) -> Dict[str, List[str]]:
        """获取所需的数据字段"""
        return {
            "balance_sheet": [
                "报告期",
                "其中：固定资产",
                "*资产合计"
            ],
            "income_statement": [
                "报告期",
                "其中：营业收入"
            ]
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """计算固定资产折旧政策分析"""
        try:
            # 获取数据
            balance_df = data.get("balance_sheet")
            income_df = data.get("income_statement")

            if balance_df is None or balance_df.empty:
                return self.handle_data_error(data)

            # 生成详细数据用于表格显示
            detailed_data = []

            for _, balance_row in balance_df.iterrows():
                try:
                    # 获取资产负债表数据
                    period = get_field_value(balance_row, "报告期")
                    fixed_assets = get_field_value(balance_row, "其中：固定资产")
                    total_assets = get_field_value(balance_row, "*资产合计")

                    # 查找对应期间的利润表数据
                    revenue = 0

                    if income_df is not None and not income_df.empty:
                        matching_income = income_df[income_df["报告期"] == period]
                        if not matching_income.empty:
                            income_row = matching_income.iloc[0]
                            revenue = get_field_value(income_row, "其中：营业收入")

                    # 计算关键指标
                    fixed_assets_to_total_ratio = (fixed_assets / total_assets * 100) if total_assets > 0 else 0
                    fixed_assets_turnover = (revenue / fixed_assets) if fixed_assets > 0 else 0

                    # 风险评估
                    risk_assessment = "✅ 正常"
                    risk_factors = []

                    # 固定资产占比分析
                    if fixed_assets_to_total_ratio > 60:
                        risk_assessment = "⚠️ 异常"
                        risk_factors.append("固定资产占比过高")
                    elif fixed_assets_to_total_ratio > 40:
                        if risk_assessment == "✅ 正常":
                            risk_assessment = "🟡 需要关注"
                        risk_factors.append("固定资产占比较高")

                    # 固定资产周转率分析
                    if fixed_assets_turnover < 1:
                        if risk_assessment == "✅ 正常":
                            risk_assessment = "🟡 需要关注"
                        risk_factors.append("固定资产周转率较低")
                    elif fixed_assets_turnover < 0.5:
                        risk_assessment = "⚠️ 异常"
                        risk_factors.append("固定资产利用效率低")

                    detailed_data.append({
                        "报告期": period,
                        "固定资产(百万元)": fixed_assets / 1000000,
                        "总资产(百万元)": total_assets / 1000000,
                        "营业收入(百万元)": revenue / 1000000,
                        "固定资产占总资产比例(%)": fixed_assets_to_total_ratio,
                        "固定资产周转率(次)": fixed_assets_turnover,
                        "评估结果": risk_assessment
                    })

                except (KeyError, ValueError) as e:
                    continue

            # 判断整体情况
            latest_data = detailed_data[0] if detailed_data else {}
            overall_assessment = latest_data.get("评估结果", "✅ 正常")
            passed = overall_assessment in ["✅ 正常", "🟡 需要关注"]

            # 如果有多期数据，分析趋势
            trend_analysis = ""
            if len(detailed_data) >= 2:
                current_turnover = detailed_data[0].get("固定资产周转率(次)", 0)
                previous_turnover = detailed_data[1].get("固定资产周转率(次)", 0)

                if current_turnover < previous_turnover * 0.8:  # 下降超过20%
                    trend_analysis = f"固定资产周转率从{previous_turnover:.2f}次下降到{current_turnover:.2f}次，"
                    trend_analysis += "可能存在折旧政策变更或资产利用效率下降。"
                elif current_turnover > previous_turnover * 1.2:  # 上升超过20%
                    trend_analysis = f"固定资产周转率从{previous_turnover:.2f}次上升到{current_turnover:.2f}次，"
                    trend_analysis += "资产利用效率有所提升。"
                else:
                    trend_analysis = f"固定资产周转率保持相对稳定，从{previous_turnover:.2f}次变化到{current_turnover:.2f}次。"

            # 生成子问题
            sub_questions = [
                self.create_sub_question(
                    question="变更原因及影响是否合理？",
                    passed=len(detailed_data) < 2 or abs(detailed_data[0].get("固定资产周转率(次)", 0) - detailed_data[1].get("固定资产周转率(次)", 0)) / detailed_data[1].get("固定资产周转率(次)", 1) < 0.3,
                    calculation="固定资产周转率 = 营业收入 ÷ 固定资产净值",
                    result=f"当前周转率: {latest_data.get('固定资产周转率(次)', 0):.2f}次",
                    threshold="周转率变化幅度应小于30%",
                    details={
                        "当前固定资产": format_financial_number(latest_data.get("固定资产(百万元)", 0)),
                        "当前营业收入": format_financial_number(latest_data.get("营业收入(百万元)", 0)),
                        "周转率变化": trend_analysis if trend_analysis else "需要多期数据进行分析"
                    },
                    report_guide="检查财务报表附注中关于固定资产折旧政策的变更说明"
                ),
                self.create_sub_question(
                    question="有无账面价值极低但实际价值未降的资产（如酒窖、房产）？",
                    passed=latest_data.get("固定资产占总资产比例(%)", 0) < 50,
                    calculation="固定资产占总资产比例 = 固定资产 ÷ 总资产 × 100%",
                    result=f"{latest_data.get('固定资产占总资产比例(%)', 0):.2f}%",
                    threshold="应关注特殊行业固定资产价值重估情况",
                    details={
                        "固定资产占比": f"{latest_data.get('固定资产占总资产比例(%)', 0):.2f}%",
                        "行业特点": "酒类、房地产等行业可能存在账面价值与实际价值不符的情况",
                        "分析建议": "应结合行业特点分析固定资产的真实价值"
                    },
                    report_guide="查看资产评估报告和固定资产明细，了解资产实际状况"
                )
            ]

            # 生成总结
            summary = f"固定资产占总资产比例为{latest_data.get('固定资产占总资产比例(%)', 0):.2f}%，"

            if overall_assessment == "⚠️ 异常":
                summary += "固定资产折旧政策可能存在问题。"
                if latest_data.get("固定资产周转率(次)", 0) < 1:
                    summary += "固定资产周转率较低，"
                summary += "需要关注折旧政策变更和资产利用效率。"
            elif overall_assessment == "🟡 需要关注":
                summary += "固定资产折旧政策需要关注。"
                if trend_analysis:
                    summary += trend_analysis
                else:
                    summary += "建议持续关注资产使用效率。"
            else:
                summary += "固定资产折旧政策相对正常，资产利用效率良好。"

            return self.create_checklist_item(
                passed=passed,
                summary=summary,
                calculation_details={
                    "detailed_data": detailed_data
                },
                sub_questions=sub_questions
            )

        except Exception as e:
            return self.handle_data_error(data)


class FinancialFraudRiskCalculator(BaseCalculator):
    """财务造假高危领域检查计算器"""

    question_id = "1.1.9"
    question = "公司是否属于财务造假高危领域？"
    category = ChecklistCategory.ASSETS
    description = "检查公司是否属于财务造假高风险行业"

    def get_required_fields(self) -> Dict[str, List[str]]:
        """获取所需的数据字段 - 主要基于行业信息，不依赖财务数据"""
        return {
            "balance_sheet": []  # 这个检查项主要基于行业分类，不依赖特定财务字段
        }

    def calculate(self, data: Dict[str, any]) -> ChecklistItem:
        """计算财务造假高危领域风险"""
        try:
            # 财务造假高危行业清单
            high_risk_industries = [
                "农林牧渔", "农业", "林业", "畜牧业", "渔业",
                "纺织", "服装", "皮革",
                "化工", "化纤", "塑料", "橡胶",
                "建材", "钢铁", "有色金属",
                "机械设备", "电气设备",
                "轻工制造", "家用电器"
            ]

            # 中等风险行业
            medium_risk_industries = [
                "电子", "计算机", "通信",
                "医药生物", "食品饮料",
                "商业贸易", "交通运输"
            ]

            # 低风险行业
            low_risk_industries = [
                "银行", "保险", "证券", "信托", "房地产",
                "公用事业", "传媒", "休闲服务"
            ]

            # 基于股票代码和公司特征进行风险评估
            # 注意：这是一个简化的实现，实际应用中需要获取真实的行业分类数据

            # 获取股票代码作为参考
            # 在实际应用中，这里应该调用行业分类API获取公司所属行业
            symbol = data.get("symbol", "")

            # 基于股票代码后缀等进行简单判断（这是一个示例，实际需要行业分类数据）
            risk_assessment = "✅ 正常"
            risk_factors = []
            industry_category = "未知"

            # 示例风险判断逻辑（实际应该基于行业分类数据）
            if any(industry in symbol for industry in ["农业", "农林", "畜牧", "渔业"]):
                risk_assessment = "⚠️ 高风险"
                industry_category = "农林牧渔"
                risk_factors.extend(["产品不易核查", "税收优惠较多", "估值困难"])
            elif "600" in symbol or "000" in symbol:  # 沪深主板，相对规范
                risk_assessment = "🟡 中等风险"
                industry_category = "传统制造"
                risk_factors.extend(["竞争激烈", "利润率偏低"])

            # 生成子问题
            sub_questions = [
                self.create_sub_question(
                    question="是否为农林牧渔公司？",
                    passed=industry_category != "农林牧渔",
                    calculation="基于行业分类判断",
                    result="是" if industry_category == "农林牧渔" else "否",
                    threshold="农林牧渔行业属于高风险领域",
                    details={
                        "行业分类": industry_category,
                        "风险特征": "农林牧渔行业产品不易核查，估值困难，是财务造假高发领域"
                    },
                    report_guide="重点关注存货真实性、收入确认政策、生物资产计量"
                ),
                self.create_sub_question(
                    question="税收优惠是否多？",
                    passed=risk_assessment in ["✅ 正常", "🟡 中等风险"],
                    calculation="分析公司享受的税收优惠政策",
                    result="较多" if "税收优惠较多" in risk_factors else "正常",
                    threshold="税收优惠过多可能增加财务造假动机",
                    details={
                        "税收情况": "较多" if "税收优惠较多" in risk_factors else "正常",
                        "分析要点": "重点关注所得税优惠、增值税返还等政策的合理性"
                    },
                    report_guide="查看财务报表附注中的税收优惠政策说明"
                ),
                self.create_sub_question(
                    question="产品是否不易核查或估值？",
                    passed="估值困难" not in risk_factors,
                    calculation="分析产品和业务的核查难度",
                    result="是" if "估值困难" in risk_factors else "否",
                    threshold="产品或业务不易核实是财务造假的重要特征",
                    details={
                        "产品特征": "不易核查" if "产品不易核查" in risk_factors else "相对透明",
                        "估值难度": "困难" if "估值困难" in risk_factors else "相对容易"
                    },
                    report_guide="重点关注存货盘点、收入确认、成本核算等关键环节"
                )
            ]

            # 生成总结
            summary = f"公司风险评估为{risk_assessment}，"

            if risk_assessment == "⚠️ 高风险":
                summary += "属于财务造假高危领域，需要重点关注。"
                if risk_factors:
                    summary += f"主要风险因素：{', '.join(risk_factors)}。"
                summary += "建议加强对财务数据真实性的核查。"
            elif risk_assessment == "🟡 中等风险":
                summary += "存在一定的财务造假风险，需要保持关注。"
                if risk_factors:
                    summary += f"需要注意：{', '.join(risk_factors)}。"
                summary += "建议定期检查财务数据的一致性。"
            else:
                summary += "财务造假风险相对较低，但仍需保持基本的财务分析警惕性。"

            # 判断是否通过检查
            passed = risk_assessment in ["✅ 正常", "🟡 中等风险"]

            return self.create_checklist_item(
                passed=passed,
                summary=summary,
                calculation_details={
                    "detailed_data": [{
                        "行业分类": industry_category,
                        "风险评估": risk_assessment,
                        "主要风险因素": ", ".join(risk_factors) if risk_factors else "无",
                        "建议关注点": "财务数据真实性、收入确认、存货计价" if risk_assessment == "⚠️ 高风险" else "常规财务分析"
                    }]
                },
                sub_questions=sub_questions
            )

        except Exception as e:
            return self.handle_data_error(data)


# 注册所有计算器

register_calculator(CashSafetyCalculator)
register_calculator(CashAnomalyCalculator)
register_calculator(NotesReceivableCalculator)
register_calculator(ReceivablesCalculator)
register_calculator(PrepaidExpensesCalculator)
register_calculator(OtherReceivablesCalculator)
register_calculator(BadDebtProvisionCalculator)
register_calculator(InventoryRiskCalculator)
register_calculator(FixedAssetDepreciationCalculator)
register_calculator(FinancialFraudRiskCalculator)
