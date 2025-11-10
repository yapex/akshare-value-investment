# 财务指标查询Feature测试需求文档

## 测试案例格式规范
每个测试案例严格按照以下格式：
- Test Case X: [Descriptive name]
- Input: [Specific input data]
- Expected Output: [Exact expected result]
- Validation: [How to verify success]

## 1. 数据模型测试案例

### Test Case 1-1: FinancialIndicator创建验证
- Input: symbol="600519", market=MarketType.A_STOCK, company_name="贵州茅台", indicators={"basic_eps": Decimal("71.12")}
- Expected Output: FinancialIndicator对象，包含所有传入数据，类型正确
- Validation: 断言对象属性值与输入一致，类型检查通过

### Test Case 1-2: MarketType枚举验证
- Input: 字符串值"A_STOCK"
- Expected Output: MarketType.A_STOCK枚举值
- Validation: 枚举转换正确，支持所有3个市场类型

### Test Case 1-3: QueryResult验证
- Input: success=True, data=[FinancialIndicator], total_records=1
- Expected Output: QueryResult对象，包含查询结果和元数据
- Validation: 结果状态和数据完整性验证

## 2. 字段映射测试案例

### Test Case 2-1: A股字段映射
- Input: unified_field="basic_eps", market=MarketType.A_STOCK
- Expected Output: "摊薄每股收益(元)"
- Validation: 验证10个核心指标在A股市场的字段映射正确

### Test Case 2-2: 港股字段映射
- Input: unified_field="basic_eps", market=MarketType.HK_STOCK
- Expected Output: "BASIC_EPS"
- Validation: 验证10个核心指标在港股市场的字段映射正确

### Test Case 2-3: 美股字段映射
- Input: unified_field="basic_eps", market=MarketType.US_STOCK
- Expected Output: "BASIC_EPS"
- Validation: 验证10个核心指标在美股市场的字段映射正确

## 3. 股票识别测试案例

### Test Case 3-1: 显式前缀识别
- Input: ["CN.600519", "HK.00700", "US.TSLA"]
- Expected Output: [(MarketType.A_STOCK, "600519"), (MarketType.HK_STOCK, "00700"), (MarketType.US_STOCK, "TSLA")]
- Validation: 识别结果正确，前缀正确去除

### Test Case 3-2: 格式推断识别
- Input: ["600519", "00700", "TSLA"]
- Expected Output: [(MarketType.A_STOCK, "600519"), (MarketType.HK_STOCK, "00700"), (MarketType.US_STOCK, "TSLA")]
- Validation: 基于格式正确推断市场类型

### Test Case 3-3: 边界情况处理
- Input: ["", "INVALID", "123456789"]
- Expected Output: 适当的错误处理或默认推断
- Validation: 异常情况正确处理

## 4. 查询服务测试案例

### Test Case 4-1: 单股票查询
- Input: symbol="600519"
- Expected Output: QueryResult(success=True, data包含FinancialIndicator列表)
- Validation: 查询成功，返回正确的财务数据

### Test Case 4-2: 批量查询
- Input: symbols=["600519", "000001", "TSLA"]
- Expected Output: Dict[symbol, QueryResult]，每个股票都有查询结果
- Validation: 批量查询正确，每个结果都包含有效数据

### Test Case 4-3: 指标对比
- Input: symbols=["600519", "TSLA"], indicators=["basic_eps", "roe"]
- Expected Output: 包含对比结果的字典
- Validation: 指标对比数据正确，格式符合预期

## 5. akshare API集成测试案例

### Test Case 5-1: A股API集成
- Input: symbol="600519"
- Expected Output: 使用ak.stock_financial_analysis_indicator()获取数据
- Validation: API调用成功，数据格式正确

### Test Case 5-2: 港股API集成
- Input: symbol="00700"
- Expected Output: 使用ak.stock_financial_hk_analysis_indicator_em()获取数据
- Validation: API调用成功，数据格式正确

### Test Case 5-3: 美股API集成
- Input: symbol="TSLA"
- Expected Output: 使用ak.stock_financial_us_indicator_yahoo()获取数据
- Validation: API调用成功，数据格式正确

## 6. 错误处理测试案例

### Test Case 6-1: 无效股票代码
- Input: symbol="INVALID_CODE"
- Expected Output: QueryResult(success=False, message包含错误信息)
- Validation: 错误信息明确，错误处理正确

### Test Case 6-2: API调用失败
- Input: 模拟API异常
- Expected Output: QueryResult(success=False, 包含异常信息)
- Validation: 异常正确捕获和处理

### Test Case 6-3: 数据格式错误
- Input: API返回非预期格式数据
- Expected Output: 适当的数据转换或错误处理
- Validation: 数据格式处理正确

## 测试覆盖率目标
- 整体测试覆盖率: >90%
- 核心业务逻辑覆盖率: 100%
- 错误处理覆盖率: >85%

## 测试分类
- **unit**: 单元测试 - 快速，隔离测试单个组件
- **integration**: 集成测试 - 测试组件间交互
- **e2e**: 端到端测试 - 完整业务流程测试
- **slow**: 慢速测试 - 涉及真实API调用的测试