"""
有效字段发现服务

通过查询代表性股票，获取各市场数据源的所有可用字段，
为FastAPI字段发现功能提供基础数据支持。

接口设计:
- A股: 4个细粒度接口 (指标 + 三表分别独立)
- 港股: 2个细粒度接口 (指标 + 基本面分别独立)
- 美股: 4个细粒度接口 (指标 + 三表分别独立)

代表股票:
- A股: 贵州茅台 (SH600519)
- 港股: 腾讯 (00700)
- 美股: 伯克希尔 (BRK_A)
"""

import logging
from typing import List

from ..core.models import MarketType


class FieldDiscoveryService:
    """
    有效字段发现服务

    通过查询代表性股票的真实数据，发现各市场数据源中所有可用的字段。
    为后续的字段映射和学习机制提供准确的字段候选列表。
    """

    def __init__(self, container):
        """
        初始化字段发现服务

        Args:
            container: 依赖注入容器实例
        """
        self.container = container
        self.logger = logging.getLogger(__name__)

        # 代表股票配置
        self.representative_stocks = {
            MarketType.A_STOCK: "SH600519",  # 贵州茅台
            MarketType.HK_STOCK: "00700",    # 腾讯
            MarketType.US_STOCK: "AAPL",     # 苹果（AKShare支持更好）
        }

        # 固定查询日期 - 2024年末，字段信息不会变更，缓存更有效
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"

    # ==================== A股细粒度接口 ====================

    def discover_a_stock_indicator_fields(self) -> List[str]:
        """
        发现A股财务指标字段

        Returns:
            A股财务指标字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.A_STOCK]
        self.logger.info(f"发现A股财务指标字段，使用股票: {symbol}")

        try:
            data = self.container.a_stock_indicators().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现A股财务指标字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"A股财务指标数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"A股财务指标字段发现失败: {e}")
            raise Exception(f"A股财务指标字段发现失败: {e}")

    def discover_a_stock_balance_sheet_fields(self) -> List[str]:
        """
        发现A股资产负债表字段

        Returns:
            A股资产负债表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.A_STOCK]
        self.logger.info(f"发现A股资产负债表字段，使用股票: {symbol}")

        try:
            data = self.container.a_stock_balance_sheet().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现A股资产负债表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"A股资产负债表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"A股资产负债表字段发现失败: {e}")
            raise Exception(f"A股资产负债表字段发现失败: {e}")

    def discover_a_stock_income_statement_fields(self) -> List[str]:
        """
        发现A股利润表字段

        Returns:
            A股利润表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.A_STOCK]
        self.logger.info(f"发现A股利润表字段，使用股票: {symbol}")

        try:
            data = self.container.a_stock_income_statement().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现A股利润表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"A股利润表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"A股利润表字段发现失败: {e}")
            raise Exception(f"A股利润表字段发现失败: {e}")

    def discover_a_stock_cash_flow_fields(self) -> List[str]:
        """
        发现A股现金流量表字段

        Returns:
            A股现金流量表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.A_STOCK]
        self.logger.info(f"发现A股现金流量表字段，使用股票: {symbol}")

        try:
            data = self.container.a_stock_cash_flow().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现A股现金流量表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"A股现金流量表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"A股现金流量表字段发现失败: {e}")
            raise Exception(f"A股现金流量表字段发现失败: {e}")

    # ==================== 港股细粒度接口 ====================

    def discover_hk_stock_indicator_fields(self) -> List[str]:
        """
        发现港股财务指标字段

        Returns:
            港股财务指标字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.HK_STOCK]
        self.logger.info(f"发现港股财务指标字段，使用股票: {symbol}")

        try:
            data = self.container.hk_stock_indicators().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现港股财务指标字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"港股财务指标数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"港股财务指标字段发现失败: {e}")
            raise Exception(f"港股财务指标字段发现失败: {e}")

    def discover_hk_stock_statement_fields(self) -> List[str]:
        """
        发现港股基本面字段

        Returns:
            港股基本面字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.HK_STOCK]
        self.logger.info(f"发现港股基本面字段，使用股票: {symbol}")

        try:
            data = self.container.hk_stock_statement().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现港股基本面字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"港股基本面数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"港股基本面字段发现失败: {e}")
            raise Exception(f"港股基本面字段发现失败: {e}")

    def discover_hk_stock_balance_sheet_fields(self) -> List[str]:
        """
        发现港股资产负债表字段

        Returns:
            港股资产负债表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.HK_STOCK]
        self.logger.info(f"发现港股资产负债表字段，使用股票: {symbol}")

        try:
            data = self.container.hk_stock_balance_sheet().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现港股资产负债表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"港股资产负债表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"港股资产负债表字段发现失败: {e}")
            raise Exception(f"港股资产负债表字段发现失败: {e}")

    def discover_hk_stock_income_statement_fields(self) -> List[str]:
        """
        发现港股利润表字段

        Returns:
            港股利润表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.HK_STOCK]
        self.logger.info(f"发现港股利润表字段，使用股票: {symbol}")

        try:
            data = self.container.hk_stock_income_statement().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现港股利润表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"港股利润表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"港股利润表字段发现失败: {e}")
            raise Exception(f"港股利润表字段发现失败: {e}")

    def discover_hk_stock_cash_flow_fields(self) -> List[str]:
        """
        发现港股现金流量表字段

        Returns:
            港股现金流量表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.HK_STOCK]
        self.logger.info(f"发现港股现金流量表字段，使用股票: {symbol}")

        try:
            data = self.container.hk_stock_cash_flow().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现港股现金流量表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"港股现金流量表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"港股现金流量表字段发现失败: {e}")
            raise Exception(f"港股现金流量表字段发现失败: {e}")

    # ==================== 美股细粒度接口 ====================

    def discover_us_stock_indicator_fields(self) -> List[str]:
        """
        发现美股财务指标字段

        Returns:
            美股财务指标字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.US_STOCK]
        self.logger.info(f"发现美股财务指标字段，使用股票: {symbol}")

        try:
            data = self.container.us_stock_indicators().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现美股财务指标字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"美股财务指标数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"美股财务指标字段发现失败: {e}")
            raise Exception(f"美股财务指标字段发现失败: {e}")

    def discover_us_stock_balance_sheet_fields(self) -> List[str]:
        """
        发现美股资产负债表字段

        Returns:
            美股资产负债表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.US_STOCK]
        self.logger.info(f"发现美股资产负债表字段，使用股票: {symbol}")

        try:
            data = self.container.us_stock_balance_sheet().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现美股资产负债表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"美股资产负债表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"美股资产负债表字段发现失败: {e}")
            raise Exception(f"美股资产负债表字段发现失败: {e}")

    def discover_us_stock_income_statement_fields(self) -> List[str]:
        """
        发现美股利润表字段

        Returns:
            美股利润表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.US_STOCK]
        self.logger.info(f"发现美股利润表字段，使用股票: {symbol}")

        try:
            data = self.container.us_stock_income_statement().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现美股利润表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"美股利润表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"美股利润表字段发现失败: {e}")
            raise Exception(f"美股利润表字段发现失败: {e}")

    def discover_us_stock_cash_flow_fields(self) -> List[str]:
        """
        发现美股现金流量表字段

        Returns:
            美股现金流量表字段列表

        Raises:
            Exception: 当查询失败时直接报错
        """
        symbol = self.representative_stocks[MarketType.US_STOCK]
        self.logger.info(f"发现美股现金流量表字段，使用股票: {symbol}")

        try:
            data = self.container.us_stock_cash_flow().query(symbol)
            if data is not None and not data.empty and len(data) > 0:
                fields = list(data.columns)
                self.logger.info(f"发现美股现金流量表字段: {len(fields)}个")
                return fields
            else:
                raise Exception(f"美股现金流量表数据为空: {symbol}")
        except Exception as e:
            self.logger.error(f"美股现金流量表字段发现失败: {e}")
            raise Exception(f"美股现金流量表字段发现失败: {e}")

    # ==================== 统一服务入口 ====================

    def discover_a_stock_all_fields(self) -> dict:
        """
        发现A股所有接口的字段

        Returns:
            A股所有接口字段字典
        """
        return {
            'indicators': self.discover_a_stock_indicator_fields(),
            'balance_sheet': self.discover_a_stock_balance_sheet_fields(),
            'income_statement': self.discover_a_stock_income_statement_fields(),
            'cash_flow': self.discover_a_stock_cash_flow_fields()
        }

    def discover_hk_stock_all_fields(self) -> dict:
        """
        发现港股所有接口的字段

        Returns:
            港股所有接口字段字典
        """
        return {
            'indicators': self.discover_hk_stock_indicator_fields(),
            'balance_sheet': self.discover_hk_stock_balance_sheet_fields(),
            'income_statement': self.discover_hk_stock_income_statement_fields(),
            'cash_flow': self.discover_hk_stock_cash_flow_fields(),
        }

    def discover_us_stock_all_fields(self) -> dict:
        """
        发现美股所有接口的字段

        Returns:
            美股所有接口字段字典
        """
        return {
            'indicators': self.discover_us_stock_indicator_fields(),
            'balance_sheet': self.discover_us_stock_balance_sheet_fields(),
            'income_statement': self.discover_us_stock_income_statement_fields(),
            'cash_flow': self.discover_us_stock_cash_flow_fields()
        }

    def discover_all_fields(self) -> dict:
        """
        发现所有市场的所有接口字段

        Returns:
            所有市场接口字段字典
        """
        self.logger.info("开始发现所有市场的接口字段...")

        all_fields = {
            'A_STOCK': self.discover_a_stock_all_fields(),
            'HK_STOCK': self.discover_hk_stock_all_fields(),
            'US_STOCK': self.discover_us_stock_all_fields()
        }

        # 统计信息
        total_markets = len(all_fields)
        total_interfaces = sum(len(market_fields) for market_fields in all_fields.values())
        total_fields = sum(
            len(field_list)
            for market_fields in all_fields.values()
            for field_list in market_fields.values()
        )

        self.logger.info(f"字段发现完成: {total_markets}个市场, {total_interfaces}个接口, {total_fields}个字段")

        return all_fields

    def print_field_summary(self) -> None:
        """打印字段发现结果摘要"""
        try:
            all_fields = self.discover_all_fields()

            print("\n" + "="*60)
            print("🔍 有效字段发现结果摘要")
            print("="*60)

            total_interfaces = 0
            total_fields = 0

            for market, interfaces in all_fields.items():
                market_interface_count = len(interfaces)
                market_field_count = sum(len(field_list) for field_list in interfaces.values())

                print(f"\n📊 {market}:")
                print(f"   接口数: {market_interface_count}")
                print(f"   字段数: {market_field_count}")

                for interface_name, field_list in interfaces.items():
                    print(f"   - {interface_name}: {len(field_list)}个字段")

                total_interfaces += market_interface_count
                total_fields += market_field_count

            print(f"\n📈 总计:")
            print(f"   市场数: {len(all_fields)}")
            print(f"   接口数: {total_interfaces}")
            print(f"   字段数: {total_fields}")
            print("="*60)

        except Exception as e:
            print(f"❌ 字段发现摘要生成失败: {e}")