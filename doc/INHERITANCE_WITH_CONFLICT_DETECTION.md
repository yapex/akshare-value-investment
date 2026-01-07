# 基于继承的市场字段扩展架构 - 完整方案

## 📋 设计目标

1. ✅ **继承StandardFields** - 市场字段自动获得标准字段
2. ✅ **防止字段冲突** - 严格检测重复定义
3. ✅ **类型安全** - 完整IDE提示
4. ✅ **易用性** - 一个类访问所有字段
5. ✅ **可扩展** - 添加新市场超简单

---

## 🛡️ 核心机制: 元类冲突检测

### 元类实现

```python
# src/akshare_value_investment/domain/models/base_fields.py

class FieldConflictError(Exception):
    """字段冲突异常"""
    pass


class StrictFieldMeta(type):
    """
    严格字段元类

    功能:
    1. 检测子类是否重复定义父类字段
    2. 防止字段值冲突
    3. 提供清晰的错误提示
    """

    def __new__(mcs, name, bases, namespace):
        # 1. 收集所有父类的字段
        parent_fields = set()
        for base in bases:
            if hasattr(base, '__annotations__'):
                parent_fields.update(getattr(base, '__annotations__'))
            parent_fields.update({
                attr for attr in dir(base)
                if attr.isupper() and not attr.startswith('_')
            })

        # 2. 检查子类是否冲突
        conflicts = []
        for attr in namespace:
            if attr.isupper() and attr in parent_fields:
                # 获取父类的字段值
                parent_value = None
                for base in bases:
                    if hasattr(base, attr):
                        parent_value = getattr(base, attr)
                        break

                child_value = namespace[attr]

                # 检查值是否不同
                if parent_value != child_value:
                    conflicts.append({
                        'field': attr,
                        'parent_value': parent_value,
                        'child_value': child_value,
                        'parent_class': base.__name__
                    })

        # 3. 如果有冲突,抛出异常
        if conflicts:
            conflict_list = '\n'.join([
                f"  - {c['field']}: "
                f"父类({c['parent_class']})='{c['parent_value']}' "
                f"vs 子类='{c['child_value']}'"
                for c in conflicts
            ])
            raise FieldConflictError(
                f"{name} 试图覆盖父类字段,造成冲突:\n"
                f"{conflict_list}\n\n"
                f"解决方案:\n"
                f"  1. 不要在子类中重新定义父类已有的字段\n"
                f"  2. 如果需要不同的映射,请在配置文件中处理,而非修改字段值"
            )

        # 4. 无冲突,正常创建类
        return super().__new__(mcs, name, bases, namespace)
```

### 使用元类

```python
# src/akshare_value_investment/domain/models/financial_standard.py

class StandardFields(metaclass=StrictFieldMeta):
    """
    IFRS财务标准字段 (基类)

    使用StrictFieldMeta元类,防止子类意外覆盖字段
    """
    # ========== 基础字段 ==========
    REPORT_DATE = "report_date"

    # ========== 利润表字段 ==========
    TOTAL_REVENUE = "total_revenue"
    # ... 其他28个字段
```

### 市场字段继承

```python
# src/akshare_value_investment/domain/models/market_fields/a_stock_fields.py

class AStockMarketFields(StandardFields):
    """
    A股市场字段

    继承自StandardFields,自动获得所有标准字段
    使用StrictFieldMeta防止字段冲突
    """

    # ========== A股特定字段 ==========
    MINORITY_INTEREST = "a_minority_interest"  # ✅ 新字段,OK

    # ❌ 如果尝试重复定义,会触发FieldConflictError
    # TOTAL_REVENUE = "a_total_revenue"  # 这行会报错!


# src/akshare_value_investment/domain/models/market_fields/hk_stock_fields.py

class HKStockMarketFields(StandardFields):
    """港股市场字段"""

    # ========== 港股特定字段 ==========
    GOODWILL = "hk_goodwill"  # ✅ 新字段,OK
    ASSOCIATES_INVESTMENT = "hk_associates_investment"  # ✅ 新字段,OK
```

---

## 🧪 冲突检测测试

