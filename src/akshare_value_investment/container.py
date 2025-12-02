"""
依赖注入容器配置 - 简化版本

使用 dependency-injector 框架管理核心查询器依赖关系。
专注于数据查询器功能，移除已删除的业务层和服务层组件。
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dependency_injector import containers, providers

from .core.models import MarketType
from .core.stock_identifier import StockIdentifier

# 导入查询器架构
from .datasource.queryers.a_stock_queryers import (
    AStockIndicatorQueryer, AStockBalanceSheetQueryer,
    AStockIncomeStatementQueryer, AStockCashFlowQueryer
)
from .datasource.queryers.hk_stock_queryers import HKStockIndicatorQueryer, HKStockStatementQueryer
from .datasource.queryers.us_stock_queryers import (
    USStockIndicatorQueryer, USStockBalanceSheetQueryer,
    USStockIncomeStatementQueryer, USStockCashFlowQueryer
)


# 导入DiskCache支持
import diskcache



class ProductionContainer(containers.DeclarativeContainer):
    """生产环境容器 - 简化版本"""

    # 配置
    config = providers.Configuration()

    # 日志配置
    logger = providers.Singleton(
        logging.getLogger,
        "investment.container"
    )

    @staticmethod
    def _setup_logging():
        """设置系统日志配置 - 单日轮换"""
        # 获取根logger，让所有子logger都能使用相同的handler
        root_logger = logging.getLogger("investment")

        if not root_logger.handlers:
            # 避免重复配置
            root_logger.setLevel(logging.INFO)

            # 创建日志目录
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # 创建单日轮换文件处理器
            log_file = log_dir / "akshare_value_investment.log"
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',  # 每天午夜轮换
                interval=1,       # 每天一次
                backupCount=30,   # 保留30天的日志
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)

            # 设置轮换文件名格式
            file_handler.suffix = "%Y-%m-%d"

            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            # 添加处理器到根logger
            root_logger.addHandler(file_handler)
            root_logger.propagate = False

    def __init__(self):
        """初始化容器并设置日志"""
        super().__init__()
        self._setup_logging()

    
    # DiskCache配置
    diskcache = providers.Singleton(
        diskcache.Cache,
        ".cache/diskcache"
    )

    # 核心组件
    stock_identifier = providers.Singleton(StockIdentifier)

    # 查询器架构 - 遵循SOLID原则，注入缓存依赖
    # A股Queryers
    a_stock_indicators = providers.Singleton(AStockIndicatorQueryer, cache=diskcache)
    a_stock_balance_sheet = providers.Singleton(AStockBalanceSheetQueryer, cache=diskcache)
    a_stock_income_statement = providers.Singleton(AStockIncomeStatementQueryer, cache=diskcache)
    a_stock_cash_flow = providers.Singleton(AStockCashFlowQueryer, cache=diskcache)

    # 港股Queryers
    hk_stock_indicators = providers.Singleton(HKStockIndicatorQueryer, cache=diskcache)
    hk_stock_statement = providers.Singleton(HKStockStatementQueryer, cache=diskcache)

    # 美股Queryers
    us_stock_indicators = providers.Singleton(USStockIndicatorQueryer, cache=diskcache)
    us_stock_balance_sheet = providers.Singleton(USStockBalanceSheetQueryer, cache=diskcache)
    us_stock_income_statement = providers.Singleton(USStockIncomeStatementQueryer, cache=diskcache)
    us_stock_cash_flow = providers.Singleton(USStockCashFlowQueryer, cache=diskcache)

    

def create_container() -> ProductionContainer:
    """
    创建完整的容器实例

    Returns:
        配置好的容器实例
    """
    # 首先设置日志
    ProductionContainer._setup_logging()
    return ProductionContainer()





