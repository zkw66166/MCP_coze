#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试加计扣除在数据库中的记录"""

import sqlite3

conn = sqlite3.connect('database/tax_incentives.db')
cursor = conn.cursor()

# 搜索加计扣除
cursor.execute("""
    SELECT tax_type, project_name, incentive_method, detailed_rules
    FROM tax_incentives 
    WHERE detailed_rules LIKE '%加计扣除%' 
    OR project_name LIKE '%加计扣除%'
    OR incentive_method LIKE '%加计扣除%'
""")

results = cursor.fetchall()
print(f"加计扣除相关记录: {len(results)}条")

for i, r in enumerate(results[:10]):
    print(f"\n--- {i+1} ---")
    print(f"税种: {r[0]}")
    print(f"项目: {r[1][:50] if r[1] else 'N/A'}...")
    print(f"优惠方式: {r[2]}")
    print(f"规定: {r[3][:80] if r[3] else 'N/A'}...")

conn.close()