```python
# tests/domain/test_field_conflicts.py

import pytest
from src.akshare_value_investment.domain.models.financial_standard import StandardFields
from src.akshare_value_investment.domain.models.market_fields.a_stock_fields import AStockMarketFields


def test_cannot_override_parent_fields():
    """测试: 不能覆盖父类字段"""

    # 尝试创建冲突的子类
    with pytest.raises(FieldConflictError) as exc_info:
        class BadMarketFields(StandardFields):
            TOTAL_REVENUE = "bad_total_revenue"  # ❌ 冲突!

    # 验证错误信息
    assert "TOTAL_REVENUE" in str(exc_info.value)
    assert "试图覆盖父类字段" in str(exc_info.value)


def test_new_fields_allowed():
    """测试: 新字段可以正常添加"""

    # 这应该成功
    class GoodMarketFields(StandardFields):
        NEW_FIELD = "new_field"  # ✅ 新字段,OK

    assert GoodMarketFields.NEW_FIELD == "new_field"
    # 继承的标准字段也可用
    assert GoodMarketFields.TOTAL_REVENUE == "total_revenue"


def test_a_stock_fields_no_conflicts():
    """测试: AStockMarketFields无冲突"""
    # 应该能正常创建
    fields = AStockMarketFields()

    # 标准字段可用
    assert hasattr(fields, 'TOTAL_REVENUE')
    # A股特定字段可用
    assert hasattr(fields, 'MINORITY_INTEREST')
```

---

## 📦 完整实现

### 1. 基础字段类

```python
# src/akshare_value_investment/domain/models/base_fields.py

from typing import Dict, List

class FieldConflictError(Exception):
    """字段冲突异常"""
    pass


class StrictFieldMeta(type):
    """
    严格字段元类 - 防止子类覆盖父类字段

    机制:
    1. 收集所有父类的字段定义
    2. 检查子类是否重复定义
    3. 如果值不同,抛出FieldConflictError
    4. 如果值相同,允许(幂等性)
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
    def _collect_parent_fields(bases):
        """收集父类的所有字段"""
        parent_fields = {}
        for base in bases:
            for attr in dir(base):
                if attr.isupper() and not attr.startswith('_'):
                    value = getattr(base, attr)
                    if isinstance(value, str):
                        parent_fields[attr] = value
        return parent_fields

    @staticmethod
    def _check_conflicts(namespace, parent_fields, bases):
        """检查字段冲突"""
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
    def _raise_conflict_error(class_name, conflicts):
        """抛出冲突异常"""
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
```

### 2. 标准字段基类

```python
# src/akshare_value_investment/domain/models/financial_standard.py

class StandardFields(metaclass=StrictFieldMeta):
    """
    IFRS财务标准字段 (基类)

    特性:
    - 严格对照IFRS定义
    - 使用StrictFieldMeta防止子类覆盖
    - 包含29个核心字段
    """
    __metaclass__ = StrictFieldMeta

    # ... 29个字段定义
```

### 3. 市场字段类

```python
# src/akshare_value_investment/domain/models/market_fields/__init__.py

from .a_stock_fields import AStockMarketFields
from .hk_stock_fields import HKStockMarketFields
from .us_stock_fields import USStockMarketFields

__all__ = [
    'AStockMarketFields',
    'HKStockMarketFields',
    'USStockMarketFields',
]


# src/akshare_value_investment/domain/models/market_fields/a_stock_fields.py

class AStockMarketFields(StandardFields):
    """
    A股市场字段 = IFRS标准字段 + A股特定字段

    继承关系:
        StandardFields (IFRS标准)
            ↓ 继承
        AStockMarketFields (A股扩展)

    使用:
        # 标准字段 (继承)
        revenue = df[AStockMarketFields.TOTAL_REVENUE]

        # A股特定字段
        minority = df[AStockMarketFields.MINORITY_INTEREST]
    """

    # ========== A股特定字段 ==========
    # 少数股东权益
    MINORITY_INTEREST = "a_minority_interest"

    # 在建工程
    CONSTRUCTION_IN_PROGRESS = "a_construction_in_progress"

    # 生产物资
    PRODUCTION_MATERIALS = "a_production_materials"
```

---

## 🧪 测试验证

