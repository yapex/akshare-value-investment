"""
A股数据查询器模块

实现A股市场财务数据查询的核心功能，基于同花顺(ths)数据源API。

## 架构特点

### API结构
- **独立API设计**: A股财务三表使用三个独立的API，不同于港股/美股的统一API
- **数据源**: 同花顺(ths) - 国内权威金融数据提供商
- **数据格式**: 原生宽表格式，无需格式转换

### 查询器分类

#### 财务指标查询器
- **AStockIndicatorQueryer**: 核心财务指标，如ROE、EPS、净利润等
- **数据内容**: 关键财务比率和业绩指标

#### 财务三表查询器
- **AStockBalanceSheetQueryer**: 资产负债表数据
- **AStockIncomeStatementQueryer**: 利润表数据
- **AStockCashFlowQueryer**: 现金流量表数据

### 数据字段特点

#### 中文字段名
- 使用中文字段名，如"净利润"、"基本每股收益"
- 符合国内财务报表标准
- 便于中文用户理解和分析

#### 报告期字段
- 使用"报告期"作为时间标识
- 支持年度、半年度、季度数据
- 格式化时间戳便于缓存管理

## 缓存机制

- **缓存类型**: a_stock_indicators, a_stock_balance, a_stock_profit, a_stock_cashflow
- **日期字段**: report_date
- **增量更新**: 智能识别缺失数据范围

## 使用示例

```python
from akshare_value_investment.datasource.queryers import (
    AStockIndicatorQueryer, AStockBalanceSheetQueryer
)

# 查询财务指标
indicator_queryer = AStockIndicatorQueryer()
indicators = indicator_queryer.query("SH600519", "2023-01-01", "2023-12-31")

# 查询资产负债表
balance_queryer = AStockBalanceSheetQueryer()
balance_sheet = balance_queryer.query("SH600519", "2023-01-01", "2023-12-31")
```

## 注意事项

- A股API不支持日期参数，返回全量数据
- 日期过滤由缓存层自动处理
- 不同股票代码格式：SH(上海)、SZ(深圳)
- API访问频率需遵循同花顺限制
"""

import akshare as ak
import pandas as pd
from typing import Optional

from .base_queryer import BaseDataQueryer


