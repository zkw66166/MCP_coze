#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看financial.db表结构"""

import sqlite3

conn = sqlite3.connect('database/financial.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

print("=" * 60)
print("financial.db 表结构分析")
print("=" * 60)

for table in tables:
    print(f"\n【表: {table}】")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    print("字段:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 获取记录数
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"记录数: {count}")
    
    # 获取前2条示例数据
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 2")
        rows = cursor.fetchall()
        print("示例数据:")
        for row in rows:
            print(f"  {row[:5]}...")  # 只显示前5个字段

conn.close()
