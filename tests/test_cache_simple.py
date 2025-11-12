"""
简单的缓存测试
验证SmartCache装饰器是否正常工作
"""

import time
import unittest
from unittest.mock import patch, Mock

from akshare_value_investment.smart_cache import smart_cache


class TestCacheSimple(unittest.TestCase):
    """简单缓存测试"""

    def test_decorator_basic_functionality(self):
        """测试装饰器基本功能"""
        call_count = 0

        @smart_cache("test_prefix", ttl=3600)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return f"result_{x}"

        # 第一次调用
        result1 = test_function("abc")
        self.assertEqual(result1.data, "result_abc")
        self.assertFalse(result1.cache_hit)
        self.assertEqual(call_count, 1)

        # 第二次调用相同参数
        result2 = test_function("abc")
        self.assertEqual(result2.data, "result_abc")
        self.assertTrue(result2.cache_hit)
        self.assertEqual(call_count, 1)  # 函数应该只调用一次

        # 第三次调用不同参数
        result3 = test_function("xyz")
        self.assertEqual(result3.data, "result_xyz")
        self.assertFalse(result3.cache_hit)
        self.assertEqual(call_count, 2)

    def test_cache_key_generation(self):
        """测试缓存键生成"""
        @smart_cache("key_test")
        def key_test_func(a, b, c=None):
            return f"{a}_{b}_{c}"

        # 测试不同参数生成不同缓存键
        result1 = key_test_func(1, 2, c=3)
        result2 = key_test_func(1, 2)  # 没有c参数
        result3 = key_test_func(1, 2, c=4)

        # 所有调用都应该缓存未命中（因为参数不同）
        self.assertFalse(result1.cache_hit)
        self.assertFalse(result2.cache_hit)
        self.assertFalse(result3.cache_hit)

        # 重复调用第一个应该命中
        result4 = key_test_func(1, 2, c=3)
        self.assertTrue(result4.cache_hit)


if __name__ == '__main__':
    unittest.main()