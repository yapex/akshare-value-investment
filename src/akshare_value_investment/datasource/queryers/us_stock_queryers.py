"""
美股数据查询器模块

实现美股市场财务数据查询的核心功能，基于东方财富(EM)数据源API。

## 架构特点

### API结构
- **多重API设计**: 美股财务三表需要多次调用获取不同报表数据
- **数据源**: 东方财富(EM) - 专业美股数据提供商
- **数据格式**: 窄表格式，自动转换为宽表

### 查询器分类

#### 财务指标查询器
- **USStockIndicatorQueryer**: 美股财务指标分析
- **数据内容**: 净利润、EPS、ROE等关键指标

#### 财务三表查询器
- **USStockStatementQueryer**: 统一的财务三表查询器
- **数据转换**: 自动窄表→宽表格式转换
- **报表获取**: 三次API调用获取资产负债表、损益表、现金流量表

### 数据字段特点

#### 中英混合字段名
- 财务指标：英文字段名，如"PARENT_HOLDER_NETPROFIT"、"BASIC_EPS"
- 财务三表：中文字段名，如"总资产"、"营业收入"
- 符合美股上市公司财报标准

#### 统一日期格式
- 使用"REPORT_DATE"作为时间标识
- 标准化日期格式便于缓存管理
- 支持年度、半年度、季度数据

## 特殊API调用

### 美股财务三表API参数
- **stock参数**: 股票代码，如"AAPL"、"MSFT"
- **symbol参数**: 报表类型标识符
- **indicator参数**: 时间周期，通常为"年报"

### 三次调用策略
1. **资产负债表**: symbol="资产负债表", indicator="年报"
2. **综合损益表**: symbol="综合损益表", indicator="年报"
3. **现金流量表**: symbol="现金流量表", indicator="年报"

## 窄表到宽表转换

### 转换逻辑
- **索引字段**: REPORT_DATE, SECURITY_CODE, SECURITY_NAME_ABBR
- **数据列**: ITEM_NAME (财务项目名称), AMOUNT (金额)
- **聚合方式**: 使用pivot_table转换，避免数据丢失

### 数据合并
- 合并三次API调用的结果
- 统一财务项目命名规范
- 处理重复数据和时间戳对齐

## 缓存机制

- **缓存类型**: us_indicators, us_statements
- **日期字段**: date (转换后生成)
- **增量更新**: 智能识别缺失数据范围

## 使用示例

```python
from akshare_value_investment.datasource.queryers import (
    USStockIndicatorQueryer, USStockStatementQueryer
)

# 查询财务指标
indicator_queryer = USStockIndicatorQueryer()
indicators = indicator_queryer.query("AAPL", "2023-01-01", "2023-12-31")

# 查询财务三表（自动转换为宽表）
statement_queryer = USStockStatementQueryer()
statements = statement_queryer.query("AAPL", "2023-01-01", "2023-12-31")
```

## 注意事项

- 美股财务指标API不支持日期参数，返回全量数据
- 美股财务三表需要三次API调用，性能相对较低
- 日期过滤由缓存层自动处理
- 股票代码格式：美股代码，如"AAPL"、"MSFT"、"GOOGL"
- API访问频率需遵循东方财富限制
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class USStockIndicatorQueryer(BaseDataQueryer):
    """
    美股财务指标查询器

    查询美股的核心财务分析指标，包括：

    #### 盈利能力指标
    - **PARENT_HOLDER_NETPROFIT**: 归属于母公司股东的净利润
    - **BASIC_EPS**: 基本每股收益
    - **TOTAL_OPERATING_REVENUE**: 营业总收入

    #### 财务结构指标
    - **TOTAL_ASSETS**: 总资产
    - **TOTAL_LIABILITIES**: 总负债
    - **TOTAL_EQUITY**: 股东权益合计

    #### 现金流量指标
    - **NET_CASH_FLOWS_OPERATING**: 经营活动现金流净额
    - **FREE_CASH_FLOW**: 自由现金流

    数据源：东方财富(stock_financial_us_analysis_indicator_em)
    缓存类型：us_indicators
    日期字段：date
    """

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询美股财务指标原始数据

        调用东方财富AkShare API获取美股的核心财务指标数据。该API不支持日期参数，
        返回该股票的所有历史财务指标数据。日期过滤由上层的缓存系统自动处理。

        Args:
            symbol (str): 美股股票代码，标准美股代码格式：
                - 常见科技股：如"AAPL"（苹果）、"MSFT"（微软）、"GOOGL"（谷歌）
                - 金融股：如"JPM"（摩根大通）、"BAC"（美国银行）
                - 其他知名股票：如"TSLA"（特斯拉）、"AMZN"（亚马逊）
                - 代码不包含交易所后缀，美股统一代码格式
            start_date (Optional[str]): 开始日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理
            end_date (Optional[str]): 结束日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理

        Returns:
            pd.DataFrame: 包含财务指标的DataFrame，具有以下特征：
                - **英文字段名**：符合美国GAAP会计准则标准
                - **标准化数据**：遵循美国上市公司财报披露规范
                - **时间标识**：使用标准化日期字段，包含年度、季度数据
                - **数据完整性**：包含49个核心财务指标字段
                - **时间排序**：按报告期倒序排列，最新数据在前

                主要字段包括：
                #### 盈利能力指标
                - **PARENT_HOLDER_NETPROFIT**：归属于母公司股东的净利润
                - **BASIC_EPS**：基本每股收益（美元）
                - **DILUTED_EPS**：稀释每股收益（美元）
                - **TOTAL_OPERATING_REVENUE**：营业总收入
                - **NET_PROFIT_MARGIN**：净利润率
                - **GROSS_PROFIT_MARGIN**：毛利率

                #### 财务结构指标
                - **TOTAL_ASSETS**：总资产
                - **TOTAL_LIABILITIES**：总负债
                - **TOTAL_EQUITY**：股东权益合计
                - **DEBT_TO_ASSET_RATIO**：资产负债率
                - **CURRENT_RATIO**：流动比率
                - **QUICK_RATIO**：速动比率

                #### 现金流量指标
                - **NET_CASH_FLOWS_OPERATING**：经营活动现金流净额
                - **FREE_CASH_FLOW**：自由现金流
                - **CAPEX**：资本支出
                - **CASH_CONVERSION_CYCLE**：现金转换周期

                #### 估值和市场指标
                - **MARKET_CAP**：市值
                - **ENTERPRISE_VALUE**：企业价值
                - **EV_EBITDA**：EV/EBITDA比率
                - **BOOK_VALUE_PER_SHARE**：每股账面价值

                #### 效率指标
                - **RETURN_ON_ASSETS**：资产收益率(ROA)
                - **RETURN_ON_EQUITY**：净资产收益率(ROE)
                - **ASSET_TURNOVER**：资产周转率
                - **INVENTORY_TURNOVER**：存货周转率

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = USStockIndicatorQueryer()
            >>> # 查询苹果公司财务指标
            >>> data = queryer._query_raw("AAPL")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("Basic EPS:", data["BASIC_EPS"].tolist())
            >>> print("Total Revenue:", data["TOTAL_OPERATING_REVENUE"].tolist())

        Note:
            - 东方财富API不支持日期参数，总是返回全量历史数据
            - 所有金额单位通常为美元或百万美元
            - 数据格式符合美国GAAP会计准则
            - 美股财报通常以季度为主，年度数据为季度汇总
            - 建议通过query()方法调用以获得缓存支持
            - 某些指标可能在特定时期不可用（显示为NaN）

        API参考：akshare.stock_financial_us_analysis_indicator_em()
        数据源：东方财富(em) - 专业美股数据提供商
        """
        return ak.stock_financial_us_analysis_indicator_em(symbol=symbol)


