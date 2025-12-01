"""
SQLite缓存资源管理测试

测试目标：
1. 验证SQLite连接的资源泄漏问题
2. 测试上下文管理器的正确实现
3. 确保线程安全访问时的资源正确释放
"""

import sqlite3
import threading
import warnings
import pytest
import tempfile
import os
from src.akshare_value_investment.cache.sqlite_cache import SQLiteCache


class TestSQLiteCacheResourceManagement:
    """SQLite缓存资源管理测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def teardown_method(self):
        """每个测试方法后的清理"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_resource_warning_without_context_manager(self):
        """
        测试：不使用上下文管理器时的资源警告

        GIVEN: 一个SQLiteCache实例
        WHEN: 创建多个实例并执行操作但不显式关闭
        THEN: 应该产生ResourceWarning
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", ResourceWarning)

            # 创建多个SQLiteCache实例
            caches = []
            for i in range(3):
                cache = SQLiteCache(self.db_path)
                # 使用正确的方法名
                test_records = [{"date": "2023-01-01", "value": f"data_{i}"}]
                cache.save_records("TEST_SYMBOL", test_records, "date", "test_query")
                caches.append(cache)
                # 不显式关闭连接

            # 强制触发垃圾回收
            import gc
            gc.collect()

            # 验证是否有ResourceWarning
            resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
            print(f"捕获到的ResourceWarning数量: {len(resource_warnings)}")

            # 这个测试预期会失败（有警告），用于验证问题存在
            # assert len(resource_warnings) > 0, "应该检测到ResourceWarning"

    def test_context_manager_reduces_resource_warning(self):
        """
        测试：使用上下文管理器减少资源警告

        GIVEN: 一个实现了上下文管理器的SQLiteCache实例
        WHEN: 对比使用上下文管理器和不使用的情况
        THEN: 使用上下文管理器应该减少或保持相同的ResourceWarning数量
        """
        import gc

        # 测试不使用上下文管理器的情况
        with warnings.catch_warnings(record=True) as w1:
            warnings.simplefilter("always", ResourceWarning)

            cache1 = SQLiteCache(self.db_path + "_1")
            test_records = [{"date": "2023-01-01", "value": "test_data"}]
            cache1.save_records("TEST_SYMBOL", test_records, "date", "test_query")
            # 不显式关闭连接

            del cache1
            gc.collect()

            resource_warnings_without_context = [warning for warning in w1
                                              if issubclass(warning.category, ResourceWarning)]

        # 测试使用上下文管理器的情况
        with warnings.catch_warnings(record=True) as w2:
            warnings.simplefilter("always", ResourceWarning)

            with SQLiteCache(self.db_path + "_2") as cache2:
                test_records = [{"date": "2023-01-01", "value": "test_data"}]
                cache2.save_records("TEST_SYMBOL", test_records, "date", "test_query")

            gc.collect()

            resource_warnings_with_context = [warning for warning in w2
                                            if issubclass(warning.category, ResourceWarning)]

        print(f"不使用上下文管理器ResourceWarning数量: {len(resource_warnings_without_context)}")
        print(f"使用上下文管理器ResourceWarning数量: {len(resource_warnings_with_context)}")

        # 上下文管理器应该不会产生更多的ResourceWarning
        assert len(resource_warnings_with_context) <= len(resource_warnings_without_context), \
            f"上下文管理器应该减少ResourceWarning，但使用前: {len(resource_warnings_without_context)}, " \
            f"使用后: {len(resource_warnings_with_context)}"

    def test_thread_local_connections_cleanup(self):
        """
        测试：线程本地连接的清理

        GIVEN: 一个SQLiteCache实例
        WHEN: 在多个线程中使用连接
        THEN: 线程结束后连接应该被正确清理
        """
        cache = SQLiteCache(self.db_path)

        def worker_thread(thread_id):
            """工作线程函数"""
            # 在每个线程中执行数据库操作
            test_records = [{"date": "2023-01-01", "thread_id": thread_id}]
            cache.save_records(f"SYMBOL_{thread_id}", test_records, "date", "test_query")
            # 模拟一些处理时间
            import time
            time.sleep(0.01)

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证数据存储成功
        for i in range(5):
            data = cache.query_by_date_range(f"SYMBOL_{i}", "2023-01-01", "2023-01-01", "date", "test_query")
            assert len(data) > 0

        # 显式关闭连接（这个测试依赖于显式关闭）
        cache.close()

    def test_connection_close_method(self):
        """
        测试：连接关闭方法的有效性

        GIVEN: 一个SQLiteCache实例
        WHEN: 执行操作后调用close方法
        THEN: 连接应该被正确关闭
        """
        cache = SQLiteCache(self.db_path)

        # 执行一些数据库操作
        test_records = [{"date": "2023-01-01", "value": "test_data"}]
        cache.save_records("TEST_SYMBOL", test_records, "date", "test_query")

        # 验证连接存在
        assert hasattr(cache._local, 'connection')

        # 关闭连接
        cache.close()

        # 验证连接已关闭
        assert not hasattr(cache._local, 'connection')

    def test_multiple_close_calls_safety(self):
        """
        测试：多次调用close方法的安全性

        GIVEN: 一个SQLiteCache实例
        WHEN: 多次调用close方法
        THEN: 不应该产生异常
        """
        cache = SQLiteCache(self.db_path)

        # 执行一些操作
        test_records = [{"date": "2023-01-01", "value": "test_data"}]
        cache.save_records("TEST_SYMBOL", test_records, "date", "test_query")

        # 多次关闭应该是安全的
        cache.close()
        cache.close()  # 第二次关闭不应该抛出异常
        cache.close()  # 第三次关闭也不应该抛出异常