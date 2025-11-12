"""
财务指标配置加载器 [DEPRECATED - 完全废弃]

⚠️ 此文件已完全废弃，请使用以下新架构：

✅ 新架构导入路径：
   - 数据模型: from .models import FieldInfo, MarketConfig
   - 配置加载: from .multi_config_loader import MultiConfigLoader
   - 字段映射: from .unified_field_mapper import UnifiedFieldMapper
   - 接口定义: from .interfaces import IConfigLoader, IFieldMapper

📚 迁移指南：
   1. 使用 MultiConfigLoader 替代 FinancialFieldConfigLoader
   2. 使用 UnifiedFieldMapper 替代 FinancialFieldMapper
   3. FieldInfo 和 MarketConfig 已迁移到 models.py
   4. 所有新功能请使用基于 SOLID 原则的新架构

🚫 此文件将在下一个版本中完全移除

@deprecated 完全废弃，使用新架构替代
@see models.py - 数据模型
@see multi_config_loader.py - 配置加载器
@see unified_field_mapper.py - 统一字段映射器
"""

import warnings
from typing import Dict, List, Any, Optional

# 当任何人尝试从此文件导入时，发出强烈的废弃警告
def __getattr__(name: str):
    if name in ['FinancialFieldConfigLoader', 'FieldInfo', 'MarketConfig']:
        warnings.warn(
            f"\n"
            f"🚨 DEPRECATION WARNING 🚨\n"
            f"'{name}' 已从 config_loader.py 完全废弃！\n"
            f"\n"
            f"✅ 请使用新的导入路径：\n"
            f"   - FieldInfo, MarketConfig: from .models import FieldInfo, MarketConfig\n"
            f"   - 配置加载器: from .multi_config_loader import MultiConfigLoader\n"
            f"   - 字段映射器: from .unified_field_mapper import UnifiedFieldMapper\n"
            f"\n"
            f"📖 详细迁移指南请参考 MIGRATION_GUIDE.md\n",
            DeprecationWarning,
            stacklevel=2
        )
        raise ImportError(f"'{name}' 已废弃，请使用新架构")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# 当模块被导入时立即发出警告
warnings.warn(
    "\n"
    "🚨 MODULE DEPRECATED 🚨\n"
    "config_loader.py 已完全废弃，请使用新架构：\n"
    "\n"
    "✅ 新架构导入：\n"
    "   from .models import FieldInfo, MarketConfig\n"
    "   from .multi_config_loader import MultiConfigLoader\n"
    "   from .unified_field_mapper import UnifiedFieldMapper\n"
    "\n"
    "📚 迁移指南：MIGRATION_GUIDE.md\n",
    DeprecationWarning,
    stacklevel=2
)