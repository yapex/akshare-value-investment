"""
数据结构处理器

负责处理不同市场数据结构的统一化处理。
"""

from typing import Any, Dict
from ...services.interfaces import IDataStructureProcessor


class DataStructureProcessor(IDataStructureProcessor):
    """数据结构处理器实现"""

    def extract_indicator_data(self, data: Any) -> Dict[str, Dict[str, Any]]:
        """
        提取指标数据结构

        Args:
            data: 原始数据

        Returns:
            指标数据字典 {field_name: {date: value}}
        """
        if not data:
            return {}

        indicator_map = {}

        # 判断数据类型并处理
        if hasattr(data, '__iter__') and data:
            # 处理列表数据 (新架构)
            for indicator in data:
                if hasattr(indicator, 'indicators') and indicator.indicators:
                    market_type = getattr(indicator, 'market', None)
                    market_value = market_type.value if market_type else 'unknown'
                    report_date = getattr(indicator, 'report_date', None)

                    if report_date:
                        date_str = report_date.strftime('%Y-%m-%d')
                        self._process_indicator_data(
                            indicator.indicators,
                            indicator_map,
                            date_str,
                            market_value
                        )

        return indicator_map

    def extract_metadata(self, data: Any) -> Dict[str, Any]:
        """
        提取元数据

        Args:
            data: 原始数据

        Returns:
            元数据字典
        """
        if not data:
            return {}

        # 获取第一条记录的基本信息
        first_record = None
        if hasattr(data, '__iter__') and data:
            for item in data:
                if hasattr(item, 'symbol') and hasattr(item, 'market'):
                    first_record = item
                    break

        if not first_record:
            return {}

        return {
            'symbol': getattr(first_record, 'symbol', ''),
            'company_name': getattr(first_record, 'company_name', ''),
            'market': getattr(first_record, 'market', ''),
            'currency': getattr(first_record, 'currency', ''),
            'total_records': len(data) if hasattr(data, '__len__') else 0,
            'available_fields_count': self._count_available_fields(first_record)
        }

    def _process_indicator_data(self,
                               indicators: Dict[str, Any],
                               indicator_map: Dict[str, Dict[str, Any]],
                               date_str: str,
                               market_value: str) -> None:
        """处理单个指标的数�据"""
        for field_name, field_value in indicators.items():
            if field_value is not None:
                if field_name not in indicator_map:
                    indicator_map[field_name] = {}
                indicator_map[field_name][date_str] = field_value

    def _count_available_fields(self, record: Any) -> int:
        """计算可用字段数量"""
        if hasattr(record, 'indicators') and record.indicators:
            return len(record.indicators)
        return 0