class AStockIndicatorQueryer(BaseDataQueryer):
    """
    A股财务指标查询器

    查询A股的核心财务指标，包括：
    - 盈利能力指标：净利润、ROE、毛利率等
    - 偿债能力指标：资产负债率、流动比率等
    - 运营能力指标：存货周转率、应收账款周转率等
    - 成长能力指标：营收增长率、净利润增长率等

    数据源：同花顺(stock_financial_abstract_ths)
    缓存类型：a_stock_indicators
    日期字段：report_date
    """

    # 缓存配置
    cache_query_type = 'a_stock_indicators'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        查询A股财务指标原始数据

        调用同花顺AkShare API获取A股的核心财务指标数据。该API不支持日期参数，
        返回该股票的所有历史财务指标数据。日期过滤由上层的缓存系统自动处理。

        Args:
            symbol (str): A股股票代码，必须包含交易所前缀：
                - SH前缀：上海证券交易所，如"SH600519"（贵州茅台）
                - SZ前缀：深圳证券交易所，如"SZ000001"（平安银行）
                - 代码格式：交易所前缀 + 6位数字股票代码

        Returns:
            pd.DataFrame: 包含财务指标的DataFrame，具有以下特征：
                - **中文字段名**：符合国内财务报表标准，如"净资产收益率"、"基本每股收益"
                - **时间标识**：使用"报告期"字段，包含年度、半年度、季度数据
                - **数据完整性**：包含67个核心财务指标字段
                - **时间排序**：按报告期倒序排列，最新数据在前

                主要字段包括：
                - 盈利能力：净利润、基本每股收益、净资产收益率(ROE)、毛利率等
                - 偿债能力：资产负债率、流动比率、速动比率等
                - 运营能力：存货周转率、应收账款周转率、总资产周转率等
                - 成长能力：营业收入增长率、净利润增长率、净资产增长率等

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = AStockIndicatorQueryer()
            >>> # 查询贵州茅台财务指标
            >>> data = queryer._query_raw("SH600519")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("包含字段:", data.columns.tolist())

        Note:
            - 该方法不进行日期过滤，返回所有历史数据
            - 同花顺API可能有访问频率限制
            - 数据质量依赖于同花顺的数据源质量
            - 建议通过query()方法调用以获得缓存支持

        API参考：akshare.stock_financial_abstract_ths()
        数据源：同花顺(ths) - 国内权威金融数据提供商
        """
        return ak.stock_financial_abstract_ths(symbol=symbol)


class AStockBalanceSheetQueryer(BaseDataQueryer):
    """
    A股资产负债表查询器

    虽然API名为debt，但实际返回完整的资产负债表数据，包括：

    #### 资产类项目
    - 流动资产：货币资金、应收账款、存货等
    - 非流动资产：固定资产、无形资产、长期投资等
    - 资产总计：总资产

    #### 负债类项目
    - 流动负债：短期借款、应付账款、预收款项等
    - 非流动负债：长期借款、应付债券等
    - 负债总计：总负债

    #### 所有者权益项目
    - 股本、资本公积、盈余公积等
    - 未分配利润、归属于母公司所有者权益

    数据源：同花顺(stock_financial_debt_ths)
    缓存类型：a_stock_balance
    日期字段：report_date
    """

    # 缓存配置
    cache_query_type = 'a_stock_balance'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        查询A股资产负债表原始数据

        调用同花顺AkShare API获取A股的资产负债表数据。虽然API名称为"debt"，
        但实际返回完整的资产负债表，包含资产、负债和所有者权益的所有项目。

        Args:
            symbol (str): A股股票代码，必须包含交易所前缀：
                - SH前缀：上海证券交易所，如"SH600519"（贵州茅台）
                - SZ前缀：深圳证券交易所，如"SZ000001"（平安银行）
                - 代码格式：交易所前缀 + 6位数字股票代码

        Returns:
            pd.DataFrame: 包含资产负债表数据的DataFrame，具有以下特征：
                - **中文字段名**：符合国内财务报表标准，如"货币资金"、"应收账款"
                - **完整覆盖**：包含资产、负债、所有者权益的所有主要项目
                - **时间标识**：使用"报告期"字段，包含年度、半年度、季度数据
                - **数据完整性**：涵盖流动性和非流动性项目

                主要字段包括：
                #### 资产类项目
                - **流动资产**：货币资金、应收账款、存货、预付款项等
                - **非流动资产**：固定资产、无形资产、长期股权投资、商誉等
                - **资产总计**：总资产，反映公司规模

                #### 负债类项目
                - **流动负债**：短期借款、应付账款、预收款项等
                - **非流动负债**：长期借款、应付债券、递延收益等
                - **负债总计**：总负债

                #### 所有者权益项目
                - **股本**、**资本公积**、**盈余公积**
                - **未分配利润**、**归属于母公司所有者权益**
                - **所有者权益合计**

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = AStockBalanceSheetQueryer()
            >>> # 查询贵州茅台资产负债表
            >>> data = queryer._query_raw("SH600519")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("资产总计:", data["资产总计"].tolist())

        Note:
            - API名为debt但返回完整资产负债表，这是历史命名的遗留问题
            - 该方法不进行日期过滤，返回所有历史数据
            - 数据格式符合中国企业会计准则
            - 建议通过query()方法调用以获得缓存支持

        API参考：akshare.stock_financial_debt_ths()
        数据源：同花顺(ths) - 国内权威金融数据提供商
        """
        return ak.stock_financial_debt_ths(symbol=symbol)


