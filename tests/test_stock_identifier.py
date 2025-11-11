"""
股票识别测试案例

Test Case 3-1: 显式前缀识别
Test Case 3-2: 格式推断识别
Test Case 3-3: 边界情况处理
"""

import pytest

try:
    from akshare_value_investment.core.models import MarketType
    from akshare_value_investment.core.stock_identifier import StockIdentifier
except ImportError:
    pytest.skip("Stock identifier not implemented yet", allow_module_level=True)


class TestStockIdentifier:
    """股票识别测试"""

    def setup_method(self):
        """测试前设置"""
        self.identifier = StockIdentifier()

    def test_explicit_prefix_identification(self):
        """Test Case 3-1: 显式前缀识别"""
        # Input: ["CN.600519", "HK.00700", "US.TSLA"]
        test_cases = [
            ("CN.600519", MarketType.A_STOCK, "600519"),
            ("A.600519", MarketType.A_STOCK, "600519"),
            ("HK.00700", MarketType.HK_STOCK, "00700"),
            ("H.00700", MarketType.HK_STOCK, "00700"),
            ("US.TSLA", MarketType.US_STOCK, "TSLA"),
            ("U.TSLA", MarketType.US_STOCK, "TSLA"),
        ]

        for symbol, expected_market, expected_clean_symbol in test_cases:
            # Expected Output: [(MarketType.A_STOCK, "600519"), (MarketType.HK_STOCK, "00700"), (MarketType.US_STOCK, "TSLA")]
            actual_market, actual_clean_symbol = self.identifier.identify(symbol)

            # Validation: 识别结果正确，前缀正确去除
            assert actual_market == expected_market, f"Failed market identification for {symbol}"
            assert actual_clean_symbol == expected_clean_symbol, f"Failed symbol cleaning for {symbol}"

    def test_pattern_inference_identification(self):
        """Test Case 3-2: 格式推断识别"""
        # Input: ["600519", "00700", "TSLA"]
        test_cases = [
            # A股：6位数字
            ("600519", MarketType.A_STOCK, "600519"),
            ("000001", MarketType.A_STOCK, "000001"),
            ("123456", MarketType.A_STOCK, "123456"),
            # 港股：5位数字且以0开头
            ("00700", MarketType.HK_STOCK, "00700"),
            ("00941", MarketType.HK_STOCK, "00941"),
            ("00005", MarketType.HK_STOCK, "00005"),
            # 美股：字母代码（不区分大小写）
            ("TSLA", MarketType.US_STOCK, "TSLA"),
            ("AAPL", MarketType.US_STOCK, "AAPL"),
            ("GOOGL", MarketType.US_STOCK, "GOOGL"),
            ("tsla", MarketType.US_STOCK, "TSLA"),  # 大写标准化
            ("aapl", MarketType.US_STOCK, "AAPL"),
        ]

        for symbol, expected_market, expected_clean_symbol in test_cases:
            # Expected Output: [(MarketType.A_STOCK, "600519"), (MarketType.HK_STOCK, "00700"), (MarketType.US_STOCK, "TSLA")]
            actual_market, actual_clean_symbol = self.identifier.identify(symbol)

            # Validation: 基于格式正确推断市场类型
            assert actual_market == expected_market, f"Failed market inference for {symbol}"
            assert actual_clean_symbol == expected_clean_symbol, f"Failed symbol cleaning for {symbol}"

    def test_boundary_conditions_handling(self):
        """Test Case 3-3: 边界情况处理"""
        boundary_cases = [
            # 空字符串
            ("", MarketType.US_STOCK, ""),  # 默认美股
            # 无效前缀
            ("INVALID.600519", MarketType.US_STOCK, "INVALID.600519"),  # 默认美股
            # 特殊字符
            ("600519.SH", MarketType.US_STOCK, "600519.SH"),  # 默认美股
            # 纯数字但长度异常
            ("123", MarketType.US_STOCK, "123"),  # 默认美股
            ("12345678", MarketType.US_STOCK, "12345678"),  # 默认美股
            # 单字母
            ("A", MarketType.US_STOCK, "A"),
            # 混合格式
            ("US00700", MarketType.US_STOCK, "US00700"),  # 没有点分隔符，默认美股
        ]

        for symbol, expected_market, expected_clean_symbol in boundary_cases:
            # Expected Output: 适当的错误处理或默认推断
            try:
                actual_market, actual_clean_symbol = self.identifier.identify(symbol)
                assert actual_market == expected_market, f"Failed boundary case for {symbol}"
                assert actual_clean_symbol == expected_clean_symbol, f"Failed symbol cleaning for {symbol}"
            except Exception as e:
                # 对于某些边界情况，允许抛出有意义的异常
                if symbol == "":
                    assert str(e) in ["Empty symbol", "Invalid symbol format"], f"Unexpected error for {symbol}: {e}"
                else:
                    raise  # 重新抛出其他异常

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        test_cases = [
            ("cn.600519", MarketType.A_STOCK, "600519"),  # 小写前缀应该工作
            ("hk.00700", MarketType.HK_STOCK, "00700"),
            ("us.TSLA", MarketType.US_STOCK, "TSLA"),
        ]

        for symbol, expected_market, expected_clean_symbol in test_cases:
            actual_market, actual_clean_symbol = self.identifier.identify(symbol)
            assert actual_market == expected_market, f"Failed case sensitivity test for {symbol}"
            assert actual_clean_symbol == expected_clean_symbol, f"Failed case cleaning for {symbol}"

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        test_cases = [
            (" 600519 ", MarketType.A_STOCK, "600519"),
            ("\t00700\n", MarketType.HK_STOCK, "00700"),
            ("  US.TSLA  ", MarketType.US_STOCK, "TSLA"),
        ]

        for symbol, expected_market, expected_clean_symbol in test_cases:
            actual_market, actual_clean_symbol = self.identifier.identify(symbol)
            assert actual_market == expected_market, f"Failed whitespace test for {symbol}"
            assert actual_clean_symbol == expected_clean_symbol, f"Failed whitespace cleaning for {symbol}"

    def test_edge_cases_identification(self):
        """测试边缘情况识别"""
        # 测试空字符串和默认市场
        market, symbol = self.identifier.identify("")
        assert market == MarketType.US_STOCK
        assert symbol == ""

        # 测试指定默认市场
        market, symbol = self.identifier.identify("", default_market=MarketType.HK_STOCK)
        assert market == MarketType.HK_STOCK
        assert symbol == ""

        # 测试后缀模式匹配
        test_cases = [
            ("600519.SS", MarketType.A_STOCK, "600519"),
            ("AAPL.O", MarketType.US_STOCK, "AAPL"),
            ("00700.HK", MarketType.HK_STOCK, "00700"),
            ("TSLA.NASDAQ", MarketType.US_STOCK, "TSLA"),
        ]

        for symbol_with_suffix, expected_market, expected_clean_symbol in test_cases:
            market, clean_symbol = self.identifier.identify(symbol_with_suffix)
            assert market == expected_market
            assert clean_symbol == expected_clean_symbol

        # 测试无法识别的代码使用默认市场
        market, symbol = self.identifier.identify("INVALID_CODE", default_market=MarketType.HK_STOCK)
        assert market == MarketType.HK_STOCK
        assert symbol == "INVALID_CODE"

        # 测试无法识别的代码默认为美股
        market, symbol = self.identifier.identify("INVALID_CODE")
        assert market == MarketType.US_STOCK
        assert symbol == "INVALID_CODE"

    def test_validate_symbol_edge_cases(self):
        """测试validate_symbol的边缘情况"""
        # 测试空字符串
        assert self.identifier.validate_symbol("", MarketType.A_STOCK) is False
        assert self.identifier.validate_symbol("", MarketType.HK_STOCK) is False
        assert self.identifier.validate_symbol("", MarketType.US_STOCK) is False

        # 测试不匹配市场的格式
        assert self.identifier.validate_symbol("600519", MarketType.HK_STOCK) is False  # A股格式
        assert self.identifier.validate_symbol("00700", MarketType.A_STOCK) is False  # 港股格式
        assert self.identifier.validate_symbol("TSLA", MarketType.HK_STOCK) is False   # 美股格式

        # 测试无效的股票代码格式
        assert self.identifier.validate_symbol("12345", MarketType.A_STOCK) is False  # 5位数字不是A股
        assert self.identifier.validate_symbol("1234567", MarketType.HK_STOCK) is False  # 7位数字不是港股
        assert self.identifier.validate_symbol("123456", MarketType.US_STOCK) is False   # 数字不是美股
        assert self.identifier.validate_symbol("TOOLONG", MarketType.US_STOCK) is False  # 超过5个字母

    def test_supported_markets(self):
        """测试支持的市场类型"""
        supported_markets = self.identifier.get_supported_markets()
        assert MarketType.A_STOCK in supported_markets
        assert MarketType.HK_STOCK in supported_markets
        assert MarketType.US_STOCK in supported_markets
        assert len(supported_markets) == 3