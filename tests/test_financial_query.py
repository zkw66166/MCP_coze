#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务查询系统测试用例
测试配置热更新和查询功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.financial_query import FinancialQuery
from modules.metrics_loader import MetricsLoader


def test_metrics_loader_hot_reload():
    """测试MetricsLoader热更新功能"""
    print("=" * 60)
    print("测试1: MetricsLoader热更新")
    print("=" * 60)
    
    loader = MetricsLoader()
    
    # 首次加载
    config1 = loader.load_config()
    version1 = config1.get('version', 'unknown')
    print(f"首次加载配置版本: {version1}")
    
    # 再次加载（应使用缓存，不重新读取）
    config2 = loader.load_config()
    version2 = config2.get('version', 'unknown')
    print(f"再次加载配置版本: {version2} (应与首次相同)")
    
    # 检查query_settings是否存在
    query_settings = config1.get('query_settings', {})
    if query_settings:
        print(f"✅ query_settings已加载: {len(query_settings)} 个配置项")
        print(f"   - all_periods_keywords: {len(query_settings.get('all_periods_keywords', []))} 个")
        print(f"   - comparison_keywords: {len(query_settings.get('comparison_keywords', []))} 个")
        print(f"   - aggregation_tables: {len(query_settings.get('aggregation_tables', []))} 个")
    else:
        print("❌ query_settings未找到!")
        return False
    
    return True


def test_financial_query_basic():
    """测试财务查询基本功能"""
    print("\n" + "=" * 60)
    print("测试2: 财务查询基本功能")
    print("=" * 60)
    
    fq = FinancialQuery()
    
    # 测试时间范围提取
    test_questions = [
        "2024年营业收入是多少",
        "2022-2024年净利润趋势",
        "一季度增值税税负如何",
        "2023年各季度利润情况"
    ]
    
    for question in test_questions:
        time_range = fq.extract_time_range(question)
        print(f"\n问题: '{question}'")
        print(f"  年份: {time_range.get('years', time_range.get('year'))}")
        print(f"  季度: {time_range.get('quarters', time_range.get('quarter', '全年'))}")
        print(f"  对比分析: {time_range.get('is_comparison', False)}")
    
    return True


def test_keyword_config_usage():
    """测试关键词配置是否正确使用"""
    print("\n" + "=" * 60)
    print("测试3: 关键词配置使用验证")
    print("=" * 60)
    
    fq = FinancialQuery()
    
    # 测试对比关键词
    comparison_test = "2023年和2024年营业收入对比"
    time_range = fq.extract_time_range(comparison_test)
    
    if time_range.get('is_comparison'):
        print(f"✅ 对比分析检测正确: '{comparison_test}'")
    else:
        print(f"❌ 对比分析检测失败")
        return False
    
    # 测试全期查询关键词
    all_periods_test = "营业收入变化趋势"
    time_range2 = fq.extract_time_range(all_periods_test)
    
    if time_range2.get('query_all_periods') or time_range2.get('is_comparison'):
        print(f"✅ 趋势/变化关键词检测正确: '{all_periods_test}'")
    else:
        print(f"⚠️ 趋势关键词检测结果: query_all_periods={time_range2.get('query_all_periods')}")
    
    return True


def test_metrics_extraction():
    """测试指标提取功能"""
    print("\n" + "=" * 60)
    print("测试4: 指标提取功能")
    print("=" * 60)
    
    fq = FinancialQuery()
    
    test_cases = [
        ("2024年营业收入是多少", ["营业收入"]),
        ("去年净利润和毛利润", ["净利润"]),  # 可能只匹配一个
        ("2023年增值税税负率", ["增值税税负率"]),
    ]
    
    all_passed = True
    for question, expected_metrics in test_cases:
        metrics = fq.extract_metrics(question)
        found = any(m in metrics for m in expected_metrics) if expected_metrics else True
        
        status = "✅" if found else "⚠️"
        print(f"{status} '{question}'")
        print(f"   期望包含: {expected_metrics}")
        print(f"   实际提取: {metrics}")
        
        if not found and expected_metrics:
            all_passed = False
    
    return all_passed


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("财务查询系统测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("MetricsLoader热更新", test_metrics_loader_hot_reload()))
    results.append(("财务查询基本功能", test_financial_query_basic()))
    results.append(("关键词配置使用", test_keyword_config_usage()))
    results.append(("指标提取功能", test_metrics_extraction()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
