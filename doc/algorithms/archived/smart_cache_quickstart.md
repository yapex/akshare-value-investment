# Smart Cache 快速开始指南

## 🎯 项目目标

基于成功验证的原型，开发生产级 `smart_cache` 装饰器，为财务数据查询系统提供高效缓存能力。

## 🚀 立即开始

### 1. 创建项目结构

```bash
# 在项目根目录执行
mkdir -p src/akshare_value_investment/smart_cache/{core,adapters,utils}
touch src/akshare_value_investment/smart_cache/__init__.py
touch src/akshare_value_investment/smart_cache/core/__init__.py
touch src/akshare_value_investment/smart_cache/adapters/__init__.py
touch src/akshare_value_investment/smart_cache/utils/__init__.py
```

### 2. 核心装饰器实现 (第一天)

创建 `src/akshare_value_investment/smart_cache/core/cache.py`:

```python
"""
Smart Cache 核心装饰器实现
基于原型验证，生产级缓存装饰器
"""

from functools import wraps
import hashlib
import json
import time
from typing import Any, Callable, Optional, Dict
from ..adapters.diskcache_adapter import DiskCacheAdapter
from ..config import CacheConfig

class CacheResult:
    """缓存结果包装器"""
    def __init__(self, data: Any, cache_hit: bool, cache_key: str, timestamp: float = None):
        self.data = data
        self.cache_hit = cache_hit
        self.cache_key = cache_key
        self.timestamp = timestamp or time.time()

class SmartCache:
    """智能缓存装饰器类"""

    def __init__(
        self,
        prefix: str = "default",
        ttl: Optional[int] = None,
        config: Optional[CacheConfig] = None
    ):
        self.prefix = prefix
        self.ttl = ttl
        self.config = config or CacheConfig()
        self.adapter = DiskCacheAdapter(self.config)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)

            # 尝试从缓存获取
            cached_data = self.adapter.get(cache_key)

            if cached_data is not None:
                # 缓存命中
                return CacheResult(cached_data, True, cache_key)

            # 缓存未命中，执行原函数
            try:
                result = func(*args, **kwargs)
                # 存入缓存
                self.adapter.set(cache_key, result, expire=self.ttl)
                return CacheResult(result, False, cache_key)

            except Exception as e:
                # 异常处理：降级策略
                if self.config.fallback_on_error:
                    result = func(*args, **kwargs)
                    return CacheResult(result, False, None)
                else:
                    raise

        return wrapper

    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 过滤self参数
        filtered_args = args[1:] if args and hasattr(args[0], '__class__') else args

        # 创建参数签名
        param_data = {
            'args': filtered_args,
            'kwargs': sorted(kwargs.items())
        }

        # 生成哈希
        param_hash = hashlib.md5(
            json.dumps(param_data, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()[:8]

        return f"{self.prefix}_{func_name}_{param_hash}"

def smart_cache(prefix: str = "default", ttl: Optional[int] = None, **kwargs):
    """智能缓存装饰器函数"""
    return SmartCache(prefix, ttl, **kwargs)
```

### 3. 磁盘缓存适配器 (第一天)

创建 `src/akshare_value_investment/smart_cache/adapters/diskcache_adapter.py`:

```python
"""
DiskCache 适配器实现
基于验证过的 diskcache 库
"""

from diskcache import Cache
from typing import Any, Optional
from .base import CacheAdapter

class DiskCacheAdapter(CacheAdapter):
    """DiskCache 适配器"""

    def __init__(self, config):
        self.config = config
        self._cache = Cache(
            directory=config.cache_dir,
            eviction_policy=config.eviction_policy,
            size_limit=config.max_size
        )

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            return self._cache.get(key)
        except Exception as e:
            # 日志记录错误，但不抛出异常
            print(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            return self._cache.set(key, value, expire=expire)
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            return self._cache.delete(key)
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """清空缓存"""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    def stats(self) -> dict:
        """获取缓存统计"""
        try:
            return {
                'size': len(self._cache),
                'volume': self._cache.volume()
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {'size': 0, 'volume': 0}
```

### 4. 配置管理 (第一天)

创建 `src/akshare_value_investment/smart_cache/core/config.py`:

```python
"""
Smart Cache 配置管理
"""

import os
from typing import Optional

class CacheConfig:
    """缓存配置类"""

    def __init__(self):
        # 基础配置
        self.cache_dir = "./cache_data"
        self.max_size = 1000
        self.eviction_policy = "least-recently-used"

        # 功能开关
        self.enable_metrics = True
        self.fallback_on_error = True
        self.compression_enabled = False

        # 默认TTL（秒）
        self.default_ttl = 3600  # 1小时

        # 加载环境变量配置
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        self.cache_dir = os.getenv("CACHE_DIR", self.cache_dir)
        self.max_size = int(os.getenv("CACHE_MAX_SIZE", str(self.max_size)))
        self.default_ttl = int(os.getenv("CACHE_TTL", str(self.default_ttl)))
        self.enable_metrics = os.getenv("CACHE_ENABLE_METRICS", "true").lower() == "true"
        self.fallback_on_error = os.getenv("CACHE_FALLBACK_ON_ERROR", "true").lower() == "true"
```

### 5. 基础适配器接口 (第一天)

创建 `src/akshare_value_investment/smart_cache/adapters/base.py`:

```python
"""
缓存适配器基类
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

class CacheAdapter(ABC):
    """缓存适配器基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        pass
```

### 6. 集成现有系统 (第二天)

更新 `src/akshare_value_investment/adapters.py`:

