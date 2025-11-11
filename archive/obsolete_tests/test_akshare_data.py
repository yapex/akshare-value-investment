#!/usr/bin/env python3
"""
测试akshare数据获取
"""

import akshare as ak

def test_dongpeng_data():
    """测试东鹏饮料的akshare数据获取"""

    symbol = "600932"  # 东鹏饮料

    print(f"🔍 测试获取东鹏饮料({symbol})的财务数据...")

    try:
        # 获取财务数据
        data = ak.stock_financial_abstract(symbol=symbol)

        print(f"📊 数据类型: {type(data)}")

        if hasattr(data, 'shape'):
            print(f"📊 数据形状: {data.shape}")

        if hasattr(data, 'empty') and data.empty:
            print("❌ 数据为空")
            return

        if hasattr(data, 'columns'):
            print(f"📋 列名: {list(data.columns)}")

        if hasattr(data, 'head'):
            print("\n📄 前5行数据:")
            print(data.head())

        if hasattr(data, 'to_dict'):
            records = data.to_dict('records')
            print(f"\n📝 转换为记录，共{len(records)}条")

            # 查看前3条记录的详细信息
            for i, record in enumerate(records[:3]):
                print(f"\n--- 记录 {i+1} ---")
                for key, value in record.items():
                    print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dongpeng_data()