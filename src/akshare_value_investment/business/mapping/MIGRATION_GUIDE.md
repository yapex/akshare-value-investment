# 配置加载器迁移指南

## 📋 迁移概述

本文档指导如何从旧版 `FinancialFieldConfigLoader` 迁移到新版 `MultiConfigLoader`。

## 🔄 迁移步骤

### 1. 更新导入语句

```python
# 旧版本 [DEPRECATED]
from .config_loader import FinancialFieldConfigLoader, FieldInfo

# 新版本 ✅ 推荐
from .multi_config_loader import MultiConfigLoader
from .config_loader import FieldInfo  # FieldInfo 仍然可用
```

### 2. 更新映射器初始化

```python
# 旧版本 [DEPRECATED]
from .config_loader import FinancialFieldConfigLoader
mapper = FinancialFieldMapper("/path/to/config.yaml")

# 新版本 ✅ 推荐 - 多配置文件
from .multi_config_loader import MultiConfigLoader
mapper = MultiConfigLoader([
    "/path/to/financial_indicators.yaml",
    "/path/to/financial_statements.yaml",
    "/path/to/other_config.yaml"
])

# 或者使用 FieldMapper (自动使用 MultiConfigLoader)
mapper = FieldMapper(config_paths=[
    "/path/to/financial_indicators.yaml",
    "/path/to/financial_statements.yaml"
])
```

### 3. 配置文件结构

#### 旧版：单个配置文件
```yaml
# financial_indicators.yaml
version: "2.0.0"
metadata:
  description: "财务指标配置"
markets:
  a_stock:
    "净利润":
      name: "净利润"
      keywords: ["净利润", "利润"]
      priority: 1
```

#### 新版：多个配置文件
```yaml
# financial_indicators.yaml - 财务指标
version: "2.0.0"
metadata:
  description: "财务指标配置"
markets:
  a_stock:
    "净利润":
      name: "净利润"
      keywords: ["净利润", "利润"]
      priority: 1

# financial_statements.yaml - 财务三表
version: "1.0.0"
metadata:
  description: "财务三表配置"
markets:
  a_stock:
    "TOTAL_ASSETS":
      name: "总资产"
      keywords: ["总资产", "资产总额"]
      priority: 1
```

## 🚀 新版本优势

### 1. **多配置文件支持**
- 支持同时加载多个YAML配置文件
- 每个配置文件专注于特定领域（财务指标、财务三表等）
- 配置文件独立维护，职责清晰

### 2. **智能合并机制**
- 自动合并多个配置文件
- 智能处理字段冲突（优先保留先加载的字段）
- 支持配置文件热加载

### 3. **更好的扩展性**
- 新增配置类型只需添加新文件，无需修改现有代码
- 支持插件化配置加载
- 更灵活的配置管理

### 4. **向后兼容**
- 保持现有API接口不变
- 支持逐步迁移策略
- 弃用警告引导开发者迁移

## 📚 API 对比

### 配置加载器对比

| 功能 | FinancialFieldConfigLoader | MultiConfigLoader |
|------|---------------------------|-------------------|
| 配置文件数量 | 单个 | 多个 |
| 配置路径 | 字符串 | 列表 |
| 配置合并 | 不支持 | ✅ 智能合并 |
| 字段冲突处理 | 不适用 | ✅ 优先级处理 |
| 热重加载 | 不支持 | ✅ 支持 |

### 字段映射器对比

| 功能 | 旧版本 | 新版本 |
|------|--------|--------|
| 初始化参数 | `config_path` | `config_paths` (推荐) / `config_path` (兼容) |
| 配置加载器类型 | `FinancialFieldConfigLoader` | `MultiConfigLoader` |
| 向后兼容 | N/A | ✅ 完全兼容 |
| 弃用警告 | N/A | ✅ 迁移提示 |

## ⚠️ 重要提醒

### 弃用警告
当使用旧版API时，会收到 `DeprecationWarning`：
```python
mapper = FinancialFieldMapper("/path/to/config.yaml")
# 警告: config_path参数已弃用，请使用config_paths参数列表
```

### 迁移建议
1. **立即可行**：新代码直接使用新版本API
2. **渐进迁移**：现有代码可以继续工作，但建议逐步迁移
3. **测试验证**：迁移后运行完整测试套件确保功能正常

## 🔧 故障排除

### 常见问题

#### 1. 配置文件找不到
```
错误：配置文件不存在: /path/to/config.yaml
解决：检查文件路径，确保多配置文件路径正确
```

#### 2. 字段映射异常
```
错误：字段映射失败
解决：检查配置文件格式，确保符合YAML规范
```

#### 3. 弃用警告过多
```
建议：及时更新代码使用新的 `config_paths` 参数
```

## 📞 获取帮助

如需帮助或遇到问题，请参考：
1. 现有测试用例：`tests/test_multi_config_balance_sheet_tdd.py`
2. 配置文件示例：`datasource/config/` 目录下的配置文件
3. 核心实现：`business/mapping/multi_config_loader.py`

---

**迁移完成标志**：当你看到字段映射器正常工作，且没有弃用警告时，表示迁移成功完成。