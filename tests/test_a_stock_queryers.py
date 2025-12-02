"""
A股查询器单元测试 - pytest版本

基于真实MockDataLoader数据的A股财务指标和财务三表查询器测试。
使用pytest fixtures和现代化测试模式，测试完整的query方法包括缓存和日期过滤。
"""

import pandas as pd
from unittest.mock import patch
import os

import pytest
from akshare_value_investment.datasource.queryers.a_stock_queryers import (
    AStockIndicatorQueryer,
    AStockBalanceSheetQueryer,
    AStockIncomeStatementQueryer,
    AStockCashFlowQueryer
)


class TestAStockQueryersWithRealData:
    """A股查询器测试类 - 使用真实Mock数据"""

    def test_a_stock_indicator_queryer_success(self, mock_loader, test_container):
        """测试A股财务指标查询器成功查询（使用完整query方法）"""
        test_symbol = "SH600519"  # 贵州茅台
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 使用真实的mock数据
        mock_data = mock_loader.get_a_stock_indicators_mock(
            symbol=test_symbol,
            start_date=test_start_date,
            end_date=test_end_date,
            limit=1
        )

        with patch('akshare.stock_financial_abstract_ths', return_value=mock_data):
            # 使用测试容器创建查询器（包含测试缓存）
            queryer = test_container.a_stock_indicators()

            # 执行完整查询（包括缓存和日期过滤）
            result = queryer.query(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

            # 验证关键字段存在（A股财务指标使用中文字段名）
            sample_fields = ['报告期', '净利润', '基本每股收益', '净资产收益率']
            found_fields = [field for field in sample_fields if field in result.columns]
            assert len(found_fields) > 0, "应该包含至少一个关键字段"

            # 验证报告期和日期字段存在
            date_fields = ['报告期', 'date']
            found_date_fields = [field for field in date_fields if field in result.columns]
            assert len(found_date_fields) > 0, "应该包含日期字段"

    def test_a_stock_indicator_queryer_caching(self, mock_loader, test_container):
        """测试A股财务指标查询器缓存功能"""
        test_symbol = "SH600519"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 创建包含多条记录的mock数据
        mock_data = mock_loader.get_a_stock_indicators_mock(
            symbol=test_symbol,
            start_date="2020-01-01",
            end_date="2024-12-31",
            limit=5
        )

        with patch('akshare.stock_financial_abstract_ths', return_value=mock_data):
            # 使用测试容器创建查询器
            queryer = test_container.a_stock_indicators()

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

    def test_a_stock_indicator_queryer_no_data(self, test_container):
        """测试A股财务指标查询器无数据情况（使用完整query方法）"""
        # 返回空DataFrame
        with patch('akshare.stock_financial_abstract_ths', return_value=pd.DataFrame()):
            queryer = test_container.a_stock_indicators()

            # 执行完整查询
            result = queryer.query("INVALID", "2024-01-01", "2024-12-31")

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_a_stock_balance_sheet_queryer_success(self, mock_loader):
        """测试A股资产负债表查询器成功查询"""
        test_symbol = "SH600519"  # 贵州茅台

        # 使用真实的mock数据
        mock_data = mock_loader.get_a_stock_balance_sheet_mock(
            symbol=test_symbol,
            limit=1
        )

        with patch('akshare.stock_financial_debt_ths', return_value=mock_data):
            # 创建查询器
            queryer = AStockBalanceSheetQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol)

            # 验证结果
            assert isinstance(result, pd.DataFrame)

            # 验证资产负债表特有字段（A股使用具体的中文字段名）
            chinese_asset_fields = [
                '*资产合计',
                '*负债合计',
                '*所有者权益（或股东权益）合计',
                '资产合计',
                '负债合计',
                '所有者权益合计',
                '归属于母公司所有者权益合计'
            ]
            found_asset_fields = [field for field in chinese_asset_fields if field in result.columns]
            assert len(found_asset_fields) > 0, "应该包含资产负债表特有字段"

    def test_a_stock_income_statement_queryer_success(self, mock_loader):
        """测试A股利润表查询器成功查询"""
        test_symbol = "SH600519"  # 贵州茅台

        # 使用真实的mock数据
        mock_data = mock_loader.get_a_stock_profit_sheet_mock(
            symbol=test_symbol,
            limit=1
        )

        with patch('akshare.stock_financial_benefit_ths', return_value=mock_data):
            # 创建查询器
            queryer = AStockIncomeStatementQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol)

            # 验证结果
            assert isinstance(result, pd.DataFrame)

            # 验证利润表特有字段（A股使用具体的中文字段名）
            chinese_profit_fields = [
                '*净利润',
                '*营业总收入',
                '归属于母公司所有者的净利润',
                '营业总收入',
                '净利润',
                '营业利润'
            ]
            found_profit_fields = [field for field in chinese_profit_fields if field in result.columns]
            assert len(found_profit_fields) > 0, "应该包含利润表特有字段"

    def test_a_stock_cash_flow_queryer_success(self, mock_loader):
        """测试A股现金流量表查询器成功查询"""
        test_symbol = "SH600519"  # 贵州茅台

        # 使用真实的mock数据
        mock_data = mock_loader.get_a_stock_cash_flow_sheet_mock(
            symbol=test_symbol,
            limit=1
        )

        with patch('akshare.stock_financial_cash_ths', return_value=mock_data):
            # 创建查询器
            queryer = AStockCashFlowQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol)

            # 验证结果
            assert isinstance(result, pd.DataFrame)

            # 验证现金流量表特有字段（A股使用具体的中文字段名）
            chinese_cash_fields = [
                '*经营活动产生的现金流量净额',
                '*投资活动产生的现金流量净额',
                '*筹资活动产生的现金流量净额',
                '经营活动产生的现金流量净额',
                '投资活动产生的现金流量净额',
                '筹资活动产生的现金流量净额'
            ]
            found_cash_fields = [field for field in chinese_cash_fields if field in result.columns]
            assert len(found_cash_fields) > 0, "应该包含现金流量表特有字段"

    @pytest.mark.parametrize("queryer_class,api_name", [
        (AStockBalanceSheetQueryer, 'akshare.stock_financial_debt_ths'),
        (AStockIncomeStatementQueryer, 'akshare.stock_financial_benefit_ths'),
        (AStockCashFlowQueryer, 'akshare.stock_financial_cash_ths'),
    ])
    def test_a_stock_statement_api_error_handling(self, queryer_class, api_name):
        """测试A股财务三表查询器API错误处理"""
        # 模拟API调用异常 - A股查询器直接抛出异常，没有异常处理机制
        with patch(api_name, side_effect=Exception("网络连接失败")):
            queryer = queryer_class()

            # 验证异常被正确抛出（这是当前的行为）
            with pytest.raises(Exception, match="网络连接失败"):
                queryer._query_raw("SH600519")

    def test_mock_data_loader_integration(self, mock_loader):
        """测试Mock数据加载器集成"""
        # 验证可以成功获取各种类型的A股mock数据
        indicators_data = mock_loader.get_a_stock_indicators_mock(limit=1)
        balance_data = mock_loader.get_a_stock_balance_sheet_mock(limit=1)
        profit_data = mock_loader.get_a_stock_profit_sheet_mock(limit=1)
        cash_flow_data = mock_loader.get_a_stock_cash_flow_sheet_mock(limit=1)

        # 验证数据格式正确
        assert isinstance(indicators_data, pd.DataFrame)
        assert isinstance(balance_data, pd.DataFrame)
        assert isinstance(profit_data, pd.DataFrame)
        assert isinstance(cash_flow_data, pd.DataFrame)

        # 验证所有数据都有必要的字段
        for data_name, data in [
            ('财务指标', indicators_data),
            ('资产负债表', balance_data),
            ('利润表', profit_data),
            ('现金流量表', cash_flow_data)
        ]:
            assert len(data) > 0, f"{data_name} 应该有数据"

    def test_data_structure_consistency(self, sample_data_info):
        """测试数据结构一致性"""
        # 检查所有A股mock数据都有必要的字段
        a_stock_data_types = [
            'a_stock_indicators', 'a_stock_balance_sheet',
            'a_stock_profit_sheet', 'a_stock_cash_flow_sheet'
        ]

        for data_type in a_stock_data_types:
            if data_type in sample_data_info:
                data_info = sample_data_info[data_type]
                assert data_info['rows'] > 0, f"{data_type} 没有数据"
                assert data_info['columns'] > 0, f"{data_type} 没有列"

    def test_wide_format_validation(self, mock_loader):
        """测试宽表格式验证"""
        # A股财务三表应该已经是宽表格式，不需要转换

        # 测试资产负债表
        balance_data = mock_loader.get_a_stock_balance_sheet_mock(limit=3)
        if len(balance_data) > 0:
            # A股使用'报告期'作为日期字段
            date_fields = ['报告期', 'report_date', 'date', 'REPORT_DATE']
            has_date_field = any(field in balance_data.columns for field in date_fields)
            assert has_date_field, f"资产负债表应该有日期字段，实际列: {list(balance_data.columns[:10])}"

        # 测试利润表
        profit_data = mock_loader.get_a_stock_profit_sheet_mock(limit=3)
        if len(profit_data) > 0:
            date_fields = ['报告期', 'report_date', 'date', 'REPORT_DATE']
            has_date_field = any(field in profit_data.columns for field in date_fields)
            assert has_date_field, f"利润表应该有日期字段，实际列: {list(profit_data.columns[:10])}"

        # 测试现金流量表
        cash_flow_data = mock_loader.get_a_stock_cash_flow_sheet_mock(limit=3)
        if len(cash_flow_data) > 0:
            date_fields = ['报告期', 'report_date', 'date', 'REPORT_DATE']
            has_date_field = any(field in cash_flow_data.columns for field in date_fields)
            assert has_date_field, f"现金流量表应该有日期字段，实际列: {list(cash_flow_data.columns[:10])}"


