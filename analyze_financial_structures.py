import pandas as pd
import sqlite3
import os

base_dir = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\财务报表"
db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

files_map = {
    "income_statements": "利润表.xlsx",
    "balance_sheets": "资产负债表.xlsx",
    "account_balances": "科目余额表.xlsx",
    "cash_flow_statements": "现金流量表.xlsx" # Likely new table
}

def analyze_structures():
    print("--- Analyzing Structures ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for table_name, excel_file in files_map.items():
        print(f"\n[{table_name}] vs [{excel_file}]")
        
        # 1. Get DB Schema
        db_cols = set()
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            rows = cursor.fetchall()
            if rows:
                db_cols = {row[1] for row in rows}
                print(f"  DB Columns ({len(db_cols)}): {sorted(list(db_cols))}")
            else:
                print(f"  Table '{table_name}' does not exist in DB.")
        except Exception as e:
            print(f"  Error reading DB table: {e}")

        # 2. Get Excel Headers
        excel_path = os.path.join(base_dir, excel_file)
        if os.path.exists(excel_path):
            try:
                # Read header. Assuming row 0 or 1. Let's inspect first few rows to be sure.
                df = pd.read_excel(excel_path, nrows=5)
                # Usually headers are somewhat complex in these forms. 
                # Let's print the first few rows to manually interpret for now if it's not clean.
                print(f"  Excel Sample Data:")
                print(df.head())
                # Naive header extraction if row 0 is header
                excel_cols = set(df.columns)
                # print(f"  Excel Columns (Naive): {sorted(list(excel_cols))}")
            except Exception as e:
                print(f"  Error reading Excel: {e}")
        else:
            print(f"  Excel file not found: {excel_path}")

    conn.close()

if __name__ == "__main__":
    analyze_structures()
