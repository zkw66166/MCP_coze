#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证跨税种实体搜索功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db_query import TaxIncentiveQuery

print("=" * 70)
print("测试: 跨税种实体搜索验证")
print("=" * 70)

query = TaxIncentiveQuery()

# 测试1: 直接调用entity_search (跨税种)
print("\n【测试1】直接调用entity_search(['小微企业'])")
print("-" * 50)
results = query.entity_search(["小微企业"], limit=20)
print(f"\n跨税种搜索结果: {len(results)} 条")
for idx, r in enumerate(results, 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")

# 按税种统计
tax_dist = {}
for r in results:
    t = r.get('tax_type', '未知')
    tax_dist[t] = tax_dist.get(t, 0) + 1

print(f"\n按税种统计:")
for t, c in tax_dist.items():
    print(f"  - {t}: {c}条")

# 测试2: 模拟当DeepSeek无法推理税种时的场景
print("\n\n【测试2】问题: '小微优惠' (无税种，触发跨税种搜索)")
print("-" * 50)
# 这个问题不包含完整的"小微企业"，无法匹配核心实体关键词
# 但我们可以测试直接跨税种搜索的效果
results2 = query.entity_search(["小微"], limit=20)
print(f"\n结果: {len(results2)} 条")
for idx, r in enumerate(results2[:10], 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")

# 测试3: 增值税小微企业优惠
print("\n\n【测试3】问题: '增值税小微企业优惠'")
print("-" * 50)
results3, total3, _ = query.search("增值税小微企业优惠", limit=10)
print(f"\n结果: {total3} 条")
for idx, r in enumerate(results3[:5], 1):
    print(f"  {idx}. [{r.get('tax_type', 'N/A'):10}] {r.get('incentive_items', 'N/A')[:40]}")

print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
