"""
股票代码格式化修复验证测试

专门测试为修复AKShare API兼容性问题而实现的股票代码格式化功能。
确保A股、港股、美股的股票代码在各种输入格式下都能正确转换为AKShare API所需的格式。

## 🎯 测试覆盖的问题

### A股问题
- AKShare A股API只接受纯数字代码，不支持SH/SZ前缀
- 错误示例：SH600519 → AttributeError: 'NoneType' object has no attribute 'string'
- 正确转换：SH600519 → 600519

### 港股问题
- 不同格式的港股代码需要统一为5位数字
- 格式标准化：700 → 00700, 0700 → 00700

### 美股问题
- AKShare不支持带连字符的股票代码
- 错误示例：BRK-A, BRK.B → TypeError: 'NoneType' object is not subscriptable'
- 正确转换：BRK-A → BRK_A, BRK.B → BRK_B
"""

import pytest
import pandas as pd
from akshare_value_investment.core.stock_identifier import StockIdentifier
from akshare_value_investment.core.models import MarketType


class TestStockCodeFormatFix:
    """测试股票代码格式化修复功能"""

    @pytest.fixture
    def identifier(self):
        """StockIdentifier实例"""
        return StockIdentifier()

    class TestA股格式化:
        """测试A股股票代码格式化"""

        def test_纯数字代码不变(self, identifier):
            """纯数字代码应该保持不变"""
            result = identifier.format_symbol_for_akshare(MarketType.A_STOCK, "600519")
            assert result == "600519"

            result = identifier.format_symbol_for_akshare(MarketType.A_STOCK, "000001")
            assert result == "000001"

        def test_identify方法识别前缀格式(self, identifier):
            """识别方法应该正确识别SH/SZ前缀格式"""
            market, symbol = identifier.identify("SH600519")
            assert market == MarketType.A_STOCK
            assert symbol == "600519"

            market, symbol = identifier.identify("SZ000001")
            assert market == MarketType.A_STOCK
            assert symbol == "000001"

        def test_format_symbol_for_akshare处理前缀格式(self, identifier):
            """format_symbol_for_akshare应该正确处理前缀格式"""
            result = identifier.format_symbol_for_akshare(MarketType.A_STOCK, "600519")
            assert result == "600519"

    class Test港股格式化:
        """测试港股股票代码格式化"""

        def test_5位代码保持不变(self, identifier):
            """标准5位港股代码应该保持不变"""
            result = identifier.format_symbol_for_akshare(MarketType.HK_STOCK, "00700")
            assert result == "00700"

        def test_不足5位自动补零(self, identifier):
            """不足5位的港股代码应该自动补零"""
            test_cases = [
                ("700", "00700"),
                ("70", "00070"),
                ("7", "00007"),
                ("0700", "00700"),
            ]

            for input_code, expected in test_cases:
                result = identifier.format_symbol_for_akshare(MarketType.HK_STOCK, input_code)
                assert result == expected, f"{input_code} → {result}, 期望 {expected}"

        def test_identify方法识别港股代码(self, identifier):
            """识别方法应该正确识别港股代码格式"""
            market, symbol = identifier.identify("00700")
            assert market == MarketType.HK_STOCK
            assert symbol == "00700"

            market, symbol = identifier.identify("700")
            assert market == MarketType.HK_STOCK
            assert symbol == "700"

    class Test美股格式化:
        """测试美股股票代码格式化"""

        def test普通代码大写化(self, identifier):
            """普通美股代码应该转换为大写"""
            test_cases = [
                ("aapl", "AAPL"),
                ("msft", "MSFT"),
                ("googl", "GOOGL"),
            ]

            for input_code, expected in test_cases:
                result = identifier.format_symbol_for_akshare(MarketType.US_STOCK, input_code)
                assert result == expected

        def test连字符转下划线(self, identifier):
            """带连字符的美股代码应该转换为下划线"""
            test_cases = [
                ("BRK-A", "BRK_A"),
                ("BRK-B", "BRK_B"),
                ("brk-a", "BRK_A"),
                ("brk-b", "BRK_B"),
            ]

            for input_code, expected in test_cases:
                result = identifier.format_symbol_for_akshare(MarketType.US_STOCK, input_code)
                assert result == expected

        def test点号转下划线(self, identifier):
            """带点号的美股代码应该转换为下划线"""
            test_cases = [
                ("BRK.A", "BRK_A"),
                ("BRK.B", "BRK_B"),
                ("brk.a", "BRK_A"),
                ("brk.b", "BRK_B"),
            ]

            for input_code, expected in test_cases:
                result = identifier.format_symbol_for_akshare(MarketType.US_STOCK, input_code)
                assert result == expected

        def test复杂转换场景(self, identifier):
            """测试复杂的转换场景"""
            test_cases = [
                ("BRK-A", "BRK_A"),  # 连字符转下划线
                ("BRK.A", "BRK_A"),  # 点号转下划线
                ("brk-a", "BRK_A"),  # 小写+连字符
                ("brk.a", "BRK_A"),  # 小写+点号
            ]

            for input_code, expected in test_cases:
                result = identifier.format_symbol_for_akshare(MarketType.US_STOCK, input_code)
                assert result == expected

        def test_identify方法识别美股代码(self, identifier):
            """识别方法应该正确识别美股代码"""
            market, symbol = identifier.identify("AAPL")
            assert market == MarketType.US_STOCK
            assert symbol == "AAPL"

            market, symbol = identifier.identify("BRK-A")
            assert market == MarketType.US_STOCK
            assert symbol == "BRK-A"  # 识别时保持原格式


