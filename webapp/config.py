"""
Webapp 配置文件

集中管理应用配置，支持环境变量覆盖
"""

import os
from pathlib import Path
from typing import Final

# ==================== 路径配置 ====================

# 项目根目录
PROJECT_ROOT: Final = Path(__file__).parent.parent

# src 目录（用于导入核心模块）
SRC_PATH: Final = PROJECT_ROOT / "src"


# ==================== API 配置 ====================

# FastAPI 服务地址
API_BASE_URL: Final = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
)

# API 超时设置（秒）
API_TIMEOUT: Final = int(os.getenv("API_TIMEOUT", "30"))


# ==================== Streamlit 配置 ====================

# 页面配置
PAGE_TITLE: Final = "股票质量分析"
PAGE_LAYOUT: Final = "wide"
INITIAL_SIDEBAR_STATE: Final = "auto"

# 默认股票代码
DEFAULT_SYMBOL: Final = os.getenv("DEFAULT_SYMBOL", "600519")


# ==================== 缓存配置 ====================

# 历史记录缓存路径
HISTORY_CACHE_PATH: Final = PROJECT_ROOT / "webapp" / ".cache" / "stock_history.json"

# 历史记录最大条数
MAX_HISTORY_RECORDS: Final = int(os.getenv("MAX_HISTORY_RECORDS", "50"))


# ==================== UI 配置 ====================

# 查询年数选项
YEARS_OPTIONS: Final = {
    "5年": 5,
    "10年": 10,
    "20年": 20,
    "全部": None
}

# 默认查询年数索引（0=5年, 1=10年, 2=20年, 3=全部）
DEFAULT_YEARS_INDEX: Final = 1

# 搜索框延迟（毫秒）
SEARCHBOX_RERUN_DELAY: Final = 200

# 搜索框默认显示数量
SEARCHBOX_DEFAULT_LIMIT: Final = 8


# ==================== 市场类型映射 ====================

from akshare_value_investment.core.models import MarketType

MARKET_TYPE_MAP: Final = {
    MarketType.A_STOCK: "A股",
    MarketType.HK_STOCK: "港股",
    MarketType.US_STOCK: "美股"
}


# ==================== 估值分析配置 ====================

# 市值输入范围（亿元）
MARKET_CAP_MIN: Final = 0.0
MARKET_CAP_MAX: Final = 100000.0
MARKET_CAP_STEP: Final = 100.0
MARKET_CAP_DEFAULT: Final = 0.0


# ==================== 开发模式配置 ====================

# 开发模式（启用时显示调试信息）
DEBUG_MODE: Final = os.getenv("DEBUG_MODE", "false").lower() == "true"

# 日志级别
LOG_LEVEL: Final = os.getenv("LOG_LEVEL", "INFO")


# ==================== 辅助函数 ====================

def get_api_endpoint(endpoint: str) -> str:
    """获取完整的 API 端点 URL

    Args:
        endpoint: API 端点路径（如 "/api/v1/financial/statements"）

    Returns:
        完整的 API URL
    """
    return f"{API_BASE_URL}{endpoint}"


def is_production() -> bool:
    """判断是否为生产环境"""
    return not DEBUG_MODE
