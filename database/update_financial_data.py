#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补全财务数据库缺失字段

公式:
- total_revenue = operating_revenue + non_operating_income
- cost_of_sales = operating_costs + non_operating_expenses  
- gross_profit = total_revenue - cost_of_sales
"""

import sqlite3

def update_financial_data():
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    
    # 1. 先查看当前数据状态
    print("=" * 60)
    print("更新前数据检查")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, company_id, period_year, period_quarter,
               operating_revenue, non_operating_income,
               operating_costs, non_operating_expenses,
               total_revenue, cost_of_sales, gross_profit
        FROM income_statements
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"ID={row[0]}: operating_revenue={row[4]}, non_operating_income={row[5]}")
        print(f"         operating_costs={row[6]}, non_operating_expenses={row[7]}")
        print(f"         total_revenue={row[8]}, cost_of_sales={row[9]}, gross_profit={row[10]}")
        print()
    
    # 2. 统计需要更新的记录数
    cursor.execute("""
        SELECT COUNT(*) FROM income_statements
        WHERE total_revenue = 0 OR total_revenue IS NULL
    """)
    count = cursor.fetchone()[0]
    print(f"需要更新的记录数: {count}")
    
    # 3. 执行更新
    print("\n" + "=" * 60)
    print("执行数据更新")
    print("=" * 60)
    
    # 更新 total_revenue
    cursor.execute("""
        UPDATE income_statements
        SET total_revenue = COALESCE(operating_revenue, 0) + COALESCE(non_operating_income, 0)
        WHERE total_revenue = 0 OR total_revenue IS NULL
    """)
    print(f"total_revenue 更新行数: {cursor.rowcount}")
    
    # 更新 cost_of_sales
    cursor.execute("""
        UPDATE income_statements
        SET cost_of_sales = COALESCE(operating_costs, 0) + COALESCE(non_operating_expenses, 0)
        WHERE cost_of_sales = 0 OR cost_of_sales IS NULL
    """)
    print(f"cost_of_sales 更新行数: {cursor.rowcount}")
    
    # 更新 gross_profit
    cursor.execute("""
        UPDATE income_statements
        SET gross_profit = total_revenue - cost_of_sales
        WHERE gross_profit = 0 OR gross_profit IS NULL
    """)
    print(f"gross_profit 更新行数: {cursor.rowcount}")
    
    # 4. 提交更改
    conn.commit()
    print("\n✅ 数据更新已提交")
    
    # 5. 验证更新结果
    print("\n" + "=" * 60)
    print("更新后数据验证")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, company_id, period_year, period_quarter,
               total_revenue, cost_of_sales, gross_profit
        FROM income_statements
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"ID={row[0]}: year={row[2]}, Q{row[3]}")
        print(f"         total_revenue={row[4]:,.2f}")
        print(f"         cost_of_sales={row[5]:,.2f}")
        print(f"         gross_profit={row[6]:,.2f}")
        print()
    
    conn.close()
    print("✅ 数据补全完成!")

if __name__ == "__main__":
    update_financial_data()
