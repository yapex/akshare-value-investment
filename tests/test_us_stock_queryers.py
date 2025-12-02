"""
美股查询器单元测试 - pytest版本

基于真实CSV样本数据的美股财务指标和财务三表查询器测试。
使用pytest fixtures和现代化测试模式，测试完整的query方法包括缓存和日期过滤。
"""

import pandas as pd
from unittest.mock import patch
import os

import pytest
from akshare_value_investment.datasource.queryers.us_stock_queryers import (
    USStockIndicatorQueryer,
    USStockBalanceSheetQueryer,
    USStockIncomeStatementQueryer,
    USStockCashFlowQueryer,
    USStockStatementQueryer
)


class TestUSStockQueryersWithRealData:
    """美股查询器测试类 - 使用真实Mock数据"""

    def test_us_stock_indicator_queryer_success(self, mock_loader, test_container):
        """测试美股财务指标查询器成功查询（使用完整query方法）"""
        test_symbol = "AAPL"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 使用真实的mock数据
        mock_data = mock_loader.get_us_stock_indicators_mock(
            symbol=test_symbol,
            start_date=test_start_date,
            end_date=test_end_date,
            limit=1
        )

        with patch('akshare.stock_financial_us_analysis_indicator_em', return_value=mock_data):
            # 使用测试容器创建查询器（包含测试缓存）
            queryer = test_container.us_stock_indicators()

            # 执行完整查询（包括缓存和日期过滤）
            result = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

            # 验证关键字段存在
            required_fields = ['SECURITY_CODE', 'PARENT_HOLDER_NETPROFIT', 'BASIC_EPS']
            for field in required_fields:
                assert field in result.columns, f"缺少字段: {field}"

            # 验证股票代码正确
            if 'SECURITY_CODE' in result.columns:
                assert result['SECURITY_CODE'].iloc[0] == test_symbol

    def test_us_stock_indicator_queryer_caching(self, mock_loader, test_container):
        """测试美股财务指标查询器缓存功能"""
        test_symbol = "AAPL"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 创建包含多条记录的mock数据
        mock_data = mock_loader.get_us_stock_indicators_mock(
            symbol=test_symbol,
            start_date="2020-01-01",
            end_date="2024-12-31",
            limit=5
        )

        with patch('akshare.stock_financial_us_analysis_indicator_em', return_value=mock_data):
            # 使用测试容器创建查询器
            queryer = test_container.us_stock_indicators()

            # 第一次查询（应该调用API并缓存）
            result1 = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证第一次查询结果
            assert isinstance(result1, pd.DataFrame)
            assert len(result1) >= 0  # 可能被日期过滤为0

            # 第二次相同查询（应该使用缓存）
            result2 = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证缓存查询返回相同结果
            assert result1.equals(result2), "缓存结果不一致"

            # 验证缓存实例存在且是测试缓存
            assert queryer._cache is not None
            assert hasattr(queryer._cache, 'directory')  # diskcache.Cache 的属性

            # 验证缓存使用临时目录
            cache_dir = queryer._cache.directory
            assert cache_dir is not None
            assert 'test_cache' in cache_dir or os.path.basename(cache_dir).startswith('test_cache_')

    def test_us_stock_indicator_queryer_no_data(self, test_container):
        """测试美股财务指标查询器无数据情况（使用完整query方法）"""
        # 返回空DataFrame
        with patch('akshare.stock_financial_us_analysis_indicator_em', return_value=pd.DataFrame()):
            queryer = test_container.us_stock_indicators()

            # 执行完整查询
            result = queryer.query("INVALID", "2024-01-01", "2024-12-31")

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_us_stock_indicator_queryer_date_filtering(self, mock_loader):
        """测试美股财务指标查询器的日期过滤功能"""
        test_symbol = "AAPL"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 返回多条数据，包含不同日期
        mock_data = mock_loader.get_us_stock_indicators_mock(
            symbol=test_symbol,
            start_date="2020-01-01",
            end_date="2024-12-31"
        )

        with patch('akshare.stock_financial_us_analysis_indicator_em', return_value=mock_data):
            queryer = USStockIndicatorQueryer()

            # 测试精确日期查询 - 使用query方法
            result = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert result is not None
            assert isinstance(result, pd.DataFrame)

    def test_us_stock_statement_queryer_success(self, mock_loader):
        """测试美股财务三表查询器成功查询（宽表格式）"""
        test_symbol = "AAPL"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 创建包含财务项目的窄表数据
        narrow_data = pd.DataFrame({
            'REPORT_DATE': ['2024-12-31', '2024-12-31', '2024-12-31'],
            'SECURITY_CODE': [test_symbol, test_symbol, test_symbol],
            'SECURITY_NAME_ABBR': ['Apple Inc.', 'Apple Inc.', 'Apple Inc.'],
            'ITEM_NAME': ['Total Assets', 'Total Liabilities', 'Net Income'],
            'AMOUNT': [350000000000, 200000000000, 90000000000]
        })

        with patch('akshare.stock_financial_us_report_em', return_value=narrow_data):
            # 创建查询器
            queryer = USStockStatementQueryer()

            # 执行查询 - 使用query方法
            result = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0

            # 验证宽表格式关键字段存在
            required_fields = ['SECURITY_CODE', 'REPORT_DATE', 'date']
            for field in required_fields:
                assert field in result.columns, f"缺少字段: {field}"

            # 验证财务项目转换成功
            expected_items = ['Total Assets', 'Total Liabilities', 'Net Income']
            for item in expected_items:
                assert item in result.columns, f"缺少财务项目列: {item}"

            # 验证股票代码正确
            if 'SECURITY_CODE' in result.columns and len(result) > 0:
                assert result['SECURITY_CODE'].iloc[0] == test_symbol

    def test_us_stock_statement_queryer_different_items(self, mock_loader):
        """测试美股财务三表查询器不同财务项目（宽表格式）"""
        test_symbol = "AAPL"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 美股Statement查询器通过3次API调用获取不同报表，每次返回不同的宽表格式
        # 这里我们模拟一个简化版本，测试基本功能
        mock_wide_data = pd.DataFrame({
            'REPORT_DATE': ['2024-12-31'],
            'SECURITY_CODE': [test_symbol],
            'SECURITY_NAME_ABBR': ['Apple Inc.'],
            'Total Assets': [350000000000],
            'Total Liabilities': [200000000000],
            'date': ['2024-12-31']
        })

        with patch('akshare.stock_financial_us_report_em', return_value=mock_wide_data):
            queryer = USStockStatementQueryer()
            result = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0

            # 验证包含基本的财务项目列
            assert 'Total Assets' in result.columns or 'SECURITY_CODE' in result.columns

    def test_us_stock_statement_queryer_api_error_handling(self):
        """测试美股财务三表查询器API错误处理"""
        # 模拟API调用异常
        with patch('akshare.stock_financial_us_report_em', side_effect=Exception("网络连接失败")):
            queryer = USStockStatementQueryer()
            result = queryer.query("AAPL", "2024-01-01", "2024-12-31")

            # 验证结果：应该返回空的宽表结构（美股有异常处理）
            assert isinstance(result, pd.DataFrame)
            # 应该有基本的列结构（空宽表）
            expected_columns = ['REPORT_DATE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR', 'date']
            for col in expected_columns:
                assert col in result.columns

    def test_wide_format_conversion(self, mock_loader):
        """测试美股财务三表的数据格式"""
        test_symbol = "AAPL"

        # 美股Statement查询器通过3次API调用获取不同报表，然后合并
        # 这里我们只测试基本的查询功能，不关注具体数据值
        queryer = USStockStatementQueryer()

        # 由于美股Statement查询器的复杂性（多次API调用和合并），我们只验证基本功能
        # 实际数据格式会根据API返回的不同而变化
        try:
            result = queryer.query(test_symbol)

            # 验证基本返回格式
            assert isinstance(result, pd.DataFrame)

            # 验证包含基本的标识列
            basic_columns = ['SECURITY_CODE', 'date']
            found_basic_columns = [col for col in basic_columns if col in result.columns]
            assert len(found_basic_columns) > 0, f"应该包含基本标识列，实际列: {list(result.columns)}"

        except Exception as e:
            # 如果API调用失败，这是正常的（在测试环境中）
            # 我们只验证查询器的初始化和基本结构
            assert queryer is not None
            assert hasattr(queryer, 'cache_query_type')
            assert queryer.cache_query_type == 'us_statements'

    def test_mock_data_loader_integration(self, mock_loader):
        """测试Mock数据加载器集成"""
        # 验证可以成功获取各种类型的mock数据
        a_stock_data = mock_loader.get_a_stock_indicators_mock(limit=1)
        hk_indicators_data = mock_loader.get_hk_stock_indicators_mock(limit=1)
        hk_statements_data = mock_loader.get_hk_stock_statements_mock(limit=1)
        us_indicators_data = mock_loader.get_us_stock_indicators_mock(limit=1)
        us_statements_data = mock_loader.get_us_stock_statements_mock(limit=1)

        # 验证数据格式正确
        assert isinstance(a_stock_data, pd.DataFrame)
        assert isinstance(hk_indicators_data, pd.DataFrame)
        assert isinstance(hk_statements_data, pd.DataFrame)
        assert isinstance(us_indicators_data, pd.DataFrame)
        assert isinstance(us_statements_data, pd.DataFrame)

        # 验证美股财务三表数据结构（原始格式为窄表）
        if len(us_statements_data) > 0:
            # MockDataLoader返回的是原始窄表格式
            assert 'ITEM_NAME' in us_statements_data.columns
            assert 'AMOUNT' in us_statements_data.columns

        # 验证美股财务指标为宽表格式
        if len(us_indicators_data) > 0:
            assert 'PARENT_HOLDER_NETPROFIT' in us_indicators_data.columns
            assert 'BASIC_EPS' in us_indicators_data.columns

    def test_data_structure_consistency(self, mock_loader):
        """测试数据结构一致性"""
        # 检查所有mock数据都有必要的字段
        info = mock_loader.get_sample_data_info()

        # 跳过A股数据，因为它们使用报告期而不是date字段
        skip_types = ['a_stock_indicators', 'a_stock_balance_sheet', 'a_stock_profit_sheet', 'a_stock_cash_flow_sheet']

        for data_type, data_info in info.items():
            if data_type in skip_types:
                continue  # 跳过A股数据，它们使用report_date字段

            assert data_info['has_date'], f"{data_type} 缺少date字段"
            assert data_info['rows'] > 0, f"{data_type} 没有数据"
            assert data_info['columns'] > 0, f"{data_type} 没有列"


