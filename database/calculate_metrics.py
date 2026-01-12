#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
计算并填充financial_metrics表
从利润表、资产负债表等原始数据计算27个财务指标
"""

import sqlite3
from datetime import datetime

DB_PATH = 'database/financial.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_metrics_for_period(company_id: int, year: int, quarter: int):
    """计算指定期间的财务指标"""
    conn = get_connection()
    cursor = conn.cursor()
    
    metrics = {
        'company_id': company_id,
        'period_year': year,
        'period_quarter': quarter,
    }
    
    # 1. 获取利润表数据
    cursor.execute('''
        SELECT * FROM income_statements
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    income = cursor.fetchone()
    
    # 2. 获取资产负债表数据
    cursor.execute('''
        SELECT * FROM balance_sheets
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    balance = cursor.fetchone()
    
    # 3. 获取上期资产负债表(用于计算平均值)
    prev_quarter = quarter - 1 if quarter > 1 else 4
    prev_year = year if quarter > 1 else year - 1
    cursor.execute('''
        SELECT * FROM balance_sheets
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, prev_year, prev_quarter))
    prev_balance = cursor.fetchone()
    
    # 4. 获取上期利润表(用于计算增长率)
    cursor.execute('''
        SELECT * FROM income_statements
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, prev_year, prev_quarter))
    prev_income = cursor.fetchone()
    
    # 5. 获取税务数据
    cursor.execute('''
        SELECT SUM(paid_amount) as total_tax,
               SUM(CASE WHEN tax_type LIKE '%增值税%' THEN paid_amount ELSE 0 END) as vat,
               SUM(CASE WHEN tax_type LIKE '%所得税%' THEN paid_amount ELSE 0 END) as income_tax
        FROM tax_reports
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    tax = cursor.fetchone()
    
    if not income or not balance:
        conn.close()
        return None
    
    # 计算各项指标
    try:
        revenue = income['total_revenue'] or 0
        gross_profit = income['gross_profit'] or 0
        operating_profit = income['operating_profit'] or 0
        net_profit = income['net_profit'] or 0
        cost_of_sales = income['cost_of_sales'] or 0
        selling_expenses = income['selling_expenses'] or 0
        admin_expenses = income['administrative_expenses'] or 0
        financial_expenses = income['financial_expenses'] or 0
        
        total_assets = balance['total_assets'] or 0
        total_liabilities = balance['total_liabilities'] or 0
        total_equity = balance['total_equity'] or 0
        current_assets = balance['current_assets_total'] or balance.get('current_assets', 0) or 0
        current_liabilities = balance['current_liabilities_total'] or 0
        inventory = balance['inventory'] or 0
        accounts_receivable = balance['accounts_receivable'] or 0
        accounts_payable = balance['accounts_payable'] or 0
        
        # 平均值计算(如果有上期数据)
        if prev_balance:
            avg_assets = (total_assets + (prev_balance['total_assets'] or 0)) / 2
            avg_equity = (total_equity + (prev_balance['total_equity'] or 0)) / 2
            avg_inventory = (inventory + (prev_balance['inventory'] or 0)) / 2
            avg_receivable = (accounts_receivable + (prev_balance['accounts_receivable'] or 0)) / 2
            avg_payable = (accounts_payable + (prev_balance['accounts_payable'] or 0)) / 2
        else:
            avg_assets = total_assets
            avg_equity = total_equity
            avg_inventory = inventory
            avg_receivable = accounts_receivable
            avg_payable = accounts_payable
        
        # === 盈利能力指标 ===
        if revenue > 0:
            metrics['gross_profit_margin'] = round(gross_profit / revenue * 100, 2)
            metrics['operating_profit_margin'] = round(operating_profit / revenue * 100, 2)
            metrics['net_profit_margin'] = round(net_profit / revenue * 100, 2)
        
        if avg_assets > 0:
            metrics['roa'] = round(net_profit / avg_assets * 100, 2)
        
        if avg_equity > 0:
            metrics['roe'] = round(net_profit / avg_equity * 100, 2)
        
        # === 偿债能力指标 ===
        if total_assets > 0:
            metrics['asset_liability_ratio'] = round(total_liabilities / total_assets * 100, 2)
        
        if current_liabilities > 0:
            metrics['current_ratio'] = round(current_assets / current_liabilities, 2)
            metrics['quick_ratio'] = round((current_assets - inventory) / current_liabilities, 2)
        
        if financial_expenses > 0:
            metrics['interest_coverage_ratio'] = round((operating_profit + financial_expenses) / financial_expenses, 2)
        
        # === 运营效率指标 ===
        if avg_assets > 0:
            metrics['total_asset_turnover'] = round(revenue / avg_assets, 2)
        
        if avg_inventory > 0:
            metrics['inventory_turnover'] = round(cost_of_sales / avg_inventory, 2)
            if metrics['inventory_turnover'] > 0:
                metrics['inventory_turnover_days'] = round(365 / metrics['inventory_turnover'], 2)
        
        if avg_receivable > 0:
            metrics['receivable_turnover'] = round(revenue / avg_receivable, 2)
            if metrics['receivable_turnover'] > 0:
                metrics['receivable_turnover_days'] = round(365 / metrics['receivable_turnover'], 2)
        
        if avg_payable > 0:
            metrics['payable_turnover'] = round(cost_of_sales / avg_payable, 2)
            if metrics['payable_turnover'] > 0:
                metrics['payable_turnover_days'] = round(365 / metrics['payable_turnover'], 2)
        
        # 现金周期
        inv_days = metrics.get('inventory_turnover_days', 0)
        rec_days = metrics.get('receivable_turnover_days', 0)
        pay_days = metrics.get('payable_turnover_days', 0)
        if inv_days or rec_days:
            metrics['cash_cycle'] = round(inv_days + rec_days - pay_days, 2)
        
        # === 成长能力指标 ===
        if prev_income:
            prev_revenue = prev_income['total_revenue'] or 0
            prev_net_profit = prev_income['net_profit'] or 0
            
            if prev_revenue > 0:
                metrics['revenue_growth_rate'] = round((revenue - prev_revenue) / prev_revenue * 100, 2)
            if prev_net_profit > 0:
                metrics['profit_growth_rate'] = round((net_profit - prev_net_profit) / prev_net_profit * 100, 2)
        
        if prev_balance:
            prev_assets = prev_balance['total_assets'] or 0
            if prev_assets > 0:
                metrics['asset_growth_rate'] = round((total_assets - prev_assets) / prev_assets * 100, 2)
        
        # === 成本费用指标 ===
        if revenue > 0:
            metrics['selling_expense_ratio'] = round(selling_expenses / revenue * 100, 2)
            metrics['admin_expense_ratio'] = round(admin_expenses / revenue * 100, 2)
            period_expenses = selling_expenses + admin_expenses + financial_expenses
            metrics['period_expense_ratio'] = round(period_expenses / revenue * 100, 2)
        
        # === 税务指标 ===
        if tax and revenue > 0:
            if tax['vat']:
                metrics['vat_burden_rate'] = round(tax['vat'] / revenue * 100, 2)
            if tax['income_tax']:
                metrics['income_tax_burden_rate'] = round(tax['income_tax'] / revenue * 100, 2)
            if tax['total_tax']:
                metrics['total_tax_burden_rate'] = round(tax['total_tax'] / revenue * 100, 2)
        
    except Exception as e:
        print(f"  计算错误: {e}")
        conn.close()
        return None
    
    conn.close()
    return metrics

def save_metrics(metrics: dict):
    """保存指标到数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    
    columns = list(metrics.keys())
    placeholders = ','.join(['?' for _ in columns])
    columns_str = ','.join(columns)
    
    cursor.execute(f'''
        INSERT OR REPLACE INTO financial_metrics ({columns_str})
        VALUES ({placeholders})
    ''', list(metrics.values()))
    
    conn.commit()
    conn.close()

