#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试总数显示功能"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    ("企业所得税优惠政策有哪些", 20),
    ("个人所得税减免政策", 20),
    ("增值税优惠政策", 20),
]

print("=" * 60)
print("测试总数显示功能")
print("=" * 60)

for question, limit in test_cases:
    print(f"\n问题: {question}")
    print(f"限制: {limit}条")
    
    results, total_count = q.search(question, limit=limit)
    
    print(f"总数: {total_count}条")
    print(f"返回: {len(results)}条")
    
    if total_count > len(results):
        print(f"✅ 提示: 数据库共有{total_count}条,展示前{len(results)}条")
    else:
        print(f"✅ 提示: 找到{total_count}条相关政策")
