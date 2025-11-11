#!/usr/bin/env python3
"""
测试其他akshare数据获取方法
"""

import akshare as ak

def test_alternative_data_sources():
    """测试不同的数据获取方法"""

    symbol = "600932"  # 东鹏饮料

    print(f"🔍 测试东鹏饮料({symbol})的不同数据源...")

    # 测试方法列表
    methods = [
        ("股票基本面数据-新浪", lambda: ak.stock_financial_abstract(symbol=symbol)),
        ("股票财务指标-东方财富", lambda: ak.stock_financial_analysis(symbol=symbol)),
        ("资产负债表", lambda: ak.stock_balance_sheet_by_report_em(symbol=symbol)),
        ("利润表", lambda: ak.stock_profit_sheet_by_report_em(symbol=symbol)),
        ("现金流量表", lambda: ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)),
        ("财务指标-新浪", lambda: ak.stock_financial_indicator(symbol=symbol)),
    ]

    for method_name, method_func in methods:
        print(f"\n--- 测试: {method_name} ---")
        try:
            data = method_func()
            print(f"✅ 成功获取数据，类型: {type(data)}")

            if hasattr(data, 'shape'):
                print(f"   数据形状: {data.shape}")
                if data.shape[0] > 0:
                    print(f"   示例数据:\n{data.head(2)}")
                else:
                    print("   ⚠️ 数据为空")

            elif isinstance(data, dict):
                print(f"   字典键: {list(data.keys())}")

            elif isinstance(data, list):
                print(f"   列表长度: {len(data)}")
                if len(data) > 0:
                    print(f"   第一个元素: {data[0]}")

        except Exception as e:
            print(f"❌ 失败: {str(e)}")

def test_dongpeng_info():
    """测试获取东鹏饮料基本信息"""
    print(f"\n🔍 获取东鹏饮料基本信息...")

    try:
        # 尝试获取股票基本信息
        info = ak.stock_individual_info_em(symbol="600932")
        print(f"✅ 获取基本信息成功:\n{info}")
    except Exception as e:
        print(f"❌ 获取基本信息失败: {str(e)}")

    try:
        # 尝试获取股票实时数据
        realtime = ak.stock_zh_a_spot_em()
        dongpeng_data = realtime[realtime['代码'] == '600932']
        if not dongpeng_data.empty:
            print(f"✅ 获取实时数据成功:\n{dongpeng_data}")
        else:
            print("❌ 实时数据中未找到东鹏饮料")
    except Exception as e:
        print(f"❌ 获取实时数据失败: {str(e)}")

if __name__ == "__main__":
    test_alternative_data_sources()
    test_dongpeng_info()