#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析financial.db数据质量问题"""

import sqlite3
from collections import defaultdict

DB_PATH = 'database/financial.db'

def analyze():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 70)
    print("financial.db 数据质量分析报告")
    print("=" * 70)
    
    # 1. 分析financial_metrics表的NULL值
    print("\n【1. financial_metrics表NULL值分析】")
    cursor.execute('PRAGMA table_info(financial_metrics)')
    cols = [c[1] for c in cursor.fetchall()]
    
    null_fields = []
    for col in cols:
        cursor.execute(f'SELECT COUNT(*) FROM financial_metrics WHERE {col} IS NULL')
        null_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM financial_metrics')
        total = cursor.fetchone()[0]
        if null_count > 0:
            pct = round(null_count/total*100, 1)
            null_fields.append((col, null_count, total, pct))
            print(f"  {col}: {null_count}/{total} NULL ({pct}%)")
    
    # 2. 检查资产负债率一致性问题
    print("\n【2. 资产负债率一致性检查】")
    cursor.execute('''
        SELECT company_id, period_year, asset_liability_ratio
        FROM financial_metrics
        ORDER BY company_id, period_year
    ''')
    rows = cursor.fetchall()
    company_ratios = defaultdict(list)
    for row in rows:
        company_ratios[row['company_id']].append(row['asset_liability_ratio'])
    
    for company_id, ratios in company_ratios.items():
        unique_ratios = set(ratios)
        if len(unique_ratios) == 1:
            print(f"  企业ID={company_id}: 所有{len(ratios)}期资产负债率相同={ratios[0]}% (异常!)")
        else:
            print(f"  企业ID={company_id}: 资产负债率范围={min(ratios)}-{max(ratios)}%")
    
    # 3. 验证资产负债率计算公式
    print("\n【3. 资产负债率计算验证】")
    cursor.execute('''
        SELECT bs.company_id, bs.period_year, bs.period_quarter,
               bs.total_assets, bs.total_liabilities,
               ROUND(bs.total_liabilities * 100.0 / bs.total_assets, 2) as calc_ratio,
               fm.asset_liability_ratio as stored_ratio
        FROM balance_sheets bs
        JOIN financial_metrics fm ON bs.company_id = fm.company_id 
            AND bs.period_year = fm.period_year 
            AND bs.period_quarter = fm.period_quarter
        LIMIT 5
    ''')
    for row in cursor.fetchall():
        d = dict(row)
        match = "✓" if abs(d['calc_ratio'] - d['stored_ratio']) < 0.1 else "✗"
        print(f"  {d['period_year']}Q{d['period_quarter']}: 计算={d['calc_ratio']}% 存储={d['stored_ratio']}% {match}")
    
    # 4. 检查利润表数据完整性
    print("\n【4. income_statements数据样本】")
    cursor.execute('SELECT * FROM income_statements LIMIT 2')
    for row in cursor.fetchall():
        d = dict(row)
        print(f"  {d['period_year']}Q{d['period_quarter']}:")
        print(f"    营收:{d['total_revenue']:,.0f} 销售成本:{d['cost_of_sales']} 毛利:{d['gross_profit']}")
        print(f"    销售费用:{d['selling_expenses']} 管理费用:{d['administrative_expenses']} 财务费用:{d['financial_expenses']}")
        print(f"    净利润:{d['net_profit']:,.0f}")
    
    # 5. 检查周转率数据
    print("\n【5. 周转率指标检查】")
    cursor.execute('''
        SELECT total_asset_turnover, inventory_turnover, receivable_turnover, payable_turnover
        FROM financial_metrics LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"  总资产周转:{row[0]} 存货周转:{row[1]} 应收周转:{row[2]} 应付周转:{row[3]}")
    
    # 6. 检查企业信息
    print("\n【6. 企业信息】")
    cursor.execute('SELECT * FROM companies')
    for row in cursor.fetchall():
        d = dict(row)
        print(f"  ID={d['id']} 名称:{d['name']} 行业:{d['industry']} 规模:{d['company_scale']}")
    
    # 7. 检查其他表的数据问题
    print("\n【7. 其他表空值检查】")
    tables = ['companies', 'balance_sheets', 'income_statements', 'tax_reports']
    for table in tables:
        cursor.execute(f'PRAGMA table_info({table})')
        cols = [c[1] for c in cursor.fetchall()]
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        total = cursor.fetchone()[0]
        empty_cols = []
        for col in cols:
            cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR {col} = ""')
            count = cursor.fetchone()[0]
            if count > 0:
                empty_cols.append(f"{col}({count})")
        if empty_cols:
            print(f"  {table}: {', '.join(empty_cols[:5])}...")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == '__main__':
    analyze()
