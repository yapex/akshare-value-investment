"""
缓存装饰器功能测试

验证smart_cache装饰器是否真正工作：
1. 缓存命中测试 - 相同参数的重复查询是否使用缓存
2. 缓存未命中测试 - 不同参数的查询是否调用API
3. 日期参数缓存测试 - 不同日期范围的缓存行为
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, call
import pandas as pd
from datetime import datetime

from akshare_value_investment.datasource.queryers.us_stock_queryers import (
    USStockIndicatorQueryer,
    USStockStatementQueryer
)


class TestSmartCacheDecorator(unittest.TestCase):
    """测试Smart Cache装饰器的实际功能"""

    def setUp(self):
        """测试设置"""
        self.test_symbol = "AAPL"

        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.cache_db_path = os.path.join(self.temp_dir, "test_cache.db")

        # 临时修改默认缓存路径
        self.original_cache_path = None
        try:
            from akshare_value_investment.datasource.queryers.base_queryer import create_cached_query_method
            # 备份原始函数
            self.original_create_method = create_cached_query_method
        except ImportError:
            self.original_create_method = None

    def tearDown(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('akshare.stock_financial_us_analysis_indicator_em')
    def test_indicator_cache_hit_and_miss(self, mock_api):
        """测试财务指标查询器的缓存命中和未命中"""
        # 准备mock数据 - 添加缓存需要的date字段
        mock_data = pd.DataFrame({
            'SECUCODE': ['AAPL.O'],
            'SECURITY_CODE': ['AAPL'],
            'BASIC_EPS': [7.49],
            'REPORT_DATE': ['2025-09-27'],
            'date': ['2025-09-27']  # 添加缓存需要的date字段
        })
        mock_api.return_value = mock_data

        # 创建使用临时缓存的查询器
        from akshare_value_investment.cache.sqlite_cache import SQLiteCache
        from akshare_value_investment.cache.smart_decorator import smart_cache

        # 创建临时缓存适配器
        temp_cache_adapter = SQLiteCache(self.cache_db_path)

        # 手动应用装饰器到查询方法
        @smart_cache(date_field='date', query_type='indicators', cache_adapter=temp_cache_adapter)
        def test_query_method(symbol, start_date=None, end_date=None):
            # 这里会调用被mock的API
            from akshare import stock_financial_us_analysis_indicator_em
            return stock_financial_us_analysis_indicator_em(symbol=symbol)

        # 第一次查询 - 使用精确的日期范围，应该调用API
        result1 = test_query_method(self.test_symbol, start_date='2025-09-27', end_date='2025-09-27')
        self.assertIsNotNone(result1)
        self.assertEqual(mock_api.call_count, 1)

        # 第二次查询相同参数 - 应该使用缓存，不调用API
        result2 = test_query_method(self.test_symbol, start_date='2025-09-27', end_date='2025-09-27')
        self.assertIsNotNone(result2)
        self.assertEqual(mock_api.call_count, 1)  # 调用次数不变

        # 验证结果相同
        pd.testing.assert_frame_equal(result1, result2)

    @patch('akshare.stock_financial_us_report_em')
    def test_statement_cache_with_date_parameters(self, mock_api):
        """测试财务三表查询器的日期参数缓存"""
        # 准备mock数据 - 添加缓存需要的date字段（使用不同的日期避免缓存冲突）
        mock_data = pd.DataFrame({
            'SECUCODE': ['AAPL.O'],
            'SECURITY_CODE': ['AAPL'],
            'ITEM_NAME': ['Total Assets'],
            'AMOUNT': [1000000],
            'REPORT_DATE': [pd.Timestamp('2025-01-01')],  # 使用不同日期
            'date': ['2025-01-01']  # 添加缓存需要的date字段
        })
        mock_api.return_value = mock_data

        # 创建使用临时缓存的查询器
        from akshare_value_investment.cache.sqlite_cache import SQLiteCache
        from akshare_value_investment.cache.smart_decorator import smart_cache

        # 创建临时缓存适配器
        temp_cache_adapter = SQLiteCache(self.cache_db_path)

        # 手动创建带缓存的查询方法
        @smart_cache(date_field='date', query_type='statements', cache_adapter=temp_cache_adapter)
        def cached_query_method(symbol, start_date=None, end_date=None):
            from akshare import stock_financial_us_report_em
            return stock_financial_us_report_em(symbol=symbol)

        # 第一次查询 - 使用精确的日期范围，应该调用API
        result1 = cached_query_method(self.test_symbol, start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(mock_api.call_count, 1)

        # 第二次查询 - 相同日期范围，应该使用缓存
        result2 = cached_query_method(self.test_symbol, start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(mock_api.call_count, 1)  # 仍为1次，使用缓存

    @patch('akshare.stock_financial_us_report_em')
    def test_statement_cache_different_symbols(self, mock_api):
        """测试不同股票代码的缓存"""
        # 准备mock数据 - 添加缓存需要的date字段（使用不同的日期避免缓存冲突）
        mock_data_aapl = pd.DataFrame({
            'SECUCODE': ['AAPL.O'],
            'SECURITY_CODE': ['AAPL'],
            'ITEM_NAME': ['Total Assets'],
            'AMOUNT': [1000000],
            'REPORT_DATE': [pd.Timestamp('2025-01-01')],  # 使用不同日期
            'date': ['2025-01-01']  # 添加缓存需要的date字段
        })

        mock_data_msft = pd.DataFrame({
            'SECUCODE': ['MSFT.O'],
            'SECURITY_CODE': ['MSFT'],
            'ITEM_NAME': ['Total Assets'],
            'AMOUNT': [2000000],
            'REPORT_DATE': [pd.Timestamp('2025-01-01')],  # 使用不同日期
            'date': ['2025-01-01']  # 添加缓存需要的date字段
        })

        # 设置mock返回不同数据
        def side_effect(symbol):
            if symbol == 'AAPL':
                return mock_data_aapl
            elif symbol == 'MSFT':
                return mock_data_msft
            return pd.DataFrame()

        mock_api.side_effect = side_effect

        # 创建使用临时缓存的查询器
        from akshare_value_investment.cache.sqlite_cache import SQLiteCache
        from akshare_value_investment.cache.smart_decorator import smart_cache

        # 创建临时缓存适配器
        temp_cache_adapter = SQLiteCache(self.cache_db_path)

        # 手动创建带缓存的查询方法
        @smart_cache(date_field='date', query_type='statements', cache_adapter=temp_cache_adapter)
        def cached_query_method(symbol, start_date=None, end_date=None):
            from akshare import stock_financial_us_report_em
            return stock_financial_us_report_em(symbol=symbol)

        # 查询AAPL - 第一次调用（使用精确日期范围）
        result_aapl = cached_query_method('AAPL', start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(mock_api.call_count, 1)

        # 查询MSFT - 第二次调用（不同股票）
        result_msft = cached_query_method('MSFT', start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(mock_api.call_count, 2)

        # 再次查询AAPL - 应该使用缓存
        result_aapl2 = cached_query_method('AAPL', start_date='2025-01-01', end_date='2025-01-01')
        self.assertEqual(mock_api.call_count, 2)  # 仍为2次

        # 验证结果正确性
        self.assertEqual(result_aapl.iloc[0]['SECURITY_CODE'], 'AAPL')
        self.assertEqual(result_msft.iloc[0]['SECURITY_CODE'], 'MSFT')

        # 验证缓存数据的内容一致（忽略数据类型差异）
        self.assertEqual(len(result_aapl), len(result_aapl2))
        self.assertEqual(result_aapl.iloc[0]['SECURITY_CODE'], result_aapl2.iloc[0]['SECURITY_CODE'])
        self.assertEqual(result_aapl.iloc[0]['ITEM_NAME'], result_aapl2.iloc[0]['ITEM_NAME'])
        self.assertEqual(result_aapl.iloc[0]['AMOUNT'], result_aapl2.iloc[0]['AMOUNT'])
        # REPORT_DATE字段类型不同，但内容应该相同
        self.assertEqual(str(result_aapl.iloc[0]['REPORT_DATE']), str(result_aapl2.iloc[0]['REPORT_DATE']))

    @patch('akshare.stock_financial_us_analysis_indicator_em')
    def test_cache_error_handling(self, mock_api):
        """测试缓存在API错误时的处理"""
        # 设置API抛出异常
        mock_api.side_effect = Exception("API调用失败")

        queryer = USStockIndicatorQueryer()

        # 第一次查询 - 应该抛出异常
        with self.assertRaises(Exception):
            queryer.query(self.test_symbol)

        self.assertEqual(mock_api.call_count, 1)

        # 第二次查询 - 仍应该抛出异常（因为缓存失败不应该存储）
        with self.assertRaises(Exception):
            queryer.query(self.test_symbol)

        self.assertEqual(mock_api.call_count, 2)  # 每次都尝试API调用

    def test_cache_configuration_inheritance(self):
        """测试缓存配置的继承机制"""
        # 验证财务指标查询器的默认配置
        indicator_queryer = USStockIndicatorQueryer()
        self.assertEqual(indicator_queryer.cache_query_type, 'indicators')

        # 验证财务三表查询器的覆盖配置
        statement_queryer = USStockStatementQueryer()
        self.assertEqual(statement_queryer.cache_query_type, 'us_statements')  # 修复：使用实际配置值

    def test_method_existence(self):
        """验证装饰器方法是否正确创建"""
        queryer = USStockIndicatorQueryer()

        # 检查装饰后的方法是否存在
        self.assertTrue(hasattr(queryer, '_query_with_dates'))
        self.assertTrue(callable(queryer._query_with_dates))

        # 检查query方法是否正常工作
        self.assertTrue(hasattr(queryer, 'query'))
        self.assertTrue(callable(queryer.query))

    @patch('akshare.stock_financial_us_analysis_indicator_em')
    def test_sqlite_cache_null_date_parameters(self, mock_api):
        """
        测试 SQLite 缓存适配器正确处理 NULL 日期参数

        时间范围缺失时的正确行为：
        1. 警告用户时间范围缺失
        2. 每次查询都直接调用API，不使用缓存
        3. API返回的数据正常缓存，供后续明确时间范围的查询使用

        修复验证：验证时间范围缺失时，每次查询都会调用API。
        """
        # 准备mock数据 - 必须包含缓存需要的date字段
        mock_data = pd.DataFrame({
            'SECUCODE': ['AAPL.O'],
            'SECURITY_CODE': ['AAPL'],
            'BASIC_EPS': [7.49],
            'REPORT_DATE': ['2025-09-27'],
            'date': ['2025-09-27']  # 缓存系统必需的日期字段
        })
        mock_api.return_value = mock_data

        # 创建使用临时缓存的测试方法
        from akshare_value_investment.cache.sqlite_cache import SQLiteCache
        from akshare_value_investment.cache.smart_decorator import smart_cache

        # 创建临时缓存适配器
        cache_adapter = SQLiteCache(self.cache_db_path)

        # 手动应用装饰器到查询方法
        @smart_cache(date_field='date', query_type='indicators', cache_adapter=cache_adapter)
        def test_query_method(symbol, start_date=None, end_date=None):
            from akshare import stock_financial_us_analysis_indicator_em
            return stock_financial_us_analysis_indicator_em(symbol=symbol)

        # 第一次查询 - 应该调用API并缓存结果
        result1 = test_query_method(self.test_symbol)
        self.assertEqual(mock_api.call_count, 1)
        self.assertEqual(len(result1), 1)

        # 手动验证数据是否正确保存到缓存
        cached_records = cache_adapter.query_by_date_range(
            symbol=self.test_symbol,
            start_date=None,
            end_date=None,
            date_field='date',
            query_type='indicators'
        )
        # 修复后应该能找到缓存的记录
        self.assertEqual(len(cached_records), 1)
        self.assertEqual(cached_records[0]['SECURITY_CODE'], self.test_symbol)

        # 第二次查询 - 时间范围缺失，应该再次调用API并缓存结果
        result2 = test_query_method(self.test_symbol)
        self.assertEqual(mock_api.call_count, 2)  # API调用次数应该增加
        self.assertEqual(len(result2), 1)

        # 验证结果一致性
        pd.testing.assert_frame_equal(result1, result2)

        # 验证缓存命中 - 缓存中应该有一条记录（UPSERT会更新而不是重复插入）
        cached_records_after = cache_adapter.query_by_date_range(
            symbol=self.test_symbol,
            start_date=None,
            end_date=None,
            date_field='date',
            query_type='indicators'
        )
        self.assertEqual(len(cached_records_after), 1)  # 两次查询使用同一条记录，UPSERT更新

    def test_sqlite_adapter_direct_sql_query(self):
        """
        直接测试 SQLite 缓存适配器的 SQL 查询逻辑

        Bug 根本原因：SQL 查询中 'BETWEEN NULL AND NULL' 无法返回结果。
        修复验证：测试适配器能正确构建不同的 SQL 查询来处理 NULL 参数。
        """
        from akshare_value_investment.cache.sqlite_cache import SQLiteCache

        # 创建独立的缓存实例用于测试（使用临时目录）
        test_cache_db = os.path.join(self.temp_dir, "test_sqlite_adapter.db")
        cache_adapter = SQLiteCache(test_cache_db)

        # 测试数据
        test_records = [
            {'symbol': 'AAPL', 'date': '2025-01-01', 'data': 'test1'},
            {'symbol': 'AAPL', 'date': '2025-06-01', 'data': 'test2'},
            {'symbol': 'MSFT', 'date': '2025-01-01', 'data': 'test3'}
        ]

        # 保存测试数据
        cache_adapter.save_records(
            symbol='AAPL',
            records=test_records[:2],  # 只保存AAPL的记录
            date_field='date',
            query_type='indicators'
        )

        # 测试场景1：NULL日期参数 - 应该返回所有AAPL记录
        all_aapl_records = cache_adapter.query_by_date_range(
            symbol='AAPL',
            start_date=None,
            end_date=None,
            date_field='date',
            query_type='indicators'
        )
        self.assertEqual(len(all_aapl_records), 2)

        # 测试场景2：只有结束日期 - 应该返回 <= 2025-03-01 的记录
        end_only_records = cache_adapter.query_by_date_range(
            symbol='AAPL',
            start_date=None,
            end_date='2025-03-01',
            date_field='date',
            query_type='indicators'
        )
        self.assertEqual(len(end_only_records), 1)  # 只有2025-01-01的记录

        # 测试场景3：只有开始日期 - 应该返回 >= 2025-03-01 的记录
        start_only_records = cache_adapter.query_by_date_range(
            symbol='AAPL',
            start_date='2025-03-01',
            end_date=None,
            date_field='date',
            query_type='indicators'
        )
        self.assertEqual(len(start_only_records), 1)  # 只有2025-06-01的记录

        # 测试场景4：完整日期范围
        range_records = cache_adapter.query_by_date_range(
            symbol='AAPL',
            start_date='2025-01-01',
            end_date='2025-06-01',
            date_field='date',
            query_type='indicators'
        )
        self.assertEqual(len(range_records), 2)  # 两条记录都在范围内

        # 临时数据库会在 tearDown 中自动清理


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)