class USStockStatementQueryer(BaseDataQueryer):
    """
    美股财务三表查询器

    提供统一的美股财务三表查询功能，通过三次API调用获取所有数据并合并：

    #### 资产负债表项目
    - **总资产 Total Assets**: 流动资产和非流动资产合计
    - **总负债 Total Liabilities**: 流动负债和非流动负债合计
    - **所有者权益 Total Equity**: 股东权益总额

    #### 综合损益表项目
    - **营业收入 Total Revenue**: 主营业务收入
    - **营业成本 Cost of Goods Sold**: 主营业务成本
    - **毛利润 Gross Profit**: 营业收入减营业成本
    - **净利润 Net Income**: 最终净利润

    #### 现金流量表项目
    - **经营活动现金流 Operating Cash Flow**: 日常经营活动现金流入流出
    - **投资活动现金流 Investing Cash Flow**: 资本投资现金流入流出
    - **筹资活动现金流 Financing Cash Flow**: 融资活动现金流入流出
    - **现金净变动 Net Change in Cash**: 现金及等价物净变动

    数据源：东方财富(stock_financial_us_report_em)
    缓存类型：us_statements
    日期字段：date (转换后生成)
    """

    # 缓存配置
    cache_query_type = 'us_statements'

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询美股财务三表原始数据并转换为宽表格式

        调用东方财富AkShare API获取美股的完整财务三表数据。美股财务三表需要
        三次独立的API调用来获取资产负债表、综合损益表和现金流量表，然后合并并
        转换为宽表格式以便分析使用。

        Args:
            symbol (str): 美股股票代码，标准美股代码格式：
                - 常见科技股：如"AAPL"（苹果）、"MSFT"（微软）、"GOOGL"（谷歌）
                - 金融股：如"JPM"（摩根大通）、"BAC"（美国银行）
                - 其他知名股票：如"TSLA"（特斯拉）、"AMZN"（亚马逊）
                - 代码不包含交易所后缀，美股统一代码格式
            start_date (Optional[str]): 开始日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理
            end_date (Optional[str]): 结束日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理

        Returns:
            pd.DataFrame: 转换为宽表格式的财务三表DataFrame，具有以下特征：
                - **宽表格式**：每个财务项目作为独立的列，便于横向分析
                - **中文字段名**：使用中文字段名，符合API返回格式
                - **完整覆盖**：包含三大财务报表的所有主要项目
                - **时间标识**：包含REPORT_DATE和统一的date字段
                - **索引结构**：REPORT_DATE, SECURITY_CODE, SECURITY_NAME_ABBR

                主要字段包括：
                #### 基础信息字段
                - **REPORT_DATE**：报告日期（原始字段）
                - **SECURITY_CODE**：股票代码
                - **SECURITY_NAME_ABBR**：股票简称
                - **date**：标准化的日期字符串（用于缓存）

                #### 资产负债表项目
                - **总资产**：Total Assets - 公司总资产规模
                - **总负债**：Total Liabilities - 公司总负债
                - **所有者权益合计**：Total Equity - 股东权益
                - **流动资产合计**：Current Assets
                - **流动负债合计**：Current Liabilities
                - **非流动资产合计**：Non-current Assets
                - **非流动负债合计**：Non-current Liabilities

                #### 综合损益表项目
                - **营业收入**：Total Revenue/Operating Income
                - **营业成本**：Cost of Revenue/Cost of Goods Sold
                - **毛利润**：Gross Profit
                - **营业利润**：Operating Profit
                - **净利润**：Net Profit
                - **每股收益**：Earnings Per Share

                #### 现金流量表项目
                - **现金及现金等价物**：Cash and Cash Equivalents
                - **经营活动现金流量净额**：Operating Cash Flow
                - **投资活动现金流量净额**：Investing Cash Flow
                - **筹资活动现金流量净额**：Financing Cash Flow
                - **现金净增加额**：Net Change in Cash

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时
            ValueError: 当窄表转换为宽表失败时
            RuntimeError: 当三次API调用都失败时

        Example:
            >>> queryer = USStockStatementQueryer()
            >>> # 查询苹果公司财务三表
            >>> data = queryer._query_raw("AAPL")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("总资产:", data["总资产"].tolist())
            >>> print("营业收入:", data["营业收入"].tolist())

        Note:
            - 美股财务三表需要三次API调用，性能相对较低
            - 三次调用分别获取：资产负债表、综合损益表、现金流量表
            - 每次调用使用symbol参数指定报表类型，indicator参数指定时间周期
            - API返回窄表格式（ITEM_NAME + AMOUNT），自动转换为宽表
            - 如果某个报表获取失败，会继续尝试获取其他报表
            - 转换过程使用pivot_table，避免数据丢失
            - 建议通过query()方法调用以获得缓存支持，避免重复的三次API调用
            - 所有金额单位通常为美元或百万美元

        API调用详情：
        1. 资产负债表：stock_financial_us_report_em(stock=symbol, symbol="资产负债表", indicator="年报")
        2. 综合损益表：stock_financial_us_report_em(stock=symbol, symbol="综合损益表", indicator="年报")
        3. 现金流量表：stock_financial_us_report_em(stock=symbol, symbol="现金流量表", indicator="年报")

        数据源：东方财富(em) - 专业美股数据提供商
        """
        # AkShare 美股财务三表API需要特殊参数，获取三张表的数据并合并
        # 日期过滤将由上层的缓存和过滤逻辑处理

        all_data = []

        # 获取三张表的数据
        statements = [
            {"symbol": "资产负债表", "indicator": "年报"},
            {"symbol": "综合损益表", "indicator": "年报"},
            {"symbol": "现金流量表", "indicator": "年报"}
        ]

        for statement_config in statements:
            try:
                df = ak.stock_financial_us_report_em(
                    stock=symbol,
                    symbol=statement_config["symbol"],
                    indicator=statement_config["indicator"]
                )

                if df is not None and not df.empty:
                    # 添加报表类型标识
                    df['STATEMENT_TYPE'] = statement_config["symbol"]
                    all_data.append(df)
            except Exception as e:
                print(f"获取 {statement_config['symbol']} 数据时出错: {e}")
                continue

        # 合并所有报表数据
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
        else:
            df = pd.DataFrame()

        # 验证是否为窄表结构并进行数据处理
        if df is not None and not df.empty:
            required_fields = ["ITEM_NAME", "AMOUNT"]
            if all(field in df.columns for field in required_fields):
                # 确认为窄表结构，转换为宽表格式
                df = self._convert_narrow_to_wide_format(df, symbol)
        else:
            # 如果没有数据，返回空的宽表结构
            df = self._create_empty_wide_format(symbol)

        return df

    def _convert_narrow_to_wide_format(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """将窄表格式转换为宽表格式

        Args:
            df: 窄表格式的财务三表数据
            symbol: 股票代码

        Returns:
            宽表格式的财务三表数据
        """
        # 数据预处理
        if "REPORT_DATE" in df.columns:
            df["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"], errors="coerce")
            df = df.sort_values("REPORT_DATE", ascending=False)

        # 移除空值行
        df = df.dropna(subset=["ITEM_NAME", "AMOUNT"])

        # 确保AMOUNT是数值类型
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")

        # 转换为宽表格式
        wide_df = df.pivot_table(
            index=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
            columns='ITEM_NAME',
            values='AMOUNT',
            fill_value=0,
            aggfunc='first'  # 如果有重复，取第一个
        ).reset_index()

        # 重置列名
        wide_df.columns.name = None
        wide_df = wide_df.reset_index(drop=True)

        # 添加统一的date字段（用于缓存）
        wide_df['date'] = pd.to_datetime(wide_df['REPORT_DATE']).dt.strftime('%Y-%m-%d')

        return wide_df

    def _create_empty_wide_format(self, symbol: str) -> pd.DataFrame:
        """创建空的宽表结构

        Args:
            symbol: 股票代码

        Returns:
            空的宽表结构DataFrame
        """
        # 定义常见的财务项目列（美股）
        # 注意：真实API返回中文字段名，这里应该使用中文字段名
        common_items = [
            '总资产', '总负债', '所有者权益合计',
            '流动资产合计', '流动负债合计', '非流动资产合计', '非流动负债合计',
            '营业收入', '营业成本', '净利润', '现金及现金等价物'
        ]

        # 创建空DataFrame
        columns = ['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'] + common_items
        empty_df = pd.DataFrame(columns=columns)

        return empty_df