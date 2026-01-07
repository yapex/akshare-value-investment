"""
基础字段元类和异常

提供StrictFieldMeta元类,用于防止子类覆盖父类字段。
"""

from typing import Dict, List


class FieldConflictError(Exception):
    """字段冲突异常

    当子类试图覆盖父类字段时抛出此异常。
    """
    pass


class StrictFieldMeta(type):
    """
    严格字段元类 - 防止子类覆盖父类字段

    机制:
    1. 收集所有父类的字段定义
    2. 检查子类是否重复定义
    3. 如果值不同,抛出FieldConflictError
    4. 如果值相同,允许(幂等性)

    示例:
        >>> class StandardFields(metaclass=StrictFieldMeta):
        ...     TOTAL_REVENUE = "total_revenue"
        >>> class GoodMarketFields(StandardFields):
        ...     NEW_FIELD = "new_field"  # ✅ 新字段,OK
        >>> class BadMarketFields(StandardFields):
        ...     TOTAL_REVENUE = "bad_revenue"  # ❌ 冲突!会抛出异常
    """

    def __new__(mcs, name, bases, namespace):
        # 跳过StandardFields本身的创建
        if name == 'StandardFields':
            return super().__new__(mcs, name, bases, namespace)

        # 收集父类字段
        parent_fields = mcs._collect_parent_fields(bases)

        # 检查冲突
        conflicts = mcs._check_conflicts(namespace, parent_fields, bases)

        if conflicts:
            mcs._raise_conflict_error(name, conflicts)

        return super().__new__(mcs, name, bases, namespace)

    @staticmethod
    def _collect_parent_fields(bases) -> Dict[str, str]:
        """收集父类的所有字段

        Args:
            bases: 父类元组

        Returns:
            字段名到字段值的映射 {field_name: field_value}
        """
        parent_fields = {}
        for base in bases:
            for attr in dir(base):
                if attr.isupper() and not attr.startswith('_'):
                    value = getattr(base, attr)
                    if isinstance(value, str):
                        parent_fields[attr] = value
        return parent_fields

    @staticmethod
    def _check_conflicts(namespace: Dict, parent_fields: Dict, bases) -> List[Dict]:
        """检查字段冲突

        Args:
            namespace: 子类的命名空间
            parent_fields: 父类字段映射
            bases: 父类元组

        Returns:
            冲突列表,每个冲突包含field, parent_value, child_value, parent_class
        """
        conflicts = []
        for attr, value in namespace.items():
            if attr.isupper() and not attr.startswith('_'):
                if attr in parent_fields:
                    parent_value = parent_fields[attr]
                    if value != parent_value:
                        # 找到是哪个父类定义的
                        parent_class = 'Unknown'
                        for base in bases:
                            if hasattr(base, attr):
                                parent_class = base.__name__
                                break

                        conflicts.append({
                            'field': attr,
                            'parent_value': parent_value,
                            'child_value': value,
                            'parent_class': parent_class
                        })
        return conflicts

    @staticmethod
    def _raise_conflict_error(class_name: str, conflicts: List[Dict]):
        """抛出冲突异常

        Args:
            class_name: 子类名称
            conflicts: 冲突列表

        Raises:
            FieldConflictError: 包含详细冲突信息
        """
        conflict_list = '\n'.join([
            f"  ❌ {c['field']}:\n"
            f"     父类({c['parent_class']}) = '{c['parent_value']}'\n"
            f"     子类({class_name})     = '{c['child_value']}'"
            for c in conflicts
        ])

        raise FieldConflictError(
            f"\n{'='*60}\n"
            f"字段冲突检测失败: {class_name}\n"
            f"{'='*60}\n"
            f"{class_name} 试图覆盖父类字段:\n\n"
            f"{conflict_list}\n\n"
            f"💡 解决方案:\n"
            f"   1. 删除子类中的重复字段定义\n"
            f"   2. 父类字段已通过继承自动可用\n"
            f"   3. 如需不同映射,请在 config.py 中配置\n"
            f"{'='*60}\n"
        )
