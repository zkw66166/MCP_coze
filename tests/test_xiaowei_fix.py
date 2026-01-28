#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证小微企业优惠查询修复效果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db_query import TaxIncentiveQuery

print("=" * 70)
print("测试: 小微企业优惠查询修复验证")
print("=" * 70)

query = TaxIncentiveQuery()

# 测试1: 小微企业优惠有哪些
print("\n【测试1】问题: '小微企业优惠有哪些'")
print("-" * 50)
results, total, intent = query.search("小微企业优惠有哪些", limit=20)
print(f"\n找到 {total} 条结果:")
for idx, r in enumerate(results[:10], 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")
    
# 检查结果中是否包含小微相关
xiaowei_count = 0
for r in results:
    item = r.get('incentive_items', '') or ''
    rules = r.get('detailed_rules', '') or ''
    qual = r.get('qualification', '') or ''
    if '小微' in item or '小型微利' in item or '小微' in rules or '小型微利' in rules or '小微' in qual or '小型微利' in qual:
        xiaowei_count += 1

print(f"\n✅ 结果中包含'小微/小型微利'的记录: {xiaowei_count}/{len(results)} 条")

# 测试2: 小微企业所得税优惠
print("\n\n【测试2】问题: '小微企业所得税优惠'")
print("-" * 50)
results2, total2, intent2 = query.search("小微企业所得税优惠", limit=10)
print(f"\n找到 {total2} 条结果:")
for idx, r in enumerate(results2[:5], 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")

# 测试3: 高新技术企业有哪些优惠
print("\n\n【测试3】问题: '高新技术企业有哪些优惠'")
print("-" * 50)
results3, total3, intent3 = query.search("高新技术企业有哪些优惠", limit=10)
print(f"\n找到 {total3} 条结果:")
for idx, r in enumerate(results3[:5], 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
