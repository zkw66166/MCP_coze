import sqlite3
import pandas as pd
import os

db_path = r'd:\MyProjects\MCP_coze\database\financial.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get schema for tax_returns_income
print("=== Schema: tax_returns_income ===")
cursor.execute("PRAGMA table_info(tax_returns_income)")
for col in cursor.fetchall():
    print(col)

# Get schema for tax_return_income_items
print("\n=== Schema: tax_return_income_items ===")
cursor.execute("PRAGMA table_info(tax_return_income_items)")
for col in cursor.fetchall():
    print(col)

# Get unique item_names from tax_return_income_items
print("\n=== Unique item_names in tax_return_income_items ===")
df_items = pd.read_sql_query("SELECT DISTINCT item_name FROM tax_return_income_items", conn)
print(df_items)

# Sample data
print("\n=== Sample data: tax_return_income_items (first 5) ===")
df_sample_items = pd.read_sql_query("SELECT * FROM tax_return_income_items LIMIT 5", conn)
print(df_sample_items)

print("\n=== Sample data: tax_returns_income (first 5) ===")
df_sample_income = pd.read_sql_query("SELECT * FROM tax_returns_income LIMIT 5", conn)
print(df_sample_income)

conn.close()