```python
# tests/domain/test_market_fields_inheritance.py

import pytest
from src.akshare_value_investment.domain.models.financial_standard import StandardFields
from src.akshare_value_investment.domain.models.market_fields.a_stock_fields import AStockMarketFields
from src.akshare_value_investment.domain.models.base_fields import FieldConflictError


class TestMarketFieldsInheritance:
    """测试市场字段继承机制"""

    def test_inherits_standard_fields(self):
        """测试: 继承所有标准字段"""
        # 验证继承关系
        assert issubclass(AStockMarketFields, StandardFields)

        # 验证标准字段可用
        assert hasattr(AStockMarketFields, 'TOTAL_REVENUE')
        assert hasattr(AStockMarketFields, 'NET_INCOME')
        assert hasattr(AStockMarketFields, 'TOTAL_ASSETS')

        # 验证值正确
        assert AStockMarketFields.TOTAL_REVENUE == "total_revenue"

    def test_new_market_fields_added(self):
        """测试: A股特定字段被添加"""
        # A股特定字段
        assert hasattr(AStockMarketFields, 'MINORITY_INTEREST')
        assert hasattr(AStockMarketFields, 'CONSTRUCTION_IN_PROGRESS')

        # 值正确
        assert AStockMarketFields.MINORITY_INTEREST == "a_minority_interest"

    def test_cannot_override_standard_fields(self):
        """测试: 不能覆盖标准字段"""
        with pytest.raises(FieldConflictError) as exc_info:
            class BadFields(StandardFields):
                TOTAL_REVENUE = "bad_revenue"  # ❌ 冲突!

        assert "TOTAL_REVENUE" in str(exc_info.value)
        assert "试图覆盖父类字段" in str(exc_info.value)

    def test_field_count(self):
        """测试: 字段数量正确"""
        # StandardFields: 29个
        standard_count = len([
            attr for attr in dir(StandardFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        # AStockMarketFields: 29 + 3 = 32个
        a_stock_count = len([
            attr for attr in dir(AStockMarketFields)
            if attr.isupper() and not attr.startswith('_')
        ])

        assert a_stock_count == standard_count + 3
```

---

## ✅ 冲突防护优势

| 场景 | 无防护 | **有防护** ✨ |
|------|-------|-----------|
| 意外覆盖 | ⚠️ 静默失败,难排查 | ✅ 立即报错,清晰提示 |
| 字段值冲突 | ⚠️ 数据错误 | ✅ 创建时失败 |
| IDE提示 | ⚠️ 可能混淆 | ✅ 明确继承关系 |
| 重构安全 | ⚠️ 危险 | ✅ 类型安全 |

---

## 📋 使用规范

### ✅ 正确做法

```python
class AStockMarketFields(StandardFields):
    """✅ 正确: 只定义新字段"""

    # 只添加A股特有字段
    MINORITY_INTEREST = "a_minority_interest"

    # 标准字段自动可用,无需重复定义
    # TOTAL_REVENUE = "total_revenue"  # ❌ 不需要!
```

### ❌ 错误做法

```python
class AStockMarketFields(StandardFields):
    """❌ 错误: 重复定义标准字段"""

    TOTAL_REVENUE = "a_total_revenue"  # ❌ 冲突!会抛出异常
```

---

## 🎯 实施建议

### 阶段1: 实现元类 (1-2小时)
1. ✅ 创建`StrictFieldMeta`
2. ✅ 实现`FieldConflictError`
3. ✅ 添加单元测试

### 阶段2: 修改StandardFields (5分钟)
1. ✅ 添加`metaclass=StrictFieldMeta`

### 阶段3: 创建市场字段类 (2-3小时)
1. ✅ 创建`AStockMarketFields`
2. ✅ 创建`HKStockMarketFields`
3. ✅ 创建`USStockMarketFields`
4. ✅ 添加继承测试

### 阶段4: 集成到现有系统 (1-2小时)
1. ✅ 更新config.py使用市场字段类
2. ✅ 更新Queryer使用市场字段类
3. ✅ 添加集成测试

**总计**: 约4-7小时

---

这个方案通过**元类**在**类创建时**就检测冲突,提供了**编译时级别**的安全保证!你觉得这个方案如何? 🛡️
