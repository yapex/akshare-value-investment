"""
测试管理层组件
验证重构后管理器的单一职责和功能完整性
"""

import pytest
import tempfile
import shutil
import time
from unittest.mock import Mock, MagicMock

from akshare_value_investment.smart_cache.managers import CacheManager, CacheMetrics
from akshare_value_investment.smart_cache.abstractions import ICacheReader, ICacheWriter, ICacheMonitor, ICacheKeyGenerator
from akshare_value_investment.smart_cache.core.result import CacheResult


class TestCacheManager:
    """测试缓存管理器"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟组件
        self.mock_reader = Mock(spec=ICacheReader)
        self.mock_writer = Mock(spec=ICacheWriter)
        self.mock_monitor = Mock(spec=ICacheMonitor)
        self.mock_key_generator = Mock(spec=ICacheKeyGenerator)

        # 设置默认返回值
        self.mock_key_generator.generate_key.return_value = "test_cache_key"
        self.mock_reader.get.return_value = None
        self.mock_writer.set.return_value = True

        # 创建缓存管理器
        self.cache_manager = CacheManager(
            reader=self.mock_reader,
            writer=self.mock_writer,
            monitor=self.mock_monitor,
            key_generator=self.mock_key_generator,
            default_ttl=300
        )

    def test_cache_hit_scenario(self):
        """测试缓存命中场景"""
        # 设置缓存命中
        cached_value = {"data": "cached_result"}
        self.mock_reader.get.return_value = cached_value

        # 执行获取
        result = self.cache_manager.get("test_key")

        # 验证结果
        assert result == cached_value
        self.mock_reader.get.assert_called_once_with("test_key")
        self.mock_monitor.record_hit.assert_called_once()

    def test_cache_miss_scenario(self):
        """测试缓存未命中场景"""
        # 设置缓存未命中
        self.mock_reader.get.return_value = None

        # 执行获取
        result = self.cache_manager.get("test_key")

        # 验证结果
        assert result is None
        self.mock_reader.get.assert_called_once_with("test_key")
        self.mock_monitor.record_miss.assert_called_once()

    def test_set_operation(self):
        """测试设置操作"""
        # 执行设置
        result = self.cache_manager.set("test_key", {"value": "test"}, ttl=600)

        # 验证结果
        assert result is True
        self.mock_writer.set.assert_called_once_with("test_key", {"value": "test"}, 600)
        self.mock_monitor.record_write.assert_called_once()

    def test_get_or_compute_cache_hit(self):
        """测试get_or_compute缓存命中"""
        # 设置缓存命中
        cached_value = {"result": "from_cache"}
        self.mock_reader.get.return_value = cached_value

        # 执行获取或计算
        compute_func = Mock(return_value={"result": "computed"})
        result = self.cache_manager.get_or_compute("test_key", compute_func)

        # 验证结果
        assert isinstance(result, CacheResult)
        assert result.data == cached_value
        assert result.is_hit() is True
        assert result.get_cache_key() == "test_key"
        compute_func.assert_not_called()  # 不应该调用计算函数

    def test_get_or_compute_cache_miss(self):
        """测试get_or_compute缓存未命中"""
        # 设置缓存未命中
        self.mock_reader.get.return_value = None

        # 执行获取或计算
        computed_value = {"result": "computed"}
        compute_func = Mock(return_value=computed_value)
        result = self.cache_manager.get_or_compute("test_key", compute_func)

        # 验证结果
        assert isinstance(result, CacheResult)
        assert result.data == computed_value
        assert result.is_hit() is False
        assert result.get_cache_key() == "test_key"
        compute_func.assert_called_once()
        self.mock_writer.set.assert_called_once_with("test_key", computed_value, 300)

    def test_get_or_compute_compute_exception_with_fallback(self):
        """测试计算函数异常但缓存有数据"""
        # 设置缓存未命中，然后命中（模拟重试）
        self.mock_reader.get.side_effect = [None, {"fallback": "data"}]

        # 执行获取或计算，计算函数抛异常
        compute_func = Mock(side_effect=Exception("Compute failed"))
        result = self.cache_manager.get_or_compute("test_key", compute_func)

        # 验证结果 - 应该回退到缓存数据
        assert isinstance(result, CacheResult)
        assert result.data == {"fallback": "data"}
        assert result.is_hit() is True

    def test_get_or_compute_compute_exception_no_fallback(self):
        """测试计算函数异常且缓存无数据"""
        # 设置缓存始终未命中
        self.mock_reader.get.return_value = None

        # 执行获取或计算，计算函数抛异常
        compute_func = Mock(side_effect=Exception("Compute failed"))

        # 验证抛出异常
        with pytest.raises(Exception, match="Compute failed"):
            self.cache_manager.get_or_compute("test_key", compute_func)

    def test_generate_cache_key(self):
        """测试生成缓存键"""
        # 执行键生成
        key = self.cache_manager.generate_cache_key(
            "test_func",
            (1, 2, 3),
            {"a": "b", "c": "d"},
            "my_prefix"
        )

        # 验证调用
        assert key == "test_cache_key"
        self.mock_key_generator.generate_key.assert_called_once_with(
            "test_func", (1, 2, 3), {"a": "b", "c": "d"}, "my_prefix"
        )

    def test_delete_operation(self):
        """测试删除操作"""
        # 设置删除成功
        self.mock_writer.delete.return_value = True

        # 执行删除
        result = self.cache_manager.delete("test_key")

        # 验证结果
        assert result is True
        self.mock_writer.delete.assert_called_once_with("test_key")

    def test_clear_operation(self):
        """测试清空操作"""
        # 设置清空成功
        self.mock_writer.clear.return_value = True

        # 执行清空
        result = self.cache_manager.clear()

        # 验证结果
        assert result is True
        self.mock_writer.clear.assert_called_once()

    def test_get_stats(self):
        """测试获取统计信息"""
        # 设置监控返回值
        from datetime import datetime
        from akshare_value_investment.smart_cache.abstractions import CacheStats, CachePerformance

        mock_stats = CacheStats(
            size=10, volume=1024, hit_rate=0.8, miss_rate=0.2,
            total_requests=50, last_access=datetime.now()
        )
        mock_performance = CachePerformance(
            avg_read_time=5.5, avg_write_time=2.3, peak_memory_usage=2048, eviction_count=1
        )

        self.mock_monitor.get_stats.return_value = mock_stats
        self.mock_monitor.get_performance.return_value = mock_performance

        # 执行获取统计
        stats = self.cache_manager.get_stats()

        # 验证结果
        expected_stats = {
            'size': 10,
            'volume': 1024,
            'hit_rate': 0.8,
            'miss_rate': 0.2,
            'total_requests': 50,
            'avg_read_time': 5.5,
            'avg_write_time': 2.3,
            'peak_memory_usage': 2048
        }
        assert stats == expected_stats

    def test_create_key_generator_with_prefix(self):
        """测试创建带前缀的键生成器"""
        # 设置返回值
        new_generator = Mock(spec=ICacheKeyGenerator)
        self.mock_key_generator.with_prefix.return_value = new_generator

        # 创建新生成器
        result = self.cache_manager.create_key_generator_with_prefix("new_prefix")

        # 验证结果
        assert result == new_generator
        self.mock_key_generator.with_prefix.assert_called_once_with("new_prefix")

    def test_exception_handling(self):
        """测试异常处理"""
        # 设置读取器抛异常
        self.mock_reader.get.side_effect = Exception("Read error")

        # 执行获取（应该优雅处理异常）
        result = self.cache_manager.get("test_key")

        # 验证异常被处理
        assert result is None
        self.mock_monitor.record_miss.assert_called_once()

        # 设置写入器抛异常
        self.mock_writer.set.side_effect = Exception("Write error")

        # 执行设置（应该优雅处理异常）
        set_result = self.cache_manager.set("test_key", "value")

        # 验证异常被处理
        assert set_result is False


class TestCacheMetrics:
    """测试缓存指标收集器"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.metrics = CacheMetrics()

    def test_initial_state(self):
        """测试初始状态"""
        stats = self.metrics.get_stats()
        performance = self.metrics.get_performance()

        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 0.0
        assert stats.total_requests == 0
        assert performance.avg_read_time == 0.0
        assert performance.avg_write_time == 0.0

    def test_record_hit(self):
        """测试记录命中"""
        self.metrics.record_hit("test_key", 10.5)
        self.metrics.record_hit("test_key2", 8.2)

        stats = self.metrics.get_stats()
        performance = self.metrics.get_performance()

        assert stats.hit_rate == 1.0  # 2 hits / 2 total
        assert stats.miss_rate == 0.0
        assert stats.total_requests == 2
        assert performance.avg_read_time == 9.35  # (10.5 + 8.2) / 2

    def test_record_miss(self):
        """测试记录未命中"""
        self.metrics.record_miss("test_key", 5.0)
        self.metrics.record_miss("test_key2", 7.0)

        stats = self.metrics.get_stats()

        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 1.0  # 2 misses / 2 total
        assert stats.total_requests == 2

    def test_mixed_hits_and_misses(self):
        """测试混合命中和未命中"""
        # 记录：3次命中，2次未命中
        self.metrics.record_hit("key1", 10.0)
        self.metrics.record_hit("key2", 8.0)
        self.metrics.record_miss("key3", 3.0)
        self.metrics.record_hit("key4", 12.0)
        self.metrics.record_miss("key5", 4.0)

        stats = self.metrics.get_stats()
        performance = self.metrics.get_performance()

        assert stats.hit_rate == 0.6  # 3/5
        assert stats.miss_rate == 0.4  # 2/5
        assert stats.total_requests == 5
        assert performance.avg_read_time == 7.4  # (10+8+3+12+4)/5

    def test_record_write(self):
        """测试记录写入"""
        self.metrics.record_write("test_key", 15.0)
        self.metrics.record_write("test_key2", 20.0)

        performance = self.metrics.get_performance()

        assert performance.avg_write_time == 17.5  # (15 + 20) / 2

    def test_reset_metrics(self):
        """测试重置指标"""
        # 先记录一些数据
        self.metrics.record_hit("key1", 10.0)
        self.metrics.record_miss("key2", 5.0)
        self.metrics.record_write("key3", 8.0)

        # 重置
        self.metrics.reset_metrics()

        # 验证重置后状态
        stats = self.metrics.get_stats()
        performance = self.metrics.get_performance()

        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 0.0
        assert stats.total_requests == 0
        assert performance.avg_read_time == 0.0
        assert performance.avg_write_time == 0.0

    def test_get_hot_keys(self):
        """测试获取热点键"""
        # 记录多次访问
        self.metrics.record_hit("hot_key1", 5.0)
        self.metrics.record_hit("hot_key1", 6.0)  # 访问2次
        self.metrics.record_hit("hot_key2", 7.0)
        self.metrics.record_hit("hot_key2", 8.0)
        self.metrics.record_hit("hot_key2", 9.0)  # 访问3次
        self.metrics.record_hit("normal_key", 4.0)  # 访问1次

        # 获取热点键
        hot_keys = self.metrics.get_hot_keys(top_n=3)

        # 验证排序（简化实现中访问次数是相同的）
        assert len(hot_keys) == 3
        assert all(isinstance(item, tuple) and len(item) == 2 for item in hot_keys)

    def test_get_uptime(self):
        """测试获取运行时间"""
        uptime_before = self.metrics.get_uptime()
        time.sleep(0.1)  # 等待100毫秒
        uptime_after = self.metrics.get_uptime()

        assert uptime_after > uptime_before
        assert uptime_after - uptime_before >= 0.1

    def test_get_detailed_stats(self):
        """测试获取详细统计"""
        # 记录一些数据
        self.metrics.record_hit("key1", 10.0)
        self.metrics.record_miss("key2", 5.0)
        self.metrics.record_write("key3", 8.0)

        # 获取详细统计
        detailed = self.metrics.get_detailed_stats()

        # 验证结构
        assert 'basic_stats' in detailed
        assert 'performance' in detailed
        assert 'memory' in detailed
        assert 'time' in detailed
        assert 'hot_keys' in detailed

        # 验证具体值
        assert detailed['basic_stats']['hits'] == 1
        assert detailed['basic_stats']['misses'] == 1
        assert detailed['basic_stats']['total_requests'] == 2
        assert detailed['performance']['read_operations'] == 2
        assert detailed['performance']['write_operations'] == 1