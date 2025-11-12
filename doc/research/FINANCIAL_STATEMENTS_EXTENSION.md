# 财务三表查询扩展架构设计

## 📊 需求分析

### 当前状况
- 查询目标：单个财务指标（如ROE、毛利率等）
- 数据模型：`FinancialIndicator` 统一模型
- 查询方式：基于字段名称的点对点查询

### 扩展需求
- 查询目标：结构化财务三表（资产负债表、利润表、现金流量表）
- 数据特点：表格结构化数据，字段间有逻辑关系
- 查询方式：基于报表类型的结构化查询

## 🏗️ 架构扩展方案

### 1. 数据模型扩展

#### 新增报表类型枚举
```python
@dataclass
class StatementType(Enum):
    """财务报表类型枚举"""
    BALANCE_SHEET = "balance_sheet"        # 资产负债表
    INCOME_STATEMENT = "income_statement"   # 利润表
    CASH_FLOW_STATEMENT = "cash_flow"       # 现金流量表
    FINANCIAL_INDICATORS = "indicators"     # 财务指标（保持兼容）
```

#### 新增财务三表专用模型
```python
@dataclass
class FinancialStatement:
    """财务报表数据模型 - 专门用于结构化报表"""
    symbol: str                                    # 股票代码
    market: MarketType                             # 市场类型
    company_name: str                              # 公司名称
    statement_type: StatementType                  # 报表类型
    report_date: datetime                          # 报告日期
    period_type: PeriodType                        # 报告期类型
    currency: str                                  # 货币单位
    table_data: Dict[str, Any]                      # 表格数据
    raw_data: Optional[Dict[str, Any]] = None      # 原始数据
```

### 2. 接口扩展

#### 新增财务三表查询接口
```python
class IFinancialStatementQueryService(Protocol):
    """财务报表查询服务接口"""

    def query_balance_sheet(self, symbol: str, start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[FinancialStatement]:
        """查询资产负债表"""
        ...

    def query_income_statement(self, symbol: str, start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> List[FinancialStatement]:
        """查询利润表"""
        ...

    def query_cash_flow_statement(self, symbol: str, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[FinancialStatement]:
        """查询现金流量表"""
        ...

    def query_financial_statements(self, symbol: str, statement_types: List[StatementType],
                                   start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[StatementType, List[FinancialStatement]]:
        """批量查询多种财务报表"""
        ...
```

#### 扩展现有接口保持兼容
```python
class IQueryService(Protocol):
    """查询服务接口 - 扩展版本"""

    def query(self, symbol: str, **kwargs) -> QueryResult:
        """查询单只股票的财务数据 - 保持原有接口"""
        ...

    def query_statement(self, symbol: str, statement_type: StatementType, **kwargs) -> QueryResult:
        """查询指定类型的财务报表 - 新增接口"""
        ...
```

### 3. 服务层扩展

#### 新增财务三表查询服务
```python
class FinancialStatementQueryService:
    """财务报表查询服务"""

    def __init__(self,
                 balance_sheet_adapter: IBalanceSheetAdapter,
                 income_statement_adapter: IIncomeStatementAdapter,
                 cash_flow_adapter: ICashFlowAdapter,
                 formatter: IStatementFormatter):
        self.balance_sheet_adapter = balance_sheet_adapter
        self.income_statement_adapter = income_statement_adapter
        self.cash_flow_adapter = cash_flow_adapter
        self.formatter = formatter

    def query_balance_sheet(self, symbol: str, **kwargs) -> QueryResult:
        """查询资产负债表"""
        try:
            raw_data = self.balance_sheet_adapter.get_balance_sheet_data(symbol, **kwargs)
            statements = [self._raw_to_statement(symbol, StatementType.BALANCE_SHEET, data)
                          for data in raw_data]
            return QueryResult(success=True, data=statements)
        except Exception as e:
            return QueryResult(success=False, data=[], message=str(e))
```

### 4. 适配器扩展

#### 新增报表专用适配器接口
```python
class IBalanceSheetAdapter(Protocol):
    """资产负债表适配器接口"""
    def get_balance_sheet_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        ...

class IIncomeStatementAdapter(Protocol):
    """利润表适配器接口"""
    def get_income_statement_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        ...

class ICashFlowAdapter(Protocol):
    """现金流量表适配器接口"""
    def get_cash_flow_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        ...
```

