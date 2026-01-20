import sqlite3
import pandas as pd

conn = sqlite3.connect('database/financial.db')
df = pd.read_sql_query("PRAGMA table_info(balance_sheets)", conn)
print(df['name'].tolist())
conn.close()
