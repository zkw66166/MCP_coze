import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def check_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for t in ["vat_returns", "vat_return_items", "tax_return_income_items", "tax_return_stamp_items"]:
        cursor.execute(f"PRAGMA table_info({t})")
        print(f"\nTable: {t}")
        print([c[1] for c in cursor.fetchall()])
        
    conn.close()

if __name__ == "__main__":
    check_schema()
