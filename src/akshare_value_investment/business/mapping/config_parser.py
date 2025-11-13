"""
配置文件解析器

实现IConfigParser接口，专门负责YAML配置文件的解析和验证
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List

from .namespaced_interfaces import IConfigParser


class YAMLConfigParser(IConfigParser):
    """YAML配置文件解析器"""

    def __init__(self):
        self._parse_history: List[Dict[str, Any]] = []

    def parse_config_file(self, config_path: str) -> Dict[str, Any]:
        """
        解析YAML配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            Dict[str, Any]: 解析后的配置数据

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML格式错误
            ValueError: 配置数据格式错误
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if not self.validate_config_data(config_data):
                raise ValueError(f"配置文件格式错误: {config_path}")

            # 记录解析历史
            self._parse_history.append({
                'config_path': config_path,
                'status': 'success',
                'fields_count': self._count_fields(config_data)
            })

            return config_data

        except yaml.YAMLError as e:
            self._parse_history.append({
                'config_path': config_path,
                'status': 'failed',
                'error': str(e)
            })
            raise

        except Exception as e:
            self._parse_history.append({
                'config_path': config_path,
                'status': 'failed',
                'error': str(e)
            })
            raise

    def validate_config_data(self, config_data: Dict[str, Any]) -> bool:
        """
        验证配置数据格式

        Args:
            config_data: 配置数据

        Returns:
            bool: 验证是否通过
        """
        if not isinstance(config_data, dict):
            return False

        # 检查是否有markets配置
        if 'markets' not in config_data:
            return False

        markets = config_data['markets']
        if not isinstance(markets, dict):
            return False

        # 验证每个市场配置格式
        for market_id, market_data in markets.items():
            if not isinstance(market_data, dict):
                return False

            # 检查必需的基本字段
            if 'name' not in market_data:
                return False

            # 检查字段配置格式
            for field_id, field_data in market_data.items():
                if field_id in ['name', 'currency', 'description']:
                    continue

                if not isinstance(field_data, dict):
                    return False

                if 'name' not in field_data or 'keywords' not in field_data:
                    return False

                if not isinstance(field_data['keywords'], list):
                    return False

        return True

    def _count_fields(self, config_data: Dict[str, Any]) -> int:
        """统计配置中的字段数量"""
        if 'markets' not in config_data:
            return 0

        total_fields = 0
        for market_data in config_data['markets'].values():
            for field_id, field_data in market_data.items():
                if field_id not in ['name', 'currency', 'description']:
                    total_fields += 1

        return total_fields

    def get_parse_history(self) -> List[Dict[str, Any]]:
        """获取解析历史记录"""
        return self._parse_history.copy()

    def clear_history(self) -> None:
        """清空解析历史记录"""
        self._parse_history.clear()