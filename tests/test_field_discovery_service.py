"""
FieldDiscoveryService 测试案例

测试有效字段发现服务的所有功能，使用 tests/sample_data 中的真实样本数据：
- A股4个细粒度接口字段发现
- 港股2个细粒度接口字段发现
- 美股4个细粒度接口字段发现
- 聚合字段发现方法
- 错误处理和异常情况
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import logging

from akshare_value_investment.business.field_discovery_service import FieldDiscoveryService
from akshare_value_investment.core.models import MarketType


class TestFieldDiscoveryService:
    """FieldDiscoveryService 测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建模拟容器
        self.mock_container = Mock()

        # 创建字段发现服务实例
        self.service = FieldDiscoveryService(self.mock_container)

    # ==================== A股字段发现测试 ====================

    def test_discover_a_stock_indicator_fields_success(self, mock_loader):
        """测试A股财务指标字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_a_stock_indicators()

        # 配置模拟
        self.mock_container.a_stock_indicators.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_a_stock_indicator_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.a_stock_indicators.assert_called_once()
        self.mock_container.a_stock_indicators.return_value.query.assert_called_once_with("SH600519")

    def test_discover_a_stock_balance_sheet_fields_success(self, mock_loader):
        """测试A股资产负债表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_a_stock_balance_sheet()

        # 配置模拟
        self.mock_container.a_stock_balance_sheet.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_a_stock_balance_sheet_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.a_stock_balance_sheet.assert_called_once()
        self.mock_container.a_stock_balance_sheet.return_value.query.assert_called_once_with("SH600519")

    def test_discover_a_stock_income_statement_fields_success(self, mock_loader):
        """测试A股利润表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_a_stock_profit_sheet()

        # 配置模拟
        self.mock_container.a_stock_income_statement.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_a_stock_income_statement_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.a_stock_income_statement.assert_called_once()
        self.mock_container.a_stock_income_statement.return_value.query.assert_called_once_with("SH600519")

    def test_discover_a_stock_cash_flow_fields_success(self, mock_loader):
        """测试A股现金流量表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_a_stock_cash_flow_sheet()

        # 配置模拟
        self.mock_container.a_stock_cash_flow.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_a_stock_cash_flow_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.a_stock_cash_flow.assert_called_once()
        self.mock_container.a_stock_cash_flow.return_value.query.assert_called_once_with("SH600519")

    # ==================== 港股字段发现测试 ====================

    def test_discover_hk_stock_indicator_fields_success(self, mock_loader):
        """测试港股财务指标字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_hk_stock_indicators()

        # 配置模拟
        self.mock_container.hk_stock_indicators.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_hk_stock_indicator_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.hk_stock_indicators.assert_called_once()
        self.mock_container.hk_stock_indicators.return_value.query.assert_called_once_with("00700")

    def test_discover_hk_stock_statement_fields_success(self, mock_loader):
        """测试港股基本面字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_hk_stock_statements()

        # 配置模拟
        self.mock_container.hk_stock_statement.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_hk_stock_statement_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.hk_stock_statement.assert_called_once()
        self.mock_container.hk_stock_statement.return_value.query.assert_called_once_with("00700")

    # ==================== 美股字段发现测试 ====================

    def test_discover_us_stock_indicator_fields_success(self, mock_loader):
        """测试美股财务指标字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_us_stock_indicators()

        # 配置模拟
        self.mock_container.us_stock_indicators.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_us_stock_indicator_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.us_stock_indicators.assert_called_once()
        self.mock_container.us_stock_indicators.return_value.query.assert_called_once_with("AAPL")

    def test_discover_us_stock_balance_sheet_fields_success(self, mock_loader):
        """测试美股资产负债表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_us_stock_statements()

        # 配置模拟（美股三表使用同一个样本数据文件）
        self.mock_container.us_stock_balance_sheet.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_us_stock_balance_sheet_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.us_stock_balance_sheet.assert_called_once()
        self.mock_container.us_stock_balance_sheet.return_value.query.assert_called_once_with("AAPL")

    def test_discover_us_stock_income_statement_fields_success(self, mock_loader):
        """测试美股利润表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_us_stock_statements()

        # 配置模拟（美股三表使用同一个样本数据文件）
        self.mock_container.us_stock_income_statement.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_us_stock_income_statement_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.us_stock_income_statement.assert_called_once()
        self.mock_container.us_stock_income_statement.return_value.query.assert_called_once_with("AAPL")

    def test_discover_us_stock_cash_flow_fields_success(self, mock_loader):
        """测试美股现金流量表字段发现成功"""
        # 使用真实样本数据
        sample_data = mock_loader.load_us_stock_statements()

        # 配置模拟（美股三表使用同一个样本数据文件）
        self.mock_container.us_stock_cash_flow.return_value.query.return_value = sample_data

        # 执行测试
        result = self.service.discover_us_stock_cash_flow_fields()

        # 验证结果 - 使用实际样本数据的字段
        expected_fields = list(sample_data.columns)
        assert result == expected_fields

        # 验证调用
        self.mock_container.us_stock_cash_flow.assert_called_once()
        self.mock_container.us_stock_cash_flow.return_value.query.assert_called_once_with("AAPL")

    # ==================== 聚合字段发现测试 ====================

    def test_discover_a_stock_all_fields_success(self, mock_loader):
        """测试A股所有接口字段发现成功"""
        # 使用真实样本数据配置所有A股查询器的模拟
        a_indicator_data = mock_loader.load_a_stock_indicators()
        a_balance_data = mock_loader.load_a_stock_balance_sheet()
        a_income_data = mock_loader.load_a_stock_profit_sheet()
        a_cash_flow_data = mock_loader.load_a_stock_cash_flow_sheet()

        self.mock_container.a_stock_indicators.return_value.query.return_value = a_indicator_data
        self.mock_container.a_stock_balance_sheet.return_value.query.return_value = a_balance_data
        self.mock_container.a_stock_income_statement.return_value.query.return_value = a_income_data
        self.mock_container.a_stock_cash_flow.return_value.query.return_value = a_cash_flow_data

        # 执行测试
        result = self.service.discover_a_stock_all_fields()

        # 验证结果 - 使用实际样本数据的字段
        assert result == {
            'indicators': list(a_indicator_data.columns),
            'balance_sheet': list(a_balance_data.columns),
            'income_statement': list(a_income_data.columns),
            'cash_flow': list(a_cash_flow_data.columns)
        }

    def test_discover_hk_stock_all_fields_success(self, mock_loader):
        """测试港股所有接口字段发现成功"""
        # 使用真实样本数据配置所有港股查询器的模拟
        hk_indicator_data = mock_loader.load_hk_stock_indicators()
        hk_statement_data = mock_loader.load_hk_stock_statements()

        self.mock_container.hk_stock_indicators.return_value.query.return_value = hk_indicator_data
        self.mock_container.hk_stock_balance_sheet.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_income_statement.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_cash_flow.return_value.query.return_value = hk_statement_data

        # 执行测试
        result = self.service.discover_hk_stock_all_fields()

        # 验证结果 - 使用实际样本数据的字段
        assert result == {
            'indicators': list(hk_indicator_data.columns),
            'balance_sheet': list(hk_statement_data.columns),
            'income_statement': list(hk_statement_data.columns),
            'cash_flow': list(hk_statement_data.columns)
        }

    def test_discover_us_stock_all_fields_success(self, mock_loader):
        """测试美股所有接口字段发现成功"""
        # 使用真实样本数据配置所有美股查询器的模拟
        us_indicator_data = mock_loader.load_us_stock_indicators()
        us_statement_data = mock_loader.load_us_stock_statements()

        self.mock_container.us_stock_indicators.return_value.query.return_value = us_indicator_data
        self.mock_container.us_stock_balance_sheet.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_income_statement.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_cash_flow.return_value.query.return_value = us_statement_data

        # 执行测试
        result = self.service.discover_us_stock_all_fields()

        # 验证结果 - 使用实际样本数据的字段
        assert result == {
            'indicators': list(us_indicator_data.columns),
            'balance_sheet': list(us_statement_data.columns),
            'income_statement': list(us_statement_data.columns),
            'cash_flow': list(us_statement_data.columns)
        }

    def test_discover_all_fields_success(self, mock_loader):
        """测试所有市场所有接口字段发现成功"""
        # 使用真实样本数据配置所有查询器的模拟
        a_indicator_data = mock_loader.load_a_stock_indicators()
        a_balance_data = mock_loader.load_a_stock_balance_sheet()
        a_income_data = mock_loader.load_a_stock_profit_sheet()
        a_cash_flow_data = mock_loader.load_a_stock_cash_flow_sheet()
        hk_indicator_data = mock_loader.load_hk_stock_indicators()
        hk_statement_data = mock_loader.load_hk_stock_statements()
        us_indicator_data = mock_loader.load_us_stock_indicators()
        us_statement_data = mock_loader.load_us_stock_statements()

        self.mock_container.a_stock_indicators.return_value.query.return_value = a_indicator_data
        self.mock_container.a_stock_balance_sheet.return_value.query.return_value = a_balance_data
        self.mock_container.a_stock_income_statement.return_value.query.return_value = a_income_data
        self.mock_container.a_stock_cash_flow.return_value.query.return_value = a_cash_flow_data
        self.mock_container.hk_stock_indicators.return_value.query.return_value = hk_indicator_data
        self.mock_container.hk_stock_balance_sheet.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_income_statement.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_cash_flow.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_statement.return_value.query.return_value = hk_statement_data
        self.mock_container.us_stock_indicators.return_value.query.return_value = us_indicator_data
        self.mock_container.us_stock_balance_sheet.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_income_statement.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_cash_flow.return_value.query.return_value = us_statement_data

        # 执行测试
        result = self.service.discover_all_fields()

        # 验证结构
        assert 'A_STOCK' in result
        assert 'HK_STOCK' in result
        assert 'US_STOCK' in result

        # 验证A股接口
        a_stock_interfaces = result['A_STOCK']
        assert 'indicators' in a_stock_interfaces
        assert 'balance_sheet' in a_stock_interfaces
        assert 'income_statement' in a_stock_interfaces
        assert 'cash_flow' in a_stock_interfaces

        # 验证港股接口
        hk_stock_interfaces = result['HK_STOCK']
        assert 'indicators' in hk_stock_interfaces
        assert 'balance_sheet' in hk_stock_interfaces
        assert 'income_statement' in hk_stock_interfaces
        assert 'cash_flow' in hk_stock_interfaces

        # 验证美股接口
        us_stock_interfaces = result['US_STOCK']
        assert 'indicators' in us_stock_interfaces
        assert 'balance_sheet' in us_stock_interfaces
        assert 'income_statement' in us_stock_interfaces
        assert 'cash_flow' in us_stock_interfaces

    # ==================== 错误处理测试 ====================

    def test_discover_a_stock_indicator_fields_empty_data(self):
        """测试A股财务指标字段发现 - 数据为空"""
        # 配置模拟返回空数据
        self.mock_container.a_stock_indicators.return_value.query.return_value = pd.DataFrame()

        # 执行测试并验证异常
        with pytest.raises(Exception) as exc_info:
            self.service.discover_a_stock_indicator_fields()

        assert "A股财务指标数据为空" in str(exc_info.value)

    def test_discover_a_stock_indicator_fields_none_data(self):
        """测试A股财务指标字段发现 - 数据为None"""
        # 配置模拟返回None
        self.mock_container.a_stock_indicators.return_value.query.return_value = None

        # 执行测试并验证异常
        with pytest.raises(Exception) as exc_info:
            self.service.discover_a_stock_indicator_fields()

        assert "A股财务指标数据为空" in str(exc_info.value)

    def test_discover_hk_stock_indicator_fields_exception(self):
        """测试港股财务指标字段发现 - 查询异常"""
        # 配置模拟抛出异常
        self.mock_container.hk_stock_indicators.return_value.query.side_effect = Exception("API调用失败")

        # 执行测试并验证异常
        with pytest.raises(Exception) as exc_info:
            self.service.discover_hk_stock_indicator_fields()

        assert "港股财务指标字段发现失败" in str(exc_info.value)

    def test_discover_us_stock_indicator_fields_exception(self):
        """测试美股财务指标字段发现 - 查询异常"""
        # 配置模拟抛出异常
        self.mock_container.us_stock_indicators.return_value.query.side_effect = Exception("网络连接错误")

        # 执行测试并验证异常
        with pytest.raises(Exception) as exc_info:
            self.service.discover_us_stock_indicator_fields()

        assert "美股财务指标字段发现失败" in str(exc_info.value)

    # ==================== 日志验证测试 ====================

    def test_logging_a_stock_discovery(self, caplog, mock_loader):
        """测试A股字段发现的日志记录"""
        caplog.set_level(logging.INFO)

        # 使用真实样本数据
        sample_data = mock_loader.load_a_stock_indicators()

        # 配置模拟
        self.mock_container.a_stock_indicators.return_value.query.return_value = sample_data

        # 执行测试
        self.service.discover_a_stock_indicator_fields()

        # 验证日志
        assert "发现A股财务指标字段，使用股票: SH600519" in caplog.text
        assert f"发现A股财务指标字段: {len(sample_data.columns)}个" in caplog.text

    def test_logging_error_discovery(self, caplog):
        """测试字段发现失败的日志记录"""
        caplog.set_level(logging.ERROR)

        # 配置模拟抛出异常
        self.mock_container.a_stock_indicators.return_value.query.side_effect = Exception("测试错误")

        # 执行测试
        with pytest.raises(Exception):
            self.service.discover_a_stock_indicator_fields()

        # 验证错误日志
        assert "A股财务指标字段发现失败" in caplog.text

    def test_logging_all_fields_discovery(self, caplog, mock_loader):
        """测试全部字段发现的统计日志"""
        caplog.set_level(logging.INFO)

        # 使用真实样本数据配置所有查询器的模拟
        a_indicator_data = mock_loader.load_a_stock_indicators()
        a_balance_data = mock_loader.load_a_stock_balance_sheet()
        a_income_data = mock_loader.load_a_stock_profit_sheet()
        a_cash_flow_data = mock_loader.load_a_stock_cash_flow_sheet()
        hk_indicator_data = mock_loader.load_hk_stock_indicators()
        hk_statement_data = mock_loader.load_hk_stock_statements()
        us_indicator_data = mock_loader.load_us_stock_indicators()
        us_statement_data = mock_loader.load_us_stock_statements()

        self.mock_container.a_stock_indicators.return_value.query.return_value = a_indicator_data
        self.mock_container.a_stock_balance_sheet.return_value.query.return_value = a_balance_data
        self.mock_container.a_stock_income_statement.return_value.query.return_value = a_income_data
        self.mock_container.a_stock_cash_flow.return_value.query.return_value = a_cash_flow_data
        self.mock_container.hk_stock_indicators.return_value.query.return_value = hk_indicator_data
        self.mock_container.hk_stock_balance_sheet.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_income_statement.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_cash_flow.return_value.query.return_value = hk_statement_data
        self.mock_container.hk_stock_statement.return_value.query.return_value = hk_statement_data
        self.mock_container.us_stock_indicators.return_value.query.return_value = us_indicator_data
        self.mock_container.us_stock_balance_sheet.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_income_statement.return_value.query.return_value = us_statement_data
        self.mock_container.us_stock_cash_flow.return_value.query.return_value = us_statement_data

        # 执行测试
        self.service.discover_all_fields()

        # 验证统计日志
        assert "开始发现所有市场的接口字段" in caplog.text
        assert "字段发现完成: 3个市场, 12个接口" in caplog.text

    # ==================== 代表股票配置测试 ====================

    def test_representative_stocks_configuration(self):
        """测试代表股票配置"""
        expected_stocks = {
            MarketType.A_STOCK: "SH600519",  # 贵州茅台
            MarketType.HK_STOCK: "00700",    # 腾讯
            MarketType.US_STOCK: "AAPL",     # 苹果（AKShare支持更好）
        }

        assert self.service.representative_stocks == expected_stocks

    def test_fixed_date_configuration(self):
        """测试固定查询日期配置"""
        assert self.service.start_date == "2024-01-01"
        assert self.service.end_date == "2024-12-31"

    # ==================== 真实数据字段验证测试 ====================

    def test_real_data_field_coverage(self, mock_loader):
        """测试真实样本数据的字段覆盖率"""
        # 加载所有真实样本数据
        a_indicator_data = mock_loader.load_a_stock_indicators()
        a_balance_data = mock_loader.load_a_stock_balance_sheet()
        a_income_data = mock_loader.load_a_stock_profit_sheet()
        a_cash_flow_data = mock_loader.load_a_stock_cash_flow_sheet()
        hk_indicator_data = mock_loader.load_hk_stock_indicators()
        hk_statement_data = mock_loader.load_hk_stock_statements()
        us_indicator_data = mock_loader.load_us_stock_indicators()
        us_statement_data = mock_loader.load_us_stock_statements()

        # 验证数据不为空
        assert len(a_indicator_data) > 0
        assert len(a_balance_data) > 0
        assert len(a_income_data) > 0
        assert len(a_cash_flow_data) > 0
        assert len(hk_indicator_data) > 0
        assert len(hk_statement_data) > 0
        assert len(us_indicator_data) > 0
        assert len(us_statement_data) > 0

        # 验证字段数量合理
        assert len(a_indicator_data.columns) >= 5  # 至少包含基本字段
        assert len(a_balance_data.columns) >= 5
        assert len(a_income_data.columns) >= 5
        assert len(a_cash_flow_data.columns) >= 5
        assert len(hk_indicator_data.columns) >= 5
        assert len(hk_statement_data.columns) >= 5
        assert len(us_indicator_data.columns) >= 5
        assert len(us_statement_data.columns) >= 5

        # 验证关键字段存在（使用中文字段名）
        assert any('报告' in col or 'date' in col.lower() for col in a_indicator_data.columns)
        # A股数据可能没有symbol/code字段，但有其他标识字段
        assert len(a_indicator_data.columns) > 0  # 至少有字段存在