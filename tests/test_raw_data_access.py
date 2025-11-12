"""
原始数据访问测试案例

测试简化版本的原始数据访问功能，不进行字段映射。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from akshare_value_investment.core.models import MarketType, FinancialIndicator, QueryResult, PeriodType
from akshare_value_investment.container import create_production_service
from akshare_value_investment.core.stock_identifier import StockIdentifier


class TestRawDataAccess:
    """原始数据访问测试"""

    def setup_method(self):
        """测试前设置"""
        self.service = create_production_service()

    def test_service_creation(self):
        """测试服务创建"""
        assert self.service is not None

    def test_raw_data_access_structure(self):
        """测试原始数据访问结构"""
        # 创建模拟的原始数据
        mock_raw_data = {
            "日期": "2024-12-31",
            "摊薄每股收益(元)": 5.23,
            "净资产收益率(%)": 15.6,
            "销售毛利率(%)": 45.2,
            "资产负债率(%)": 30.1,
            "流动比率": 2.5,
            "净利润": 1000000000,
            "自定义字段1": "测试值",
            "自定义字段2": 123.45
        }

        # 创建财务指标对象
        indicator = FinancialIndicator(
            symbol="600036",
            market=MarketType.A_STOCK,
            company_name="测试公司",
            report_date="2024-12-31",
            period_type=PeriodType.ANNUAL,
            currency="CNY",
            indicators={},  # 简化版本为空
            raw_data=mock_raw_data  # 包含所有原始字段
        )

        # 验证原始数据访问
        assert indicator.raw_data == mock_raw_data
        assert indicator.raw_data["摊薄每股收益(元)"] == 5.23
        assert indicator.raw_data["净资产收益率(%)"] == 15.6
        assert indicator.raw_data["自定义字段1"] == "测试值"

        # 验证字段列表访问
        all_fields = list(indicator.raw_data.keys())
        assert len(all_fields) == len(mock_raw_data)
        assert "摊薄每股收益(元)" in all_fields
        assert "自定义字段1" in all_fields

    @patch('src.akshare_value_investment.datasource.adapters.a_stock_adapter.ak.stock_financial_abstract')
    @pytest.mark.asyncio
    async def test_a_stock_raw_data_query(self, mock_akshare):
        """测试A股原始数据查询"""
        # 基于真实DataFrame格式的模拟数据
        import pandas as pd
        mock_data = pd.DataFrame({
            '指标': ['摊薄每股收益(元)', '净资产收益率(%)', '销售毛利率(%)', '资产负债率(%)'],
            '选项': ['20241231', '20241231', '20241231', '20241231'],
            '20241231': [71.1152, 36.99, 91.18, 23.52]
        })
        mock_akshare.return_value = mock_data

        # 执行查询
        result = await self.service.query_indicators("600036")

        # 验证结果
        assert result is not None
        assert "600036" in result
        assert "摊薄每股收益" in result or "净资产收益率" in result

    @patch('src.akshare_value_investment.datasource.adapters.a_stock_adapter.ak.stock_financial_abstract')
    def test_a_stock_raw_data_query_sync(self, mock_akshare):
        """测试A股原始数据查询（同步版本）"""
        # 基于真实DataFrame格式的模拟数据
        import pandas as pd
        mock_data = pd.DataFrame({
            '指标': ['摊薄每股收益(元)', '加权每股收益(元)', '净资产收益率(%)', '销售毛利率(%)', '资产负债率(%)', '流动比率'],
            '选项': ['20241231', '20241231', '20241231', '20241231', '20241231', '20241231'],
            '20241231': [5.23, 5.15, 15.6, 45.2, 30.1, 2.5]
        })
        mock_akshare.return_value = mock_data

        # 直接使用AdapterManager的query方法（IQueryService接口）
        from src.akshare_value_investment.datasource.adapters import AdapterManager

        adapter = AdapterManager()
        query_result = adapter.query("600036")

        # 验证结果
        assert query_result.success is True
        assert len(query_result.data) > 0

        # 检查最新记录
        indicator = query_result.data[0]
        assert indicator.symbol == "600036"
        assert str(indicator.market) == str(MarketType.A_STOCK)  # 比较字符串值

        # 验证indicators包含我们mock的数据
        assert indicator.indicators is not None
        assert len(indicator.indicators) >= 6  # 应该有我们mock的6个指标

        # 验证mock数据正确传递
        assert indicator.indicators["摊薄每股收益(元)"] == 5.23
        assert indicator.indicators["加权每股收益(元)"] == 5.15
        assert indicator.indicators["净资产收益率(%)"] == 15.6
        assert indicator.indicators["销售毛利率(%)"] == 45.2
        assert indicator.indicators["资产负债率(%)"] == 30.1
        assert indicator.indicators["流动比率"] == 2.5

        # 验证raw_data也包含相同数据
        assert indicator.raw_data is not None
        assert "摊薄每股收益(元)" in indicator.raw_data
        assert indicator.raw_data["摊薄每股收益(元)"] == 5.23

    @patch('src.akshare_value_investment.datasource.adapters.hk_stock_adapter.ak.stock_financial_hk_analysis_indicator_em')
    @pytest.mark.asyncio
    async def test_hk_stock_raw_data_query(self, mock_akshare):
        """测试港股原始数据查询"""
        # 基于真实CSV格式的模拟数据（参考hk_stock_00700_financial_indicators.csv）
        mock_data = [
            {
                "REPORT_DATE": "2024-12-31 00:00:00",
                "SECURITY_CODE": "00700",
                "SECURITY_NAME_ABBR": "腾讯控股",
                "BASIC_EPS": 20.938,
                "DILUTED_EPS": 20.486,
                "BPS": 106.459538690985,
                "OPERATE_INCOME": 660257000000,
                "GROSS_PROFIT": 349246000000,
                "HOLDER_PROFIT": 194073000000,
                "GROSS_PROFIT_RATIO": 48.128371222384,
                "ROE_YEARLY": 21.77978260955,
                "ROA": 3.893716328977,
                "DEBT_ASSET_RATIO": 18.64215168644,
                "CURRENT_RATIO": 1.250110226777,
                "ROE_AVG": 11.558015044185
            }
        ]
        mock_akshare.return_value = mock_data

        # 执行查询 - 使用正确的异步方法
        result = await self.service.query_indicators("00700")

        # 验证结果
        assert result is not None
        assert "00700" in result or "腾讯控股" in result

    @patch('src.akshare_value_investment.datasource.adapters.us_stock_adapter.ak.stock_financial_us_analysis_indicator_em')
    @pytest.mark.asyncio
    async def test_us_stock_raw_data_query(self, mock_akshare):
        """测试美股原始数据查询"""
        # 基于真实CSV格式的模拟数据（参考us_stock_AAPL_financial_indicators.csv）
        mock_data = [
            {
                "SECUCODE": "AAPL.O",
                "SECURITY_CODE": "AAPL",
                "SECURITY_NAME_ABBR": "苹果",
                "REPORT_DATE": "2023-09-30 00:00:00",
                "BASIC_EPS": 6.16,
                "DILUTED_EPS": 6.13,
                "OPERATE_INCOME": 383285000000,
                "GROSS_PROFIT": 169148000000,
                "PARENT_HOLDER_NETPROFIT": 96995000000,
                "GROSS_PROFIT_RATIO": 44.1311295772,
                "NET_PROFIT_RATIO": 25.3062342643,
                "ROE_AVG": 0.162601626,
                "ROA": 1.896804487,
                "DEBT_ASSET_RATIO": 82.3740792948,
                "CURRENT_RATIO": 0.988011671759,
                "TOTAL_ASSETS_TR": 331.243956846727
            }
        ]
        mock_akshare.return_value = mock_data

        # 执行查询 - 使用正确的异步方法
        result = await self.service.query_indicators("AAPL")

        # 验证结果
        assert result is not None
        assert "AAPL" in result or "苹果" in result

    def test_field_coverage_advantage(self):
        """测试字段覆盖率优势"""
        # 模拟包含大量字段的原始数据
        comprehensive_raw_data = {
            # 基础指标
            "日期": "2024-12-31",
            "摊薄每股收益(元)": 5.23,
            "加权每股收益(元)": 5.15,
            "每股收益_调整后(元)": 5.20,
            "扣除非经常性损益后的每股收益(元)": 5.18,
            "每股净资产_调整前(元)": 35.8,
            "每股净资产_调整后(元)": 34.2,
            "每股经营性现金流(元)": 8.5,

            # 盈利能力指标
            "净资产收益率(%)": 15.6,
            "总资产利润率(%)": 8.2,
            "销售毛利率(%)": 45.2,
            "营业利润率(%)": 25.1,
            "销售净利率(%)": 20.3,

            # 偿债能力指标
            "资产负债率(%)": 30.1,
            "流动比率": 2.5,
            "速动比率": 2.1,
            "现金比率(%)": 15.2,
            "股东权益比率(%)": 69.9,

            # 运营效率指标
            "存货周转率(次)": 8.5,
            "存货周转天数(天)": 42.9,
            "应收账款周转率(次)": 12.3,
            "应收账款周转天数(天)": 29.8,
            "总资产周转率(次)": 0.8,

            # 规模指标
            "总资产(元)": 50000000000,
            "净利润": 1000000000,
            "主营业务利润": 2000000000,
            "每股资本公积金(元)": 3.2,
            "每股未分配利润(元)": 18.5,

            # 自定义和特殊字段
            "自定义财务指标1": "特殊值1",
            "自定义财务指标2": 987654321,
            "行业特殊字段": "金融行业特有数据",
            "地区调整因子": 1.05
        }

        # 创建财务指标对象
        indicator = FinancialIndicator(
            symbol="600036",
            market=MarketType.A_STOCK,
            company_name="测试公司",
            report_date="2024-12-31",
            period_type=PeriodType.ANNUAL,
            currency="CNY",
            indicators={},
            raw_data=comprehensive_raw_data
        )

        # 验证100%字段覆盖率
        assert len(indicator.raw_data) == len(comprehensive_raw_data)

        # 验证可以访问任意字段，包括自定义字段
        assert indicator.raw_data["行业特殊字段"] == "金融行业特有数据"
        assert indicator.raw_data["地区调整因子"] == 1.05

        # 验证可以获取所有字段列表
        all_fields = list(indicator.raw_data.keys())
        assert len(all_fields) >= 30  # 至少30个字段
        assert "自定义财务指标1" in all_fields
        assert "地区调整因子" in all_fields

    def test_different_market_field_names(self):
        """测试不同市场的字段名差异"""
        # 三个市场相同概念的字段名
        a_stock_data = {"摊薄每股收益(元)": 5.23, "净资产收益率(%)": 15.6}
        hk_stock_data = {"BASIC_EPS": 10.5, "ROE_YEARLY": 25.3}
        us_stock_data = {"BASIC_EPS": 15.75, "ROE_AVG": 28.4}

        # 验证不同市场使用不同的字段名
        assert "摊薄每股收益(元)" in a_stock_data
        assert "BASIC_EPS" in hk_stock_data
        assert "BASIC_EPS" in us_stock_data

        # 用户需要根据不同市场选择正确的字段名
        assert a_stock_data["摊薄每股收益(元)"] != hk_stock_data["BASIC_EPS"]
        assert hk_stock_data["BASIC_EPS"] != us_stock_data["BASIC_EPS"]

    def test_simplified_architecture_benefits(self):
        """测试简化架构的优势"""
        # 简化版本：没有字段映射限制
        # 用户可以直接访问任意原始字段

        # 模拟包含非常规字段的数据
        unusual_fields = {
            "常规字段1": "正常值",
            "2024年特殊指标": "特殊年份的数据",
            "行业自定义字段_制造业": "制造业特有数据",
            "地方特色指标_长三角": "地区特色数据",
            "临时字段_疫情期间": "特殊时期的数据",
            "实验性字段": "实验性指标"
        }

        indicator = FinancialIndicator(
            symbol="600036",
            market=MarketType.A_STOCK,
            company_name="测试公司",
            report_date="2024-12-31",
            period_type=PeriodType.ANNUAL,
            currency="CNY",
            indicators={},
            raw_data=unusual_fields
        )

        # 验证简化版本可以处理任意字段，无限制
        assert indicator.raw_data["2024年特殊指标"] == "特殊年份的数据"
        assert indicator.raw_data["行业自定义字段_制造业"] == "制造业特有数据"
        assert indicator.raw_data["临时字段_疫情期间"] == "特殊时期的数据"