```python
# 在文件顶部添加导入
from .smart_cache import smart_cache

# 在 AStockAdapter 类中添加装饰器
class AStockAdapter(BaseMarketAdapter):
    @smart_cache("astock_financial", ttl=3600)  # 1小时缓存
    def get_financial_indicator(self, symbol: str, fields: list = None) -> FinancialIndicator:
        # 现有逻辑保持不变
        pass
```

### 7. 添加依赖 (第一天)

更新 `pyproject.toml`:

```toml
[tool.poetry.dependencies]
diskcache = "^5.6.0"
# 现有依赖保持不变
```

或者使用 uv:
```bash
uv add diskcache
```

### 8. 基础测试 (第二天)

创建 `tests/test_smart_cache.py`:

```python
"""
Smart Cache 基础测试
"""

import pytest
import time
from akshare_value_investment.smart_cache import smart_cache, CacheResult

class TestSmartCache:
    """Smart Cache 测试类"""

    def test_cache_miss_and_hit(self):
        """测试缓存未命中和命中"""
        call_count = 0

        @smart_cache("test")
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用：缓存未命中
        result1 = expensive_function(5)
        assert isinstance(result1, CacheResult)
        assert result1.data == 10
        assert not result1.cache_hit
        assert call_count == 1

        # 第二次调用：缓存命中
        result2 = expensive_function(5)
        assert isinstance(result2, CacheResult)
        assert result2.data == 10
        assert result2.cache_hit
        assert call_count == 1  # 函数只被调用一次

    def test_different_parameters(self):
        """测试不同参数使用不同缓存"""
        call_count = 0

        @smart_cache("test")
        def process_data(symbol: str, year: int) -> str:
            nonlocal call_count
            call_count += 1
            return f"{symbol}_{year}"

        # 不同参数应该产生不同缓存
        result1 = process_data("600519", 2024)
        result2 = process_data("600519", 2023)
        result3 = process_data("000858", 2024)

        assert call_count == 3  # 三次不同调用
        assert not result1.cache_hit
        assert not result2.cache_hit
        assert not result3.cache_hit

        # 重复调用应该命中缓存
        result4 = process_data("600519", 2024)
        assert result4.cache_hit
        assert call_count == 3  # 函数调用次数不变
```

### 9. 运行测试 (第二天)

```bash
# 安装依赖
uv add diskcache pytest

# 运行测试
uv run pytest tests/test_smart_cache.py -v
```

### 10. 验证集成 (第三天)

创建简单的集成测试:

```python
# examples/smart_cache_demo.py
"""
Smart Cache 集成演示
"""

from akshare_value_investment.adapters import AStockAdapter
from akshare_value_investment.smart_cache import get_cache_stats

def demo_cache_integration():
    """演示缓存集成效果"""
    adapter = AStockAdapter()

    print("🚀 Smart Cache 集成演示")
    print("=" * 50)

    # 第一次查询（缓存未命中）
    print("📡 第一次查询：获取财务数据")
    result1 = adapter.get_financial_indicator("600519")
    print(f"   缓存命中: {result1.cache_hit}")
    print(f"   数据: {result1.data.symbol} 营收: {result1.data.raw_data.get('revenue', 'N/A')}")

    # 第二次查询（缓存命中）
    print("\n🎯 第二次查询：相同数据")
    result2 = adapter.get_financial_indicator("600519")
    print(f"   缓存命中: {result2.cache_hit}")
    print(f"   数据一致: {result1.data.raw_data == result2.data.raw_data}")

    # 缓存统计
    stats = get_cache_stats()
    print(f"\n📊 缓存统计: {stats}")

if __name__ == "__main__":
    demo_cache_integration()
```

## 📋 开发检查清单

### 第一天：核心功能
- [ ] 创建项目目录结构
- [ ] 实现核心装饰器 `SmartCache`
- [ ] 实现 `DiskCacheAdapter`
- [ ] 实现 `CacheConfig`
- [ ] 创建基础测试
- [ ] 添加 diskcache 依赖

### 第二天：系统集成
- [ ] 集成到 `AStockAdapter`
- [ ] 更新依赖注入配置
- [ ] 完善测试覆盖
- [ ] 创建演示代码
- [ ] 验证基础功能

### 第三天：集成和测试
- [ ] 集成到现有container配置
- [ ] 更新依赖注入
- [ ] 完善错误处理
- [ ] 集成测试
- [ ] 文档更新

### 第四天：生产准备
- [ ] 环境配置管理
- [ ] 部署配置
- [ ] 运维手册
- [ ] 发布准备

## 🎯 成功标准

### 功能标准
- ✅ 装饰器正常工作，透明缓存
- ✅ 缓存命中率 > 95%
- ✅ 数据一致性 100%
- ✅ 错误降级机制有效

### 性能标准
- ✅ 缓存命中响应时间 < 1ms
- ✅ 缓存未命中响应时间 < 原始响应时间 + 1ms
- ✅ 内存使用 < 100MB（1000条记录）
- ✅ 磁盘空间 < 50MB（1000条记录）

### 质量标准
- ✅ 单元测试覆盖率 > 90%
- ✅ 集成测试通过
- ✅ 代码审查通过
- ✅ 文档完整

## 🚨 常见问题

### Q: 如何处理缓存过期？
A: 使用 TTL 参数，`@smart_cache("prefix", ttl=3600)` 设置1小时过期。

### Q: 如何清空特定缓存？
A: 使用 `cache_adapter.delete(cache_key)` 或实现标签批量删除。

### Q: 如何监控缓存效果？
A: 通过 `cache.stats()` 获取统计信息，或集成监控指标收集。

### Q: 缓存数据不一致怎么办？
A: 检查数据序列化/反序列化，确保对象可pickle，或使用自定义序列化。

---

*基于原型验证的成功经验，按照这个快速开始指南，可以在4天内完成生产级 smart_cache 的开发。*