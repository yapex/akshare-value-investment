# akshare-value-investment 示例代码

本目录包含 `akshare-value-investment` 系统的使用示例。

## 📁 示例文件

### `demo.py` - 简化版原始数据访问演示

展示简化版财务指标查询系统的核心功能，直接访问akshare原始数据，不进行字段映射。

#### 运行方式

```bash
# 从项目根目录运行
uv run python examples/demo.py
```

#### 演示内容

1. **跨市场数据查询**
   - A股：招商银行 (600036)
   - 港股：腾讯控股 (00700)
   - 美股：苹果 (AAPL)

2. **原始数据访问**
   - 100%字段覆盖率展示
   - 直接通过`raw_data`访问所有原始字段
   - 不同市场的字段名差异对比

3. **性能统计**
   - 查询耗时统计
   - 字段数量统计
   - 数据质量分析

#### 预期输出

```
🚀 财务指标查询系统 - 简化版原始数据访问演示
================================================================================

📊 简化版原始数据访问汇总报告
================================================================================
🔍 查询统计:
   查询时间范围: 最近3年财务数据
   成功查询股票数: 3
   总原始字段数: 151 个

📈 各股票详情:
   招商银行 (600036): 记录数: 12, 原始字段数: 86
   腾讯控股 (00700): 记录数: 9, 原始字段数: 36
   苹果 (AAPL): 记录数: 26, 原始字段数: 49

💡 简化版优势:
   ✓ 用户可以访问所有akshare原始字段（151个字段）
   ✓ 没有字段映射限制，100%字段覆盖率
   ✓ 简化的架构，更易理解和维护
```

## 💡 使用建议

1. **运行前准备**
   ```bash
   # 确保已安装依赖
   uv pip install -e .

   # 或直接安装依赖
   uv pip install akshare dependency-injector
   ```

2. **网络要求**
   - 需要稳定的网络连接访问akshare数据源
   - 某些情况下可能需要代理设置

3. **数据频率**
   - akshare有API调用频率限制
   - 建议不要过于频繁地运行演示

## 🔧 自定义使用

基于示例代码，您可以：

```python
from akshare_value_investment import create_production_service

# 创建查询服务
service = create_production_service()

# 查询任意股票
result = service.query("您的股票代码")

if result.success:
    latest = result.data[0]

    # 访问所有原始字段
    all_fields = list(latest.raw_data.keys())

    # 选择需要的字段
    if "摊薄每股收益(元)" in latest.raw_data:
        eps = latest.raw_data["摊薄每股收益(元)"]
        print(f"每股收益: {eps}")
```

## 📖 更多文档

- 简化版使用指南：[doc/SIMPLIFIED_USAGE_GUIDE.md](../doc/SIMPLIFIED_USAGE_GUIDE.md)
- 核心架构文档：[doc/universal-financial-query.md](../doc/universal-financial-query.md)