"""
Smart Cache 集成测试
验证缓存系统与财务数据查询的集成效果
"""

import time
import unittest
from unittest.mock import patch, Mock

from akshare_value_investment.datasource.adapters import AStockAdapter, HKStockAdapter, USStockAdapter
from akshare_value_investment.smart_cache import CacheResult, get_cache_stats


class TestSmartCacheIntegration(unittest.TestCase):
    """Smart Cache 集成测试类"""

    def setUp(self):
        """测试设置"""
        # 清理缓存状态
        try:
            config = __import__('akshare_value_investment.smart_cache.config', fromlist=['CacheConfig'])
            cache_config = config.CacheConfig()
            adapter = __import__('akshare_value_investment.smart_cache.adapters.diskcache_adapter', fromlist=['DiskCacheAdapter'])
            disk_adapter = adapter.DiskCacheAdapter(cache_config)
            disk_adapter.clear()
        except Exception:
            pass  # 忽略清理错误

    @patch('akshare.stock_financial_abstract')
    def test_astock_adapter_cache_integration(self, mock_akshare):
        """测试A股适配器缓存集成"""
        # 模拟akshare返回数据 - 直接返回列表格式
        mock_akshare.return_value = [
            {
                '指标': '营业收入',
                '选项': '',
                '20231231': '1000000000',
                '20221231': '900000000'
            },
            {
                '指标': '净利润',
                '选项': '',
                '20231231': '200000000',
                '20221231': '180000000'
            }
        ]

        adapter = AStockAdapter()
        symbol = "600519"

        # 第一次调用 - 缓存未命中
        start_time = time.time()
        result1 = adapter._get_a_stock_financial_data(symbol)
        first_call_time = time.time() - start_time

        # 验证第一次调用
        self.assertIsInstance(result1, list)
        self.assertGreater(len(result1), 0)
        self.assertEqual(mock_akshare.call_count, 1)

        # 第二次调用 - 缓存命中
        start_time = time.time()
        result2 = adapter._get_a_stock_financial_data(symbol)
        second_call_time = time.time() - start_time

        # 验证第二次调用
        self.assertEqual(result1, result2)  # 数据应该相同
        self.assertEqual(mock_akshare.call_count, 1)  # akshare应该只被调用一次
        self.assertLess(second_call_time, first_call_time)  # 第二次应该更快

    @patch('akshare.stock_financial_hk_analysis_indicator_em')
    def test_hkstock_adapter_cache_integration(self, mock_akshare):
        """测试港股适配器缓存集成"""
        # 模拟akshare返回数据
        mock_akshare.return_value = [
            {
                'REPORT_DATE': '2023-12-31',
                'REVENUE': '5000000000',
                'NET_PROFIT': '1000000000'
            }
        ]

        adapter = HKStockAdapter()
        symbol = "00700"

        # 第一次调用
        result1 = adapter._get_hk_stock_financial_data(symbol)
        self.assertEqual(mock_akshare.call_count, 1)

        # 第二次调用（应该命中缓存）
        result2 = adapter._get_hk_stock_financial_data(symbol)
        self.assertEqual(result1, result2)
        self.assertEqual(mock_akshare.call_count, 1)  # 应该只调用一次

    @patch('akshare.stock_financial_us_analysis_indicator_em')
    def test_usstock_adapter_cache_integration(self, mock_akshare):
        """测试美股适配器缓存集成"""
        # 模拟akshare返回数据
        mock_akshare.return_value = [
            {
                'REPORT_DATE': '2023-12-31',
                'TOTAL_REVENUE': '400000000000',
                'NET_INCOME': '100000000000'
            }
        ]

        adapter = USStockAdapter()
        symbol = "AAPL"

        # 第一次调用
        result1 = adapter._get_us_stock_financial_data(symbol)
        self.assertEqual(mock_akshare.call_count, 1)

        # 第二次调用（应该命中缓存）
        result2 = adapter._get_us_stock_financial_data(symbol)
        self.assertEqual(result1, result2)
        self.assertEqual(mock_akshare.call_count, 1)  # 应该只调用一次

    def test_cache_stats_functionality(self):
        """测试缓存统计功能"""
        # 获取初始统计
        initial_stats = get_cache_stats()
        self.assertIsInstance(initial_stats, dict)
        self.assertIn('size', initial_stats)
        self.assertIn('volume', initial_stats)

        # 模拟一些缓存操作后的统计
        with patch('akshare.stock_financial_abstract') as mock_akshare:
            mock_akshare.return_value = [{'指标': '测试', '20231231': '100'}]

            adapter = AStockAdapter()
            adapter._get_a_stock_financial_data("000001")

            # 再次获取统计
            final_stats = get_cache_stats()
            self.assertGreaterEqual(final_stats['size'], initial_stats['size'])

    def test_cache_key_differentiation(self):
        """测试不同参数生成不同缓存键"""
        with patch('akshare.stock_financial_abstract') as mock_akshare:
            mock_akshare.return_value = [{'指标': '测试', '20231231': '100'}]

            adapter = AStockAdapter()

            # 查询不同股票
            adapter._get_a_stock_financial_data("000001")
            adapter._get_a_stock_financial_data("000002")
            adapter._get_a_stock_financial_data("600519")

            # 验证每个不同的股票代码都会调用akshare
            self.assertEqual(mock_akshare.call_count, 3)

            # 重复查询第一个股票（应该命中缓存）
            adapter._get_a_stock_financial_data("000001")
            self.assertEqual(mock_akshare.call_count, 3)  # 调用次数不应该增加


if __name__ == '__main__':
    unittest.main()