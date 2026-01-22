#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理financial_metrics表中的重复数据

问题：每个季度有多条重复记录（如2024 Q1有5条相同记录）
原因：多次运行calculate_metrics.py导致
解决：保留每个(company_id, period_year, period_quarter)的最新一条记录
"""

import sqlite3
from datetime import datetime

def clean_duplicate_metrics():
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("清理 financial_metrics 表重复数据")
    print("=" * 80)
    
    # 1. 查看重复情况
    cursor.execute('''
        SELECT company_id, period_year, period_quarter, COUNT(*) as cnt
        FROM financial_metrics
        GROUP BY company_id, period_year, period_quarter
        HAVING COUNT(*) > 1
        ORDER BY company_id, period_year, period_quarter
    ''')
    
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\n发现 {len(duplicates)} 组重复数据:")
        for row in duplicates[:10]:  # 只显示前10组
            print(f"  公司{row[0]} {row[1]}年Q{row[2]}: {row[3]}条记录")
        if len(duplicates) > 10:
            print(f"  ... 还有 {len(duplicates) - 10} 组重复")
    else:
        print("\n✅ 没有发现重复数据")
        conn.close()
        return
    
    # 2. 删除重复记录，保留每组最新的一条（id最大）
    print("\n开始清理...")
    cursor.execute('''
        DELETE FROM financial_metrics
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM financial_metrics
            GROUP BY company_id, period_year, period_quarter
        )
    ''')
    
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ 已删除 {deleted_count} 条重复记录")
    
    # 3. 验证清理结果
    cursor.execute('SELECT COUNT(*) FROM financial_metrics')
    total_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT company_id, period_year, period_quarter, COUNT(*) 
        FROM financial_metrics
        GROUP BY company_id, period_year, period_quarter
        HAVING COUNT(*) > 1
    ''')
    
    remaining_duplicates = cursor.fetchall()
    
    if remaining_duplicates:
        print(f"\n⚠️ 仍有 {len(remaining_duplicates)} 组重复数据")
    else:
        print(f"\n✅ 清理完成！当前共 {total_count} 条记录，无重复")
    
    conn.close()

if __name__ == '__main__':
    clean_duplicate_metrics()
