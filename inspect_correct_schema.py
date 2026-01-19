
import sqlite3
import os

db_path = 'database/financial.db'
tables = [
    'account_balances', 
    'balance_sheets', 
    'income_statements', 
    'cash_flow_statements', 
    'vat_returns', 
    'vat_return_items',
    'tax_returns_income', 
    'tax_returns_stamp',
    'tax_return_stamp_items'
]

conn = sqlite3.connect(db_path)
c = conn.cursor()

with open("correct_schema.txt", "w", encoding="utf-8") as f:
    for table in tables:
        f.write(f"\n--- {table} ---\n")
        try:
            c.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in c.fetchall()]
            f.write(f"Columns: {cols}\n")
            
            # Sample row
            c.execute(f"SELECT * FROM {table} LIMIT 1")
            row = c.fetchone()
            f.write(f"Sample: {row}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

conn.close()
print("Done")
