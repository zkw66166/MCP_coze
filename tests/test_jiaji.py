#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试加计扣除查询"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

print("测试: 加计扣除政策有哪些")
print("=" * 60)

results, total, intent = q.search("加计扣除政策有哪些")

print(f"\n总数: {total}条")
print(f"返回: {len(results)}条")
print(f"意图: {intent}")

for i, r in enumerate(results[:5]):
    print(f"\n--- 结果 {i+1} ---")
    print(f"税种: {r.get('税种', 'N/A')}")
    print(f"优惠方式: {r.get('优惠方式', 'N/A')}")
    print(f"具体规定: {r.get('具体优惠规定', 'N/A')[:100]}...")
