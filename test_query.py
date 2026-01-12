#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试优化后的查询功能"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

print("=" * 60)
print("测试优化后的查询功能")
print("=" * 60)

# 测试1: 高新技术企业增值税优惠
print("\n【测试1: 高新技术企业增值税优惠】")
r1 = q.search('高新技术企业有哪些增值税优惠?')
print(f"结果数: {len(r1)}条")
for i, r in enumerate(r1[:5], 1):
    print(f"  {i}. [{r['tax_type']}] {r['project_name'][:40]}")

# 测试2: 小微企业所得税
print("\n【测试2: 小微企业所得税】")
r2 = q.search('小微企业所得税减免政策')
print(f"结果数: {len(r2)}条")
for i, r in enumerate(r2[:5], 1):
    print(f"  {i}. [{r['tax_type']}] {r['project_name'][:40]}")

# 测试3: 农产品增值税
print("\n【测试3: 农产品增值税】")
r3 = q.search('农产品增值税免征')
print(f"结果数: {len(r3)}条")
for i, r in enumerate(r3[:5], 1):
    print(f"  {i}. [{r['tax_type']}] {r['project_name'][:40]}")

print("\n" + "=" * 60)
print("✅ 测试完成!")
print("=" * 60)
