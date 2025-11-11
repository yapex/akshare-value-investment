"""
时间范围处理器

负责处理查询时间范围的逻辑，纯业务逻辑，无外部依赖。
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from ...services.interfaces import ITimeRangeProcessor


class TimeRangeProcessor(ITimeRangeProcessor):
    """时间范围处理器实现"""

    def process_time_range(self,
                           start_date: Optional[str],
                           end_date: Optional[str],
                           default_years: int = 5) -> Tuple[str, str]:
        """
        处理时间范围参数

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            default_years: 默认年数

        Returns:
            (处理后的开始日期, 结束日期)
        """
        # 处理结束日期
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # 处理开始日期
        if not start_date:
            start_date_obj = datetime.now() - timedelta(days=default_years * 365)
            start_date = start_date_obj.strftime('%Y-%m-%d')

        # 验证日期格式
        if not self._is_valid_date_format(start_date) or not self._is_valid_date_format(end_date):
            raise ValueError("日期格式无效，请使用YYYY-MM-DD格式")

        # 验证日期范围合理性
        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期")

        return start_date, end_date

    def _is_valid_date_format(self, date_str: str) -> bool:
        """验证日期格式是否为YYYY-MM-DD"""
        if not date_str or len(date_str) != 10:
            return False

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False