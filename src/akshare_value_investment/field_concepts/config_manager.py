"""
配置管理器
"""

import os
import yaml
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

from .models import ConceptConfig


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._config_cache: Optional[Dict[str, Any]] = None
        self._last_modified: float = 0

    def load_config(self, force_reload: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """智能配置加载"""
        try:
            current_modified = self.config_path.stat().st_mtime

            if (force_reload or
                not self._config_cache or
                self._last_modified < current_modified):

                with open(self.config_path, 'r', encoding='utf-8') as f:
                    new_config = yaml.safe_load(f)

                ConceptConfig.validate_config(new_config)
                self._config_cache = new_config
                self._last_modified = current_modified

                return True, new_config

            return False, self._config_cache

        except Exception as e:
            raise RuntimeError(f"配置加载失败: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        if not self._config_cache:
            self.load_config()
        return self._config_cache or {}

    def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """获取指定概念配置"""
        config = self.get_config()
        return config.get('concepts', {}).get(concept_id)

    def get_concept_config(self) -> ConceptConfig:
        """获取概念配置对象"""
        config = self.get_config()
        return ConceptConfig(config)

    def is_config_modified(self) -> bool:
        """检查配置文件是否被修改"""
        if not self.config_path.exists():
            return False

        current_modified = self.config_path.stat().st_mtime
        return current_modified > self._last_modified

    def reload_if_modified(self) -> bool:
        """如果配置被修改则重载"""
        if self.is_config_modified():
            self.load_config(force_reload=True)
            return True
        return False