#### 实现A股三表适配器
```python
class AStockBalanceSheetAdapter(BaseMarketAdapter):
    """A股资产负债表适配器"""

    def get_balance_sheet_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """使用akshare获取A股资产负债表数据"""
        import akshare as ak
        return ak.stock_balance_sheet_by_quarterly_em(symbol=symbol).to_dict('records')

class AStockIncomeStatementAdapter(BaseMarketAdapter):
    """A股利润表适配器"""

    def get_income_statement_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """使用akshare获取A股利润表数据"""
        import akshare as ak
        return ak.stock_income_sheet_by_quarterly_em(symbol=symbol).to_dict('records')

class AStockCashFlowAdapter(BaseMarketAdapter):
    """A股现金流量表适配器"""

    def get_cash_flow_data(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """使用akshare获取A股现金流量表数据"""
        import akshare as ak
        return ak.stock_cash_flow_by_quarterly_em(symbol=symbol).to_dict('records')
```

### 5. MCP工具扩展

#### 新增财务三表查询处理器
```python
class StatementQueryHandler(BaseHandler):
    """财务报表查询处理器"""

    def __init__(self, statement_service: IFinancialStatementQueryService):
        super().__init__()
        self.statement_service = statement_service

    async def handle(self, request: Dict[str, Any]) -> ToolResult:
        """处理财务报表查询请求"""
        symbol = request.get("symbol")
        statement_type = request.get("statement_type", "indicators")

        if statement_type == "indicators":
            # 使用原有财务指标查询
            return await self._handle_indicators_query(symbol, request)
        else:
            # 使用新的财务报表查询
            return await self._handle_statement_query(symbol, statement_type, request)
```

## 🔄 渐进式迁移策略

### 阶段1：数据模型扩展（1周）
1. 新增`StatementType`枚举
2. 新增`FinancialStatement`模型
3. 保持`FinancialIndicator`模型兼容性

### 阶段2：接口扩展（1周）
1. 新增财务三表查询接口
2. 扩展现有接口
3. 更新服务层接口

### 阶段3：适配器实现（2周）
1. 实现A股三表适配器
2. 实现港股三表适配器
3. 实现美股三表适配器

### 阶段4：服务层集成（1周）
1. 实现`FinancialStatementQueryService`
2. 集成到依赖注入容器
3. 更新MCP处理器

### 阶段5：测试和文档（1周）
1. 编写财务三表查询测试
2. 更新使用文档
3. 集成测试验证

## 📋 使用示例

### 单个报表查询
```python
# 查询资产负债表
result = statement_service.query_balance_sheet(
    symbol="600519",
    start_date="2023-01-01",
    end_date="2024-12-31"
)

# 查询利润表
result = statement_service.query_income_statement(
    symbol="600519",
    start_date="2023-01-01",
    end_date="2024-12-31"
)
```

### 批量报表查询
```python
# 同时查询多种报表
results = statement_service.query_financial_statements(
    symbol="600519",
    statement_types=[StatementType.BALANCE_SHEET, StatementType.INCOME_STATEMENT],
    start_date="2023-01-01",
    end_date="2024-12-31"
)
```

### MCP工具使用
```python
# 通过MCP工具查询财务报表
{
    "symbol": "600519",
    "statement_type": "balance_sheet",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31"
}
```

## 🎯 SOLID原则遵循度

### 单一职责原则
- ✅ 每个适配器只负责一种报表类型
- ✅ 查询服务专注于报表查询协调

### 开闭原则
- ✅ 新增报表类型不需要修改现有代码
- ✅ 通过接口扩展支持新功能

### 里氏替换原则
- ✅ 所有报表适配器都可以替换基类

### 接口隔离原则
- ✅ 报表查询接口与指标查询接口分离
- ✅ 每个报表类型有专门的适配器接口

### 依赖倒置原则
- ✅ 服务层依赖抽象接口
- ✅ 支持依赖注入和Mock测试

## 🔮 技术优势

1. **向后兼容**: 现有财务指标查询功能不受影响
2. **类型安全**: 使用强类型模型和接口
3. **可扩展性**: 易于添加新的报表类型和市场
4. **测试友好**: 支持Mock测试和依赖注入
5. **统一体验**: MCP工具提供统一的查询接口

## 📈 业务价值

1. **数据完整性**: 提供完整的财务三表数据
2. **分析深度**: 支持更深入的财务分析
3. **专业标准**: 符合财务分析行业标准
4. **竞争优势**: 区别于简单的指标查询
5. **扩展潜力**: 为未来AI分析提供数据基础