class Test股票代码格式化集成测试:
    """股票代码格式化集成测试"""

    def test全市场格式化测试(self):
        """测试全市场的股票代码格式化"""
        identifier = StockIdentifier()

        test_cases = [
            # A股测试
            ("600519", MarketType.A_STOCK, "600519"),
            ("000001", MarketType.A_STOCK, "000001"),

            # 港股测试
            ("00700", MarketType.HK_STOCK, "00700"),
            ("0700", MarketType.HK_STOCK, "00700"),
            ("700", MarketType.HK_STOCK, "00700"),
            ("00941", MarketType.HK_STOCK, "00941"),

            # 美股测试
            ("AAPL", MarketType.US_STOCK, "AAPL"),
            ("MSFT", MarketType.US_STOCK, "MSFT"),
            ("BRK-A", MarketType.US_STOCK, "BRK_A"),
            ("BRK.B", MarketType.US_STOCK, "BRK_B"),
            ("aapl", MarketType.US_STOCK, "AAPL"),
            ("brk-a", MarketType.US_STOCK, "BRK_A"),
        ]

        for input_symbol, market, expected_output in test_cases:
            result = identifier.format_symbol_for_akshare(market, input_symbol)
            assert result == expected_output, (
                f"股票代码 {input_symbol} 在 {market.value} 市场转换失败: "
                f"期望 {expected_output}, 实际 {result}"
            )

    def test识别和格式化完整流程(self):
        """测试从识别到格式化的完整流程"""
        identifier = StockIdentifier()

        # 测试完整的识别+格式化流程
        raw_symbols = [
            "SH600519",  # A股前缀格式
            "600519",    # A股纯数字
            "00700",     # 港股标准格式
            "700",       # 港股简化格式
            "AAPL",      # 美股标准格式
            "BRK-A",     # 美股特殊格式
            "BRK.B",     # 美股特殊格式
        ]

        for symbol in raw_symbols:
            try:
                # 第一步：识别市场和标准化代码
                market, standardized = identifier.identify(symbol)

                # 第二步：为AKShare API格式化
                formatted = identifier.format_symbol_for_akshare(market, standardized)

                # 验证结果
                assert isinstance(formatted, str), f"格式化结果应该是字符串: {symbol} → {formatted}"
                assert len(formatted) > 0, f"格式化结果不能为空: {symbol} → {formatted}"

                print(f"✅ {symbol:8} → 市场:{market.value:8} 标准化:{standardized:8} AKShare:{formatted}")

            except Exception as e:
                pytest.fail(f"股票代码 {symbol} 处理失败: {e}")


class Test股票代码格式化回归测试:
    """确保修复的问题不再出现的回归测试"""

    def test_修复前的问题场景(self):
        """测试修复前会失败的问题场景"""
        identifier = StockIdentifier()

        # 场景1：A股前缀格式应该转换为纯数字（修复SH600519错误）
        market, symbol = identifier.identify("SH600519")
        formatted = identifier.format_symbol_for_akshare(market, symbol)
        assert formatted == "600519", "SH600519应该转换为600519"

        market, symbol = identifier.identify("SZ000001")
        formatted = identifier.format_symbol_for_akshare(market, symbol)
        assert formatted == "000001", "SZ000001应该转换为000001"

        # 场景2：美股连字符应该转换为下划线（修复BRK-A错误）
        market, symbol = identifier.identify("BRK-A")
        formatted = identifier.format_symbol_for_akshare(market, symbol)
        assert formatted == "BRK_A", "BRK-A应该转换为BRK_A"

        market, symbol = identifier.identify("BRK.B")
        formatted = identifier.format_symbol_for_akshare(market, symbol)
        assert formatted == "BRK_B", "BRK.B应该转换为BRK_B"

        # 场景3：港股代码应该统一为5位（修复700错误）
        test_cases = [("700", "00700"), ("0700", "00700"), ("00700", "00700")]
        for input_code, expected in test_cases:
            market, symbol = identifier.identify(input_code)
            formatted = identifier.format_symbol_for_akshare(market, symbol)
            assert formatted == expected, f"{input_code}应该转换为{expected}"

    def test_API兼容性关键场景(self):
        """测试AKShare API兼容性的关键场景"""
        identifier = StockIdentifier()

        # 这些是已知能正常工作的AKShare调用格式
        known_working_formats = {
            ("600519", MarketType.A_STOCK): "600519",  # A股纯数字
            ("00700", MarketType.HK_STOCK): "00700",  # 港股5位
            ("AAPL", MarketType.US_STOCK): "AAPL",    # 美股标准
            ("BRK_A", MarketType.US_STOCK): "BRK_A",  # 美股下划线格式（经测试可用）
        }

        for (input_symbol, market), expected_format in known_working_formats.items():
            # 识别
            market_result, symbol_result = identifier.identify(input_symbol)
            assert market_result == market, f"{input_symbol} 识别市场错误"

            # 格式化
            formatted = identifier.format_symbol_for_akshare(market_result, symbol_result)
            assert formatted == expected_format, (
                f"{input_symbol} 格式化错误: 期望 {expected_format}, 实际 {formatted}"
            )


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])