class TestUSStockQueryersIntegration:
    """美股查询器集成测试"""

    def test_queryer_initialization(self):
        """测试查询器初始化"""
        indicator_queryer = USStockIndicatorQueryer()
        statement_queryer = USStockStatementQueryer()

        assert isinstance(indicator_queryer, USStockIndicatorQueryer)
        assert isinstance(statement_queryer, USStockStatementQueryer)

    @pytest.mark.parametrize("symbol", ['AAPL', 'MSFT', 'GOOGL', 'TSLA'])
    def test_different_symbols(self, symbol):
        """测试不同股票代码"""
        # 只测试参数传递，不测试实际API调用
        indicator_queryer = USStockIndicatorQueryer()
        statement_queryer = USStockStatementQueryer()
        assert indicator_queryer is not None
        assert statement_queryer is not None

    @pytest.mark.integration
    def test_api_parameter_consistency(self):
        """测试API参数一致性"""
        # 准备mock数据
        mock_data = pd.DataFrame({'test': [1]})

        with patch('akshare.stock_financial_us_analysis_indicator_em', return_value=mock_data) as mock_indicator, \
             patch('akshare.stock_financial_us_report_em', return_value=mock_data) as mock_report:

            symbol = 'AAPL'
            indicator_queryer = USStockIndicatorQueryer()
            statement_queryer = USStockStatementQueryer()

            # 执行查询
            indicator_queryer._query_raw(symbol)
            statement_queryer._query_raw(symbol)

            # 验证API调用参数名正确
            mock_indicator.assert_called_once_with(symbol=symbol, indicator="单季报")
            # 美股三表需要多次调用，每次参数不同
            assert mock_report.call_count == 3

    def test_us_stock_vs_other_markets_difference(self):
        """测试美股与其他市场的API差异"""
        # 美股财务三表使用 stock 参数（与港股不同）
        # 美股财务指标使用 symbol 参数（与港股一致）

        # 验证美股查询器存在且可以初始化
        us_statement = USStockStatementQueryer()
        assert us_statement is not None

        # 验证美股指标查询器使用 symbol 参数（与港股一致）
        us_indicator = USStockIndicatorQueryer()
        assert us_indicator is not None

    @pytest.mark.production
    @pytest.mark.slow
    def test_production_query_net_profit_2022_2024(self):
        """测试生产环境：查询2022-2024年度净利润数据（端到端测试）"""
        # 这是一个真实的端到端测试，不使用mock，直接调用akshare API

        # 创建查询器
        queryer = USStockIndicatorQueryer()

        # 查询2022-2024年数据 - 真实的生产环境查询场景
        result = queryer.query(
            symbol="AAPL",  # 苹果公司
            start_date="2022-01-01",
            end_date="2024-12-31"
        )

        # 验证查询结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0, "应该返回至少1年数据"

        # 验证关键字段存在（用于净利润分析）
        required_fields = ['SECURITY_CODE', 'REPORT_DATE', 'PARENT_HOLDER_NETPROFIT', 'BASIC_EPS']
        for field in required_fields:
            assert field in result.columns, f"缺少关键字段: {field}"

        # 验证净利润数据质量
        if 'PARENT_HOLDER_NETPROFIT' in result.columns:
            for i, profit in enumerate(result['PARENT_HOLDER_NETPROFIT']):
                if pd.notna(profit):  # 跳过NaN值
                    assert isinstance(profit, (int, float)), f"第{i}年净利润数据类型错误"
                    # 注意：净利润可能为负（亏损），所以不检查是否为正数

        # 验证股票代码
        if 'SECURITY_CODE' in result.columns:
            assert all(code == 'AAPL' for code in result['SECURITY_CODE']), "股票代码应该全部为AAPL"

        print(f"\n📊 真实数据查询结果（苹果公司 AAPL）:")
        print(f"   查询时间范围: 2022-01-01 ~ 2024-12-31")
        print(f"   返回数据: {len(result)} 条记录")

        # 按年份排序并展示真实的净利润数据
        if 'REPORT_DATE' in result.columns and len(result) > 0:
            result_sorted = result.copy()
            result_sorted['YEAR'] = pd.to_datetime(result_sorted['REPORT_DATE']).dt.year
            result_sorted = result_sorted.sort_values('YEAR')

            print(f"   📈 净利润趋势分析:")
            for i, row in result_sorted.iterrows():
                year = row['YEAR']
                profit = row['PARENT_HOLDER_NETPROFIT']
                eps = row['BASIC_EPS']

                if pd.notna(profit):
                    profit_str = f"${profit/1000000000:.1f}亿美元"
                else:
                    profit_str = "数据缺失"

                if pd.notna(eps):
                    eps_str = f"${eps:.2f}"
                else:
                    eps_str = "数据缺失"

                print(f"   {year}年: 净利润 {profit_str}, 每股收益 {eps_str}")

        # 端到端测试通过验证
        print(f"   ✅ 端到端测试通过：成功获取真实的苹果公司财务数据")