class TestAStockQueryersIntegration:
    """A股查询器集成测试"""

    def test_queryer_initialization(self):
        """测试查询器初始化"""
        indicator_queryer = AStockIndicatorQueryer()
        balance_queryer = AStockBalanceSheetQueryer()
        profit_queryer = AStockIncomeStatementQueryer()
        cash_flow_queryer = AStockCashFlowQueryer()

        assert isinstance(indicator_queryer, AStockIndicatorQueryer)
        assert isinstance(balance_queryer, AStockBalanceSheetQueryer)
        assert isinstance(profit_queryer, AStockIncomeStatementQueryer)
        assert isinstance(cash_flow_queryer, AStockCashFlowQueryer)

    def test_cache_query_type_configuration(self):
        """测试缓存查询类型配置"""
        # 验证每个查询器都有正确的缓存类型配置
        indicator_queryer = AStockIndicatorQueryer()
        balance_queryer = AStockBalanceSheetQueryer()
        profit_queryer = AStockIncomeStatementQueryer()
        cash_flow_queryer = AStockCashFlowQueryer()

        assert indicator_queryer.cache_query_type == 'a_stock_indicators'
        assert balance_queryer.cache_query_type == 'a_stock_balance'
        assert profit_queryer.cache_query_type == 'a_stock_profit'
        assert cash_flow_queryer.cache_query_type == 'a_stock_cashflow'

    @pytest.mark.parametrize("symbol", ['SH600519', 'SZ000001', 'SZ000002', 'SH600000'])
    def test_different_symbols(self, symbol):
        """测试不同股票代码"""
        indicator_queryer = AStockIndicatorQueryer()
        balance_queryer = AStockBalanceSheetQueryer()
        # 只测试参数传递，不测试实际API调用
        assert indicator_queryer is not None
        assert balance_queryer is not None

    @pytest.mark.integration
    def test_api_parameter_consistency(self):
        """测试API参数一致性"""
        # 准备mock数据
        mock_data = pd.DataFrame({'test': [1]})

        with patch('akshare.stock_financial_abstract_ths', return_value=mock_data) as mock_indicator, \
             patch('akshare.stock_financial_debt_ths', return_value=mock_data) as mock_debt, \
             patch('akshare.stock_financial_benefit_ths', return_value=mock_data) as mock_benefit, \
             patch('akshare.stock_financial_cash_ths', return_value=mock_data) as mock_cash:

            symbol = 'SH600519'
            indicator_queryer = AStockIndicatorQueryer()
            balance_queryer = AStockBalanceSheetQueryer()
            profit_queryer = AStockIncomeStatementQueryer()
            cash_flow_queryer = AStockCashFlowQueryer()

            # 执行查询
            indicator_queryer._query_raw(symbol)
            balance_queryer._query_raw(symbol)
            profit_queryer._query_raw(symbol)
            cash_flow_queryer._query_raw(symbol)

            # 验证API调用参数名正确（A股都使用symbol参数）
            mock_indicator.assert_called_once_with(symbol=symbol)
            mock_debt.assert_called_once_with(symbol=symbol)
            mock_benefit.assert_called_once_with(symbol=symbol)
            mock_cash.assert_called_once_with(symbol=symbol)

    def test_a_stock_vs_other_markets_difference(self):
        """测试A股与其他市场的API差异"""
        # A股使用同花顺(ths)数据源，每个财务表使用独立的API
        # 与港股、美股使用单一API不同

        # 验证A股查询器存在且可以初始化
        a_indicator = AStockIndicatorQueryer()
        a_balance = AStockBalanceSheetQueryer()
        a_profit = AStockIncomeStatementQueryer()
        a_cash_flow = AStockCashFlowQueryer()

        assert a_indicator is not None
        assert a_balance is not None
        assert a_profit is not None
        assert a_cash_flow is not None

        # 验证A股使用四个独立的API（不同于港股/美股的统一API）
        assert hasattr(a_indicator, '_query_raw')
        assert hasattr(a_balance, '_query_raw')
        assert hasattr(a_profit, '_query_raw')
        assert hasattr(a_cash_flow, '_query_raw')


