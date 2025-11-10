# 项目文档

## 📚 当前版本文档

| 文档 | 描述 | 适用版本 |
|------|------|----------|
| [SIMPLIFIED_USAGE_GUIDE.md](./SIMPLIFIED_USAGE_GUIDE.md) | **简化版完整使用指南** - 100%字段覆盖，原始数据访问 | ✅ 当前版本 |

## 📜 历史文档

过时的字段映射相关文档已归档至 [`archive/`](./archive/) 目录。

## 🔗 项目文档体系

```
akshare-value-investment/
├── README.md                           # 项目总览和快速开始
├── CLAUDE.md                           # 详细架构说明（供AI使用）
├── doc/
│   ├── README.md                      # 文档索引（本文件）
│   ├── SIMPLIFIED_USAGE_GUIDE.md       # ✅ 简化版使用指南
│   └── archive/                        # 📜 历史文档归档
└── examples/
    ├── demo.py                         # 简化版演示程序
    └── README.md                       # 示例使用说明
```

## 💡 推荐阅读顺序

1. **项目入门**：项目根目录 `README.md`
2. **详细使用**：`doc/SIMPLIFIED_USAGE_GUIDE.md`
3. **运行示例**：`examples/demo.py`
4. **架构了解**：`CLAUDE.md`

## ⚠️ 重要提醒

- 当前版本**不再使用字段映射**，直接返回akshare原始数据
- 通过 `FinancialIndicator.raw_data` 访问所有原始字段
- 不同市场使用原生字段名（如A股用中文，港股/美股用英文）