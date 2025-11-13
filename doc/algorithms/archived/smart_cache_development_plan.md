# Smart Cache 开发计划

## 📋 项目背景

基于 `prototype/cache_validation/` 的成功验证，装饰器模式缓存方案已通过业务场景验证，具备以下优势：

- ✅ **业务验证通过**：年度、季度、混合数据场景100%缓存命中
- ✅ **数据一致性保证**：缓存数据与原始数据完全一致
- ✅ **智能缓存复用**：自动识别和复用相关缓存数据
- ✅ **零代码侵入**：装饰器透明实现，业务代码无修改

## 🎯 开发目标

开发生产级的 `smart_cache` 装饰器，为财务数据查询系统提供高效缓存能力。

## 📊 验证成果总结

### 业务验证结果
```python
# 验证覆盖的业务场景
✅ 年度数据缓存: 5/5 (100% 命中率)
✅ 季度数据缓存: 7/7 (100% 命中率)
✅ 混合数据缓存: 9/9 (100% 命中率)
✅ 缓存复用: 5个季度成功复用
✅ 数据一致性: 100% 一致
```

### 关键技术验证
- **缓存键生成**：基于函数参数的MD5哈希，确保唯一性
- **参数过滤**：自动过滤self参数，只保留业务参数
- **数据持久化**：使用diskcache实现SQLite后端缓存
- **缓存检测**：通过stdout捕获实现命中状态检测（测试用）

## 🏗️ 技术架构设计

### 1. 核心组件架构

```
smart_cache/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── cache.py              # 核心缓存装饰器
│   ├── key_generator.py      # 缓存键生成器
│   └── config.py            # 配置管理
├── adapters/
│   ├── __init__.py
│   ├── base.py              # 基础适配器接口
│   └── diskcache_adapter.py # diskcache适配器
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py           # 缓存指标收集
│   └── reporter.py          # 监控报告
└── utils/
    ├── __init__.py
    └── helpers.py           # 工具函数
```

### 2. 核心装饰器设计

```python
# 生产级装饰器设计
from smart_cache.core import smart_cache
from typing import Any, Dict, Optional, Tuple

class CacheResult:
    """缓存结果包装器"""
    def __init__(self, data: Any, cache_hit: bool, cache_key: str):
        self.data = data
        self.cache_hit = cache_hit
        self.cache_key = cache_key
        self.timestamp = time.time()

@smart_cache(
    prefix="financial",           # 缓存前缀
    ttl=3600,                    # 过期时间（秒）
    key_strategy="param_hash",   # 键生成策略
    enable_metrics=True          # 启用指标收集
)
def get_financial_data(self, symbol: str) -> CacheResult:
    """财务数据获取函数"""
    # 业务逻辑实现
    pass
```

### 3. 缓存键生成策略

```python
class KeyGenerator:
    """缓存键生成器"""

    @staticmethod
    def generate_param_hash(
        func_name: str,
        args: tuple,
        kwargs: dict,
        prefix: str = "default"
    ) -> str:
        """基于参数哈希生成缓存键"""
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

        return f"{prefix}_{func_name}_{param_hash}"
```

## 📋 开发任务分解

### Phase 1: 核心功能开发 (Week 1)

#### 1.1 基础装饰器实现
- [ ] `smart_cache/core/cache.py` - 核心装饰器逻辑
- [ ] `smart_cache/core/key_generator.py` - 缓存键生成器
- [ ] `smart_cache/core/config.py` - 配置管理

**关键特性**：
- 支持TTL过期时间
- 参数过滤和哈希生成
- 异常处理和降级策略

#### 1.2 适配器层实现
- [ ] `smart_cache/adapters/base.py` - 适配器接口定义
- [ ] `smart_cache/adapters/diskcache_adapter.py` - diskcache适配器

**关键特性**：
- 可插拔的存储后端
- 统一的缓存操作接口
- 连接池和资源管理

### Phase 2: 监控和指标 (Week 2)

#### 2.1 指标收集系统
- [ ] `smart_cache/monitoring/metrics.py` - 缓存指标收集
- [ ] `smart_cache/monitoring/reporter.py` - 监控报告生成

**核心指标**：
- 缓存命中率
- 平均响应时间
- 缓存大小和内存使用
- 热点key统计

#### 2.2 集成现有系统
- [ ] 集成到 `src/akshare_value_investment/adapters.py`
- [ ] 集成到 `src/akshare_value_investment/query_service.py`
- [ ] 更新依赖注入配置

### Phase 3: 优化和扩展 (Week 3)

#### 3.1 性能优化
- [ ] 缓存预热机制
- [ ] 批量缓存操作
- [ ] 异步缓存更新

#### 3.2 高级特性
- [ ] 缓存标签和批量失效
- [ ] 多级缓存策略
- [ ] 缓存压缩和序列化优化

## 🔧 技术实现要点

### 1. 缓存命中检测优化

**当前问题**：原型使用stdout捕获，不够优雅

