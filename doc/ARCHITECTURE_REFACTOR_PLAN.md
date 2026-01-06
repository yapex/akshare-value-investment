# 架构分析与重构计划 (Architecture Refactoring Plan)

**日期**: 2026-01-04
**状态**: 提案/进行中
**目标受众**: AI 辅助编程模型 (Vibe Coding Models), 核心开发者

---

## 1. 现状分析 (Current State Assessment)

目前项目 (`akshare-value-investment`) 呈现出典型的初期快速迭代后的**"精神分裂 (Split-Brain)"**架构特征。逻辑分层不清，核心业务价值分散，维护成本随功能扩展呈指数级上升。

### 1.1 系统二元对立

项目实际上由两个重叠且耦合的系统组成：

| 特征 | System A: 后端核心 (`src/`) | System B: 前端应用 (`webapp/`) |
| :--- | :--- | :--- |
| **定位** | API 服务、基础数据源封装 | Streamlit 数据可视化前端 |
| **核心逻辑** | `api/`, `business/`, `datasource/` | **重度包含** `services/calculators/` (ROIC, DCF 等核心金融模型) |
| **数据流** | 提供部分原始数据接口 | 混合调用：直接调 `akshare` + 调 System A 的 API + 内部逻辑计算 |
| **问题** | 业务逻辑贫血，未有效复用 WebApp 中的高价值逻辑 | **胖客户端 (Fat Client)**：承担了过多的数据清洗、标准化和金融建模职责 |

### 1.2 关键痛点 (Pain Points)

1.  **市场逻辑高度耦合 (Market Logic Coupling)**:
    *   **现象**: 计算器代码（如 `roic.py`）中充斥着大量的 `if market == "A股": ... elif market == "美股": ...` 条件判断。
    *   **后果**: 每接入一个新市场或 AkShare 接口变动，需要修改所有相关的计算逻辑文件，违反开闭原则 (OCP)。

2.  **数据标准化缺失 (Lack of Normalization)**:
    *   **现象**: 原始数据的异构性（字段名差异、缺失值处理、正负号惯例）直接透传到业务计算层。例如：拼多多无"商誉"字段导致计算崩溃，代码需要在使用处进行防御性编程。
    *   **后果**: 业务逻辑脆弱，难以编写纯粹的单元测试。

3.  **魔术字符串泛滥 (Magic Strings)**:
    *   **现象**: `"购建固定资产"`, `"持续经营税前利润"` 等硬编码字符串散落在各个文件中。
    *   **后果**: 重构困难，IDE 无法有效辅助检查。

4.  **测试策略脆弱**:
    *   **现象**: 由于计算逻辑与数据获取 (`requests` / `akshare`) 强绑定，单元测试必须大量 Mock 外部 API。
    *   **后果**: 测试容易失效，且难以覆盖边缘数据情况（如字段缺失）。

---

## 2. 目标架构：核心库驱动 (Core-Library Driven Architecture)

重构的核心目标是将项目转型为 **"厚后端（Core Library），薄前端（WebApp）"** 的洋葱架构。

### 2.1 架构分层图

```text
[ Presentation Layer ]  (最外层，无业务逻辑)
       /          \
  (WebApp)      (API - FastAPI)
Streamlit UI    REST Endpoints
       \          /
        \        /
       (Interface)
[ Application Layer ]  (中间层，流程编排)
   src/akshare_value_investment/business/
      - AnalysisService (协调数据获取与计算)
      - ReportService
             |
[ Domain Layer ]  (核心层，纯粹金融逻辑) <--- 价值核心！
   src/akshare_value_investment/domain/
      - models/ (Standardized Financial Models, e.g., FinancialStatements)
      - calculators/ (ROIC, DCF, Liquidity - 纯函数，不含IO)
             |
[ Infrastructure Layer ]  (基础层，脏活累活)
   src/akshare_value_investment/datasource/
      - adapters/ (DataNormalizer - 腐败防止层)
          - CNAdapter (A股清洗)
          - USAdapter (美股清洗)
          - HKAdapter (港股清洗)
      - cache/
```

### 2.2 核心重构策略

#### A. 领域下沉 (Sink the Domain)
*   **行动**: 将 `webapp/services/calculators/*.py` 中的金融模型逻辑剥离，移动至 `src/akshare_value_investment/domain/calculators/`。
*   **原则**: 移动后的代码必须是**纯函数 (Pure Functions)**，输入标准数据对象，输出计算结果，**严禁**包含任何 `requests`、`akshare` 调用或 Streamlit 依赖。

#### B. 数据适配器与标准化 (Adapters & Normalization)
*   **行动**: 在 `src/datasource` 中建立 `adapters` 模块。
*   **职责**:
    *   **Input**: AkShare 返回的异构 DataFrame。
    *   **Process**: 字段映射、单位统一、缺失值默认处理（如美股无商誉补0，负利息转正）。
    *   **Output**: 标准化的 `FinancialData` 对象（统一字段名：`revenue`, `net_income`, `interest_expense`, `goodwill`）。
*   **收益**: 彻底屏蔽底层数据源的差异，上层计算器只针对"标准财务报表"编程。

#### C. 前端瘦身 (Slim WebApp)
*   **行动**: `webapp/` 仅保留 UI 渲染逻辑 (`components`) 和简单的状态管理。
*   **调用方式**: WebApp 直接 import `src` 中的 `business` 服务层，或调用 API（视部署模式而定，推荐直接 import 以保持单体简便性）。

---

## 3. 实施路线图 (Implementation Roadmap)

### Phase 1: 基础建设 (Foundation)
- [ ] **定义标准模型**: 在 `src/core/models.py` 中定义 `StandardFinancialStatements` 数据类。
- [ ] **配置提取**: 将所有硬编码的字段名提取到 `src/core/constants.py` 或 `mappings.py`。

### Phase 2: 核心迁移与适配 (Migration & Adaptation)
- [ ] **创建适配器**: 实现 `USStockAdapter`，封装"拼多多商誉缺失"和"利息为负"的处理逻辑。
- [ ] **迁移 ROIC**: 将 `webapp/services/calculators/roic.py` 重构并迁移至 `src/domain/calculators/`，使其依赖适配器输出的标准数据。
- [ ] **测试重构**: 为新 ROIC 计算器编写无需 Mock IO 的纯逻辑单元测试。

### Phase 3: WebApp 接入 (Integration)
- [ ] **修改组件**: 更新 `webapp/components/roic.py`，使其调用新的后端服务。
- [ ] **验证**: 确保 WebApp 功能与重构前一致（Regression Testing）。

### Phase 4: 全面推广 (Rollout)
- [ ] 对 `liquidity_ratio.py`, `dcf_valuation.py` 等其余计算器执行相同的迁移步骤。
- [ ] 删除 `webapp/services/` 目录。

---

## 4. 编码规范 (Coding Standards for Refactoring)

*   **Type Hinting**: 所有新代码必须包含完整的类型注解。
*   **Docstrings**: 核心计算逻辑必须包含详细的金融含义说明。
*   **Fail Fast vs Resilience**:
    *   数据获取层 (`datasource`) 应具备韧性（Resilience），尽量通过默认值（如0）让流程继续。
    *   业务计算层 (`domain`) 应严格校验（Fail Fast），如果关键数据（如净利润）缺失应直接抛出明确异常。
*   **No Circular Imports**: 严格遵守层级依赖，上层可调下层，下层不可调上层。

---

**备注**: 此文档应作为后续 AI 编码任务的上下文输入 (`context`)，确保所有修改均向此架构目标收敛。
