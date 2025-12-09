"""
检查项计算器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.base_models import ChecklistItem, SubQuestion, ChecklistCategory
from core.data_accessor import get_field_value, parse_amount, format_accounting


class BaseCalculator(ABC):
    """检查项计算器基类"""

    # 子类需要定义的属性
    question_id: str = ""          # 检查项ID，如 "1.1.1"
    question: str = ""             # 检查项问题
    category: ChecklistCategory = ChecklistCategory.ASSETS  # 检查分类
    description: str = ""          # 检查项描述

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> ChecklistItem:
        """执行计算，生成检查清单项

        Args:
            data: 包含财务数据的字典
                   - balance_sheet: DataFrame 资产负债表数据
                   - income_statement: DataFrame 利润表数据
                   - cash_flow: DataFrame 现金流量表数据（可选）

        Returns:
            ChecklistItem: 检查清单项
        """
        pass

    @abstractmethod
    def get_required_fields(self) -> Dict[str, List[str]]:
        """获取计算所需的字段

        Returns:
            Dict: 键为查询类型(balance_sheet, income_statement, cash_flow)，
                  值为字段名称列表
        """
        pass

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证数据是否完整

        Args:
            data: 财务数据字典

        Returns:
            bool: 数据是否有效
        """
        required_fields = self.get_required_fields()

        for query_type, fields in required_fields.items():
            df = data.get(query_type)
            if df is None or df.empty:
                if fields:  # 只有当确实需要这些字段时才报错
                    return False
                continue

            # 检查最新数据行是否包含所需字段
            latest_row = df.iloc[0]
            for field in fields:
                try:
                    get_field_value(latest_row, field)
                except KeyError:
                    return False

        return True

    def create_sub_question(
        self,
        question: str,
        passed: bool,
        calculation: str,
        result: float,
        threshold: float,
        details: Dict[str, Any],
        report_guide: str
    ) -> SubQuestion:
        """创建子问题

        Args:
            question: 追问内容
            passed: 通过/失败
            calculation: 计算公式
            result: 计算结果
            threshold: 判断阈值
            details: 详细数据
            report_guide: 财报指引

        Returns:
            SubQuestion: 子问题对象
        """
        return SubQuestion(
            question=question,
            passed=passed,
            calculation=calculation,
            result=result,
            threshold=threshold,
            details=details,
            report_guide=report_guide
        )

    def create_checklist_item(
        self,
        passed: bool,
        summary: str,
        calculation_details: Dict[str, Any],
        sub_questions: List[SubQuestion]
    ) -> ChecklistItem:
        """创建检查清单项

        Args:
            passed: 通过/失败
            summary: 检查总结
            calculation_details: 计算详细数据
            sub_questions: 子问题列表

        Returns:
            ChecklistItem: 检查清单项
        """
        return ChecklistItem(
            question_id=self.question_id,
            question=self.question,
            category=self.category,
            passed=passed,
            summary=summary,
            calculation_details=calculation_details,
            sub_questions=sub_questions
        )

    def get_data_status_message(self, data: Dict[str, Any]) -> str:
        """获取数据状态信息

        Args:
            data: 财务数据字典

        Returns:
            str: 状态信息
        """
        if not data:
            return "无数据"

        status = []
        for query_type in ["balance_sheet", "income_statement", "cash_flow"]:
            df = data.get(query_type)
            if df is not None and not df.empty:
                status.append(f"{query_type}: {len(df)}期数据")
            else:
                required_fields = self.get_required_fields().get(query_type, [])
                if required_fields:  # 只有当需要这些数据时才提示缺失
                    status.append(f"{query_type}: 缺失")

        return ", ".join(status)

    def handle_data_error(self, data: Dict[str, Any]) -> ChecklistItem:
        """处理数据错误情况，返回错误状态的检查项

        Args:
            data: 财务数据字典

        Returns:
            ChecklistItem: 错误状态的检查清单项
        """
        error_msg = self.get_data_status_message(data)

        sub_question = self.create_sub_question(
            question="数据是否完整？",
            passed=False,
            calculation="检查数据完整性",
            result=0,
            threshold=0,
            details={
                "说明": f"数据不足：{error_msg}",
                "报告期": "未知"
            },
            report_guide="请确认数据源是否包含相关字段"
        )

        return self.create_checklist_item(
            passed=False,
            summary=f"数据不足：{error_msg}",
            calculation_details={
                "错误": error_msg,
                "说明": "缺少必要字段，无法进行分析"
            },
            sub_questions=[sub_question]
        )