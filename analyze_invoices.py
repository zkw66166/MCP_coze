import pandas as pd
import sqlite3
import os

base_dir = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版"
db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def analyze_invoices():
    print("--- Analyzing Invoice Data ---")
    
    # Files
    input_inv = os.path.join(base_dir, "进项发票(采购发票).xlsx")
    output_inv = os.path.join(base_dir, "销项发票（销售发票）.xlsx")
    
    for f in [input_inv, output_inv]:
        print(f"\nProcessing: {os.path.basename(f)}")
        if os.path.exists(f):
            try:
                # Read first few rows
                df = pd.read_excel(f, nrows=5)
                print(df.to_string())
                print(f"Columns: {df.columns.tolist()}")
            except Exception as e:
                print(f"Error reading Excel: {e}")
        else:
            print(f"File not found: {f}")

    # DB Schema
    print("\n--- Existing DB Schema ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for 'invoices' or similar
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%invoice%';")
    tables = cursor.fetchall()
    print(f"Tables found: {[t[0] for t in tables]}")
    
    for t in tables:
        t_name = t[0]
        print(f"\nTable: {t_name}")
        cursor.execute(f"PRAGMA table_info({t_name})")
        cols = cursor.fetchall()
        print([c[1] for c in cols])
        
    conn.close()

if __name__ == "__main__":
    analyze_invoices()
