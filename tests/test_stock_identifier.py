"""
StockIdentifier 单元测试

测试智能股票代码识别器的所有功能，包括：
- 股票代码市场识别
- 前缀和后缀匹配
- 格式推断
- 代码格式化和验证
"""

import pytest
import re
from src.akshare_value_investment.core.stock_identifier import StockIdentifier
from src.akshare_value_investment.core.models import MarketType


class TestStockIdentifier:
    """StockIdentifier 测试类"""

    @pytest.fixture
    def identifier(self):
        """创建 StockIdentifier 实例"""
        return StockIdentifier()

    # ==================== identify 方法测试 ====================

    @pytest.mark.parametrize("symbol,expected_market,expected_clean_symbol", [
        # 前缀匹配测试
        ("CN.600519", MarketType.A_STOCK, "600519"),
        ("A.000001", MarketType.A_STOCK, "000001"),
        ("HK.00700", MarketType.HK_STOCK, "00700"),
        ("H.09988", MarketType.HK_STOCK, "09988"),
        ("US.AAPL", MarketType.US_STOCK, "AAPL"),
        ("U.TSLA", MarketType.US_STOCK, "TSLA"),

        # 新增：SH/SZ前缀测试（Bug修复验证）
        ("SH600519", MarketType.A_STOCK, "600519"),  # 上海证券交易所前缀
        ("SZ000001", MarketType.A_STOCK, "000001"),  # 深圳证券交易所前缀
        ("SH688981", MarketType.A_STOCK, "688981"),  # 科创板股票
        ("SZ300015", MarketType.A_STOCK, "300015"),  # 创业板股票

        # 前缀大小写不敏感测试
        ("cn.600519", MarketType.A_STOCK, "600519"),
        ("a.000001", MarketType.A_STOCK, "000001"),
        ("hk.00700", MarketType.HK_STOCK, "00700"),
        ("h.09988", MarketType.HK_STOCK, "09988"),
        ("us.aapl", MarketType.US_STOCK, "aapl"),
        ("u.tsla", MarketType.US_STOCK, "tsla"),

        # 新增：SH/SZ前缀大小写不敏感测试
        ("sh600519", MarketType.A_STOCK, "600519"),
        ("sz000001", MarketType.A_STOCK, "000001"),
        ("Sh600519", MarketType.A_STOCK, "600519"),
        ("Sz000001", MarketType.A_STOCK, "000001"),
    ])
    def test_identify_prefix_matching(self, identifier, symbol, expected_market, expected_clean_symbol):
        """测试前缀匹配功能"""
        market, clean_symbol = identifier.identify(symbol)
        assert market == expected_market
        assert clean_symbol == expected_clean_symbol

    @pytest.mark.parametrize("symbol,expected_market,expected_clean_symbol", [
        # 后缀模式匹配测试
        ("600519.SS", MarketType.A_STOCK, "600519"),
        ("000001.SZ", MarketType.A_STOCK, "000001"),
        ("00700.HK", MarketType.HK_STOCK, "00700"),
        ("AAPL.O", MarketType.US_STOCK, "AAPL"),
        ("TSLA.NASDAQ", MarketType.US_STOCK, "TSLA"),
        ("MSFT.NYSE", MarketType.US_STOCK, "MSFT"),

        # 后缀大小写不敏感测试
        ("600519.ss", MarketType.A_STOCK, "600519"),
        ("000001.sz", MarketType.A_STOCK, "000001"),
        ("00700.hk", MarketType.HK_STOCK, "00700"),
        ("aapl.o", MarketType.US_STOCK, "aapl"),
        ("tsla.nasdaq", MarketType.US_STOCK, "tsla"),
        ("msft.nyse", MarketType.US_STOCK, "msft"),
    ])
    def test_identify_suffix_matching(self, identifier, symbol, expected_market, expected_clean_symbol):
        """测试后缀模式匹配功能"""
        market, clean_symbol = identifier.identify(symbol)
        assert market == expected_market
        assert clean_symbol == expected_clean_symbol

    @pytest.mark.parametrize("symbol,expected_market,expected_clean_symbol", [
        # A股格式推断：6位数字
        ("600519", MarketType.A_STOCK, "600519"),
        ("000001", MarketType.A_STOCK, "000001"),
        ("300015", MarketType.A_STOCK, "300015"),
        ("688981", MarketType.A_STOCK, "688981"),

        # 港股格式推断：5位数字，以0开头优先
        ("00700", MarketType.HK_STOCK, "00700"),
        ("09988", MarketType.HK_STOCK, "09988"),
        ("00005", MarketType.HK_STOCK, "00005"),
        ("00123", MarketType.HK_STOCK, "00123"),
        # 其他5位数字也识别为港股
        ("99999", MarketType.HK_STOCK, "99999"),
        ("12345", MarketType.HK_STOCK, "12345"),

        # 美股格式推断：字母代码
        ("AAPL", MarketType.US_STOCK, "AAPL"),
        ("TSLA", MarketType.US_STOCK, "TSLA"),
        ("MSFT", MarketType.US_STOCK, "MSFT"),
        ("GOOGL", MarketType.US_STOCK, "GOOGL"),
        ("META", MarketType.US_STOCK, "META"),
        ("B", MarketType.US_STOCK, "B"),
        ("BRK", MarketType.US_STOCK, "BRK"),
    ])
    def test_identify_format_inference(self, identifier, symbol, expected_market, expected_clean_symbol):
        """测试格式推断功能"""
        market, clean_symbol = identifier.identify(symbol)
        assert market == expected_market
        assert clean_symbol == expected_clean_symbol

    def test_identify_empty_symbol_with_default_market(self, identifier):
        """测试空股票代码且有默认市场"""
        # 测试有默认市场的情况
        market, clean_symbol = identifier.identify("", default_market=MarketType.HK_STOCK)
        assert market == MarketType.HK_STOCK
        assert clean_symbol == ""

        # 测试None且有默认市场
        market, clean_symbol = identifier.identify(None, default_market=MarketType.A_STOCK)
        assert market == MarketType.A_STOCK
        assert clean_symbol == ""

    def test_identify_empty_symbol_without_default_market(self, identifier):
        """测试空股票代码且无默认市场"""
        # 测试无默认市场时的默认行为（美股）
        market, clean_symbol = identifier.identify("")
        assert market == MarketType.US_STOCK
        assert clean_symbol == ""

        market, clean_symbol = identifier.identify(None)
        assert market == MarketType.US_STOCK
        assert clean_symbol == ""

    def test_identify_unrecognized_symbol_with_default(self, identifier):
        """测试无法识别的股票代码且有默认市场"""
        unrecognized = "UNKNOWN123"
        market, clean_symbol = identifier.identify(unrecognized, default_market=MarketType.HK_STOCK)
        assert market == MarketType.HK_STOCK
        assert clean_symbol == unrecognized

    def test_identify_unrecognized_symbol_without_default(self, identifier):
        """测试无法识别的股票代码且无默认市场"""
        unrecognized = "UNKNOWN123"
        market, clean_symbol = identifier.identify(unrecognized)
        assert market == MarketType.US_STOCK  # 默认美股
        assert clean_symbol == unrecognized

    def test_identify_whitespace_handling(self, identifier):
        """测试空白字符处理"""
        # 测试前后空格
        market, clean_symbol = identifier.identify("  600519  ")
        assert market == MarketType.A_STOCK
        assert clean_symbol == "600519"

        # 测试制表符和换行符
        market, clean_symbol = identifier.identify("\t600519\n")
        assert market == MarketType.A_STOCK
        assert clean_symbol == "600519"

    @pytest.mark.parametrize("invalid_symbol", [
        "", "   ", None, "1234567", "ABC123", "123ABC", "TOOLONGSYMBOL"
    ])
    def test_identify_invalid_formats(self, identifier, invalid_symbol):
        """测试无效格式处理"""
        if invalid_symbol in [None, ""]:
            # 空值会触发默认市场逻辑
            market, clean_symbol = identifier.identify(invalid_symbol)
            assert market == MarketType.US_STOCK
            assert clean_symbol == ""
        else:
            # 无效格式会回退到默认市场
            market, clean_symbol = identifier.identify(invalid_symbol)
            assert market == MarketType.US_STOCK
            assert clean_symbol == invalid_symbol.strip()

    # ==================== format_symbol 方法测试 ====================

    def test_format_symbol_a_stock(self, identifier):
        """测试A股代码格式化"""
        market = MarketType.A_STOCK
        symbol = "600519"
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "600519"  # A股代码保持不变

    def test_format_symbol_hk_stock_normal(self, identifier):
        """测试港股代码格式化（正常长度）"""
        market = MarketType.HK_STOCK
        symbol = "00700"
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "00700"  # 5位代码保持不变

    def test_format_symbol_hk_stock_padding(self, identifier):
        """测试港股代码格式化（补零）"""
        market = MarketType.HK_STOCK
        symbol = "700"  # 少于5位
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "00700"  # 补零到5位

    def test_format_symbol_hk_stock_longer(self, identifier):
        """测试港股代码格式化（超过5位）"""
        market = MarketType.HK_STOCK
        symbol = "123456"  # 超过5位
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "123456"  # 保持不变

    def test_format_symbol_us_stock(self, identifier):
        """测试美股代码格式化"""
        market = MarketType.US_STOCK

        # 测试小写转大写
        symbol = "aapl"
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "AAPL"

        # 测试混合大小写
        symbol = "AaPl"
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "AAPL"

        # 测试已经大写
        symbol = "AAPL"
        formatted = identifier.format_symbol(market, symbol)
        assert formatted == "AAPL"

    # ==================== validate_symbol 方法测试 ====================

    @pytest.mark.parametrize("symbol,is_valid", [
        # A股有效代码
        ("600519", True), ("000001", True), ("300015", True), ("688981", True),
        # A股无效代码
        ("12345", False), ("1234567", False), ("ABCDE", False), ("60051", False), ("6005190", False),
        ("", False), (None, False),
    ])
    def test_validate_symbol_a_stock(self, identifier, symbol, is_valid):
        """测试A股代码验证"""
        result = identifier.validate_symbol(symbol, MarketType.A_STOCK)
        assert result == is_valid

    @pytest.mark.parametrize("symbol,is_valid", [
        # 港股有效代码
        ("00700", True), ("09988", True), ("00005", True), ("12345", True), ("99999", True),
        ("1234", True), ("0070", True), ("123", True), ("987", True),  # 3-4位数字也有效
        # 港股无效代码
        ("123456", False), ("ABCDE", False), ("007001", False), ("12", False), ("1234567", False),
        ("", False), (None, False),
    ])
    def test_validate_symbol_hk_stock(self, identifier, symbol, is_valid):
        """测试港股代码验证"""
        result = identifier.validate_symbol(symbol, MarketType.HK_STOCK)
        assert result == is_valid

    @pytest.mark.parametrize("symbol,is_valid", [
        # 美股有效代码
        ("A", True), ("AA", True), ("AAA", True), ("AAAA", True), ("AAAAA", True),
        ("AAPL", True), ("TSLA", True), ("MSFT", True), ("GOOGL", True), ("META", True),
        ("BRK", True), ("B", True),
        # 美股无效代码
        ("AAAAAA", False), ("123", False), ("A123", False), ("AAPL1", False), ("", False), (None, False),
    ])
    def test_validate_symbol_us_stock(self, identifier, symbol, is_valid):
        """测试美股代码验证"""
        result = identifier.validate_symbol(symbol, MarketType.US_STOCK)
        assert result == is_valid

    # ==================== get_supported_markets 方法测试 ====================

    def test_get_supported_markets(self, identifier):
        """测试获取支持的市场列表"""
        markets = identifier.get_supported_markets()
        assert isinstance(markets, list)
        assert MarketType.A_STOCK in markets
        assert MarketType.HK_STOCK in markets
        assert MarketType.US_STOCK in markets
        assert len(markets) == 3  # 确保包含所有支持的市场

    # ==================== 边界情况和集成测试 ====================

    def test_integration_identify_and_format(self, identifier):
        """测试识别和格式化的集成"""
        test_cases = [
            ("CN.600519", MarketType.A_STOCK, "600519", "600519"),
            ("HK.00700", MarketType.HK_STOCK, "00700", "00700"),
            ("US.aapl", MarketType.US_STOCK, "aapl", "AAPL"),
            ("700", MarketType.HK_STOCK, "700", "00700"),  # 3位数字识别为港股，格式化补齐到5位
            ("00700", MarketType.HK_STOCK, "00700", "00700"),  # 5位数字且以0开头，识别为港股
        ]

        for input_symbol, expected_market, expected_clean, expected_formatted in test_cases:
            # 识别
            market, clean_symbol = identifier.identify(input_symbol)
            assert market == expected_market
            assert clean_symbol == expected_clean

            # 格式化
            formatted = identifier.format_symbol(market, clean_symbol)
            assert formatted == expected_formatted

    def test_integration_identify_and_validate(self, identifier):
        """测试识别和验证的集成"""
        test_cases = [
            ("600519", MarketType.A_STOCK, True),
            ("00700", MarketType.HK_STOCK, True),
            ("12345", MarketType.HK_STOCK, True),  # 5位数字被识别为港股
            ("AAPL", MarketType.US_STOCK, True),
            ("700", MarketType.HK_STOCK, True),  # 3位数字识别为港股，港股验证通过
        ]

        for input_symbol, expected_market, should_be_valid in test_cases:
            # 识别
            market, clean_symbol = identifier.identify(input_symbol)
            assert market == expected_market

            # 验证
            is_valid = identifier.validate_symbol(clean_symbol, market)
            assert is_valid == should_be_valid

    def test_complex_real_world_examples(self, identifier):
        """测试真实世界的复杂示例"""
        real_world_cases = [
            # 茅台股票的各种表示方式
            ("600519.SS", MarketType.A_STOCK, "600519"),
            ("CN.600519", MarketType.A_STOCK, "600519"),
            ("SH600519", MarketType.A_STOCK, "600519"),  # Bug修复：现在支持SH前缀
            ("600519", MarketType.A_STOCK, "600519"),

            # 平安银行股票的各种表示方式
            ("SZ000001", MarketType.A_STOCK, "000001"),  # Bug修复：现在支持SZ前缀
            ("000001.SZ", MarketType.A_STOCK, "000001"),
            ("000001", MarketType.A_STOCK, "000001"),

            # 腾讯股票的各种表示方式
            ("HK.00700", MarketType.HK_STOCK, "00700"),
            ("00700.HK", MarketType.HK_STOCK, "00700"),
            ("00700", MarketType.HK_STOCK, "00700"),  # 5位数字且以0开头
            # 700 不是5位数字，会识别为美股

            # 苹果股票的各种表示方式
            ("US.AAPL", MarketType.US_STOCK, "AAPL"),
            ("AAPL.O", MarketType.US_STOCK, "AAPL"),
            ("AAPL", MarketType.US_STOCK, "AAPL"),
            ("aapl", MarketType.US_STOCK, "AAPL"),  # 识别时自动转大写
        ]

        for input_symbol, expected_market, expected_clean in real_world_cases:
            market, clean_symbol = identifier.identify(input_symbol)
            assert market == expected_market, f"Failed for {input_symbol}: expected {expected_market}, got {market}"
            assert clean_symbol == expected_clean, f"Failed for {input_symbol}: expected {expected_clean}, got {clean_symbol}"

    def test_performance_large_number_of_symbols(self, identifier):
        """测试大量股票代码的处理性能"""
        import time

        # 准备测试数据
        test_symbols = []
        for i in range(1000):
            # 生成各种格式的股票代码
            if i % 3 == 0:
                test_symbols.append(f"600{str(i % 1000).zfill(3)}")  # A股格式
            elif i % 3 == 1:
                test_symbols.append(f"{str(i % 100000).zfill(5)}")  # 港股格式
            else:
                test_symbols.append(f"STOCK{i % 26}")  # 美股格式

        # 测试性能
        start_time = time.time()
        for symbol in test_symbols:
            identifier.identify(symbol)
        end_time = time.time()

        # 验证性能（应该在合理时间内完成）
        processing_time = end_time - start_time
        assert processing_time < 1.0  # 1000个符号应该在1秒内处理完成
        print(f"处理1000个股票代码耗时: {processing_time:.3f}秒")

    @pytest.mark.parametrize("edge_case", [
        ("", MarketType.US_STOCK, ""),
        ("   ", MarketType.US_STOCK, ""),
        (None, MarketType.US_STOCK, ""),
        ("0", MarketType.US_STOCK, "0"),  # 单个数字，不符合任何格式，默认美股
        ("123456789", MarketType.US_STOCK, "123456789"),  # 超长数字，默认美股
        ("ABC123DEF", MarketType.US_STOCK, "ABC123DEF"),  # 混合字符，默认美股
    ])
    def test_edge_cases(self, identifier, edge_case):
        """测试边界情况"""
        symbol, expected_market, expected_clean = edge_case
        market, clean_symbol = identifier.identify(symbol)
        assert market == expected_market
        assert clean_symbol == expected_clean

    def test_akshare_api_compatibility(self, identifier):
        """
        测试StockIdentifier标准化输出与akshare API的兼容性

        Bug根本原因：SH600519等常见前缀不被识别，导致API调用失败
        修复目标：确保所有标准化的A股代码都能被akshare API正确处理

        测试场景：
        1. 验证SH/SZ前缀被正确识别为A股
        2. 验证标准化后的代码格式符合akshare要求
        3. 模拟API调用验证兼容性（不实际调用网络API）
        """
        from unittest.mock import patch, MagicMock
        import akshare as ak

        # 测试关键的前缀识别场景
        test_cases = [
            ("SH600519", MarketType.A_STOCK, "600519", "贵州茅台"),
            ("SZ000001", MarketType.A_STOCK, "000001", "平安银行"),
            ("SH688981", MarketType.A_STOCK, "688981", "科创股票"),
            ("SZ300015", MarketType.A_STOCK, "300015", "创业股票"),
        ]

        for input_symbol, expected_market, expected_clean, description in test_cases:
            # 1. 验证识别和标准化
            market, clean_symbol = identifier.identify(input_symbol)
            assert market == expected_market, f"{description}: 识别失败，期望 {expected_market}, 得到 {market}"
            assert clean_symbol == expected_clean, f"{description}: 标准化失败，期望 {expected_clean}, 得到 {clean_symbol}"

            # 2. 验证标准化代码格式符合akshare要求（6位数字）
            assert re.fullmatch(r"\d{6}", clean_symbol), f"{description}: 标准化代码格式不符合akshare要求: {clean_symbol}"

            # 3. 验证验证功能
            is_valid = identifier.validate_symbol(clean_symbol, market)
            assert is_valid, f"{description}: 标准化代码验证失败: {clean_symbol}"

        print(f"✅ akshare API兼容性测试通过：所有A股前缀都能正确识别和标准化")

        # 4. 模拟API调用验证（使用Mock避免实际网络调用）
        with patch('akshare.stock_financial_abstract_ths') as mock_api:
            # 模拟API成功返回
            mock_api.return_value = MagicMock()
            mock_api.return_value.__len__ = MagicMock(return_value=100)
            mock_api.return_value.columns = ['报告期', '净利润', '基本每股收益']

            # 验证修复后的代码能够成功调用API
            try:
                market, clean_symbol = identifier.identify("SH600519")
                if market == MarketType.A_STOCK:
                    result = ak.stock_financial_abstract_ths(symbol=clean_symbol)
                    mock_api.assert_called_once_with(symbol=clean_symbol)
                    print(f"✅ API调用模拟成功：{clean_symbol} 被正确传递给akshare API")
            except Exception as e:
                self.fail(f"API调用模拟失败: {e}")

        print(f"✅ akshare API兼容性验证完成：SH/SZ前缀Bug已修复")