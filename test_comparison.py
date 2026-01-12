#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试多时间段对比分析"""

from modules.financial_query import FinancialQuery

q = FinancialQuery()

# 测试时间提取
print("=" * 60)
print("测试时间提取")
print("=" * 60)

tests = [
    "2023、2024利润率增长情况",
    "2022-2024收入趋势",
    "Q1和Q2毛利率对比",
    "2023年Q1 vs Q2",
    "23年与24年净利润变化"
]

for t in tests:
    result = q.extract_time_range(t)
    print(f"\n问题: {t}")
    print(f"  years: {result.get('years')}")
    print(f"  quarters: {result.get('quarters')}")
    print(f"  is_comparison: {result.get('is_comparison')}")

# 测试多年份查询
print("\n" + "=" * 60)
print("测试多年份查询")
print("=" * 60)

time_range = q.extract_time_range("2023、2024利润率增长")
print(f"\n时间范围: {time_range}")

# 使用第一家公司测试
results = q.execute_query(1, time_range, ['利润'])
print(f"\n查询结果: {len(results)}条")
for r in results:
    print(f"  {r['year']}年Q{r['quarter']}: {r['metric_name']} = {r['value']}")

# 测试对比计算
if results:
    comparison = q.calculate_comparison(results, time_range)
    print(f"\n对比分析: {comparison}")
    
    if comparison.get('has_comparison'):
        formatted = q.format_comparison(comparison, {'name': '测试公司'})
        print(formatted)
