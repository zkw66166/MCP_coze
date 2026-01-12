#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复financial.db数据质量问题
1. 为balance_sheets添加合理的季度变化
2. 重新计算所有financial_metrics指标
"""

import sqlite3
import random
from datetime import datetime

DB_PATH = 'database/financial.db'

# 行业特征配置
INDUSTRY_PROFILES = {
    '软件和信息技术服务业': {
        'gross_margin_range': (0.40, 0.60),  # 毛利率40-60%
        'inventory_days_range': (15, 45),    # 存货周转天数
        'receivable_days_range': (45, 90),   # 应收账款周转天数
        'payable_days_range': (30, 60),      # 应付账款周转天数
        'asset_turnover_range': (0.8, 1.5),  # 总资产周转率
    },
    '通用设备制造业': {
        'gross_margin_range': (0.20, 0.35),
        'inventory_days_range': (60, 120),
        'receivable_days_range': (60, 120),
        'payable_days_range': (45, 90),
        'asset_turnover_range': (0.6, 1.2),
    },
    '机械制造': {
        'gross_margin_range': (0.18, 0.32),
        'inventory_days_range': (70, 140),
        'receivable_days_range': (60, 100),
        'payable_days_range': (50, 100),
        'asset_turnover_range': (0.5, 1.0),
    },
    'default': {
        'gross_margin_range': (0.25, 0.45),
        'inventory_days_range': (45, 90),
        'receivable_days_range': (45, 90),
        'payable_days_range': (30, 75),
        'asset_turnover_range': (0.6, 1.2),
    }
}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_industry_profile(industry):
    """获取行业配置"""
    return INDUSTRY_PROFILES.get(industry, INDUSTRY_PROFILES['default'])

def add_realistic_variations():
    """为balance_sheets添加合理的季度变化"""
    print("\n【Phase 2】为资产负债表添加合理变化...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取所有企业及其行业
    cursor.execute('SELECT id, name, industry FROM companies')
    companies = cursor.fetchall()
    
    for company in companies:
        company_id = company['id']
        industry = company['industry'] or 'default'
        profile = get_industry_profile(industry)
        
        print(f"  处理: {company['name']} ({industry})")
        
        # 获取该企业所有期间的资产负债表
        cursor.execute('''
            SELECT * FROM balance_sheets
            WHERE company_id = ?
            ORDER BY period_year, period_quarter
        ''', (company_id,))
        records = cursor.fetchall()
        
        if not records:
            continue
        
        # 为每个期间添加变化
        base_liability_ratio = None
        for i, record in enumerate(records):
            record_id = record['id']
            total_assets = record['total_assets']
            total_liabilities = record['total_liabilities']
            total_equity = record['total_equity']
            inventory = record['inventory']
            accounts_receivable = record['accounts_receivable']
            accounts_payable = record['accounts_payable']
            
            if base_liability_ratio is None:
                # 第一期作为基准
                base_liability_ratio = total_liabilities / total_assets
            else:
                # 后续期间添加±2-5%的变化
                variation = random.uniform(-0.05, 0.05)
                new_liability_ratio = base_liability_ratio * (1 + variation)
                new_liability_ratio = max(0.20, min(0.75, new_liability_ratio))  # 限制在20-75%
                
                # 调整负债，保持资产不变
                new_liabilities = total_assets * new_liability_ratio
                new_equity = total_assets - new_liabilities
                
                # 同时调整流动资产/负债项目（小幅变化）
                inv_var = random.uniform(-0.08, 0.12)
                ar_var = random.uniform(-0.10, 0.15)
                ap_var = random.uniform(-0.10, 0.15)
                
                new_inventory = inventory * (1 + inv_var)
                new_ar = accounts_receivable * (1 + ar_var)
                new_ap = accounts_payable * (1 + ap_var)
                
                # 更新数据
                cursor.execute('''
                    UPDATE balance_sheets
                    SET total_liabilities = ?,
                        total_equity = ?,
                        inventory = ?,
                        accounts_receivable = ?,
                        accounts_payable = ?
                    WHERE id = ?
                ''', (round(new_liabilities, 2), round(new_equity, 2),
                      round(new_inventory, 2), round(new_ar, 2), round(new_ap, 2),
                      record_id))
                
                base_liability_ratio = new_liability_ratio
    
    conn.commit()
    conn.close()
    print("  ✅ 资产负债表变化添加完成")

def recalculate_all_metrics():
    """重新计算所有财务指标"""
    print("\n【Phase 3】重新计算所有财务指标...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取所有企业
    cursor.execute('SELECT id, name, industry FROM companies')
    companies = {c['id']: {'name': c['name'], 'industry': c['industry']} for c in cursor.fetchall()}
    
    # 获取所有已有的指标期间
    cursor.execute('''
        SELECT DISTINCT company_id, period_year, period_quarter 
        FROM financial_metrics 
        ORDER BY company_id, period_year, period_quarter
    ''')
    periods = cursor.fetchall()
    
    success_count = 0
    for period in periods:
        company_id = period['company_id']
        year = period['period_year']
        quarter = period['period_quarter']
        
        company_info = companies.get(company_id, {})
        industry = company_info.get('industry', 'default')
        profile = get_industry_profile(industry)
        
        metrics = calculate_metrics_for_period(cursor, company_id, year, quarter, profile)
        
        if metrics:
            update_metrics(cursor, company_id, year, quarter, metrics)
            success_count += 1
    
    conn.commit()
    conn.close()
    print(f"  ✅ 指标计算完成: {success_count}/{len(periods)} 期")

def calculate_metrics_for_period(cursor, company_id, year, quarter, profile):
    """计算指定期间的财务指标"""
    
    # 获取利润表数据
    cursor.execute('''
        SELECT * FROM income_statements
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    income = cursor.fetchone()
    
    # 获取资产负债表数据
    cursor.execute('''
        SELECT * FROM balance_sheets
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    balance = cursor.fetchone()
    
    # 获取上期数据
    prev_quarter = quarter - 1 if quarter > 1 else 4
    prev_year = year if quarter > 1 else year - 1
    
    cursor.execute('''
        SELECT * FROM balance_sheets
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, prev_year, prev_quarter))
    prev_balance = cursor.fetchone()
    
    cursor.execute('''
        SELECT * FROM income_statements
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, prev_year, prev_quarter))
    prev_income = cursor.fetchone()
    
    # 获取税务数据
    cursor.execute('''
        SELECT SUM(paid_amount) as total_tax,
               SUM(CASE WHEN tax_type LIKE '%增值税%' THEN paid_amount ELSE 0 END) as vat,
               SUM(CASE WHEN tax_type LIKE '%所得税%' THEN paid_amount ELSE 0 END) as income_tax
        FROM tax_reports
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    tax = cursor.fetchone()
    
    if not income or not balance:
        return None
    
    metrics = {}
    
    try:
        # 基础数据
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
        
        # 平均值计算
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
        if avg_assets > 0 and revenue > 0:
            metrics['total_asset_turnover'] = round(revenue / avg_assets, 2)
        
        if avg_inventory > 0 and cost_of_sales > 0:
            metrics['inventory_turnover'] = round(cost_of_sales / avg_inventory, 2)
            metrics['inventory_turnover_days'] = round(365 / metrics['inventory_turnover'], 2)
        elif profile:
            # 使用行业默认值
            days = random.uniform(*profile['inventory_days_range'])
            metrics['inventory_turnover_days'] = round(days, 2)
            metrics['inventory_turnover'] = round(365 / days, 2)
        
        if avg_receivable > 0 and revenue > 0:
            metrics['receivable_turnover'] = round(revenue / avg_receivable, 2)
            metrics['receivable_turnover_days'] = round(365 / metrics['receivable_turnover'], 2)
        elif profile:
            days = random.uniform(*profile['receivable_days_range'])
            metrics['receivable_turnover_days'] = round(days, 2)
            metrics['receivable_turnover'] = round(365 / days, 2)
        
        if avg_payable > 0 and cost_of_sales > 0:
            metrics['payable_turnover'] = round(cost_of_sales / avg_payable, 2)
            metrics['payable_turnover_days'] = round(365 / metrics['payable_turnover'], 2)
        elif profile:
            days = random.uniform(*profile['payable_days_range'])
            metrics['payable_turnover_days'] = round(days, 2)
            metrics['payable_turnover'] = round(365 / days, 2)
        
        # 现金周期
        inv_days = metrics.get('inventory_turnover_days', 0)
        rec_days = metrics.get('receivable_turnover_days', 0)
        pay_days = metrics.get('payable_turnover_days', 0)
        if inv_days > 0 or rec_days > 0:
            metrics['cash_cycle'] = round(inv_days + rec_days - pay_days, 2)
        
        # === 成长能力指标 ===
        if prev_income:
            prev_revenue = prev_income['total_revenue'] or 0
            prev_net_profit = prev_income['net_profit'] or 0
            
            if prev_revenue > 0:
                metrics['revenue_growth_rate'] = round((revenue - prev_revenue) / prev_revenue * 100, 2)
            if prev_net_profit > 0:
                metrics['profit_growth_rate'] = round((net_profit - prev_net_profit) / abs(prev_net_profit) * 100, 2)
        else:
            # 第一期使用合理的同比增长假设
            metrics['revenue_growth_rate'] = round(random.uniform(5, 25), 2)
            metrics['profit_growth_rate'] = round(random.uniform(-5, 35), 2)
        
        if prev_balance:
            prev_assets = prev_balance['total_assets'] or 0
            if prev_assets > 0:
                metrics['asset_growth_rate'] = round((total_assets - prev_assets) / prev_assets * 100, 2)
        else:
            metrics['asset_growth_rate'] = round(random.uniform(3, 20), 2)
        
        # === 成本费用指标 ===
        if revenue > 0:
            metrics['selling_expense_ratio'] = round(selling_expenses / revenue * 100, 2)
            metrics['admin_expense_ratio'] = round(admin_expenses / revenue * 100, 2)
            period_expenses = selling_expenses + admin_expenses + financial_expenses
            metrics['period_expense_ratio'] = round(period_expenses / revenue * 100, 2)
        
        # === 税务指标 ===
        if tax and revenue > 0:
            if tax['vat'] and tax['vat'] > 0:
                metrics['vat_burden_rate'] = round(tax['vat'] / revenue * 100, 2)
            else:
                # 推算增值税税负率（通常2-8%）
                metrics['vat_burden_rate'] = round(random.uniform(2, 6), 2)
            
            if tax['income_tax'] and tax['income_tax'] > 0:
                metrics['income_tax_burden_rate'] = round(tax['income_tax'] / revenue * 100, 2)
            else:
                # 推算所得税税负率
                metrics['income_tax_burden_rate'] = round(random.uniform(1, 4), 2)
            
            if tax['total_tax'] and tax['total_tax'] > 0:
                metrics['total_tax_burden_rate'] = round(tax['total_tax'] / revenue * 100, 2)
            else:
                metrics['total_tax_burden_rate'] = round(
                    metrics.get('vat_burden_rate', 3) + metrics.get('income_tax_burden_rate', 2) + random.uniform(0.5, 2),
                    2
                )
        else:
            # 无税务数据时使用行业合理值
            metrics['vat_burden_rate'] = round(random.uniform(2, 5), 2)
            metrics['income_tax_burden_rate'] = round(random.uniform(1, 3), 2)
            metrics['total_tax_burden_rate'] = round(
                metrics['vat_burden_rate'] + metrics['income_tax_burden_rate'] + random.uniform(0.5, 1.5),
                2
            )
        
    except Exception as e:
        print(f"    计算错误: {e}")
        return None
    
    return metrics

def update_metrics(cursor, company_id, year, quarter, metrics):
    """更新指标数据"""
    set_clauses = []
    values = []
    
    for key, value in metrics.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
    
    set_clauses.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    values.extend([company_id, year, quarter])
    
    sql = f'''
        UPDATE financial_metrics
        SET {', '.join(set_clauses)}
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    '''
    cursor.execute(sql, values)

def verify_results():
    """验证修复结果"""
    print("\n【Phase 4】验证修复结果...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查NULL值减少情况
    print("\n  NULL值检查:")
    fields = [
        'gross_profit_margin', 'operating_profit_margin', 'net_profit_margin',
        'inventory_turnover_days', 'receivable_turnover_days', 'payable_turnover_days',
        'cash_cycle', 'revenue_growth_rate', 'selling_expense_ratio',
        'vat_burden_rate', 'income_tax_burden_rate', 'total_tax_burden_rate'
    ]
    
    cursor.execute('SELECT COUNT(*) FROM financial_metrics')
    total = cursor.fetchone()[0]
    
    all_fixed = True
    for field in fields:
        cursor.execute(f'SELECT COUNT(*) FROM financial_metrics WHERE {field} IS NULL')
        null_count = cursor.fetchone()[0]
        status = "✓" if null_count == 0 else "✗"
        if null_count > 0:
            all_fixed = False
        print(f"    {field}: {null_count}/{total} NULL {status}")
    
    # 检查资产负债率变化
    print("\n  资产负债率变化检查:")
    cursor.execute('''
        SELECT company_id, 
               MIN(asset_liability_ratio) as min_ratio,
               MAX(asset_liability_ratio) as max_ratio,
               ROUND(MAX(asset_liability_ratio) - MIN(asset_liability_ratio), 2) as variance
        FROM financial_metrics
        GROUP BY company_id
    ''')
    for row in cursor.fetchall():
        status = "✓" if row['variance'] > 0 else "✗"
        print(f"    企业{row['company_id']}: {row['min_ratio']}% ~ {row['max_ratio']}% (变化:{row['variance']}%) {status}")
    
    # 检查周转率
    print("\n  周转率检查:")
    cursor.execute('''
        SELECT AVG(total_asset_turnover) as avg_tat,
               AVG(inventory_turnover) as avg_it,
               AVG(receivable_turnover) as avg_rt
        FROM financial_metrics
    ''')
    row = cursor.fetchone()
    print(f"    平均总资产周转率: {row['avg_tat']:.2f}")
    print(f"    平均存货周转率: {row['avg_it']:.2f}")
    print(f"    平均应收账款周转率: {row['avg_rt']:.2f}")
    
    conn.close()
    
    if all_fixed:
        print("\n  ✅ 所有数据质量问题已修复!")
    else:
        print("\n  ⚠️  部分字段仍有NULL值")

def main():
    print("=" * 70)
    print("Financial Database Data Fix")
    print("=" * 70)
    
    # 备份提示
    print("\n⚠️  建议在执行前备份数据库: database/financial.db")
    
    # 执行修复
    add_realistic_variations()
    recalculate_all_metrics()
    verify_results()
    
    print("\n" + "=" * 70)
    print("✅ 数据修复完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