**解决方案**：
```python
# 方案A：返回值包装（推荐）
@smart_cache("financial")
def get_data(symbol: str) -> CacheResult:
    data = fetch_data(symbol)
    return CacheResult(data, cache_hit=True, cache_key="xxx")

# 方案B：结果属性标记
@smart_cache("financial")
def get_data(symbol: str):
    data = fetch_data(symbol)
    result._cache_hit = True  # 动态添加属性
    return result
```

### 2. 配置管理

```python
# smart_cache/config.py
class CacheConfig:
    """缓存配置类"""

    def __init__(self):
        self.default_ttl = 3600
        self.cache_dir = "./cache_data"
        self.max_size = 1000
        self.eviction_policy = "least-recently-used"
        self.enable_metrics = True
        self.compression_enabled = False

    def from_env(self):
        """从环境变量加载配置"""
        self.default_ttl = int(os.getenv("CACHE_TTL", self.default_ttl))
        self.cache_dir = os.getenv("CACHE_DIR", self.cache_dir)
        return self
```

### 3. 错误处理和降级

```python
def smart_cache(prefix: str, **config):
    """智能缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 缓存逻辑
                cache_key = generate_key(prefix, func.__name__, args, kwargs)
                result = cache.get(cache_key)

                if result is not None:
                    return CacheResult(result, True, cache_key)

                # 缓存未命中，执行原函数
                data = func(*args, **kwargs)
                cache.set(cache_key, data, expire=config.get('ttl'))

                return CacheResult(data, False, cache_key)

            except Exception as e:
                # 缓存异常时的降级策略
                logger.warning(f"Cache error: {e}, executing original function")
                data = func(*args, **kwargs)
                return CacheResult(data, False, None)

        return wrapper
    return decorator
```

## 📊 性能预期

基于原型验证结果：

| 指标 | 预期值 | 说明 |
|------|--------|------|
| **缓存命中率** | >95% | 重复查询场景 |
| **响应时间提升** | 10-100x | 缓存命中 vs 原始查询 |
| **内存占用** | <100MB | 1000条财务记录 |
| **磁盘空间** | <10MB | SQLite缓存文件 |

## 🧪 测试策略

### 1. 单元测试
```python
# tests/test_smart_cache.py
class TestSmartCache:
    def test_cache_hit(self):
        """测试缓存命中"""
        pass

    def test_cache_miss(self):
        """测试缓存未命中"""
        pass

    def test_ttl_expiration(self):
        """测试TTL过期"""
        pass
```

### 2. 集成测试
```python
# tests/test_integration.py
class TestCacheIntegration:
    def test_financial_adapter_caching(self):
        """测试财务适配器缓存集成"""
        pass

    def test_query_service_caching(self):
        """测试查询服务缓存集成"""
        pass
```

### 3. 性能测试
```python
# tests/test_performance.py
class TestCachePerformance:
    def test_cache_performance_improvement(self):
        """测试缓存性能提升"""
        pass

    def test_concurrent_access(self):
        """测试并发访问"""
        pass
```

## 🚀 部署和配置

### 1. 环境配置
```bash
# .env
CACHE_DIR=/var/cache/akshare
CACHE_TTL=3600
CACHE_MAX_SIZE=10000
CACHE_ENABLE_METRICS=true
```

### 2. 依赖更新
```toml
# pyproject.toml
[tool.poetry.dependencies]
diskcache = "^5.6.0"
# 现有依赖...
```

### 3. 容器化支持
```dockerfile
# Dockerfile
ENV CACHE_DIR=/app/cache
ENV CACHE_TTL=3600
VOLUME ["/app/cache"]
```

## 📈 监控和运维

### 1. 指标监控
```python
# 缓存指标示例
cache_metrics = {
    "hit_rate": 0.95,
    "total_requests": 10000,
    "cache_size": 856,
    "avg_response_time": 0.002,
    "memory_usage": "45MB"
}
```

### 2. 健康检查
```python
def cache_health_check():
    """缓存健康检查"""
    try:
        stats = cache.stats()
        return {
            "status": "healthy",
            "cache_size": len(cache),
            "last_access": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## ✅ 验收标准

1. **功能完整性**：所有业务场景缓存正常工作
2. **性能提升**：缓存命中时响应时间提升>10倍
3. **稳定性**：7x24小时稳定运行，错误率<0.1%
4. **可观测性**：完整的监控指标和健康检查
5. **易用性**：装饰器使用简单，文档完整

## 📅 时间计划

- **Week 1**: 核心功能开发
- **Week 2**: 监控系统和集成
- **Week 3**: 性能优化和测试
- **Week 4**: 文档完善和部署

## 🎯 下一步行动

1. **创建smart_cache包结构**
2. **实现核心装饰器逻辑**
3. **集成到现有适配器系统**
4. **添加监控和指标收集**
5. **完善测试和文档**

---

*基于原型验证的成功结果，smart_cache开发计划已准备就绪，可以开始实施。*