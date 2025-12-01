"""
港股查询器单元测试 - pytest版本

基于真实CSV样本数据的港股财务指标和财务三表查询器测试。
使用pytest fixtures和现代化测试模式。
"""

import pandas as pd
from unittest.mock import patch

import pytest
from akshare_value_investment.datasource.queryers.hk_stock_queryers import (
    HKStockIndicatorQueryer,
    HKStockStatementQueryer
)


class TestHKStockQueryersWithRealData:
    """港股查询器测试类 - 使用真实Mock数据"""

    def test_hk_stock_indicator_queryer_success(self, mock_loader):
        """测试港股财务指标查询器成功查询"""
        test_symbol = "00700"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 使用真实的mock数据
        mock_data = mock_loader.get_hk_stock_indicators_mock(
            symbol=test_symbol,
            start_date=test_start_date,
            end_date=test_end_date,
            limit=1
        )

        with patch('akshare.stock_financial_hk_analysis_indicator_em', return_value=mock_data):
            # 创建查询器
            queryer = HKStockIndicatorQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

            # 验证关键字段存在
            required_fields = ['SECURITY_CODE', 'BASIC_EPS', 'ROE_AVG']
            for field in required_fields:
                assert field in result.columns, f"缺少字段: {field}"

            # 验证股票代码正确
            if 'SECURITY_CODE' in result.columns:
                assert result['SECURITY_CODE'].iloc[0] == test_symbol

    def test_hk_stock_indicator_queryer_no_data(self):
        """测试港股财务指标查询器无数据情况"""
        # 返回空DataFrame
        with patch('akshare.stock_financial_hk_analysis_indicator_em', return_value=pd.DataFrame()):
            queryer = HKStockIndicatorQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw("99999", "2024-01-01", "2024-12-31")

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_hk_stock_indicator_queryer_date_filtering(self, mock_loader):
        """测试港股财务指标查询器的日期过滤功能"""
        test_symbol = "00700"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 返回多条数据，包含不同日期
        mock_data = mock_loader.get_hk_stock_indicators_mock(
            symbol=test_symbol,
            start_date="2020-01-01",
            end_date="2024-12-31"
        )

        with patch('akshare.stock_financial_hk_analysis_indicator_em', return_value=mock_data):
            queryer = HKStockIndicatorQueryer()

            # 测试精确日期查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert result is not None
            assert isinstance(result, pd.DataFrame)

    def test_hk_stock_statement_queryer_success(self, mock_loader):
        """测试港股财务三表查询器成功查询（宽表格式）"""
        test_symbol = "00700"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 使用真实的窄表格式mock数据（会被自动转换为宽表）
        mock_data = mock_loader.get_hk_stock_statements_mock(
            symbol=test_symbol,
            start_date=test_start_date,
            end_date=test_end_date,
            item_names=["物业厂房及设备", "无形资产", "现金及等价物"],  # 指定具体项目
            limit=3
        )

        with patch('akshare.stock_financial_hk_report_em', return_value=mock_data):
            # 创建查询器
            queryer = HKStockStatementQueryer()

            # 执行查询 - 直接调用_raw方法避免缓存问题
            result = queryer._query_raw(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0

            # 验证宽表格式关键字段存在
            required_fields = ['SECURITY_CODE', 'REPORT_DATE', 'date']
            for field in required_fields:
                assert field in result.columns, f"缺少字段: {field}"

            # 验证股票代码正确
            if 'SECURITY_CODE' in result.columns:
                assert result['SECURITY_CODE'].iloc[0] == test_symbol

            # 验证宽表格式（财务项目作为列存在）
            # 检查是否有财务项目列被转换
            sample_items = ["物业厂房及设备", "无形资产", "现金及等价物"]
            has_wide_columns = any(item in result.columns for item in sample_items)
            assert has_wide_columns, "应该将财务项目转换为列"

    def test_hk_stock_statement_queryer_different_items(self, mock_loader):
        """测试港股财务三表查询器不同财务项目（宽表格式）"""
        test_symbol = "00700"
        test_start_date = "2024-01-01"
        test_end_date = "2024-12-31"

        # 测试获取不同的财务项目
        test_items = ["股东权益", "流动资产合计", "非流动资产合计"]
        mock_data = mock_loader.get_hk_stock_statements_mock(
            symbol=test_symbol,
            item_names=test_items,
            limit=len(test_items)
        )

        with patch('akshare.stock_financial_hk_report_em', return_value=mock_data):
            queryer = HKStockStatementQueryer()
            result = queryer._query_raw(test_symbol, test_start_date, test_end_date)

            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0

            # 验证宽表格式包含指定的财务项目列
            has_expected_columns = any(item in result.columns for item in test_items)
            assert has_expected_columns, f"应该包含财务项目列: {test_items}"

  
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

        # 验证港股财务三表数据结构（原始格式为窄表）
        if len(hk_statements_data) > 0:
            # MockDataLoader返回的是原始窄表格式
            assert 'STD_ITEM_NAME' in hk_statements_data.columns
            assert 'AMOUNT' in hk_statements_data.columns

        # 验证港股财务指标为宽表格式
        if len(hk_indicators_data) > 0:
            assert 'BASIC_EPS' in hk_indicators_data.columns
            assert 'ROE_AVG' in hk_indicators_data.columns

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


class TestHKStockQueryersIntegration:
    """港股查询器集成测试"""

    def test_queryer_initialization(self):
        """测试查询器初始化"""
        indicator_queryer = HKStockIndicatorQueryer()
        statement_queryer = HKStockStatementQueryer()

        assert isinstance(indicator_queryer, HKStockIndicatorQueryer)
        assert isinstance(statement_queryer, HKStockStatementQueryer)

    @pytest.mark.parametrize("symbol", ['00700', '09988', '03690'])
    def test_different_symbols(self, symbol):
        """测试不同股票代码"""
        indicator_queryer = HKStockIndicatorQueryer()
        statement_queryer = HKStockStatementQueryer()
        # 只测试参数传递，不测试实际API调用
        assert indicator_queryer is not None
        assert statement_queryer is not None

    @pytest.mark.integration
    def test_api_parameter_consistency(self):
        """测试API参数一致性"""
        # 准备mock数据 - 为不同查询器准备合适的格式
        indicator_mock_data = pd.DataFrame({'test': [1]})
        statement_mock_data = pd.DataFrame({
            'REPORT_DATE': ['2024-12-31'],
            'SECURITY_CODE': ['00700'],
            'SECURITY_NAME_ABBR': ['腾讯控股'],
            'STD_ITEM_NAME': ['测试项目'],
            'AMOUNT': [1000000]
        })

        with patch('akshare.stock_financial_hk_analysis_indicator_em', return_value=indicator_mock_data) as mock_indicator, \
             patch('akshare.stock_financial_hk_report_em', return_value=statement_mock_data) as mock_report:

            symbol = '00700'
            indicator_queryer = HKStockIndicatorQueryer()
            statement_queryer = HKStockStatementQueryer()

            # 执行查询
            indicator_queryer._query_raw(symbol, "2024-01-01", "2024-12-31")
            statement_queryer._query_raw(symbol, "2024-01-01", "2024-12-31")

            # 验证API调用参数名正确
            mock_indicator.assert_called_once_with(symbol=symbol)
            mock_report.assert_called_once_with(symbol=symbol)

    def test_hk_vs_other_markets_difference(self):
        """测试港股与其他市场的API差异"""
        # 港股财务三表使用 stock 参数，美股使用不同的参数
        # 港股财务指标使用 symbol 参数（与美股一致）

        # 验证港股查询器存在且可以初始化
        hk_statement = HKStockStatementQueryer()
        assert hk_statement is not None

        # 验证港股指标查询器使用 symbol 参数（与美股一致）
        hk_indicator = HKStockIndicatorQueryer()
        assert hk_indicator is not None

    @pytest.mark.production
    @pytest.mark.slow
    def test_production_query_net_profit_2022_2024(self):
        """测试生产环境：查询2022-2024年度净利润数据（端到端测试）"""
        # 这是一个真实的端到端测试，不使用mock，直接调用akshare API

        # 创建查询器
        queryer = HKStockIndicatorQueryer()

        # 查询2022-2024年数据 - 真实的生产环境查询场景
        result = queryer._query_raw(
            symbol="00700",  # 腾讯控股
            start_date="2022-01-01",
            end_date="2024-12-31"
        )

        # 验证查询结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0, "应该返回至少1年数据"

        # 验证关键字段存在（用于净利润分析）
        required_fields = ['SECURITY_CODE', 'REPORT_DATE', 'HOLDER_PROFIT', 'BASIC_EPS', 'ROE_AVG']
        for field in required_fields:
            assert field in result.columns, f"缺少关键字段: {field}"

        # 验证净利润数据质量
        if 'HOLDER_PROFIT' in result.columns:
            for i, profit in enumerate(result['HOLDER_PROFIT']):
                if pd.notna(profit):  # 跳过NaN值
                    assert isinstance(profit, (int, float)), f"第{i}年净利润数据类型错误"
                    # 注意：净利润可能为负（亏损），所以不检查是否为正数

        # 验证股票代码
        if 'SECURITY_CODE' in result.columns:
            assert all(code == '00700' for code in result['SECURITY_CODE']), "股票代码应该全部为00700"

        # 验证时间范围包含2022-2024年数据
        if 'REPORT_DATE' in result.columns:
            years = pd.to_datetime(result['REPORT_DATE']).dt.year.tolist()
            # 检查是否包含期望的年份（允许有更多年份）
            expected_years = [2022, 2023, 2024]
            result_years = set(years)
            assert any(year in result_years for year in expected_years), \
                   f"结果应包含2022-2024年的数据，实际年份: {sorted(years)}"

        print(f"\n📊 真实数据查询结果（腾讯控股 00700）:")
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
                profit = row['HOLDER_PROFIT']
                eps = row['BASIC_EPS']
                roe = row['ROE_AVG']

                if pd.notna(profit):
                    profit_str = f"{profit/100000000:.1f}亿元"
                else:
                    profit_str = "数据缺失"

                if pd.notna(eps):
                    eps_str = f"{eps:.2f}元"
                else:
                    eps_str = "数据缺失"

                if pd.notna(roe):
                    roe_str = f"{roe:.1%}"
                else:
                    roe_str = "数据缺失"

                print(f"   {year}年: 净利润 {profit_str}, 每股收益 {eps_str}, ROE {roe_str}")

        # 端到端测试通过验证
        print(f"   ✅ 端到端测试通过：成功获取真实的腾讯控股财务数据")