class AStockIncomeStatementQueryer(BaseDataQueryer):
    """
    A股利润表查询器

    虽然API名为benefit，但实际返回完整的利润表数据，包括：

    #### 收入类项目
    - 营业总收入：主营业务收入和其他业务收入
    - 营业收入：主营业务收入
    - 利息收入、手续费及佣金收入等

    #### 成本费用类项目
    - 营业总成本：营业成本、税金及附加、销售费用等
    - 营业成本：主营业务成本
    - 销售费用、管理费用、研发费用、财务费用

    #### 利润类项目
    - 营业利润：营业收入减去营业成本和期间费用
    - 利润总额：营业利润加营业外收入减营业外支出
    - 净利润：利润总额减去所得税费用
    - 归属于母公司所有者的净利润

    #### 每股收益
    - 基本每股收益：基本EPS
    - 稀释每股收益：稀释EPS

    数据源：同花顺(stock_financial_benefit_ths)
    缓存类型：a_stock_profit
    日期字段：report_date
    """

    # 缓存配置
    cache_query_type = 'a_stock_profit'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        查询A股利润表原始数据

        调用同花顺AkShare API获取A股的利润表数据。虽然API名称为"benefit"，
        但实际返回完整的利润表（综合损益表），反映企业在一定期间的经营成果。

        Args:
            symbol (str): A股股票代码，必须包含交易所前缀：
                - SH前缀：上海证券交易所，如"SH600519"（贵州茅台）
                - SZ前缀：深圳证券交易所，如"SZ000001"（平安银行）
                - 代码格式：交易所前缀 + 6位数字股票代码

        Returns:
            pd.DataFrame: 包含利润表数据的DataFrame，具有以下特征：
                - **中文字段名**：符合国内财务报表标准，如"营业收入"、"营业成本"
                - **利润层次**：从营业收入到净利润的完整利润计算过程
                - **时间标识**：使用"报告期"字段，包含年度、半年度、季度数据
                - **每股收益**：包含基本和稀释每股收益数据

                主要字段包括：
                #### 收入类项目
                - **营业总收入**：包含主营业务和其他业务收入
                - **营业收入**：企业主要经营活动的收入
                - **利息收入**、**手续费及佣金收入**（金融企业特有）

                #### 成本费用类项目
                - **营业总成本**：包含营业成本、期间费用等
                - **营业成本**：主营业务成本
                - **期间费用**：销售费用、管理费用、研发费用、财务费用
                - **税金及附加**：消费税、城市维护建设税等

                #### 利润类项目
                - **营业利润**：营业收入减去营业成本和期间费用
                - **利润总额**：营业利润加营业外收支净额
                - **净利润**：利润总额减去所得税费用
                - **归属于母公司所有者的净利润**：核心盈利指标

                #### 每股收益
                - **基本每股收益**：按加权平均股本计算的EPS
                - **稀释每股收益**：考虑潜在普通股稀释效应的EPS

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = AStockIncomeStatementQueryer()
            >>> # 查询贵州茅台利润表
            >>> data = queryer._query_raw("SH600519")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("营业收入:", data["营业收入"].tolist())
            >>> print("净利润:", data["归属于母公司所有者的净利润"].tolist())

        Note:
            - API名为benefit但返回完整利润表，这是历史命名的遗留问题
            - 该方法不进行日期过滤，返回所有历史数据
            - 数据格式符合中国企业会计准则
            - 建议通过query()方法调用以获得缓存支持

        API参考：akshare.stock_financial_benefit_ths()
        数据源：同花顺(ths) - 国内权威金融数据提供商
        """
        return ak.stock_financial_benefit_ths(symbol=symbol)


class AStockCashFlowQueryer(BaseDataQueryer):
    """
    A股现金流量表查询器

    提供完整的现金流量表数据，采用直接法和间接法编制：

    #### 经营活动产生的现金流量
    - 销售商品、提供劳务收到的现金
    - 收到的税费返还、收到其他与经营活动有关的现金
    - 购买商品、接受劳务支付的现金
    - 支付给职工以及为职工支付的现金
    - 支付的各项税费、支付其他与经营活动有关的现金

    #### 投资活动产生的现金流量
    - 收回投资收到的现金、取得投资收益收到的现金
    - 处置固定资产、无形资产等收回的现金净额
    - 购建固定资产、无形资产等支付的现金
    - 投资支付的现金、取得子公司支付的现金净额

    #### 筹资活动产生的现金流量
    - 吸收投资收到的现金、取得借款收到的现金
    - 偿还债务支付的现金、分配股利、利润或偿付利息支付的现金
    - 支付其他与筹资活动有关的现金

    #### 现金及现金等价物净增加额
    - 现金及现金等价物净变动情况
    - 期末现金及现金等价物余额

    数据源：同花顺(stock_financial_cash_ths)
    缓存类型：a_stock_cashflow
    日期字段：report_date
    """

    # 缓存配置
    cache_query_type = 'a_stock_cashflow'

    def _query_raw(self, symbol: str) -> pd.DataFrame:
        """
        查询A股现金流量表原始数据

        调用同花顺AkShare API获取A股的现金流量表数据，反映企业在一定期间内
        现金及现金等价物流入和流出的情况，包含直接法和间接法编制的信息。

        Args:
            symbol (str): A股股票代码，必须包含交易所前缀：
                - SH前缀：上海证券交易所，如"SH600519"（贵州茅台）
                - SZ前缀：深圳证券交易所，如"SZ000001"（平安银行）
                - 代码格式：交易所前缀 + 6位数字股票代码

        Returns:
            pd.DataFrame: 包含现金流量表数据的DataFrame，具有以下特征：
                - **中文字段名**：符合国内财务报表标准，如"经营活动现金流量"
                - **三大活动**：经营、投资、筹资活动的完整现金流信息
                - **时间标识**：使用"报告期"字段，包含年度、半年度、季度数据
                - **现金管理**：现金及现金等价物变动情况

                主要字段包括：
                #### 经营活动产生的现金流量
                - **现金流入**：
                  - "销售商品、提供劳务收到的现金"：主要经营活动收入
                  - "收到的税费返还"：税费返还收入
                  - "收到其他与经营活动有关的现金"：其他经营收入
                - **现金流出**：
                  - "购买商品、接受劳务支付的现金"：采购支出
                  - "支付给职工以及为职工支付的现金"：人工成本
                  - "支付的各项税费"：税费支出
                  - "支付其他与经营活动有关的现金"：其他经营支出
                - **净额**："经营活动产生的现金流量净额"

                #### 投资活动产生的现金流量
                - **现金流入**：
                  - "收回投资收到的现金"：投资回收
                  - "取得投资收益收到的现金"：投资收益
                  - "处置固定资产等收回的现金净额"：资产处置收入
                - **现金流出**：
                  - "购建固定资产等支付的现金"：资本支出
                  - "投资支付的现金"：对外投资
                  - "取得子公司支付的现金净额"：并购支出
                - **净额**："投资活动产生的现金流量净额"

                #### 筹资活动产生的现金流量
                - **现金流入**：
                  - "吸收投资收到的现金"：股权融资
                  - "取得借款收到的现金"：债务融资
                - **现金流出**：
                  - "偿还债务支付的现金"：债务偿还
                  - "分配股利、偿付利息支付的现金"：股东回报
                - **净额**："筹资活动产生的现金流量净额"

                #### 现金及现金等价物
                - "现金及现金等价物净增加额"：总体现金变动
                - "期末现金及现金等价物余额"：期末现金状况

        Raises:
            ValueError: 当股票代码格式不正确时
            ConnectionError: 当网络连接失败时
            Exception: 当API调用失败或数据获取异常时

        Example:
            >>> queryer = AStockCashFlowQueryer()
            >>> # 查询贵州茅台现金流量表
            >>> data = queryer._query_raw("SH600519")
            >>> print(f"获取到 {len(data)} 个报告期的数据")
            >>> print("经营现金流净额:", data["经营活动产生的现金流量净额"].tolist())

        Note:
            - 该方法不进行日期过滤，返回所有历史数据
            - 现金流量表数据对分析企业现金流质量至关重要
            - 经营活动现金流净额常被用来评估企业盈利质量
            - 建议通过query()方法调用以获得缓存支持

        API参考：akshare.stock_financial_cash_ths()
        数据源：同花顺(ths) - 国内权威金融数据提供商
        """
        return ak.stock_financial_cash_ths(symbol=symbol)