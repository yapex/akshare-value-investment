#!/usr/bin/env python3
"""
获取akshareA股真实财务字段数据

为重新设计关键字索引系统提供真实数据基础
"""

import akshare as ak
import pandas as pd
import json
from collections import defaultdict

def get_a_stock_fields():
    """获取A股真实财务字段"""

    print("🔍 正在获取A股财务数据字段...")

    # 测试多个股票以确保字段完整性
    test_stocks = ["605499", "000001", "600036", "600519", "600000"]

    all_fields = set()
    fields_by_stock = {}

    for symbol in test_stocks:
        print(f"📊 获取股票 {symbol} 的财务数据...")

        try:
            # 获取财务摘要数据
            data = ak.stock_financial_abstract(symbol=symbol)

            if hasattr(data, 'empty') and not data.empty:
                print(f"   ✅ 成功获取 {data.shape[0]} 条记录")

                # 收集所有字段
                for _, row in data.iterrows():
                    field_name = row.get('指标', '')
                    if field_name and field_name.strip():
                        all_fields.add(field_name.strip())

                fields_by_stock[symbol] = list(all_fields)
                print(f"   📋 发现字段数: {len(all_fields)}")
            else:
                print(f"   ❌ 数据为空")

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")

    return sorted(list(all_fields)), fields_by_stock

def analyze_fields_structure(fields):
    """分析字段结构和命名规律"""

    print(f"\n🔍 分析字段结构 (共{len(fields)}个字段)...")

    # 按名称长度分析
    length_stats = defaultdict(int)
    name_patterns = defaultdict(int)

    for field in fields:
        length_stats[len(field)] += 1

        # 分析命名模式
        if '(' in field:
            name_patterns['带括号'] += 1
        if '%' in field:
            name_patterns['百分比字段'] += 1
        if '率' in field:
            name_patterns['比率字段'] += 1
        if '每' in field:
            name_patterns['每股字段'] += 1
        if '周转' in field:
            name_patterns['周转字段'] += 1
        if '增长' in field:
            name_patterns['增长字段'] += 1
        if '资产' in field:
            name_patterns['资产字段'] += 1
        if '负债' in field:
            name_patterns['负债字段'] += 1
        if '现金' in field:
            name_patterns['现金流字段'] += 1

    print(f"\n📊 字段长度分布:")
    for length in sorted(length_stats.keys()):
        print(f"   {length}字: {length_stats[length]}个字段")

    print(f"\n📊 命名模式分析:")
    for pattern, count in name_patterns.items():
        print(f"   {pattern}: {count}个字段")

    return name_patterns

def categorize_fields(fields):
    """基于字段名称进行业务分类"""

    print(f"\n🏷️ 对字段进行业务分类...")

    categories = {
        '盈利能力': [],
        '营运能力': [],
        '偿债能力': [],
        '成长能力': [],
        '现金流': [],
        '每股指标': [],
        '资产规模': [],
        '资本结构': [],
        '其他': []
    }

    for field in fields:
        field_lower = field.lower()

        # 基于关键词进行分类
        if any(keyword in field_lower for keyword in ['净利润', '利润', '毛利率', '净利率', 'roe', 'roa', '营业利润']):
            categories['盈利能力'].append(field)
        elif any(keyword in field_lower for keyword in ['周转', '存货', '应收', '应付', '营运']):
            categories['营运能力'].append(field)
        elif any(keyword in field_lower for keyword in ['负债', '比率', '速动', '流动', '偿债']):
            categories['偿债能力'].append(field)
        elif any(keyword in field_lower for keyword in ['增长', '同比', '环比']):
            categories['成长能力'].append(field)
        elif any(keyword in field_lower for keyword in ['现金', '流', '经营活动', '投资', '筹资']):
            categories['现金流'].append(field)
        elif '每股' in field_lower:
            categories['每股指标'].append(field)
        elif any(keyword in field_lower for keyword in ['总资产', '净资产', '股东权益', '股本']):
            categories['资产规模'].append(field)
        elif any(keyword in field_lower for keyword in ['股本', '权益', '负债', '资本']):
            categories['资本结构'].append(field)
        else:
            categories['其他'].append(field)

    print(f"\n📊 分类结果:")
    for category, field_list in categories.items():
        print(f"   {category}: {len(field_list)}个字段")
        if field_list:
            print(f"     示例: {field_list[:3]}")

    return categories

