#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试结构化查询"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    "个人所得税减免政策有哪些",
    "个人所得税优惠政策有哪些",
    "印花税减免政策有哪些",
    "增值税优惠政策有哪些",
]

print("=" * 60)
print("测试结构化查询")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    
    # 提取税种
    tax_type, incentives = q._extract_tax_and_incentive(question)
    print(f"  提取税种: {tax_type}")
    print(f"  提取优惠词: {incentives}")
    
    # 查询
    results = q.search(question, limit=10)
    print(f"  查询结果: {len(results)}条")
    
    if results:
        print("  前3条:")
        for i, r in enumerate(results[:3], 1):
            print(f"    {i}. [{r['tax_type']}] {r['project_name'][:40]} - {r['incentive_method']}")
