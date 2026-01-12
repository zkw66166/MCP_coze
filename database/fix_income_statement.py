#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复利润表数据，添加合理的季度变化
使得计算出的利润率指标在各季度有自然波动
"""

import sqlite3
import random
from datetime import datetime

DB_PATH = 'database/financial.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_current_margins():
    """分析当前各企业各季度的利润率分布"""
    print("【分析】当前利润率分布:")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.name, fm.period_year, fm.period_quarter, 
               fm.gross_profit_margin, fm.operating_profit_margin, fm.net_profit_margin
        FROM financial_metrics fm
        JOIN companies c ON fm.company_id = c.id
        ORDER BY fm.company_id, fm.period_year, fm.period_quarter
    ''')
    
    current_company = None
    for row in cursor.fetchall():
        if row['name'] != current_company:
            current_company = row['name']
            print(f"\n{current_company}:")
        print(f"  {row['period_year']}Q{row['period_quarter']}: "
              f"毛利率={row['gross_profit_margin']:.2f}% "
              f"营业利润率={row['operating_profit_margin']:.2f}% "
              f"净利率={row['net_profit_margin']:.2f}%")
    
    conn.close()

def add_income_statement_variations():
    """为利润表添加合理的季度变化"""
    print("\n【修复】为利润表添加季度变化...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取所有利润表记录
    cursor.execute('''
        SELECT i.*, c.industry
        FROM income_statements i
        JOIN companies c ON i.company_id = c.id
        ORDER BY i.company_id, i.period_year, i.period_quarter
    ''')
    records = cursor.fetchall()
    
    # 按企业分组处理
    company_records = {}
    for record in records:
        company_id = record['company_id']
        if company_id not in company_records:
            company_records[company_id] = []
        company_records[company_id].append(dict(record))
    
    updated_count = 0
    
    for company_id, records in company_records.items():
        print(f"  处理企业ID={company_id} ({len(records)}期)")
        
        for i, record in enumerate(records):
            record_id = record['id']
            revenue = record['total_revenue']
            cost_of_sales = record['cost_of_sales']
            gross_profit = record['gross_profit']
            selling_expenses = record['selling_expenses']
            admin_expenses = record['administrative_expenses']
            financial_expenses = record['financial_expenses']
            operating_profit = record['operating_profit']
            total_profit = record['total_profit']
            income_tax = record['income_tax_expense']
            net_profit = record['net_profit']
            
            # 为各项费用添加随机变化 (±5-15%)
            # 成本变化影响毛利率
            cost_variation = random.uniform(-0.08, 0.12)
            new_cost = cost_of_sales * (1 + cost_variation)
            new_gross_profit = revenue - new_cost
            
            # 销售费用变化
            selling_variation = random.uniform(-0.10, 0.15)
            new_selling = selling_expenses * (1 + selling_variation)
            
            # 管理费用变化
            admin_variation = random.uniform(-0.08, 0.12)
            new_admin = admin_expenses * (1 + admin_variation)
            
            # 财务费用变化
            fin_variation = random.uniform(-0.15, 0.20)
            new_financial = financial_expenses * (1 + fin_variation)
            
            # 税金及附加（小幅变化）
            taxes_surcharges = record['taxes_and_surcharges'] or 0
            taxes_variation = random.uniform(-0.05, 0.10)
            new_taxes_surcharges = taxes_surcharges * (1 + taxes_variation)
            
            # 重新计算营业利润
            new_operating_profit = (new_gross_profit - new_taxes_surcharges - 
                                   new_selling - new_admin - new_financial)
            
            # 营业外收支（小幅变化）
            non_op_income = record['non_operating_income'] or 0
            non_op_expense = record['non_operating_expenses'] or 0
            non_op_income_var = random.uniform(-0.20, 0.30)
            non_op_expense_var = random.uniform(-0.15, 0.25)
            new_non_op_income = non_op_income * (1 + non_op_income_var)
            new_non_op_expense = non_op_expense * (1 + non_op_expense_var)
            
            # 重新计算利润总额
            new_total_profit = new_operating_profit + new_non_op_income - new_non_op_expense
            
            # 重新计算所得税（按原有税率）
            if total_profit and total_profit > 0 and income_tax:
                tax_rate = income_tax / total_profit
            else:
                tax_rate = 0.25  # 默认25%
            
            if new_total_profit > 0:
                new_income_tax = new_total_profit * tax_rate
            else:
                new_income_tax = 0  # 亏损不交所得税
            
            # 重新计算净利润
            new_net_profit = new_total_profit - new_income_tax
            
            # 更新数据库
            cursor.execute('''
                UPDATE income_statements SET
                    cost_of_sales = ?,
                    gross_profit = ?,
                    selling_expenses = ?,
                    administrative_expenses = ?,
                    financial_expenses = ?,
                    taxes_and_surcharges = ?,
                    operating_profit = ?,
                    non_operating_income = ?,
                    non_operating_expenses = ?,
                    total_profit = ?,
                    income_tax_expense = ?,
                    net_profit = ?
                WHERE id = ?
            ''', (
                round(new_cost, 2),
                round(new_gross_profit, 2),
                round(new_selling, 2),
                round(new_admin, 2),
                round(new_financial, 2),
                round(new_taxes_surcharges, 2),
                round(new_operating_profit, 2),
                round(new_non_op_income, 2),
                round(new_non_op_expense, 2),
                round(new_total_profit, 2),
                round(new_income_tax, 2),
                round(new_net_profit, 2),
                record_id
            ))
            updated_count += 1
    
    conn.commit()
    conn.close()
    print(f"  ✅ 更新了 {updated_count} 条利润表记录")

def recalculate_metrics():
    """重新计算financial_metrics表"""
    print("\n【重算】重新计算财务指标...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取所有期间
    cursor.execute('''
        SELECT DISTINCT company_id, period_year, period_quarter 
        FROM financial_metrics
        ORDER BY company_id, period_year, period_quarter
    ''')
    periods = cursor.fetchall()
    
    updated = 0
    for period in periods:
        company_id = period['company_id']
        year = period['period_year']
        quarter = period['period_quarter']
        
        # 获取利润表数据
        cursor.execute('''
            SELECT * FROM income_statements
            WHERE company_id = ? AND period_year = ? AND period_quarter = ?
        ''', (company_id, year, quarter))
        income = cursor.fetchone()
        
        if not income:
            continue
        
        revenue = income['total_revenue'] or 0
        gross_profit = income['gross_profit'] or 0
        operating_profit = income['operating_profit'] or 0
        net_profit = income['net_profit'] or 0
        selling_exp = income['selling_expenses'] or 0
        admin_exp = income['administrative_expenses'] or 0
        financial_exp = income['financial_expenses'] or 0
        
        if revenue > 0:
            gross_margin = round(gross_profit / revenue * 100, 2)
            op_margin = round(operating_profit / revenue * 100, 2)
            net_margin = round(net_profit / revenue * 100, 2)
            selling_ratio = round(selling_exp / revenue * 100, 2)
            admin_ratio = round(admin_exp / revenue * 100, 2)
            period_expense = selling_exp + admin_exp + financial_exp
            period_ratio = round(period_expense / revenue * 100, 2)
            
            cursor.execute('''
                UPDATE financial_metrics SET
                    gross_profit_margin = ?,
                    operating_profit_margin = ?,
                    net_profit_margin = ?,
                    selling_expense_ratio = ?,
                    admin_expense_ratio = ?,
                    period_expense_ratio = ?,
                    updated_at = ?
                WHERE company_id = ? AND period_year = ? AND period_quarter = ?
            ''', (gross_margin, op_margin, net_margin, 
                  selling_ratio, admin_ratio, period_ratio,
                  datetime.now().isoformat(),
                  company_id, year, quarter))
            updated += 1
    
    conn.commit()
    conn.close()
    print(f"  ✅ 更新了 {updated} 条财务指标记录")

def verify_results():
    """验证修复结果"""
    print("\n【验证】修复后利润率分布:")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.name, 
               MIN(fm.gross_profit_margin) as min_gpm,
               MAX(fm.gross_profit_margin) as max_gpm,
               MIN(fm.operating_profit_margin) as min_opm,
               MAX(fm.operating_profit_margin) as max_opm,
               MIN(fm.net_profit_margin) as min_npm,
               MAX(fm.net_profit_margin) as max_npm
        FROM financial_metrics fm
        JOIN companies c ON fm.company_id = c.id
        GROUP BY c.name
    ''')
    
    print("\n各企业利润率变化范围:")
    for row in cursor.fetchall():
        gpm_var = row['max_gpm'] - row['min_gpm']
        opm_var = row['max_opm'] - row['min_opm']
        npm_var = row['max_npm'] - row['min_npm']
        print(f"  {row['name']}:")
        print(f"    毛利率: {row['min_gpm']:.1f}% ~ {row['max_gpm']:.1f}% (变化:{gpm_var:.1f}%)")
        print(f"    营业利润率: {row['min_opm']:.1f}% ~ {row['max_opm']:.1f}% (变化:{opm_var:.1f}%)")
        print(f"    净利率: {row['min_npm']:.1f}% ~ {row['max_npm']:.1f}% (变化:{npm_var:.1f}%)")
    
    conn.close()

def main():
    print("=" * 70)
    print("修复利润表数据，增加季度变化")
    print("=" * 70)
    
    # 分析当前状态
    analyze_current_margins()
    
    # 添加变化
    add_income_statement_variations()
    
    # 重新计算指标
    recalculate_metrics()
    
    # 验证结果
    verify_results()
    
    print("\n" + "=" * 70)
    print("✅ 利润表数据修复完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
