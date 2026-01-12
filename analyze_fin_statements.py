import pandas as pd
import os
import sqlite3

source_dir = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\财务报表"
db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

files = [
    "利润表.xlsx",
    "资产负债表.xlsx",
    "科目余额表.xlsx",
    "现金流量表.xlsx"
]

def analyze_excels():
    print("--- Analyzing Excel Templates ---")
    for fname in files:
        fpath = os.path.join(source_dir, fname)
        print(f"\n[{fname}]")
        if not os.path.exists(fpath):
            print("File not found.")
            continue
        try:
            df = pd.read_excel(fpath, nrows=50) # Read enough rows to see structure
            print(df.to_string()) # Print structure
        except Exception as e:
            print(f"Error: {e}")

def inspect_db_schema():
    print("\n--- Inspecting Database Schema ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['income_statements', 'balance_sheets', 'account_balances']
    for table in tables:
        print(f"\nTable: {table}")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            for col in cols:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    analyze_excels()
    inspect_db_schema()
