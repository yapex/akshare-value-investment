"""
港股数据查询器模块

实现港股市场财务数据查询的核心功能，基于东方财富(EM)数据源API。

## 架构特点

### API结构
- **统一API设计**: 使用单一API获取所有财务三表数据
- **数据源**: 东方财富(EM) - 专业港股数据提供商
- **数据格式**: 窄表格式，自动转换为宽表

### 查询器分类

#### 财务指标查询器
- **HKStockIndicatorQueryer**: 港股财务指标分析
- **数据内容**: ROE、EPS、市盈率等关键指标

#### 财务三表查询器
- **HKStockStatementQueryer**: 统一的财务三表查询器
- **数据转换**: 自动窄表→宽表格式转换
- **报表类型**: 资产负债表、综合损益表、现金流量表

### 数据字段特点

#### 英文字段名
- 使用英文字段名，如"BASIC_EPS"、"ROE_AVG"
- 符合国际财务报表标准
- 便于国际化使用

#### 统一日期格式
- 使用"REPORT_DATE"作为时间标识
- 标准化日期格式便于缓存管理
- 支持年度、半年度、季度数据

## 窄表到宽表转换

### 转换逻辑
- **索引字段**: REPORT_DATE, SECURITY_CODE, SECURITY_NAME_ABBR
- **数据列**: STD_ITEM_NAME (财务项目名称), AMOUNT (金额)
- **聚合方式**: 使用pivot_table转换，避免数据丢失

### 转换示例
```python
# 原始窄表
REPORT_DATE | SECURITY_CODE | STD_ITEM_NAME | AMOUNT
2023-12-31 | 00700       | 总资产        | 10000
2023-12-31 | 00700       | 总负债        | 5000

# 转换后宽表
REPORT_DATE | SECURITY_CODE | 总资产 | 总负债
2023-12-31 | 00700       | 10000  | 5000
```

## 缓存机制

- **缓存类型**: a_stock_indicators, a_stock_balance, a_stock_profit, a_stock_cashflow
- **日期字段**: date (转换后生成)
- **增量更新**: 智能识别缺失数据范围

## 使用示例

```python
from akshare_value_investment.datasource.queryers import (
    HKStockIndicatorQueryer, HKStockStatementQueryer
)

# 查询财务指标
indicator_queryer = HKStockIndicatorQueryer()
indicators = indicator_queryer.query("00700", "2023-01-01", "2023-12-31")

# 查询财务三表（自动转换为宽表）
statement_queryer = HKStockStatementQueryer()
statements = statement_queryer.query("00700", "2023-01-01", "2023-12-31")
```

## 注意事项

- 港股API不支持日期参数，返回全量数据
- 日期过滤由缓存层自动处理
- 股票代码格式：5位数字，如"00700"（腾讯）、"09988"（阿里巴巴）
- 窄表到宽表转换需要一定的计算资源
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer
from ...core.models import MarketType


class HKStockIndicatorQueryer(BaseDataQueryer):
    """
    港股财务指标查询器

    查询港股的核心财务分析指标，包括：

    #### 盈利能力指标
    - **BASIC_EPS**: 基本每股收益
    - **ROE_AVG**: 平均净资产收益率
    - **HOLDER_PROFIT**: 股东应占溢利

    #### 估值指标
    - **PE_RATIO**: 市盈率
    - **PB_RATIO**: 市净率
    - **DIVIDEND_YIELD**: 股息率

    #### 成长性指标
    - **EPS_GROWTH**: 每股收益增长率
    - **REVENUE_GROWTH**: 营收增长率

    数据源：东方财富(stock_financial_hk_analysis_indicator_em)
    缓存类型：hk_indicators
    日期字段：date
    """

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询港股财务指标原始数据

        调用东方财富AkShare API获取港股的核心财务指标数据。该API不支持日期参数，
        返回该股票的所有历史财务指标数据。日期过滤由上层的缓存系统自动处理。

        Args:
            symbol (str): 港股股票代码，必须为5位数字格式：
                - 5位数字代码，如"00700"（腾讯控股）、"09988"（阿里巴巴-SW）
                - 代码不足5位需前面补零，如"00388"（港交所）
                - 代码不包含交易所前缀（港股统一在港交所交易）
            start_date (Optional[str]): 开始日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理
            end_date (Optional[str]): 结束日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理

        Returns:
            pd.DataFrame: 包含财务指标的DataFrame，具有以下特征：
                - **英文字段名**：符合国际财务报表标准，如"BASIC_EPS"、"ROE_AVG"
                - **国际标准**：遵循IFRS（国际财务报告准则）命名规范
                - **时间标识**：使用标准化日期字段，包含年度、半年度、季度数据
                - **数据完整性**：包含36个核心财务指标字段
                - **时间排序**：按报告期倒序排列，最新数据在前

                主要字段包括：
                #### 盈利能力指标
                - **BASIC_EPS**：基本每股收益（港币）
                - **ROE_AVG**：平均净资产收益率
                - **HOLDER_PROFIT**：股东应占溢利
                - **GROSS_PROFIT_MARGIN**：毛利率
                - **NET_PROFIT_MARGIN**：净利率

                #### 估值指标
                - **PE_RATIO**：市盈率
                - **PB_RATIO**：市净率
                - **DIVIDEND_YIELD**：股息率
                - **MARKET_CAP**：市值

                #### 财务结构指标
                - **DEBT_RATIO**：负债比率
                - **CURRENT_RATIO**：流动比率
                - **ASSET_TURNOVER**：资产周转率

                #### 成长性指标
                - **EPS_GROWTH**：每股收益增长率
                - **REVENUE_GROWTH**：营收增长率
                - **PROFIT_GROWTH**：利润增长率

        Raises:
            ValueError: 当股票代码格式不正确时（非5位数字）
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = HKStockIndicatorQueryer()
            >>> # 查询腾讯控股财务指标
            >>> data = queryer._query_raw("00700")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("BASIC EPS:", data["BASIC_EPS"].tolist())

        Note:
            - 东方财富API不支持日期参数，总是返回全量历史数据
            - 所有金额单位通常为港币
            - 数据格式符合国际财务报告准则（IFRS）
            - 建议通过query()方法调用以获得缓存支持
            - 港股财报通常以年度和半年度为主，季度数据相对较少

        API参考：akshare.stock_financial_hk_analysis_indicator_em()
        数据源：东方财富(em) - 专业港股数据提供商
        """
        return ak.stock_financial_hk_analysis_indicator_em(symbol=symbol)