def extract_keywords_from_field(field_name):
    """从字段名中提取关键词"""

    # 移除括号和单位
    clean_name = field_name.split('(')[0].strip()

    # 分解为关键词
    keywords = []

    # 财务常用关键词
    financial_keywords = [
        '净利润', '利润', '收入', '收益', '成本', '费用',
        '总资产', '净资产', '股东权益', '股本',
        '负债', '流动', '速动', '现金', '经营',
        '投资', '筹资', '每股', '率', '比',
        '周转', '存货', '应收', '应付',
        '增长', '同比', '环比', '调整',
        '基本', '稀释', '加权', '平均',
        '扣非', '非经常', '核心', '主营',
        '毛利率', '净利率', 'roe', 'roa',
        '资产负债', '流动比率', '速动比率'
    ]

    # 提取包含财务关键词的词
    words = clean_name.replace('_','').replace('/','').replace('-',' ')

    for keyword in financial_keywords:
        if keyword in words:
            keywords.append(keyword)

    # 如果没有找到财务关键词，尝试分词
    if not keywords:
        words = clean_name.replace('_',' ').replace('/',' ').replace('-',' ')
        for word in words:
            if len(word) >= 2:  # 只保留长度>=2的词
                keywords.append(word)

    return list(set(keywords))

def generate_field_keywords_index(fields, categories):
    """生成字段关键字索引配置"""

    print(f"\n🏗️ 生成字段关键字索引配置...")

    config = {
        'metadata': {
            'total_fields': len(fields),
            'categories': {k: len(v) for k, v in categories.items()},
            'generated_at': '2025-01-11'
        }
    }

    for category, field_list in categories.items():
        config[category] = {}

        for field in field_list:
            keywords = extract_keywords_from_field(field)

            if keywords:
                config[category][field] = {
                    'keywords': keywords,
                    'priority': 1,
                    'description': f"{field} - {category}相关指标"
                }

    return config

def main():
    """主函数"""

    print("=" * 80)
    print("🔍 akshare A股财务字段数据获取和分析")
    print("=" * 80)

    # 获取所有字段
    all_fields, fields_by_stock = get_a_stock_fields()

    if not all_fields:
        print("❌ 未获取到任何字段数据")
        return

    # 分析字段结构
    name_patterns = analyze_fields_structure(all_fields)

    # 业务分类
    categories = categorize_fields(all_fields)

    # 生成关键字索引
    keyword_config = generate_field_keywords_index(all_fields, categories)

    # 保存配置
    config_file = 'akshare_fields_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(keyword_config, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 配置已保存到: {config_file}")
    print(f"📊 配置包含: {len([k for k in keyword_config if k != 'metadata'])} 个分类")

    # 生成YAML格式配置示例
    yaml_content = "# akshare A股字段关键字索引配置\n"
    yaml_content += "# 基于真实akshare数据生成，支持用户友好的自然语言查询\n\n"

    for category, fields in categories.items():
        if category != 'metadata' and fields:
            yaml_content += f"# {category}\n"
            yaml_content += f"{category.lower().replace(' ', '_')}:\n"

            for field in fields[:5]:  # 只显示前5个作为示例
                keywords = extract_keywords_from_field(field)
                if keywords:
                    yaml_content += f'  "{field}":\n'
                    yaml_content += f'    keywords: {keywords}\n'
                    yaml_content += f'    priority: 1\n\n'

            yaml_content += f"  # {category}共{len(fields)}个字段，此处显示前5个\n\n"

    yaml_file = 'akshare_fields_config_example.yaml'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print(f"✅ YAML示例已保存到: {yaml_file}")

    print(f"\n📈 数据统计:")
    print(f"   总字段数: {len(all_fields)}")
    print(f"   分类数量: {len([k for k in categories if k != '其他'])}个主要分类")
    print(f"   平均每类字段: {len(all_fields) // len(categories):.1f}个")

if __name__ == "__main__":
    main()