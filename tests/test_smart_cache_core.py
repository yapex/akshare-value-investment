"""
Smart Cache 核心功能测试
TDD测试驱动开发
"""

import pytest
import time
from unittest.mock import Mock, patch
from akshare_value_investment.smart_cache import (
    CacheResult, SmartCache, smart_cache, CacheConfig, KeyGenerator
)


class TestCacheResult:
    """测试 CacheResult 类"""

    def test_cache_result_creation(self):
        """测试 CacheResult 创建"""
        data = {"key": "value"}
        cache_result = CacheResult(data, cache_hit=True, cache_key="test_key")

        assert cache_result.data == data
        assert cache_result.cache_hit is True
        assert cache_result.cache_key == "test_key"
        assert cache_result.timestamp > 0

    def test_cache_result_miss(self):
        """测试缓存未命中情况"""
        data = {"key": "value"}
        cache_result = CacheResult(data, cache_hit=False, cache_key="test_key")

        assert cache_result.data == data
        assert cache_result.cache_hit is False
        assert cache_result.cache_key == "test_key"


class TestKeyGenerator:
    """测试缓存键生成器"""

    def test_generate_cache_key_with_method(self):
        """测试方法调用生成缓存键"""
        args = (self, "param1", "param2")  # self会被过滤
        kwargs = {"opt1": "value1", "opt2": "value2"}

        cache_key = KeyGenerator.generate_cache_key(
            prefix="test",
            func_name="test_func",
            args=args,
            kwargs=kwargs
        )

        assert cache_key.startswith("test_test_func_")
        assert len(cache_key) == len("test_test_func_") + 16  # 16位MD5哈希

    def test_generate_cache_key_without_self(self):
        """测试无self参数生成缓存键"""
        args = ("param1", "param2")
        kwargs = {"opt1": "value1"}

        cache_key = KeyGenerator.generate_cache_key(
            prefix="test",
            func_name="test_func",
            args=args,
            kwargs=kwargs
        )

        assert cache_key.startswith("test_test_func_")

    def test_generate_cache_key_stability(self):
        """测试相同参数生成相同缓存键"""
        args = (self, "param1")
        kwargs = {"opt1": "value1"}

        key1 = KeyGenerator.generate_cache_key("test", "test_func", args, kwargs)
        key2 = KeyGenerator.generate_cache_key("test", "test_func", args, kwargs)

        assert key1 == key2

    def test_generate_cache_key_uniqueness(self):
        """测试不同参数生成不同缓存键"""
        args1 = (self, "param1")
        args2 = (self, "param2")

        key1 = KeyGenerator.generate_cache_key("test", "test_func", args1, {})
        key2 = KeyGenerator.generate_cache_key("test", "test_func", args2, {})

        assert key1 != key2


class TestCacheConfig:
    """测试缓存配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = CacheConfig()

        assert config.cache_dir == "./cache_data"
        assert config.default_ttl == 3600
        assert config.fallback_on_error is True

    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        with patch.dict("os.environ", {
            "CACHE_DIR": "/tmp/cache",
            "CACHE_TTL": "7200",
            "CACHE_FALLBACK_ON_ERROR": "false"
        }):
            config = CacheConfig()

            assert config.cache_dir == "/tmp/cache"
            assert config.default_ttl == 7200
            assert config.fallback_on_error is False


class TestSmartCache:
    """测试智能缓存装饰器"""

    @pytest.fixture
    def mock_adapter(self):
        """模拟缓存适配器"""
        adapter = Mock()
        adapter.get.return_value = None
        adapter.set.return_value = True
        return adapter

    def test_smart_cache_creation(self, mock_adapter):
        """测试装饰器创建"""
        with patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter', return_value=mock_adapter):
            smart_cache = SmartCache(prefix="test", ttl=60)

            assert smart_cache.prefix == "test"
            assert smart_cache.ttl == 60

    @patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter')
    def test_cache_miss_scenario(self, mock_adapter_class):
        """测试缓存未命中场景"""
        # 设置模拟适配器
        mock_adapter = Mock()
        mock_adapter.get.return_value = None  # 缓存未命中
        mock_adapter.set.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # 创建装饰器
        smart_cache = SmartCache(prefix="test", ttl=60)

        # 模拟函数
        def test_func(x):
            return x * 2

        decorated_func = smart_cache(test_func)

        # 执行装饰函数（应该缓存未命中）
        result = decorated_func(5)

        # 验证结果
        assert isinstance(result, CacheResult)
        assert result.data == 10
        assert result.cache_hit is False
        assert result.cache_key is not None

        # 验证缓存操作
        mock_adapter.get.assert_called_once()
        mock_adapter.set.assert_called_once()

    @patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter')
    def test_cache_hit_scenario(self, mock_adapter_class):
        """测试缓存命中场景"""
        # 设置模拟适配器
        mock_adapter = Mock()
        cached_data = {"result": "cached"}
        mock_adapter.get.return_value = cached_data  # 缓存命中
        mock_adapter_class.return_value = mock_adapter

        # 创建装饰器
        smart_cache = SmartCache(prefix="test", ttl=60)

        # 模拟函数
        def test_func(x):
            return x * 2

        decorated_func = smart_cache(test_func)

        # 执行装饰函数（应该缓存命中）
        result = decorated_func(5)

        # 验证结果
        assert isinstance(result, CacheResult)
        assert result.data == cached_data
        assert result.cache_hit is True
        assert result.cache_key is not None

        # 验证缓存操作
        mock_adapter.get.assert_called_once()
        mock_adapter.set.assert_not_called()  # 缓存命中时不应调用set

    @patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter')
    def test_cache_fallback_on_error(self, mock_adapter_class):
        """测试缓存错误时的降级策略"""
        # 设置模拟适配器 - get抛出异常
        mock_adapter = Mock()
        mock_adapter.get.side_effect = Exception("Cache error")
        mock_adapter.set.side_effect = Exception("Cache error")
        mock_adapter_class.return_value = mock_adapter

        # 创建启用降级的装饰器
        config = CacheConfig()
        config.fallback_on_error = True

        smart_cache = SmartCache(prefix="test", config=config)

        # 模拟函数
        def test_func(x):
            return x * 2

        decorated_func = smart_cache(test_func)

        # 执行装饰函数（应该降级执行原函数）
        result = decorated_func(5)

        # 验证降级结果
        assert isinstance(result, CacheResult)
        assert result.data == 10
        assert result.cache_hit is False
        assert result.cache_key is None


class TestSmartCacheDecorator:
    """测试装饰器工厂函数"""

    @patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter')
    def test_decorator_function(self, mock_adapter_class):
        """测试装饰器函数"""
        mock_adapter = Mock()
        mock_adapter.get.return_value = None
        mock_adapter.set.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # 使用装饰器
        @smart_cache("test_prefix", ttl=60)
        def test_function(x):
            return x * 2

        result = test_function(5)

        # 验证装饰器生效
        assert isinstance(result, CacheResult)
        assert result.data == 10

    @patch('akshare_value_investment.smart_cache.core.cache.DiskCacheAdapter')
    def test_decorator_with_no_args(self, mock_adapter_class):
        """测试无参数装饰器"""
        mock_adapter = Mock()
        mock_adapter.get.return_value = None
        mock_adapter.set.return_value = True
        mock_adapter_class.return_value = mock_adapter

        # 使用默认参数装饰器
        @smart_cache()
        def test_function(x):
            return x * 2

        result = test_function(5)

        # 验证装饰器生效
        assert isinstance(result, CacheResult)
        assert result.data == 10
        assert result.cache_key.startswith("default_test_function_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])