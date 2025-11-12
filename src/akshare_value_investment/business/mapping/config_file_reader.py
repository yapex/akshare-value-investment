"""
配置文件读取器

专门负责配置文件的I/O操作
遵循单一职责原则（SRP），只关注文件读取功能
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


class ConfigFileReader:
    """配置文件读取器

    专门负责YAML配置文件的读取和验证
    提供统一的文件访问接口
    """

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        初始化配置文件读取器

        Args:
            config_paths: 配置文件路径列表，如果为None则使用默认路径
        """
        if config_paths is None:
            current_dir = Path(__file__).parent.parent.parent / "datasource" / "config"
            config_paths = [
                str(current_dir / "financial_indicators.yaml"),  # 财务指标
                str(current_dir / "financial_statements.yaml")   # 财务三表
            ]

        self.config_paths = config_paths
        self._validated_paths: List[str] = []

    def validate_paths(self) -> List[str]:
        """
        验证配置文件路径

        Returns:
            有效路径列表
        """
        self._validated_paths = []

        for config_path in self.config_paths:
            if Path(config_path).exists():
                self._validated_paths.append(config_path)
            else:
                print(f"⚠️ 配置文件不存在: {config_path}")

        return self._validated_paths

    def read_all_configs(self) -> List[Dict[str, Any]]:
        """
        读取所有有效的配置文件

        Returns:
            配置内容列表，每个元素为解析后的配置字典
        """
        configs = []
        validated_paths = self.validate_paths()

        for config_path in validated_paths:
            try:
                config = self.read_single_config(config_path)
                configs.append(config)
                print(f"✅ 成功加载配置: {config_path}")
            except Exception as e:
                print(f"❌ 读取配置失败 {config_path}: {e}")

        return configs

    def read_single_config(self, config_path: str) -> Dict[str, Any]:
        """
        读取单个配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            解析后的配置字典

        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML解析错误
            Exception: 其他读取错误
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

                # 基本验证
                if not isinstance(config, dict):
                    raise ValueError(f"配置文件格式错误，期望字典格式: {config_path}")

                return config

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析错误 {config_path}: {e}")
        except Exception as e:
            raise Exception(f"读取配置文件失败 {config_path}: {e}")

    def get_file_info(self, config_path: str) -> Dict[str, Any]:
        """
        获取配置文件信息

        Args:
            config_path: 配置文件路径

        Returns:
            文件信息字典
        """
        path = Path(config_path)

        if not path.exists():
            return {
                'exists': False,
                'path': config_path,
                'error': 'File not found'
            }

        try:
            stat = path.stat()

            # 尝试读取基本信息
            config = self.read_single_config(config_path)

            return {
                'exists': True,
                'path': config_path,
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'version': config.get('version', 'unknown'),
                'description': config.get('metadata', {}).get('description', ''),
                'markets_count': len(config.get('markets', {}))
            }

        except Exception as e:
            return {
                'exists': True,
                'path': config_path,
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'error': str(e)
            }

    def get_all_files_info(self) -> List[Dict[str, Any]]:
        """
        获取所有配置文件的信息

        Returns:
            文件信息列表
        """
        files_info = []

        for config_path in self.config_paths:
            files_info.append(self.get_file_info(config_path))

        return files_info

    def backup_configs(self, backup_dir: Optional[str] = None) -> bool:
        """
        备份配置文件（可选功能）

        Args:
            backup_dir: 备份目录，如果为None则使用默认目录

        Returns:
            是否备份成功
        """
        if backup_dir is None:
            backup_dir = Path(self.config_paths[0]).parent / "backup"
        else:
            backup_dir = Path(backup_dir)

        try:
            backup_dir.mkdir(exist_ok=True)

            import shutil
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for config_path in self._validated_paths:
                source = Path(config_path)
                filename = f"{source.stem}_{timestamp}{source.suffix}"
                backup_path = backup_dir / filename

                shutil.copy2(source, backup_path)
                print(f"✅ 备份配置文件: {config_path} -> {backup_path}")

            return True

        except Exception as e:
            print(f"❌ 备份配置文件失败: {e}")
            return False

    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名

        Returns:
            支持的扩展名列表
        """
        return ['.yaml', '.yml']

    def is_valid_config_file(self, file_path: str) -> bool:
        """
        检查是否为有效的配置文件

        Args:
            file_path: 文件路径

        Returns:
            是否有效
        """
        path = Path(file_path)

        # 检查扩展名
        if path.suffix.lower() not in self.get_supported_extensions():
            return False

        # 检查文件是否存在
        if not path.exists():
            return False

        # 检查是否可以解析
        try:
            config = self.read_single_config(file_path)
            return isinstance(config, dict)
        except:
            return False

    def get_file_stats(self) -> Dict[str, Any]:
        """
        获取文件读取统计信息

        Returns:
            统计信息字典
        """
        validated_paths = self.validate_paths()
        all_files_info = self.get_all_files_info()

        total_size = 0
        valid_files = 0
        invalid_files = 0

        for info in all_files_info:
            if info['exists'] and 'error' not in info:
                valid_files += 1
                total_size += info.get('size_bytes', 0)
            else:
                invalid_files += 1

        return {
            'total_paths': len(self.config_paths),
            'valid_paths': len(validated_paths),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'supported_extensions': self.get_supported_extensions()
        }