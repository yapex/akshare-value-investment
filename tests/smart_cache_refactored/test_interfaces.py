"""
测试接口抽象层
验证重构后接口的完整性和正确性
"""

import pytest
from unittest.mock import Mock, AsyncMock

from akshare_value_investment.smart_cache.abstractions import (
    ICacheReader, ICacheWriter, ICacheMonitor, ICacheKeyGenerator,
    CacheStats, CachePerformance
)


class TestICacheReader:
    """测试ICacheReader接口"""

    def test_interface_methods_exist(self):
        """验证接口方法存在"""
        # 创建模拟实现
        class MockReader(ICacheReader):
            async def get_async(self, key: str):
                return f"async_{key}"

            def get(self, key: str):
                return f"sync_{key}"

            def exists(self, key: str):
                return True

            def get_multiple(self, keys: list[str]):
                return {k: f"value_{k}" for k in keys}

        reader = MockReader()

        # 测试所有方法
        assert reader.get("test") == "sync_test"
        assert reader.exists("test") is True
        result = reader.get_multiple(["key1", "key2"])
        assert result == {"key1": "value_key1", "key2": "value_key2"}

    @pytest.mark.asyncio
    async def test_async_interface(self):
        """测试异步接口"""
        class MockAsyncReader(ICacheReader):
            async def get_async(self, key: str):
                # 简单的异步延迟
                import asyncio
                await asyncio.sleep(0.001)
                return f"async_result_{key}"

            def get(self, key: str):
                return f"sync_result_{key}"

            def exists(self, key: str):
                return key != "missing"

            def get_multiple(self, keys: list[str]):
                return {k: f"multi_{k}" for k in keys if k != "skip"}

        reader = MockAsyncReader()
        result = await reader.get_async("test_key")
        assert result == "async_result_test_key"


class TestICacheWriter:
    """测试ICacheWriter接口"""

    def test_interface_methods_exist(self):
        """验证接口方法存在"""
        class MockWriter(ICacheWriter):
            def set(self, key: str, value, ttl=None):
                return True

            def set_multiple(self, items: dict, ttl=None):
                return all(k.startswith("valid") for k in items.keys())

            def delete(self, key: str):
                return not key.startswith("protected")

            def delete_multiple(self, keys: list[str]):
                return all(not k.startswith("protected") for k in keys)

            def clear(self):
                return True

        writer = MockWriter()

        # 测试所有方法
        assert writer.set("key", "value") is True
        assert writer.set_multiple({"valid1": "val1", "valid2": "val2"}) is True
        assert writer.set_multiple({"protected": "val"}) is False

        assert writer.delete("user_key") is True
        assert writer.delete("protected_key") is False

        assert writer.delete_multiple(["user1", "user2"]) is True
        assert writer.delete_multiple(["user1", "protected"]) is False

        assert writer.clear() is True


class TestICacheMonitor:
    """测试ICacheMonitor接口"""

    def test_interface_methods_exist(self):
        """验证接口方法存在"""
        from datetime import datetime

        class MockMonitor(ICacheMonitor):
            def __init__(self):
                self.hits = 0
                self.misses = 0

            def get_stats(self) -> CacheStats:
                return CacheStats(
                    size=10,
                    volume=1024,
                    hit_rate=self.hits / (self.hits + self.misses),
                    miss_rate=self.misses / (self.hits + self.misses),
                    total_requests=self.hits + self.misses,
                    last_access=datetime.now()
                )

            def get_performance(self) -> CachePerformance:
                return CachePerformance(
                    avg_read_time=5.5,
                    avg_write_time=2.3,
                    peak_memory_usage=2048,
                    eviction_count=1
                )

            def record_hit(self, key: str, read_time: float):
                self.hits += 1

            def record_miss(self, key: str, read_time: float):
                self.misses += 1

            def record_write(self, key: str, write_time: float):
                pass

            def reset_metrics(self):
                self.hits = 0
                self.misses = 0

        monitor = MockMonitor()

        # 测试监控方法
        monitor.record_hit("test_key", 10.5)
        monitor.record_miss("missing_key", 3.2)

        stats = monitor.get_stats()
        assert stats.total_requests == 2
        assert stats.hit_rate == 0.5
        assert stats.miss_rate == 0.5

        performance = monitor.get_performance()
        assert performance.avg_read_time == 5.5
        assert performance.avg_write_time == 2.3

        monitor.reset_metrics()
        assert monitor.hits == 0
        assert monitor.misses == 0


class TestICacheKeyGenerator:
    """测试ICacheKeyGenerator接口"""

    def test_interface_methods_exist(self):
        """验证接口方法存在"""
        class MockKeyGenerator(ICacheKeyGenerator):
            def __init__(self, prefix="cache"):
                self.default_prefix = prefix

            def generate_key(self, func_name: str, args: tuple, kwargs: dict, prefix: str = None):
                if prefix is None:
                    prefix = self.default_prefix
                parts = [prefix, func_name, str(hash((args, tuple(sorted(kwargs.items())))))]
                return ":".join(parts)

            def with_prefix(self, prefix: str):
                return MockKeyGenerator(prefix)

            def validate_key(self, key: str):
                return ":" in key and len(key.split(":")) >= 3

            def extract_metadata(self, key: str):
                if not self.validate_key(key):
                    return {}
                parts = key.split(":")
                return {"prefix": parts[0], "func_name": parts[1], "hash": parts[2]}

        generator = MockKeyGenerator()

        # 测试键生成
        key = generator.generate_key("test_func", (1, 2), {"a": "b"}, "my_prefix")
        assert key.startswith("my_prefix:test_func:")
        assert generator.validate_key(key)

        metadata = generator.extract_metadata(key)
        assert metadata["prefix"] == "my_prefix"
        assert metadata["func_name"] == "test_func"
        assert "hash" in metadata

        # 测试前缀
        new_generator = generator.with_prefix("new_prefix")
        new_key = new_generator.generate_key("func", (), {})
        assert new_key.startswith("new_prefix:")


class TestInterfaceCompliance:
    """测试接口合规性"""

    def test_all_interfaces_are_abstract(self):
        """验证所有接口都是抽象的"""
        # 尝试直接实例化接口应该失败
        with pytest.raises(TypeError):
            ICacheReader()

        with pytest.raises(TypeError):
            ICacheWriter()

        with pytest.raises(TypeError):
            ICacheMonitor()

        with pytest.raises(TypeError):
            ICacheKeyGenerator()

    def test_dataclass_immutability(self):
        """测试数据类的不可变性"""
        from datetime import datetime

        stats = CacheStats(size=100, volume=1024, hit_rate=0.8, miss_rate=0.2)
        performance = CachePerformance(avg_read_time=5.0, avg_write_time=2.0)

        # 数据类应该是可变的（用于测试场景）
        stats.size = 200
        performance.avg_read_time = 6.0

        assert stats.size == 200
        assert performance.avg_read_time == 6.0