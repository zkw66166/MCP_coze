#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试实体过滤功能"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    "集成电路企业有哪些优惠政策",
    "软件企业有哪些优惠政策",
    "高新技术企业有哪些优惠政策",
    "企业所得税优惠政策有哪些",  # 无实体,应返回所有企业所得税
]

print("=" * 60)
print("测试实体过滤功能")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    
    results, total_count, query_intent = q.search(question, limit=20)
    
    print(f"总数: {total_count}条")
    print(f"返回: {len(results)}条")
    print(f"意图: {query_intent}")
    
    if results:
        print("前3条:")
        for i, r in enumerate(results[:3], 1):
            print(f"  {i}. {r['project_name'][:50]}")
