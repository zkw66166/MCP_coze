import sqlite3

conn = sqlite3.connect('database/financial.db')
cursor = conn.cursor()

# 查询2024年各季度数据
cursor.execute('''
    SELECT period_quarter, gross_profit_margin, net_profit_margin, 
           sales_invoice_count, purchase_invoice_count,
           sales_expense, admin_expense
    FROM financial_metrics 
    WHERE company_id = 8 AND period_year = 2024 
    ORDER BY period_quarter
''')

rows = cursor.fetchall()

print('=' * 80)
print('公司8 (大华智能制造厂) - 2024年各季度数据分析')
print('=' * 80)
print(f"{'季度':<8} {'毛利率':<10} {'净利率':<10} {'销售发票':<12} {'采购发票':<12} {'销售费用':<15} {'管理费用':<15}")
print('-' * 80)

total_sales_invoice = 0
total_purchase_invoice = 0  
total_sales_expense = 0
total_admin_expense = 0

for r in rows:
    quarter, gpm, npm, sales_inv, purch_inv, sales_exp, admin_exp = r
    
    sales_inv = sales_inv or 0
    purch_inv = purch_inv or 0
    sales_exp = sales_exp or 0
    admin_exp = admin_exp or 0
    
    total_sales_invoice += sales_inv
    total_purchase_invoice += purch_inv
    total_sales_expense += sales_exp
    total_admin_expense += admin_exp
    
    print(f"Q{quarter:<7} {gpm:>8.1f}%  {npm:>8.2f}%  {sales_inv:>10}张  {purch_inv:>10}张  {sales_exp/10000:>12.0f}万  {admin_exp/10000:>12.0f}万")

print('=' * 80)
print('全年汇总（应显示的值）:')
print(f"  销售发票数: {total_sales_invoice} 张")
print(f"  采购发票数: {total_purchase_invoice} 张")  
print(f"  销售费用:   {total_sales_expense/10000:.0f} 万元")
print(f"  管理费用:   {total_admin_expense/10000:.0f} 万元")
print('=' * 80)

# 查看当前API返回什么
print('\n当前API只返回 Q4 的数据（ORDER BY period_quarter DESC LIMIT 1）')
cursor.execute('''
    SELECT period_quarter, sales_invoice_count, purchase_invoice_count,
           sales_expense, admin_expense
    FROM financial_metrics 
    WHERE company_id = 8 AND period_year = 2024 
    ORDER BY period_quarter DESC
    LIMIT 1
''')
q4_row = cursor.fetchone()
print(f"  Q{q4_row[0]} 销售发票: {q4_row[1]} 张 (应该是 {total_sales_invoice})")
print(f"  Q{q4_row[0]} 采购发票: {q4_row[2]} 张 (应该是 {total_purchase_invoice})")
print(f"  Q{q4_row[0]} 销售费用: {q4_row[3]/10000:.0f} 万 (应该是 {total_sales_expense/10000:.0f})")
print(f"  Q{q4_row[0]} 管理费用: {q4_row[4]/10000:.0f} 万 (应该是 {total_admin_expense/10000:.0f})")

conn.close()
