"""
集成测试
验证重构后整个缓存系统的集成工作
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock

from akshare_value_investment.smart_cache.factories.cache_factory import CacheFactory
from akshare_value_investment.smart_cache.decorators.smart_cache_decorator import SmartCacheDecorator
from akshare_value_investment.container import ProductionContainer


class TestCacheFactoryIntegration:
    """测试缓存工厂集成"""

    def test_create_complete_cache_manager(self):
        """测试创建完整的缓存管理器"""
        # 创建持久化的临时目录
        temp_dir = tempfile.mkdtemp(prefix="cache_test_")

        try:
            # 创建缓存管理器
            cache_manager = CacheFactory.create_production_cache(
                cache_dir=temp_dir,
                max_size=1000,
                default_ttl=300
            )

            # 验证缓存管理器正常工作
            test_key = "integration_test_key"
            test_value = {"message": "hello", "data": [1, 2, 3]}

            # 设置并获取缓存
            assert cache_manager.set(test_key, test_value) is True
            result = cache_manager.get(test_key)
            assert result == test_value

            # 验证缓存命中
            cache_result = cache_manager.get_or_compute(test_key, lambda: {"new": "data"})
            assert cache_result.is_hit() is True
            assert cache_result.data == test_value

            # 验证统计信息
            stats = cache_manager.get_stats()
            assert 'hit_rate' in stats
            assert 'total_requests' in stats

        finally:
            # 清理临时目录
            import shutil
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def test_memory_cache_creation(self):
        """测试内存缓存创建"""
        memory_cache = CacheFactory.create_memory_cache(default_ttl=60)

        # 基本功能测试
        assert memory_cache.set("key", "value") is True
        assert memory_cache.get("key") == "value"

        # 验证缓存未命中
        assert memory_cache.get("nonexistent") is None

        # 清理
        if hasattr(memory_cache, '_cleanup'):
            memory_cache._cleanup()

    def test_custom_components_integration(self):
        """测试自定义组件集成"""
        from akshare_value_investment.smart_cache.abstractions import ICacheReader, ICacheWriter
        from akshare_value_investment.smart_cache.managers.cache_metrics import CacheMetrics
        from akshare_value_investment.smart_cache.core.enhanced_key_generator import EnhancedKeyGenerator

        # 创建模拟组件 - 共享数据存储
        shared_data = {}

        class MockReader(ICacheReader):
            async def get_async(self, key: str):
                return shared_data.get(key)

            def get(self, key: str):
                return shared_data.get(key)

            def exists(self, key: str):
                return key in shared_data

            def get_multiple(self, keys: list[str]):
                return {k: v for k, v in shared_data.items() if k in keys}

        class MockWriter(ICacheWriter):
            def set(self, key: str, value, ttl=None):
                shared_data[key] = value
                return True

            def set_multiple(self, items: dict, ttl=None):
                shared_data.update(items)
                return True

            def delete(self, key: str):
                return shared_data.pop(key, None) is not None

            def delete_multiple(self, keys: list[str]):
                count = 0
                for key in keys:
                    if self.delete(key):
                        count += 1
                return count > 0

            def clear(self):
                shared_data.clear()
                return True

        # 使用自定义组件创建管理器
        reader = MockReader()
        writer = MockWriter()
        monitor = CacheMetrics()
        key_generator = EnhancedKeyGenerator()

        cache_manager = CacheFactory.create_with_custom_components(
            reader=reader,
            writer=writer,
            monitor=monitor,
            key_generator=key_generator,
            default_ttl=120
        )

        # 测试功能
        cache_manager.set("test", "value")
        assert cache_manager.get("test") == "value"

        stats = cache_manager.get_stats()
        assert stats['total_requests'] >= 1


class TestSmartCacheDecoratorIntegration:
    """测试智能缓存装饰器集成"""

    def test_decorator_with_cache_manager(self):
        """测试装饰器与缓存管理器的集成"""
        cache_manager = CacheFactory.create_memory_cache()
        decorator = SmartCacheDecorator(cache_manager, prefix="decorator_test")

        # 应用装饰器
        @decorator
        def slow_function(x: int, y: int) -> int:
            """模拟慢函数"""
            import time
            time.sleep(0.01)  # 10毫秒延迟
            return x * y + 1

        # 第一次调用 - 应该计算
        result1 = slow_function(5, 10)
        assert result1 == 51

        # 第二次调用 - 应该命中缓存（返回原始数据，但性能更快）
        result2 = slow_function(5, 10)
        assert result2 == 51

        # 测试带有元数据的获取 - 第二次调用应该命中
        meta_result = decorator.get_with_metadata(slow_function, 5, 10)
        assert meta_result.data == 51
        assert meta_result.is_hit() is True

        # 不同参数 - 应该重新计算
        result3 = slow_function(3, 7)
        assert result3 == 22

        # 清理
        if hasattr(cache_manager, '_cleanup'):
            cache_manager._cleanup()

    def test_decorator_factory_pattern(self):
        """测试装饰器工厂模式"""
        cache_manager = CacheFactory.create_memory_cache()

        # 使用工厂创建装饰器
        decorator = SmartCacheDecorator(cache_manager, prefix="factory_test", ttl=600)

        @decorator
        def simple_function(x: int) -> int:
            """简单函数"""
            return x * 2

        # 测试缓存功能
        result1 = simple_function(5)
        assert result1 == 10

        result2 = simple_function(5)
        assert result2 == 10

        # 测试带有元数据的获取 - 第二次调用应该命中
        meta_result = decorator.get_with_metadata(simple_function, 5)
        assert meta_result.data == 10
        assert meta_result.is_hit() is True

        # 清理
        if hasattr(cache_manager, '_cleanup'):
            cache_manager._cleanup()


class TestDependencyInjectionIntegration:
    """测试依赖注入集成"""

    def test_container_integration(self):
        """测试容器集成"""
        container = ProductionContainer()

        # 获取缓存管理器
        cache_manager = container.cache_manager()
        assert cache_manager is not None

        # 基本功能测试
        test_key = "container_test"
        test_value = {"container": "integration"}

        cache_manager.set(test_key, test_value)
        result = cache_manager.get(test_key)
        assert result == test_value

        # 获取缓存统计
        stats = cache_manager.get_stats()
        assert isinstance(stats, dict)

    def test_decorator_from_container(self):
        """测试从容器获取装饰器"""
        from akshare_value_investment.smart_cache.decorators.smart_cache_decorator import SmartCacheDecorator

        container = ProductionContainer()

        # 获取缓存管理器和装饰器
        cache_manager = container.cache_manager()
        decorator = SmartCacheDecorator(cache_manager, prefix="container_decorator", ttl=300)
        assert decorator is not None

        # 应用装饰器
        @decorator
        def container_test_func(input_str: str) -> str:
            return f"processed_{input_str}"

        # 测试功能 - 装饰器现在返回原始数据
        result1 = container_test_func("hello")
        assert result1 == "processed_hello"

        result2 = container_test_func("hello")
        assert result2 == "processed_hello"  # 应该从缓存获取

        # 测试带有元数据的获取
        meta_result = decorator.get_with_metadata(container_test_func, "hello")
        assert meta_result.data == "processed_hello"
        assert meta_result.is_hit() is True  # 第二次调用应该命中

    def test_multiple_cache_managers_isolation(self):
        """测试多个缓存管理器隔离"""
        container = ProductionContainer()

        # 获取两个不同的缓存管理器
        cache1 = container.cache_manager()
        cache2 = CacheFactory.create_memory_cache()

        # 设置相同键不同值
        cache1.set("same_key", "value_from_cache1")
        cache2.set("same_key", "value_from_cache2")

        # 验证隔离
        assert cache1.get("same_key") == "value_from_cache1"
        assert cache2.get("same_key") == "value_from_cache2"

        # 清理
        if hasattr(cache2, '_cleanup'):
            cache2._cleanup()


class TestRealWorldScenario:
    """测试真实世界场景"""

    def test_financial_data_caching_scenario(self):
        """测试财务数据缓存场景"""
        # 创建专门的财务缓存管理器
        cache_manager = CacheFactory.create_production_cache(
            cache_dir=tempfile.mkdtemp(prefix="financial_cache_"),
            max_size=5000,
            default_ttl=3600  # 1小时
        )

        # 模拟财务数据获取函数
        def fetch_financial_data(symbol: str, year: int, quarter: int) -> dict:
            """模拟财务数据获取"""
            return {
                "symbol": symbol,
                "year": year,
                "quarter": quarter,
                "revenue": 1000000 * quarter,
                "profit": 100000 * quarter,
                "timestamp": "2025-11-12T10:00:00Z"
            }

        # 测试数据缓存
        test_cases = [
            ("AAPL", 2024, 1),
            ("AAPL", 2024, 2),
            ("MSFT", 2024, 1),
            ("GOOGL", 2024, 3)
        ]

        cached_results = []
        for symbol, year, quarter in test_cases:
            # 生成缓存键
            cache_key = cache_manager.generate_cache_key(
                fetch_financial_data.__name__,
                (symbol, year, quarter),
                {},
                "financial_data"
            )

            # 获取或计算数据
            result = cache_manager.get_or_compute(
                cache_key,
                lambda: fetch_financial_data(symbol, year, quarter),
                ttl=7200  # 2小时
            )

            cached_results.append(result)
            assert result.data["symbol"] == symbol

        # 测试缓存命中
        symbol, year, quarter = test_cases[0]
        cache_key = cache_manager.generate_cache_key(
            fetch_financial_data.__name__,
            (symbol, year, quarter),
            {},
            "financial_data"
        )

        hit_result = cache_manager.get_or_compute(
            cache_key,
            lambda: {"should": "not_execute"}
        )

        assert hit_result.is_hit() is True
        assert hit_result.data["symbol"] == symbol
        assert "should" not in hit_result.data

        # 验证统计信息
        stats = cache_manager.get_stats()
        assert stats['total_requests'] > 0

    def test_high_concurrency_scenario(self):
        """测试高并发场景"""
        import threading
        import time

        cache_manager = CacheFactory.create_memory_cache()
        results = []
        errors = []

        def worker(worker_id: int):
            """工作线程函数"""
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_item_{i}"
                    value = f"value_{worker_id}_{i}"

                    # 设置缓存
                    cache_manager.set(key, value)

                    # 获取缓存
                    result = cache_manager.get(key)
                    if result == value:
                        results.append((worker_id, i, True))
                    else:
                        results.append((worker_id, i, False))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # 创建多个线程
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)

        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()
        end_time = time.time()

        # 验证结果
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50  # 5 workers * 10 operations
        assert all(success for _, _, success in results)

        # 验证性能
        execution_time = end_time - start_time
        assert execution_time < 5.0  # 应该在5秒内完成

        # 验证缓存统计
        stats = cache_manager.get_stats()
        assert stats['total_requests'] > 0

        # 清理
        if hasattr(cache_manager, '_cleanup'):
            cache_manager._cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])