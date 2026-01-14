import sqlite3
import pandas as pd
import os

db_path = r'd:\MyProjects\MCP_coze\database\financial.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== All Tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for table in cursor.fetchall():
    print(table[0])

conn.close()