def calculate_all_metrics():
    """计算所有企业所有期间的指标"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取所有企业
    cursor.execute('SELECT id, name FROM companies')
    companies = cursor.fetchall()
    
    # 获取所有已有的利润表期间
    cursor.execute('''
        SELECT DISTINCT company_id, period_year, period_quarter 
        FROM income_statements 
        ORDER BY company_id, period_year, period_quarter
    ''')
    periods = cursor.fetchall()
    
    conn.close()
    
    company_names = {c['id']: c['name'] for c in companies}
    
    print(f"共 {len(companies)} 家企业, {len(periods)} 个期间需要计算")
    
    success_count = 0
    for period in periods:
        company_id, year, quarter = period['company_id'], period['period_year'], period['period_quarter']
        company_name = company_names.get(company_id, f"企业{company_id}")
        
        metrics = calculate_metrics_for_period(company_id, year, quarter)
        if metrics:
            save_metrics(metrics)
            success_count += 1
            print(f"  ✓ {company_name} {year}年Q{quarter}")
        else:
            print(f"  ✗ {company_name} {year}年Q{quarter} - 数据不足")
    
    print(f"\n✅ 计算完成: {success_count}/{len(periods)} 个期间")

if __name__ == '__main__':
    print("=" * 60)
    print("计算财务指标")
    print("=" * 60)
    
    calculate_all_metrics()
    
    # 显示计算结果统计
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM financial_metrics')
    count = cursor.fetchone()[0]
    print(f"\n📊 financial_metrics表当前共 {count} 条记录")
    conn.close()