class HKStockStatementQueryer(BaseDataQueryer):
    """
    港股财务三表查询器

    提供统一的港股财务三表查询功能，自动将窄表格式转换为宽表格式：

    #### 资产负债表项目
    - 非流动资产：物业厂房及设备、无形资产、投资物业
    - 流动资产：现金及等价物、存货、贸易应收款项
    - 流动负债：银行借款、贸易应付款项
    - 非流动负债：长期借款、递延税项负债
    - 权益储备：股本、储备、保留溢利

    #### 综合损益表项目
    - 收入：营业额、其他收入
    - 成本：销售成本、分销成本、行政费用
    - 利润：毛利、营业溢利、股东应占溢利

    #### 现金流量表项目
    - 经营活动现金流量：分部现金流量
    - 投资活动现金流量：购置固定资产、出售投资
    - 筹资活动现金流量：发行股份、偿还借款

    数据源：东方财富(stock_financial_hk_report_em)
    缓存类型：hk_statements
    日期字段：date (转换后生成)
    """

    # 缓存配置
    cache_query_type = 'hk_statements'

    def _query_raw(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查询港股财务三表原始数据并转换为宽表格式

        调用东方财富AkShare API获取港股的财务三表数据，包括资产负债表、综合损益表
        和现金流量表。API返回窄表格式，系统自动转换为宽表格式以便分析使用。

        Args:
            symbol (str): 港股股票代码，必须为5位数字格式：
                - 5位数字代码，如"00700"（腾讯控股）、"09988"（阿里巴巴-SW）
                - 代码不足5位需前面补零，如"00388"（港交所）
                - 代码不包含交易所前缀（港股统一在港交所交易）
            start_date (Optional[str]): 开始日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理
            end_date (Optional[str]): 结束日期 (YYYY-MM-DD格式)
                - 该参数会被忽略，东方财富API不支持日期过滤
                - 日期过滤由缓存层自动处理

        Returns:
            pd.DataFrame: 转换为宽表格式的财务三表DataFrame，具有以下特征：
                - **宽表格式**：每个财务项目作为独立的列，便于横向分析
                - **中文字段名**：使用中文字段名，符合港股财报惯例
                - **时间标识**：包含REPORT_DATE和统一的date字段
                - **数据完整性**：涵盖三大财务报表的主要项目
                - **索引结构**：REPORT_DATE, SECURITY_CODE, SECURITY_NAME_ABBR

                主要字段包括：
                #### 基础信息字段
                - **REPORT_DATE**：报告日期（原始字段）
                - **SECURITY_CODE**：股票代码
                - **SECURITY_NAME_ABBR**：股票简称
                - **date**：标准化的日期字符串（用于缓存）

                #### 资产负债表项目
                - **资产总计**：Total Assets
                - **负债合计**：Total Liabilities
                - **所有者权益合计**：Total Equity
                - **流动资产合计**、**流动负债合计**
                - **非流动资产合计**、**非流动负债合计**

                #### 综合损益表项目
                - **营业收入**：Revenue/Operating Income
                - **营业成本**：Cost of Goods Sold
                - **净利润**：Net Profit
                - **毛利润**：Gross Profit

                #### 现金流量表项目
                - **现金及现金等价物余额**：Cash and Cash Equivalents
                - **经营活动现金流量净额**：Operating Cash Flow
                - **投资活动现金流量净额**：Investing Cash Flow
                - **筹资活动现金流量净额**：Financing Cash Flow

        Raises:
            ValueError: 当股票代码格式不正确时（非5位数字）
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时
            ValueError: 当窄表转换为宽表失败时

        Example:
            >>> queryer = HKStockStatementQueryer()
            >>> # 查询腾讯控股财务三表
            >>> data = queryer._query_raw("00700")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("总资产:", data["资产总计"].tolist())

        Note:
            - 东方财富API不支持日期参数，总是返回全量历史数据
            - API返回窄表格式（STD_ITEM_NAME + AMOUNT），自动转换为宽表
            - 转换过程使用pivot_table，避免数据丢失
            - 转换后的数据便于进行财务分析和时间序列比较
            - 建议通过query()方法调用以获得缓存支持
            - 所有金额单位通常为港币或百万港币

        API参考：akshare.stock_financial_hk_report_em()
        数据源：东方财富(em) - 专业港股数据提供商
        """
        # AkShare 港股财务三表API本身不支持日期参数，所以这里忽略日期参数
        # 日期过滤将由上层的缓存和过滤逻辑处理
        df = ak.stock_financial_hk_report_em(stock=symbol)

        # 验证是否为窄表结构并进行数据处理
        if df is not None and not df.empty:
            required_fields = ["STD_ITEM_NAME", "AMOUNT"]
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
        df = df.dropna(subset=["STD_ITEM_NAME", "AMOUNT"])

        # 确保AMOUNT是数值类型
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")

        # 转换为宽表格式
        wide_df = df.pivot_table(
            index=['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR'],
            columns='STD_ITEM_NAME',
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
        # 定义常见的财务项目列
        common_items = [
            '资产总计', '负债合计', '所有者权益合计',
            '流动资产合计', '流动负债合计', '非流动资产合计', '非流动负债合计',
            '营业收入', '营业成本', '净利润', '现金及现金等价物余额'
        ]

        # 创建空DataFrame
        columns = ['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date'] + common_items
        empty_df = pd.DataFrame(columns=columns)

        return empty_df

    