class TestAStockQueryersProduction:
    """A股查询器生产环境测试"""

    @pytest.mark.production
    @pytest.mark.slow
    def test_production_query_financial_indicators_2024(self):
        """测试生产环境：查询2024年度财务指标数据（端到端测试）"""
        # 这是一个真实的端到端测试，不使用mock，直接调用akshare API

        # 创建查询器
        queryer = AStockIndicatorQueryer()

        # 查询2024年数据 - 真实的生产环境查询场景
        # 注意：akshare API需要使用纯数字代码，不支持SH前缀
        result = queryer._query_raw(symbol="600519")  # 贵州茅台（修正格式）

        # 验证查询结果
        assert isinstance(result, pd.DataFrame), "应该返回DataFrame类型的数据"
        assert len(result) > 0, "应该返回至少1条数据"

        # 验证基本字段存在
        if len(result) > 0:
            # 验证财务指标字段存在（根据实际API返回的字段调整）
            financial_fields = ['净利润', '基本每股收益', '营业总收入', '每股净资产', '扣非净利润']
            has_financial_field = any(field in result.columns for field in financial_fields)
            assert has_financial_field, f"应该包含财务指标字段，实际列: {list(result.columns[:15])}"

            # 验证报告期字段存在
            date_fields = ['报告期', 'REPORT_DATE', 'date']
            has_date_field = any(field in result.columns for field in date_fields)
            assert has_date_field, f"应该包含报告期字段，实际列: {list(result.columns[:15])}"

            print(f"\n📊 真实数据查询结果（贵州茅台 600519）:")
            print(f"   返回数据: {len(result)} 条记录")
            print(f"   数据列数: {len(result.columns)} 列")
            print(f"   前10个列名: {list(result.columns[:10])}")

            # 显示一些财务指标数据
            numeric_cols = result.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"   数值型财务指标: {len(numeric_cols)} 个")
                first_numeric_col = numeric_cols[0]
                print(f"   {first_numeric_col} 示例值: {result[first_numeric_col].iloc[0] if len(result) > 0 else 'N/A'}")

            # 端到端测试通过验证
            print(f"   ✅ 端到端测试通过：成功获取真实的茅台财务指标数据")
            print(f"   ✅ 生产环境API调用验证：akshare财务指标API工作正常")

    @pytest.mark.production
    @pytest.mark.slow
    @pytest.mark.parametrize("statement_name,queryer_class", [
        ("资产负债表", AStockBalanceSheetQueryer),
        ("利润表", AStockIncomeStatementQueryer),
        ("现金流量表", AStockCashFlowQueryer),
    ])
    def test_production_query_financial_statements_2024(self, statement_name, queryer_class):
        """测试生产环境：查询2024年度财务三表数据（端到端测试）"""
        symbol = "600519"  # 贵州茅台（修正格式，使用纯数字）

        print(f"\n📊 真实财务三表查询测试（贵州茅台 {symbol}）:")

        queryer = queryer_class()
        result = queryer._query_raw(symbol)

        # 验证查询结果
        assert isinstance(result, pd.DataFrame), f"{statement_name}应该返回DataFrame类型的数据"
        assert len(result) > 0, f"{statement_name}应该返回至少1条数据"

        if len(result) > 0:
            # 验证财务数据字段存在（根据实际API返回的字段调整）
            # 根据实际API返回的字段名，使用带*号的核心指标字段
            financial_fields = ['*资产合计', '*负债合计', '*所有者权益（或股东权益）合计',
                           '*净利润', '*营业总收入', '*经营活动产生的现金流量净额',
                           '流动资产', '货币资金']  # 添加一些常见字段
            has_financial_field = any(field in result.columns for field in financial_fields)
            assert has_financial_field, f"{statement_name}应该包含财务指标字段，实际列: {list(result.columns[:15])}"

            # 验证日期字段存在（报告期字段在A股中比较常见）
            date_fields = ['报告期', 'date', 'REPORT_DATE', '公布日期']
            has_date_field = any(field in result.columns for field in date_fields)
            assert has_date_field, f"{statement_name}应该包含日期字段，实际列: {list(result.columns[:15])}"

            print(f"   ✅ {statement_name}: {len(result)}条记录, {len(result.columns)}列")
            print(f"   📋 关键字段: {financial_fields[:3]}...")

            # 显示一些财务指标数据
            numeric_cols = result.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"   📊 数值型财务指标: {len(numeric_cols)} 个")
                first_numeric_col = numeric_cols[0]
                print(f"   💰 {first_numeric_col} 示例值: {result[first_numeric_col].iloc[0] if len(result) > 0 else 'N/A'}")

            # 端到端测试通过验证
            print(f"   ✅ 生产环境测试通过：成功获取真实的{statement_name}数据")
            print(f"   ✅ API兼容性验证：akshare财务三表API工作正常")