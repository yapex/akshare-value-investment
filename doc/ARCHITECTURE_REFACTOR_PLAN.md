# 架构重构详细设计：多市场数据统一化 (Architecture Detail: Multi-Market Data Normalization)

**版本**: v2.0 (Implementation Ready)
**日期**: 2026-01-06
**状态**: 核心设计已锁定
**适用范围**: 数据获取层 (Datasource) -> 领域层 (Domain) 的转换链路

---

## 1. 设计目标 (Design Objectives)

针对 A股、港股、美股 存在的字段异构（命名不同、特有字段、缺失字段）问题，构建一套 **基于领域驱动设计 (DDD)** 和 **依赖注入 (DI)** 的高性能数据适配方案。

**核心能力**:
1.  **统一语义 (Unified Semantics)**: 业务层仅操作 `total_revenue`, `net_income` 等标准字段，屏蔽 `营业总收入`, `OPERATE_INCOME` 等方言。
2.  **高性能 (High Performance)**: 利用 Pandas 向量化操作进行清洗，避免 Python 循环。
3.  **热插拔 (Pluggability)**: 新增市场或修改字段映射只需更新配置 (Registry)，无需修改核心代码。

---

## 2. 核心架构图 (Core Architecture)

```mermaid
graph TD
    User[API / WebApp / Business Logic]
    
    subgraph "Infrastructure Layer (DI Container)"
        Container[Dependency Injector Container]
        IStockRepo(Queryer Interfaces)
    end

    subgraph "Normalization Layer (The Anti-Corruption Layer)"
        Registry[FieldMappingRegistry <br/> (Maps raw_field -> standard_field)]
        Cleaner[DataCleaner <br/> (Pandas Vectorized Engine)]
    end
    
    subgraph "Datasource Layer (Adapters)"
        A_Queryer[AStockQueryer]
        HK_Queryer[HKStockQueryer]
        US_Queryer[USStockQueryer]
        
        AkShare[AkShare API]
    end
    
    subgraph "Domain Layer"
        StdModel[Standard DataFrame <br/> columns: total_revenue, net_income...]
    end

    %% Dependencies
    User --> Container
    Container --> A_Queryer
    
    A_Queryer --> AkShare
    A_Queryer -- Raw DF --> Cleaner
    
    Cleaner --> Registry
    Cleaner -- Standardized DF --> StdModel
    
    A_Queryer -- Returns --> StdModel
```

---

## 3. 模块详细设计 (Module Specifications)

### 3.1 领域层 (Domain Layer)
**文件**: `src/akshare_value_investment/domain/models/financial_standard.py`

定义系统通用的“普通话”。使用常量类避免魔术字符串。

```python
class StandardFields:
    """标准财务字段常量定义"""
    REPORT_DATE = "report_date"          # 报告期
    TOTAL_REVENUE = "total_revenue"      # 营业总收入
    NET_INCOME = "net_income"            # 净利润
    TOTAL_ASSETS = "total_assets"        # 总资产
    TOTAL_LIABILITIES = "total_liabilities" # 总负债
    TOTAL_EQUITY = "total_equity"        # 所有者权益
    OPERATING_CASH_FLOW = "operating_cash_flow" # 经营活动现金流
    # ... 其他核心字段
```

### 3.2 归一化层 (Normalization Layer)

**组件 A: 字段映射注册表 (FieldMappingRegistry)**
**文件**: `src/akshare_value_investment/normalization/registry.py`
**职责**: 维护 `Market -> {RawField -> StandardField}` 的映射关系。

```python
from typing import Dict, List

class FieldMappingRegistry:
    def __init__(self):
        # 结构: {market_name: {raw_field_name: standard_field_name}}
        self._mappings: Dict[str, Dict[str, str]] = {}

    def register_mapping(self, market: str, standard_field: str, raw_fields: List[str]):
        """
        注册映射。支持多个 raw_fields 映射到一个 standard_field (处理别名/容错)。
        例如: A股的 "营业总收入" 和 "一、营业总收入" 都映射为 "total_revenue"
        """
        if market not in self._mappings:
            self._mappings[market] = {}
        for raw in raw_fields:
            self._mappings[market][raw] = standard_field

    def get_mapping(self, market: str) -> Dict[str, str]:
        return self._mappings.get(market, {})
```

**组件 B: 数据清洗器 (DataCleaner)**
**文件**: `src/akshare_value_investment/normalization/data_cleaner.py`
**职责**: 执行高性能清洗。

```python
import pandas as pd
from .registry import FieldMappingRegistry

class DataCleaner:
    def __init__(self, registry: FieldMappingRegistry):
        self.registry = registry

    def standardize(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
            
        # 1. 获取映射
        mapping = self.registry.get_mapping(market)
        
        # 2. 向量化重命名 (Core Performance Step)
        # 仅重命名注册表中存在的字段，其他字段保留原名放入 'extensions' (隐式)
        # Pandas rename is optimized C-level code.
        std_df = df.rename(columns=mapping)
        
        # 3. 基础类型转换 (可选)
        # if 'report_date' in std_df.columns:
        #    std_df['report_date'] = pd.to_datetime(std_df['report_date'], errors='coerce')
            
        return std_df
```

### 3.3 基础设施层 (Infrastructure Layer)

**适配器模式落地**
在 Queryer 中注入 `DataCleaner`。

**文件**: `src/akshare_value_investment/datasource/queryers/base_queryer.py`

```python
class BaseQueryer:
    def __init__(self, cache, data_cleaner: DataCleaner):
        self.cache = cache
        self.data_cleaner = data_cleaner
        
    @property
    def market_type(self) -> str:
        raise NotImplementedError

    def get_data(self, code: str) -> pd.DataFrame:
        # 1. Fetch
        raw_df = self._fetch_data_with_cache(code)
        
        # 2. Normalize
        return self.data_cleaner.standardize(raw_df, self.market_type)
```

---

## 4. 实施指南 (Agent Workflow)

AI Agent 在实现此架构时，应遵循以下步骤：

1.  **Phase 1: 基础设施搭建**
    *   创建 `src/akshare_value_investment/normalization/` 目录。
    *   实现 `registry.py` 和 `data_cleaner.py`。
    *   在 `src/akshare_value_investment/container.py` 中注册这两个类为单例。

2.  **Phase 2: 映射配置加载**
    *   读取 `doc/a_stock_fields.md`, `doc/hk_stock_fields.md`, `doc/us_stock_fields.md`。
    *   编写一个加载函数 `load_default_mappings`，将 Markdown 中的关键字段（如收入、净利、资产）硬编码注册到 Registry 中（作为初始配置）。

3.  **Phase 3: 改造 Queryers**
    *   修改 `AStock*Queryer` 等类的 `__init__` 方法，接受 `data_cleaner` 参数。
    *   在 `get_data` 方法中调用 `cleaner.standardize()`。

4.  **Phase 4: 更新 Container**
    *   在 `container.py` 中，将 `data_cleaner` 注入到所有的 Queryer 实例中。

---

## 5. 关键原则 (Rules of Engagement)

*   **Don't Loop**: 严禁在 `DataCleaner` 中使用 `for` 循环遍历 DataFrame 的行。必须使用 Pandas 的 `rename`, `apply`, `assign` 等向量化方法。
*   **Fail Softly**: 如果某个字段在映射表中不存在，保留原名字，不要报错。
*   **Dependency Injection**: 所有的依赖关系（Registry, Cleaner）必须通过 `container.py` 注入，严禁在 Queryer 内部直接实例化。