#!/usr/bin/env python3
"""
A股股票财报检查清单分析工具

基于财报检查清单的逐项检查分析
专注于问题导向的财务健康状况评估
"""

import streamlit as st
import pandas as pd
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class SubQuestion:
    """子问题/追问数据结构"""
    question: str            # 追问内容
    passed: bool             # 通过/失败
    calculation: str         # 计算公式
    result: float            # 计算结果
    threshold: float         # 判断阈值
    details: Dict            # 详细数据
    report_guide: str        # 财报指引


@dataclass
class ChecklistItem:
    """检查清单项目数据结构"""
    question_id: str          # "3.1.1"
    question: str            # "货币资金是否安全？"
    passed: bool             # True/False
    summary: str             # 检查总结
    calculation_details: Dict # 计算详细数据
    sub_questions: List[SubQuestion]  # 追问列表


class StockAnalyzer:
    """通用股票检查清单分析器"""

    def __init__(self, symbol: str, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
        self.symbol = symbol

    def fetch_financial_data(self, query_type: str, fields: List[str],
                           start_date: str, end_date: str) -> Dict:
        """从FastAPI获取财务数据"""
        try:
            response = self.client.post(
                f"{self.api_base_url}/api/v1/financial/query",
                json={
                    "market": "a_stock",
                    "query_type": query_type,
                    "symbol": self.symbol,
                    "fields": fields,
                    "start_date": start_date,
                    "end_date": end_date,
                    "frequency": "annual"
                }
            )
            response.raise_for_status()
            data = response.json()
            # 检查API响应状态
            if data.get("status") == "success":
                return data
            else:
                st.error(f"API返回错误: {data}")
                return {}
        except Exception as e:
            st.error(f"数据获取失败: {e}")
            return {}

    def validate_fields_exist(self, query_type: str, required_fields: List[str]) -> None:
        """验证所需字段是否在API中存在"""
        # 获取所有可用字段
        try:
            # 根据API路由，正确的URL格式为 /api/v1/financial/fields/{market}/{query_type}
            market = "a_stock"  # 硬编码为A股市场
            response = self.client.get(
                f"{self.api_base_url}/api/v1/financial/fields/{market}/{query_type}"
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                available_fields = data.get("metadata", {}).get("available_fields", [])
                missing_fields = [field for field in required_fields if field not in available_fields]

                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    raise ValueError(f"以下字段不存在: {missing_fields_str}")
        except httpx.ReadTimeout:
            st.warning("API连接超时，跳过字段验证，直接尝试获取数据")
        except httpx.ConnectError:
            st.error("无法连接到API服务器，请检查服务是否正常运行")
            raise
        except Exception as e:
            # 对于其他错误，我们仅显示警告并继续，不中断程序
            st.warning(f"字段验证失败: {e}，继续尝试获取数据")

    def get_balance_sheet_data(self, years: int = 5) -> pd.DataFrame:
        """获取资产负债表数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")

        # 获取资产负债表分析所需的字段
        # 参考现有代码和财报检查清单中的正确字段
        fields = [
            "报告期", "货币资金", "交易性金融资产",
            "短期借款", "长期借款",
            "*资产合计", "*负债合计",
            # 扩展字段用于其他检查项
            "应收账款", "存货", "其中：固定资产",
            "其中：在建工程", "应付账款", "预收款项",
            "其中：应收票据", "其他应收款", "应付职工薪酬"
        ]

        # 验证字段是否存在，但不中断程序执行
        try:
            self.validate_fields_exist("a_stock_balance_sheet", fields)
        except:
            # 如果验证失败，仍继续尝试获取数据
            pass

        data = self.fetch_financial_data(
            "a_stock_balance_sheet", fields, start_date, end_date
        )

        if data.get("status") == "success":
            df = pd.DataFrame(data["data"]["records"])
            # 清理报告期格式，去掉时分秒
            if "报告期" in df.columns:
                df["报告期"] = df["报告期"].str.split("T").str[0]
            # 按报告期降序排列（最新的在前）
            df = df.sort_values("报告期", ascending=False)
            return df

        return pd.DataFrame()

    def get_income_statement_data(self, years: int = 5) -> pd.DataFrame:
        """获取利润表数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")

        # 获取利润表所需的字段
        fields = [
            "报告期", "其中：营业收入", "利息收入"
        ]

        # 验证字段是否存在，但不中断程序执行
        try:
            self.validate_fields_exist("a_stock_income_statement", fields)
        except:
            # 如果验证失败，仍继续尝试获取数据
            pass

        data = self.fetch_financial_data(
            "a_stock_income_statement", fields, start_date, end_date
        )

        if data.get("status") == "success":
            df = pd.DataFrame(data["data"]["records"])
            # 清理报告期格式，去掉时分秒
            if "报告期" in df.columns:
                df["报告期"] = df["报告期"].str.split("T").str[0]
            # 按报告期降序排列（最新的在前）
            df = df.sort_values("报告期", ascending=False)
            return df

        return pd.DataFrame()


def format_accounting(value, unit='百万'):
    """将数字格式化为会计常用格式"""
    if pd.isna(value) or value == 0:
        return "0.00"

    if isinstance(value, str):
        try:
            # 如果已经是字符串格式，先转换为数字
            if '亿' in value:
                num_value = float(value.replace('亿', '')) * 100
            elif '万' in value:
                num_value = float(value.replace('万', '')) * 0.01
            else:
                num_value = float(value)
        except:
            return value
    else:
        num_value = value / 1000000  # 转换为百万

    # 会计格式：负数用括号表示，千位分隔，保留两位小数
    if num_value < 0:
        return f"({abs(num_value):,.2f})"
    else:
        return f"{num_value:,.2f}"


def _parse_amount(value):
    """解析金额字符串，处理 '924.64亿' 这样的格式"""
    if pd.isna(value) or value == 0:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        if '亿' in value:
            return float(value.replace('亿', '')) * 100000000
        elif '万' in value:
            return float(value.replace('万', '')) * 10000
        else:
            return float(value)

    return 0.0


def generate_cash_safety_checklist(balance_df: pd.DataFrame) -> List[ChecklistItem]:
    """生成货币资金安全检查清单"""
    if balance_df.empty:
        return []

    checklist_items = []

    # 先收集原始数据
    raw_data = []
    for _, row in balance_df.iterrows():
        cash = _parse_amount(row.get("货币资金", 0))
        short_debt = _parse_amount(row.get("短期借款", 0))
        long_debt = _parse_amount(row.get("长期借款", 0))
        financial_assets = _parse_amount(row.get("交易性金融资产", 0))
        # 应付债券字段不存在，设为0
        bonds = 0

        raw_data.append({
            "报告期": row["报告期"],
            "货币资金(百万元)": cash,
            "交易性金融资产(百万元)": financial_assets,
            "短期借款(百万元)": short_debt,
            "长期借款(百万元)": long_debt,
            "应付债券(百万元)": bonds
        })

    # 计算指标数据
    calculated_data = []
    for data in raw_data:
        cash = data["货币资金(百万元)"]
        short_debt = data["短期借款(百万元)"]
        long_debt = data["长期借款(百万元)"]
        financial_assets = data["交易性金融资产(百万元)"]
        bonds = data["应付债券(百万元)"]

        total_interest_debt = short_debt + long_debt + bonds
        safety_ratio = cash / total_interest_debt if total_interest_debt > 0 else float('inf')
        total_liquid_assets = cash + financial_assets
        total_coverage_ratio = total_liquid_assets / total_interest_debt if total_interest_debt > 0 else float('inf')

        calculated_data.append({
            "报告期": data["报告期"],
            "有息负债(百万元)": total_interest_debt,
            "货币资金安全比率": "100%" if safety_ratio == float('inf') else f"{safety_ratio:.2f}",
            "总覆盖率": "100%" if total_coverage_ratio == float('inf') else f"{total_coverage_ratio:.2f}",
            "安全性": "安全" if safety_ratio >= 1 else "风险"
        })

    # 获取最新年份的数据用于检查结果
    latest_row = balance_df.iloc[0]
    report_period = latest_row["报告期"]

    # 解析关键财务数据
    cash = _parse_amount(latest_row.get("货币资金", 0))
    financial_assets = _parse_amount(latest_row.get("交易性金融资产", 0))
    short_debt = _parse_amount(latest_row.get("短期借款", 0))
    long_debt = _parse_amount(latest_row.get("长期借款", 0))

    # 应付债券字段不存在，设为0
    bonds = 0

    # 计算有息负债总额
    total_interest_debt = short_debt + long_debt + bonds

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
        SubQuestion(
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
        SubQuestion(
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
            safe_ratio_text = "100%" if sub_questions[0].details['安全比率'] == "∞" else sub_questions[0].details['安全比率']
            summary = f"货币资金非常充足，安全比率={safe_ratio_text}，财务风险极低"
        else:
            safe_ratio_text = "100%" if sub_questions[0].details['安全比率'] == "∞" else sub_questions[0].details['安全比率']
            summary = f"货币资金充足，安全比率={safe_ratio_text}，能够覆盖有息负债，财务风险较低"
    else:
        safe_ratio_text = "100%" if sub_questions[0].details['安全比率'] == "∞" else sub_questions[0].details['安全比率']
        summary = f"货币资金不足，安全比率={safe_ratio_text} < 1，存在财务风险"

    # 创建检查清单项目
    checklist_item = ChecklistItem(
        question_id="1.1.1",
        question="货币资金是否安全？",
        passed=overall_passed,
        summary=summary,
        calculation_details={
            "报告期": report_period,
            "货币资金": format_accounting(cash),
            "交易性金融资产": format_accounting(financial_assets),
            "有息负债": format_accounting(total_interest_debt),
            "安全比率": "100%" if sub_questions[0].details['安全比率'] == "∞" else sub_questions[0].details['安全比率'],
            "总覆盖率": "100%" if sub_questions[1].details['总覆盖率'] == "∞" else sub_questions[1].details['总覆盖率'],
            "raw_data": raw_data,  # 原始数据
            "calculated_data": calculated_data  # 计算结果数据
        },
        sub_questions=sub_questions
    )

    checklist_items.append(checklist_item)
    return checklist_items


def generate_cash_anomaly_checklist(balance_df: pd.DataFrame, income_df: pd.DataFrame) -> List[ChecklistItem]:
    """生成货币资金异常检查清单"""
    if balance_df.empty or income_df.empty:
        return []

    checklist_items = []

    # 合并资产负债表和利润表数据
    merged_data = []
    for _, balance_row in balance_df.iterrows():
        report_period = balance_row["报告期"]
        # 查找对应年度的利润表数据
        income_row = income_df[income_df["报告期"].str.contains(report_period[:4])]

        if not income_row.empty:
            income_row = income_row.iloc[0]
            cash = _parse_amount(balance_row.get("货币资金", 0))
            short_debt = _parse_amount(balance_row.get("短期借款", 0))
            interest_income = _parse_amount(income_row.get("利息收入", 0))

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

    # 获取最新年份的数据用于检查结果
    latest_balance = balance_df.iloc[0]
    latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

    if latest_income.empty:
        return []

    latest_income = latest_income.iloc[0]
    report_period = latest_balance["报告期"]

    # 解析关键财务数据
    cash = _parse_amount(latest_balance.get("货币资金", 0))
    short_debt = _parse_amount(latest_balance.get("短期借款", 0))
    interest_income = _parse_amount(latest_income.get("利息收入", 0))

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
        SubQuestion(
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
        SubQuestion(
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
    checklist_item = ChecklistItem(
        question_id="1.1.2",
        question="货币资金是否存在异常？",
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

    checklist_items.append(checklist_item)
    return checklist_items


def generate_notes_receivable_health_checklist(balance_df: pd.DataFrame) -> List[ChecklistItem]:
    """生成应收票据健康度检查清单"""
    if balance_df.empty:
        return []

    checklist_items = []

    # 应收票据健康度分析数据 - 先收集原始数据
    raw_data = []
    for _, row in balance_df.iterrows():
        notes_receivable = _parse_amount(row.get("其中：应收票据", 0))
        total_assets = _parse_amount(row.get("*资产合计", 0))
        receivables = _parse_amount(row.get("应收账款", 0))
        revenue = _parse_amount(row.get("其中：营业收入", 0)) if "其中：营业收入" in row else 0

  
        raw_data.append({
            "报告期": row["报告期"],
            "应收票据(百万元)": notes_receivable,
            "总资产(百万元)": total_assets,
            "应收账款(百万元)": receivables,
            "营业收入(百万元)": revenue
        })

    # 计算指标数据
    calculated_data = []
    for data in raw_data:
        notes_receivable = data["应收票据(百万元)"]
        total_assets = data["总资产(百万元)"]
        receivables = data["应收账款(百万元)"]
        revenue = data["营业收入(百万元)"]

        # 应收票据占总资产比例
        notes_ratio = notes_receivable / total_assets if total_assets > 0 else 0
        # 应收票据占应收账款比例
        notes_to_receivables = notes_receivable / receivables if receivables > 0 else 0
        # 相对于营业收入的比例（保守估计，假设应收账款周转率为6次）
        estimated_revenue_ratio = notes_receivable / revenue if revenue > 0 else 0

        # 健康度评估
        if notes_ratio > 0.15:  # 超过15%
            health_level = "风险过高"
        elif notes_ratio > 0.10:  # 超过10%
            health_level = "需要关注"
        else:
            health_level = "正常"

        calculated_data.append({
            "报告期": data["报告期"],
            "占总资产比例": f"{notes_ratio:.2%}",
            "占应收账款比例": f"{notes_to_receivables:.2%}",
            "相对营业收入比例": f"{estimated_revenue_ratio:.2%}",
            "健康程度": health_level
        })

    # 获取最新年份的数据用于检查结果
    latest_row = balance_df.iloc[0]
    report_period = latest_row["报告期"]

    # 解析关键财务数据
    notes_receivable = _parse_amount(latest_row.get("其中：应收票据", 0))
    total_assets = _parse_amount(latest_row.get("*资产合计", 0))
    receivables = _parse_amount(latest_row.get("应收账款", 0))

    # 检查1：应收票据占总资产比例是否过高（>15%为风险）
    notes_ratio = notes_receivable / total_assets if total_assets > 0 else 0
    asset_ratio_passed = notes_ratio <= 0.15

    # 检查2：应收票据与应收账款的比例关系
    # 应收票据远大于应收账款是正面情况，说明应收款项更有保障
    notes_to_receivables = notes_receivable / receivables if receivables > 0 else 0
    # 应收票据占应收账款比例越高越好（票据比普通应收账款更有保障）
    matching_passed = True  # 只要有应收票据就是正面情况

    # 总体判断
    overall_passed = asset_ratio_passed and matching_passed

    # 生成追问
    sub_questions = [
        SubQuestion(
            question="应收票据占总资产比例是否过高？",
            passed=asset_ratio_passed,
            calculation="应收票据占总资产比例 = 应收票据 ÷ 总资产",
            result=notes_ratio,
            threshold=0.15,
            details={
                "应收票据": format_accounting(notes_receivable),
                "总资产": format_accounting(total_assets),
                "占比": f"{notes_ratio:.2%}",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"其中：应收票据"和"*资产合计"项目'
        ),
        SubQuestion(
            question="应收票据占应收账款比例是否合理？",
            passed=matching_passed,
            calculation="应收票据占应收账款比例 = 应收票据 ÷ 应收账款",
            result=notes_to_receivables,
            threshold=0,  # 不设上限，比例越高越好
            details={
                "应收票据": format_accounting(notes_receivable),
                "应收账款": format_accounting(receivables),
                "占比": f"{notes_to_receivables:.2%}",
                "评估": "应收票据比例越高越好，票据比应收账款更有保障",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"其中：应收票据"和"应收账款"项目'
        )
    ]

    # 生成检查总结
    if overall_passed:
        if notes_ratio == 0:
            summary = "无应收票据，应收账款质量需关注"
        elif notes_to_receivables >= 1.0 and receivables > 0:
            summary = f"应收票据占应收账款{notes_to_receivables:.1f}倍≥1，应收款项质量优秀，保障性强"
        elif notes_ratio < 0.05:
            summary = f"应收票据占比{notes_ratio:.2%}≤5%，规模合理，应收款项有保障"
        else:
            summary = f"应收票据占比{notes_ratio:.2%}≤15%，规模适中，应收款项结构健康"
    else:
        # 主要风险是占总资产比例过高
        summary = f"应收票据占总资产比例{notes_ratio:.2%}>15%，规模过大需要关注"

    # 创建检查清单项目
    checklist_item = ChecklistItem(
        question_id="1.1.3",
        question="应收票据是否健康？",
        passed=overall_passed,
        summary=summary,
        calculation_details={
            "报告期": report_period,
            "应收票据": format_accounting(notes_receivable),
            "总资产": format_accounting(total_assets),
            "应收账款": format_accounting(receivables),
            "占总资产比例": f"{notes_ratio:.2%}",
            "占应收账款比例": f"{notes_to_receivables:.2%}",
            "raw_data": raw_data,  # 原始数据
            "calculated_data": calculated_data  # 计算结果数据
        },
        sub_questions=sub_questions
    )

    checklist_items.append(checklist_item)
    return checklist_items


def generate_receivables_health_checklist(balance_df: pd.DataFrame, income_df: pd.DataFrame) -> List[ChecklistItem]:
    """生成应收账款健康度检查清单"""
    if balance_df.empty or income_df.empty:
        return []

    checklist_items = []

    # 合并资产负债表和利润表数据
    # 按报告期匹配数据
    merged_data = []
    for _, balance_row in balance_df.iterrows():
        report_period = balance_row["报告期"]
        # 查找对应年度的利润表数据
        income_row = income_df[income_df["报告期"].str.contains(report_period[:4])]

        if not income_row.empty:
            income_row = income_row.iloc[0]
            receivables = _parse_amount(balance_row.get("应收账款", 0))
            total_assets = _parse_amount(balance_row.get("*资产合计", 0))
            revenue = _parse_amount(income_row.get("其中：营业收入", 0))

            # 计算指标
            receivables_to_assets = receivables / total_assets if total_assets > 0 else 0
            receivables_turnover = revenue / receivables if receivables > 0 else float('inf')

            merged_data.append({
                "报告期": report_period,
                "应收账款(百万元)": format_accounting(receivables),
                "总资产(百万元)": format_accounting(total_assets),
                "营业收入(百万元)": format_accounting(revenue),
                "应收账款占总资产比例": f"{receivables_to_assets:.2%}",
                "应收账款周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}"
            })

    # 获取最新年份的数据用于检查结果
    latest_balance = balance_df.iloc[0]
    latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

    if latest_income.empty:
        return []

    latest_income = latest_income.iloc[0]
    report_period = latest_balance["报告期"]

    # 解析关键财务数据
    receivables = _parse_amount(latest_balance.get("应收账款", 0))
    total_assets = _parse_amount(latest_balance.get("*资产合计", 0))
    revenue = _parse_amount(latest_income.get("其中：营业收入", 0))

    # 检查1：应收账款占总资产比例是否过高（>10%为风险）
    receivables_to_assets = receivables / total_assets if total_assets > 0 else 0
    assets_ratio_passed = receivables_to_assets <= 0.10

    # 检查2：应收账款周转率是否过低（<6次为风险）
    receivables_turnover = revenue / receivables if receivables > 0 else float('inf')
    turnover_passed = receivables_turnover >= 6.0 or receivables_turnover == float('inf')

    # 总体判断
    overall_passed = assets_ratio_passed and turnover_passed

    # 生成追问
    sub_questions = [
        SubQuestion(
            question="应收账款占总资产比例是否过高？",
            passed=assets_ratio_passed,
            calculation="应收账款占总资产比例 = 应收账款 ÷ 总资产",
            result=receivables_to_assets,
            threshold=0.10,
            details={
                "应收账款": format_accounting(receivables),
                "总资产": format_accounting(total_assets),
                "占比": f"{receivables_to_assets:.2%}",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"应收账款"和"*资产合计"项目'
        ),
        SubQuestion(
            question="应收账款周转率是否过低？",
            passed=turnover_passed,
            calculation="应收账款周转率 = 营业收入 ÷ 应收账款",
            result=receivables_turnover,
            threshold=6.0,
            details={
                "营业收入": format_accounting(revenue),
                "应收账款": format_accounting(receivables),
                "周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"应收账款"和"利润表"中"其中：营业收入"项目'
        )
    ]

    # 生成检查总结
    if overall_passed:
        if receivables_turnover == float('inf'):
            turnover_text = "100%（应收账款为0）"
            summary = f"应收账款占比{receivables_to_assets:.2%}≤10%，周转率{turnover_text}，应收账款状况极好"
        else:
            summary = f"应收账款占比{receivables_to_assets:.2%}≤10%，周转率{receivables_turnover:.1f}次≥6次，应收账款状况良好"
    else:
        if not assets_ratio_passed and not turnover_passed:
            summary = f"应收账款占比{receivables_to_assets:.2%}>10%，周转率{receivables_turnover:.1f}次<6次，存在双重风险"
        elif not assets_ratio_passed:
            summary = f"应收账款占比{receivables_to_assets:.2%}>10%，占总资产比例过高"
        else:
            summary = f"应收账款周转率{receivables_turnover:.1f}次<6次，回款速度过慢"

    # 创建检查清单项目
    checklist_item = ChecklistItem(
        question_id="1.1.4",
        question="应收账款是否健康？",
        passed=overall_passed,
        summary=summary,
        calculation_details={
            "报告期": report_period,
            "应收账款": format_accounting(receivables),
            "总资产": format_accounting(total_assets),
            "营业收入": format_accounting(revenue),
            "应收账款占总资产比例": f"{receivables_to_assets:.2%}",
            "应收账款周转率": "100%" if receivables_turnover == float('inf') else f"{receivables_turnover:.2f}",
            "detailed_data": merged_data  # 添加详细数据用于表格展示
        },
        sub_questions=sub_questions
    )

    checklist_items.append(checklist_item)
    return checklist_items


def generate_prepaid_expenses_anomaly_checklist(balance_df: pd.DataFrame, income_df: pd.DataFrame) -> List[ChecklistItem]:
    """生成预付账款异常检查清单"""
    if balance_df.empty or income_df.empty:
        return []

    checklist_items = []

    # 合并资产负债表和利润表数据
    merged_data = []
    for _, balance_row in balance_df.iterrows():
        report_period = balance_row["报告期"]
        # 查找对应年度的利润表数据
        income_row = income_df[income_df["报告期"].str.contains(report_period[:4])]

        if not income_row.empty:
            income_row = income_row.iloc[0]
            prepaid_expenses = _parse_amount(balance_row.get("预付账款", 0))
            total_assets = _parse_amount(balance_row.get("*资产合计", 0))
            revenue = _parse_amount(income_row.get("其中：营业收入", 0))
            cost = _parse_amount(income_row.get("其中：营业成本", 0))

            # 计算指标
            prepaid_to_assets = prepaid_expenses / total_assets if total_assets > 0 else 0
            prepaid_to_revenue = prepaid_expenses / revenue if revenue > 0 else 0
            prepaid_to_cost = prepaid_expenses / cost if cost > 0 else 0

            merged_data.append({
                "报告期": report_period,
                "预付账款(百万元)": format_accounting(prepaid_expenses),
                "总资产(百万元)": format_accounting(total_assets),
                "营业收入(百万元)": format_accounting(revenue),
                "营业成本(百万元)": format_accounting(cost),
                "预付账款占总资产比例": f"{prepaid_to_assets:.2%}",
                "预付账款占收入比例": f"{prepaid_to_revenue:.2%}",
                "预付账款占成本比例": f"{prepaid_to_cost:.2%}"
            })

    # 获取最新年份的数据用于检查结果
    latest_balance = balance_df.iloc[0]
    latest_income = income_df[income_df["报告期"].str.contains(latest_balance["报告期"][:4])]

    if latest_income.empty:
        return []

    latest_income = latest_income.iloc[0]
    report_period = latest_balance["报告期"]

    # 解析关键财务数据
    prepaid_expenses = _parse_amount(latest_balance.get("预付账款", 0))
    total_assets = _parse_amount(latest_balance.get("*资产合计", 0))
    revenue = _parse_amount(latest_income.get("其中：营业收入", 0))
    cost = _parse_amount(latest_income.get("其中：营业成本", 0))

    # 检查1：预付账款占总资产比例是否过高（>5%为风险）
    prepaid_to_assets = prepaid_expenses / total_assets if total_assets > 0 else 0
    asset_ratio_passed = prepaid_to_assets <= 0.05

    # 检查2：预付账款占收入比例是否过大（>10%为风险）
    prepaid_to_revenue = prepaid_expenses / revenue if revenue > 0 else 0
    revenue_ratio_passed = prepaid_to_revenue <= 0.10

    # 检查3：是否有大幅增长趋势
    if len(balance_df) >= 2:
        prev_prepaid = _parse_amount(balance_df.iloc[1].get("预付账款", 0))
        # 当上期为0时，如果本期也为0，则无增长；如果本期不为0，则视为大幅增长
        if prev_prepaid == 0:
            if prepaid_expenses == 0:
                growth_rate = 0  # 都是0，无增长
                growth_abnormal = False
            else:
                growth_rate = float('inf')  # 从0到非0，视为大幅增长
                growth_abnormal = True
        else:
            growth_rate = (prepaid_expenses - prev_prepaid) / abs(prev_prepaid)
            growth_abnormal = abs(growth_rate) > 0.5  # 增长超过50%认为异常
    else:
        growth_rate = 0
        growth_abnormal = False

    # 总体判断
    overall_passed = asset_ratio_passed and revenue_ratio_passed and not growth_abnormal

    # 生成追问
    sub_questions = [
        SubQuestion(
            question="预付账款占总资产比例是否过高？",
            passed=asset_ratio_passed,
            calculation="预付账款占总资产比例 = 预付账款 ÷ 总资产",
            result=prepaid_to_assets,
            threshold=0.05,
            details={
                "预付账款": format_accounting(prepaid_expenses),
                "总资产": format_accounting(total_assets),
                "占比": f"{prepaid_to_assets:.2%}",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"预付账款"和"*资产合计"项目'
        ),
        SubQuestion(
            question="预付账款占收入比例是否过大？",
            passed=revenue_ratio_passed,
            calculation="预付账款占收入比例 = 预付账款 ÷ 营业收入",
            result=prepaid_to_revenue,
            threshold=0.10,
            details={
                "预付账款": format_accounting(prepaid_expenses),
                "营业收入": format_accounting(revenue),
                "占比": f"{prepaid_to_revenue:.2%}",
                "报告期": report_period
            },
            report_guide='查看"资产负债表"中"预付账款"和"利润表"中"其中：营业收入"项目'
        ),
        SubQuestion(
            question="预付账款是否存在大幅增长？",
            passed=not growth_abnormal,
            calculation="预付账款增长率 = (本期预付账款 - 上期预付账款) ÷ 上期预付账款",
            result=abs(growth_rate) if growth_rate != float('inf') and growth_rate != float('-inf') else float('inf'),
            threshold=0.50,
            details={
                "本期预付账款": format_accounting(prepaid_expenses),
                "上期预付账款": format_accounting(_parse_amount(balance_df.iloc[1].get("预付账款", 0)) if len(balance_df) > 1 else 0),
                "增长率": f"{growth_rate:.2%}" if growth_rate != float('inf') and growth_rate != float('-inf') else "∞",
                "报告期": report_period
            },
            report_guide='比较连续年度"资产负债表"中"预付账款"项目变化'
        )
    ]

    # 生成检查总结
    issues = []
    if not asset_ratio_passed:
        issues.append("占总资产比例过高")
    if not revenue_ratio_passed:
        issues.append("占收入比例过大")
    if growth_abnormal:
        issues.append("存在大幅增长")

    if not issues:
        summary = f"预付账款占比资产{prepaid_to_assets:.2%}≤5%，占收入{prepaid_to_revenue:.2%}≤10%，未发现异常"
    else:
        issues_str = "、".join(issues)
        summary = f"预付账款存在异常：{issues_str}"

    # 创建检查清单项目
    checklist_item = ChecklistItem(
        question_id="1.1.5",
        question="预付账款是否异常？",
        passed=overall_passed,
        summary=summary,
        calculation_details={
            "报告期": report_period,
            "预付账款": format_accounting(prepaid_expenses),
            "总资产": format_accounting(total_assets),
            "营业收入": format_accounting(revenue),
            "预付账款占总资产比例": f"{prepaid_to_assets:.2%}",
            "预付账款占收入比例": f"{prepaid_to_revenue:.2%}",
            "增长率": f"{growth_rate:.2%}" if growth_rate != float('inf') and growth_rate != float('-inf') else "∞",
            "detailed_data": merged_data  # 添加详细数据用于表格展示
        },
        sub_questions=sub_questions
    )

    checklist_items.append(checklist_item)
    return checklist_items


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

    # 设置报告期为索引并转置
    df_transposed = df.set_index("报告期").T

    # 清理列名（去掉索引名称）
    df_transposed = df_transposed.rename_axis(None, axis=1).rename_axis("指标", axis=0)

    # 只有在提供标题时才显示
    if title:
        st.subheader(title)

    # 确保所有列都是字符串类型
    df_transposed = df_transposed.astype(str)
    st.dataframe(df_transposed, width='stretch')


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


def render_checklist_item(item: ChecklistItem):
    """渲染检查清单项目"""
    status = "✅" if item.passed else "❌"

    st.markdown(f"#### {status} {item.question_id} {item.question}")
    st.markdown(f"**总结**: {item.summary}")

    with st.expander("📊 查看详细计算过程", expanded=False):
        # 根据不同的检查项显示不同的统一表格
        if item.question_id == "1.1.1":
            # 货币资金安全表格
            display_cash_safety_table(item.calculation_details)
        elif item.question_id == "1.1.2":
            # 货币资金异常表格
            display_cash_anomaly_table(item.calculation_details)
        elif item.question_id == "1.1.3":
            # 应收票据健康度表格
            display_notes_receivable_table(item.calculation_details)
        elif item.question_id == "1.1.4":
            # 应收账款健康度表格
            display_receivables_health_table(item.calculation_details)

        # 显示子问题
        for sub_question in item.sub_questions:
            render_sub_question(sub_question, item.calculation_details.get("detailed_data"))
            st.markdown("")  # 添加空行分隔


def display_cash_safety_table(calculation_details: Dict):
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


def display_notes_receivable_table(calculation_details: Dict):
    """显示应收票据健康度计算表格"""
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

    # 第1行：应收票据
    notes_row = {"指标": "应收票据(百万元)"}
    for item in raw_data_sorted:
        notes_row[item["报告期"]] = format_accounting(item["应收票据(百万元)"])
    table_data.append(notes_row)

    # 第2行：应收账款
    receivables_row = {"指标": "应收账款(百万元)"}
    for item in raw_data_sorted:
        receivables_row[item["报告期"]] = format_accounting(item["应收账款(百万元)"])
    table_data.append(receivables_row)

    # 第3行：总资产
    assets_row = {"指标": "总资产(百万元)"}
    for item in raw_data_sorted:
        assets_row[item["报告期"]] = format_accounting(item["总资产(百万元)"])
    table_data.append(assets_row)

    # 第4行：营业收入
    revenue_row = {"指标": "营业收入(百万元)"}
    for item in raw_data_sorted:
        revenue_row[item["报告期"]] = format_accounting(item["营业收入(百万元)"])
    table_data.append(revenue_row)

    # 第5行：占总资产比例
    asset_ratio_map = {item["报告期"]: item["占总资产比例"] for item in calculated_data}
    asset_ratio_row = {"指标": "占总资产比例"}
    for year in years:
        asset_ratio_row[year] = asset_ratio_map.get(year, "N/A")
    table_data.append(asset_ratio_row)

    # 第6行：占应收账款比例
    receivables_ratio_map = {item["报告期"]: item["占应收账款比例"] for item in calculated_data}
    receivables_ratio_row = {"指标": "占应收账款比例"}
    for year in years:
        receivables_ratio_row[year] = receivables_ratio_map.get(year, "N/A")
    table_data.append(receivables_ratio_row)

    # 第7行：健康程度
    health_map = {item["报告期"]: item["健康程度"] for item in calculated_data}
    health_row = {"指标": "健康程度"}
    for year in years:
        health_row[year] = health_map.get(year, "N/A")
    table_data.append(health_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)


def display_cash_anomaly_table(calculation_details: Dict):
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


def display_receivables_health_table(calculation_details: Dict):
    """显示应收账款健康度计算表格"""
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

    # 第1行：应收账款
    receivables_row = {"指标": "应收账款(百万元)"}
    for item in detailed_data_sorted:
        receivables_row[item["报告期"]] = item["应收账款(百万元)"]
    table_data.append(receivables_row)

    # 第2行：总资产
    assets_row = {"指标": "总资产(百万元)"}
    for item in detailed_data_sorted:
        assets_row[item["报告期"]] = item["总资产(百万元)"]
    table_data.append(assets_row)

    # 第3行：营业收入
    revenue_row = {"指标": "营业收入(百万元)"}
    for item in detailed_data_sorted:
        revenue_row[item["报告期"]] = item["营业收入(百万元)"]
    table_data.append(revenue_row)

    # 第4行：应收账款占总资产比例
    assets_ratio_row = {"指标": "应收账款占总资产比例"}
    for item in detailed_data_sorted:
        assets_ratio_row[item["报告期"]] = item["应收账款占总资产比例"]
    table_data.append(assets_ratio_row)

    # 第5行：应收账款周转率
    turnover_row = {"指标": "应收账款周转率"}
    for item in detailed_data_sorted:
        turnover_row[item["报告期"]] = item["应收账款周转率"]
    table_data.append(turnover_row)

    # 创建DataFrame并显示
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)


def generate_financial_summary(balance_df: pd.DataFrame, stock_code: str) -> str:
    """生成财报数据汇总（markdown格式）"""
    if balance_df.empty:
        return "# 财报数据汇总\n\n暂无数据"

    # 提取关键数据
    summary_data = []
    for _, row in balance_df.iterrows():
        report_period = row["报告期"]
        cash = format_accounting(_parse_amount(row.get("货币资金", 0)))
        financial_assets = format_accounting(_parse_amount(row.get("交易性金融资产", 0)))
        short_debt = format_accounting(_parse_amount(row.get("短期借款", 0)))
        long_debt = format_accounting(_parse_amount(row.get("长期借款", 0)))
        # 应付债券字段不存在，设为0
        bonds = format_accounting(0)
        total_assets = format_accounting(_parse_amount(row.get("*资产合计", 0)))
        total_liabilities = format_accounting(_parse_amount(row.get("*负债合计", 0)))

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


def main():
    """主应用入口"""
    st.set_page_config(
        page_title="A股财报检查清单分析",
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
            # 预处理股票代码 - 确保格式正确
            if stock_code.strip().isdigit() and len(stock_code.strip()) == 6:
                # 如果是6位数字，自动添加市场前缀
                if stock_code.startswith("6"):
                    full_code = f"SH{stock_code}"
                elif stock_code.startswith("0") or stock_code.startswith("2"):
                    full_code = f"SZ{stock_code}"
                else:
                    full_code = f"SH{stock_code}"  # 默认为SH
            else:
                full_code = stock_code.upper().strip()

            with st.spinner(f"正在分析 {full_code} 的财务数据..."):
                # 初始化分析器
                analyzer = StockAnalyzer(full_code)

                # 获取资产负债表数据和利润表数据（默认5年）
                balance_sheet_df = analyzer.get_balance_sheet_data(5)
                income_statement_df = analyzer.get_income_statement_data(5)

            if not balance_sheet_df.empty and not income_statement_df.empty:
                # 生成检查清单
                checklist_items = generate_cash_safety_checklist(balance_sheet_df)

                # 添加货币资金异常检查
                cash_anomaly_items = generate_cash_anomaly_checklist(balance_sheet_df, income_statement_df)
                checklist_items.extend(cash_anomaly_items)

                # 添加应收票据健康度检查
                notes_receivable_items = generate_notes_receivable_health_checklist(balance_sheet_df)
                checklist_items.extend(notes_receivable_items)

                # 添加应收账款健康度检查
                receivables_checklist_items = generate_receivables_health_checklist(balance_sheet_df, income_statement_df)
                checklist_items.extend(receivables_checklist_items)

                # 添加预付账款异常检查
                prepaid_expenses_items = generate_prepaid_expenses_anomaly_checklist(balance_sheet_df, income_statement_df)
                checklist_items.extend(prepaid_expenses_items)

                # 显示检查清单
                st.header(f"📊 {full_code} 财报分析结果")
                st.markdown("### 一、\"资产负债表\"及相关附注")
                st.markdown("#### 1.1 资产类项目")

                for item in checklist_items:
                    render_checklist_item(item)
                    st.markdown("---")

                # 财报数据汇总
                st.header("📄 财报原始数据汇总")

                # 生成并提供下载功能
                financial_summary = generate_financial_summary(balance_sheet_df, full_code)
                st.download_button(
                    label="📥 下载财报汇总 (Markdown)",
                    data=financial_summary,
                    file_name=f"{full_code}_财报汇总_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    key="financial_summary_download"
                )
            else:
                st.error("未能获取到财务数据，请检查API服务是否正常运行或股票代码是否正确")


if __name__ == "__main__":
    main()