"""
资产类检查项计算器
"""

import pandas as pd
from typing import Dict, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.base_calculator import BaseCalculator
from core.data_accessor import get_field_value, parse_amount, format_accounting
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
                    "货币资金(百万元)": cash,
                    "交易性金融资产(百万元)": financial_assets,
                    "短期借款(百万元)": short_debt,
                    "长期借款(百万元)": long_debt,
                    "有息负债合计(百万元)": short_debt + long_debt
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
                        "货币资金": format_accounting(cash),
                        "有息负债": format_accounting(total_interest_debt),
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
                        "货币资金": format_accounting(cash),
                        "交易性金融资产": format_accounting(financial_assets),
                        "有息负债": format_accounting(total_interest_debt),
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
                    "货币资金": format_accounting(cash),
                    "交易性金融资产": format_accounting(financial_assets),
                    "有息负债": format_accounting(total_interest_debt),
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
                        "货币资金(百万元)": format_accounting(cash),
                        "短期借款(百万元)": format_accounting(short_debt),
                        "资金覆盖度": "100%" if cash_to_short_debt == float('inf') else f"{cash_to_short_debt:.2f}",
                        "利息收入(百万元)": format_accounting(interest_income),
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
                    "货币资金": format_accounting(cash),
                    "短期借款": format_accounting(short_debt),
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
                    "利息收入": format_accounting(interest_income),
                    "货币资金": format_accounting(cash),
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
                "货币资金": format_accounting(cash),
                "短期借款": format_accounting(short_debt),
                "利息收入": format_accounting(interest_income),
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

        # 实现逻辑类似原有的generate_notes_receivable_health_checklist
        # 为简洁起见，这里只展示框架
        latest_row = balance_df.iloc[0]
        try:
            notes_receivable = parse_amount(get_field_value(latest_row, "应收票据及应收账款"))
            total_assets = parse_amount(get_field_value(latest_row, "*资产合计"))
            receivables = parse_amount(get_field_value(latest_row, "应收账款"))

            notes_ratio = notes_receivable / total_assets if total_assets > 0 else 0
            asset_ratio_passed = notes_ratio <= 0.15

            # 创建简化的检查项
            sub_question = self.create_sub_question(
                question="应收票据占总资产比例是否过高？",
                passed=asset_ratio_passed,
                calculation="应收票据占总资产比例 = 应收票据 ÷ 总资产",
                result=notes_ratio,
                threshold=0.15,
                details={
                    "应收票据": format_accounting(notes_receivable),
                    "总资产": format_accounting(total_assets),
                    "占比": f"{notes_ratio:.2%}",
                    "报告期": get_field_value(latest_row, "报告期")
                },
                report_guide='查看"资产负债表"中"应收票据及应收账款"和"*资产合计"项目'
            )

            summary = f"应收票据占比{notes_ratio:.2%}{'≤15%，规模合理' if asset_ratio_passed else '>15%，规模过大需要关注'}"

            return self.create_checklist_item(
                passed=asset_ratio_passed,
                summary=summary,
                calculation_details={
                    "报告期": get_field_value(latest_row, "报告期"),
                    "应收票据": format_accounting(notes_receivable),
                    "总资产": format_accounting(total_assets),
                    "占总资产比例": f"{notes_ratio:.2%}"
                },
                sub_questions=[sub_question]
            )
        except KeyError:
            return self.handle_data_error(data)


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

        # 实现逻辑类似原有的generate_receivables_health_checklist
        latest_balance = balance_df.iloc[0]
        latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

        if latest_income.empty:
            return self.handle_data_error(data)

        latest_income = latest_income.iloc[0]

        try:
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
                        "应收账款": format_accounting(receivables),
                        "总资产": format_accounting(total_assets),
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
                        "营业收入": format_accounting(revenue),
                        "应收账款": format_accounting(receivables),
                        "周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}",
                        "报告期": get_field_value(latest_balance, "报告期")
                    },
                    report_guide='查看"资产负债表"中"应收账款"和"利润表"中"其中：营业收入"项目'
                )
            ]

            # 生成检查总结
            if overall_passed:
                if receivables_turnover == float('inf'):
                    summary = f"应收账款占比{receivables_to_assets:.2%}≤10%，周转率100%（应收账款为0），应收账款状况极好"
                else:
                    summary = f"应收账款占比{receivables_to_assets:.2%}≤10%，周转率{receivables_turnover:.1f}次≥6次，应收账款状况良好"
            else:
                if not assets_ratio_passed and not turnover_passed:
                    summary = f"应收账款占比{receivables_to_assets:.2%}>10%，周转率{receivables_turnover:.1f}次<6次，存在双重风险"
                elif not assets_ratio_passed:
                    summary = f"应收账款占比{receivables_to_assets:.2%}>10%，占总资产比例过高"
                else:
                    summary = f"应收账款周转率{receivables_turnover:.1f}次<6次，回款速度过慢"

            return self.create_checklist_item(
                passed=overall_passed,
                summary=summary,
                calculation_details={
                    "报告期": get_field_value(latest_balance, "报告期"),
                    "应收账款": format_accounting(receivables),
                    "总资产": format_accounting(total_assets),
                    "营业收入": format_accounting(revenue),
                    "应收账款占总资产比例": f"{receivables_to_assets:.2%}",
                    "应收账款周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}"
                },
                sub_questions=sub_questions
            )
        except KeyError:
            return self.handle_data_error(data)


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

        # 实现逻辑类似原有的generate_prepaid_expenses_anomaly_checklist
        latest_balance = balance_df.iloc[0]
        latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

        if latest_income.empty:
            return self.handle_data_error(data)

        latest_income = latest_income.iloc[0]

        try:
            prepaid_expenses = parse_amount(get_field_value(latest_balance, "预付款项"))
            total_assets = parse_amount(get_field_value(latest_balance, "*资产合计"))
            revenue = parse_amount(get_field_value(latest_income, "其中：营业收入"))
            cost = parse_amount(get_field_value(latest_income, "其中：营业成本"))

            # 检查1：预付账款占总资产比例是否过高（>5%为风险）
            prepaid_to_assets = prepaid_expenses / total_assets if total_assets > 0 else 0
            asset_ratio_passed = prepaid_to_assets <= 0.05

            # 检查2：预付账款占收入比例是否过大（>10%为风险）
            prepaid_to_revenue = prepaid_expenses / revenue if revenue > 0 else 0
            revenue_ratio_passed = prepaid_to_revenue <= 0.10

            # 检查3：预付账款占成本比例是否波动过大
            prepaid_to_cost = prepaid_expenses / cost if cost > 0 else 0
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
                    "预付账款": format_accounting(prepaid_expenses),
                    "总资产": format_accounting(total_assets),
                    "占比": f"{prepaid_to_assets:.2%}",
                    "报告期": get_field_value(latest_balance, "报告期")
                },
                report_guide='查看"资产负债表"中"预付账款"和"*资产合计"项目'
            )

            # 生成检查总结
            issues = []
            if not asset_ratio_passed:
                issues.append("占总资产比例过高")
            if not revenue_ratio_passed:
                issues.append("占收入比例过大")
            if not cost_ratio_passed:
                issues.append("占成本比例过大")

            if not issues:
                summary = f"预付账款占比资产{prepaid_to_assets:.2%}≤5%，占收入{prepaid_to_revenue:.2%}≤10%，占成本{prepaid_to_cost:.2%}≤15%，未发现异常"
            else:
                issues_str = "、".join(issues)
                summary = f"预付账款存在异常：{issues_str}"

            return self.create_checklist_item(
                passed=overall_passed,
                summary=summary,
                calculation_details={
                    "报告期": get_field_value(latest_balance, "报告期"),
                    "预付账款": format_accounting(prepaid_expenses),
                    "总资产": format_accounting(total_assets),
                    "营业收入": format_accounting(revenue),
                    "营业成本": format_accounting(cost),
                    "预付账款占总资产比例": f"{prepaid_to_assets:.2%}",
                    "预付账款占收入比例": f"{prepaid_to_revenue:.2%}",
                    "预付账款占成本比例": f"{prepaid_to_cost:.2%}"
                },
                sub_questions=[sub_question]
            )
        except KeyError:
            return self.handle_data_error(data)

# 注册所有计算器

register_calculator(CashSafetyCalculator)
register_calculator(CashAnomalyCalculator)
register_calculator(NotesReceivableCalculator)
register_calculator(ReceivablesCalculator)
register_calculator(PrepaidExpensesCalculator)
