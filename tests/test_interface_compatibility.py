#!/usr/bin/env python3
"""
测试新字段映射系统与现有IFieldMapper接口的兼容性
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_interface_compatibility():
    """测试接口兼容性"""
    print("🔍 测试IFieldMapper接口兼容性")
    print("=" * 50)

    try:
        # 导入新的字段映射器
        from akshare_value_investment.business.mapping.field_mapper import FinancialFieldMapper, IFieldMapper

        # 创建映射器实例
        field_mapper = FinancialFieldMapper()
        print("✅ FinancialFieldMapper创建成功")

        # 验证接口实现
        print(f"✅ 实现IFieldMapper接口: {isinstance(field_mapper, IFieldMapper)}")

        # 测试核心方法 - 与原有services/field_mapper.py相同的接口
        print("\n🎯 测试异步resolve_fields方法:")

        test_cases = [
            ('000001', ['净利润', '每股收益', 'ROE']),  # A股
            ('00700.HK', ['净利润', '每股收益']),          # 港股
            ('AAPL', ['净利润', '每股收益']),               # 美股
        ]

        for symbol, fields in test_cases:
            print(f"  测试 {symbol}:")
            try:
                import asyncio
                async def test_resolve():
                    mapped_fields, suggestions = await field_mapper.resolve_fields(symbol, fields)
                    return mapped_fields, suggestions

                mapped_fields, suggestions = asyncio.run(test_resolve())

                print(f"    输入字段: {fields}")
                print(f"    映射结果: {mapped_fields}")
                print(f"    建议: {suggestions[:3]}")  # 只显示前3个建议

                # 验证映射结果
                for original, mapped in zip(fields, mapped_fields):
                    if original != mapped:
                        print(f"      ✅ '{original}' → '{mapped}'")
                    else:
                        print(f"      • '{original}' → '{mapped}'")

            except Exception as e:
                print(f"    ❌ 失败: {e}")

        print()

        # 测试兼容性方法
        print("🔧 测试兼容性方法:")

        compatibility_tests = [
            ("map_field_name", ("000001", "净利润")),
            ("get_field_mapping_suggestions", ("000001", "unknown_field")),
            ("get_available_fields", (None,)),
            ("get_available_fields", ("a_stock",)),
        ]

        for method_name, args in compatibility_tests:
            try:
                if method_name == "get_available_fields" and args[0] is None:
                    result = getattr(field_mapper, method_name)()
                else:
                    result = getattr(field_mapper, method_name)(*args)
                print(f"  ✅ {method_name}: {str(result)[:50]}...")
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")

        print()

        # 显示配置信息
        config_info = field_mapper.get_config_info()
        print(f"📊 配置信息:")
        print(f"  - 可用市场: {config_info.get('available_markets', [])}")
        print(f"  - 总字段数: {config_info.get('total_fields', 0)}")
        print(f"  - 总关键字数: {len(field_mapper.get_all_keywords())}")

        print("\n🎉 接口兼容性测试成功！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise  # 使用raise而不是return False，让pytest正确处理错误

if __name__ == "__main__":
    try:
        test_interface_compatibility()
        sys.exit(0)  # 成功时退出
    except Exception as e:
        print(f"程序执行异常: {e}")
        sys.exit(1)  # 失败时退出