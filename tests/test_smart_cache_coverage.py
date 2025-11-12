"""
SmartCache 覆盖率补充测试
专门测试未覆盖的代码路径，提高测试覆盖率
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch

from akshare_value_investment.smart_cache import (
    CacheResult, CacheConfig, KeyGenerator, SmartCache, smart_cache,
    DiskCacheAdapter, get_cache_stats
)


class TestCacheResultCoverage:
    """测试CacheResult的未覆盖方法"""

    def test_cache_result_all_methods(self):
        """测试CacheResult的所有方法"""
        result = CacheResult(data="test_data", cache_hit=True, cache_key="test_key")

        # 测试is_hit方法
        assert result.is_hit() is True

        # 测试get_data方法
        assert result.get_data() == "test_data"

        # 测试get_cache_key方法
        assert result.get_cache_key() == "test_key"

        # 测试get_timestamp方法（应该返回时间戳）
        timestamp = result.get_timestamp()
        assert isinstance(timestamp, float)
        assert timestamp > 0

        # 测试__eq__方法 - 相等情况
        result2 = CacheResult(data="test_data", cache_hit=True, cache_key="test_key")
        assert result == result2

        # 测试__eq__方法 - 不同情况
        result3 = CacheResult(data="different_data", cache_hit=True, cache_key="test_key")
        assert result != result3

        # 测试__eq__方法 - 不同类型
        assert result != "not_a_cache_result"

        # 测试__repr__方法
        repr_str = repr(result)
        assert "CacheResult" in repr_str
        assert "str" in repr_str  # __repr__显示类型而不是具体值
        assert "True" in repr_str


class TestDiskCacheAdapterCoverage:
    """测试DiskCacheAdapter的异常处理路径"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时缓存目录
        self.temp_dir = tempfile.mkdtemp()
        self.config = CacheConfig()
        self.config.cache_dir = self.temp_dir

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_adapter_initialization_with_size_limit(self):
        """测试带有size_limit的适配器初始化"""
        self.config.max_size = 100
        adapter = DiskCacheAdapter(self.config)
        assert adapter is not None

    @patch('akshare_value_investment.smart_cache.adapters.diskcache_adapter.Cache')
    def test_adapter_init_exception_handling(self, mock_cache_class):
        """测试适配器初始化时的异常处理"""
        mock_cache_class.side_effect = Exception("Cache creation failed")

        # 应该能够处理异常而不崩溃
        with pytest.raises(Exception):
            DiskCacheAdapter(self.config)

    def test_get_method_exception_handling(self):
        """测试get方法的异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟缓存内部错误
        with patch.object(adapter._cache, 'get', side_effect=Exception("Get failed")):
            result = adapter.get("test_key")
            assert result is None

    def test_set_method_exception_handling(self):
        """测试set方法的异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟缓存内部错误
        with patch.object(adapter._cache, 'set', side_effect=Exception("Set failed")):
            result = adapter.set("test_key", "test_value")
            assert result is False

    def test_delete_method_exception_handling(self):
        """测试delete方法的异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟缓存内部错误
        with patch.object(adapter._cache, 'delete', side_effect=Exception("Delete failed")):
            result = adapter.delete("test_key")
            assert result is False

    def test_clear_method_exception_handling(self):
        """测试clear方法的异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟缓存内部错误
        with patch.object(adapter._cache, 'clear', side_effect=Exception("Clear failed")):
            result = adapter.clear()
            assert result is False

    def test_stats_method_exception_handling(self):
        """测试stats方法的异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟缓存内部错误
        with patch.object(adapter._cache, 'volume', side_effect=Exception("Stats failed")):
            stats = adapter.stats()
            assert stats == {'size': 0, 'volume': 0}

    def test_stats_method_len_exception(self):
        """测试stats方法中len()异常处理"""
        adapter = DiskCacheAdapter(self.config)

        # 模拟len()和volume()调用异常
        with patch.object(adapter._cache, '__len__', side_effect=Exception("Len failed")), \
             patch.object(adapter._cache, 'volume', side_effect=Exception("Volume failed")):
            stats = adapter.stats()
            assert stats == {'size': 0, 'volume': 0}

    def test_normal_operations_work(self):
        """测试正常操作仍然工作"""
        adapter = DiskCacheAdapter(self.config)

        # 测试设置和获取
        test_key = "coverage_test_key"
        test_value = {"coverage": "test"}

        set_result = adapter.set(test_key, test_value)
        assert set_result is True

        get_result = adapter.get(test_key)
        assert get_result == test_value

        # 测试统计
        stats = adapter.stats()
        assert 'size' in stats
        assert 'volume' in stats
        assert stats['size'] >= 1


class TestKeyGeneratorCoverage:
    """测试KeyGenerator的未覆盖代码"""

    def test_key_generator_with_prefix(self):
        """测试with_prefix方法"""
        key_gen = KeyGenerator("original")
        new_key_gen = key_gen.with_prefix("new_prefix")

        assert isinstance(new_key_gen, KeyGenerator)
        assert new_key_gen.prefix == "new_prefix"

    def test_static_method_different_scenarios(self):
        """测试静态方法的不同场景"""
        # 测试无参数
        key1 = KeyGenerator.generate_cache_key("test", "func", (), {})
        key2 = KeyGenerator.generate_cache_key("test", "func", (), {})
        assert key1 == key2

        # 测试复杂参数（确保有明显差异）
        key5 = KeyGenerator.generate_cache_key("test", "func", (), {"opt1": "val1_very_long_string", "opt2": "val2"})
        key6 = KeyGenerator.generate_cache_key("test", "func", (), {"opt1": "val1_very_long_string", "opt2": "val3"})
        assert key5 != key6


class TestCacheConfigCoverage:
    """测试CacheConfig的环境变量加载"""

    def test_config_loads_from_environment(self):
        """测试从环境变量加载配置"""
        with patch.dict(os.environ, {
            'CACHE_DIR': '/tmp/test_cache',
            'CACHE_MAX_SIZE': '500',
            'CACHE_TTL': '7200',
            'CACHE_ENABLE_METRICS': 'false',
            'CACHE_FALLBACK_ON_ERROR': 'false'
        }):
            config = CacheConfig()
            assert config.cache_dir == '/tmp/test_cache'
            assert config.max_size == 500
            assert config.default_ttl == 7200
            assert config.enable_metrics is False
            assert config.fallback_on_error is False


class TestSmartCacheCoverage:
    """测试SmartCache的异常处理路径"""

    def test_function_exception_without_fallback(self):
        """测试函数异常且无降级策略"""
        config = CacheConfig()
        config.fallback_on_error = False

        cache = SmartCache(config=config)

        @cache
        def failing_function():
            raise ValueError("Function failed")

        # 应该抛出异常
        with pytest.raises(ValueError, match="Function failed"):
            failing_function()

    def test_function_exception_with_fallback(self):
        """测试函数异常且有降级策略"""
        config = CacheConfig()
        config.fallback_on_error = True

        cache = SmartCache(config=config)

        @cache
        def failing_function():
            raise ValueError("Function failed")

        # 应该降级执行函数（但还是会失败）
        with pytest.raises(ValueError, match="Function failed"):
            failing_function()


class TestGetCacheStatsCoverage:
    """测试get_cache_stats函数的异常处理"""

    @patch('akshare_value_investment.smart_cache.CacheConfig')
    @patch('akshare_value_investment.smart_cache.DiskCacheAdapter')
    def test_get_cache_stats_exception_handling(self, mock_adapter_class, mock_config_class):
        """测试get_cache_stats的异常处理"""
        mock_config_class.side_effect = Exception("Config creation failed")

        stats = get_cache_stats()
        assert stats == {'size': 0, 'volume': 0}


class TestSmartCacheInitCoverage:
    """测试smart_cache装饰器工厂函数"""

    def test_smart_cache_decorator_with_kwargs(self):
        """测试装饰器工厂函数（不带额外参数，因为SmartCache不接受）"""
        @smart_cache("test", ttl=1800)
        def test_func(x):
            return f"result_{x}"

        result = test_func("test_arg")
        assert hasattr(result, 'data')
        assert result.data == "result_test_arg"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])