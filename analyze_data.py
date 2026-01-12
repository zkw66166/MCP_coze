import pandas as pd
import sqlite3
import os

excel_path = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\增值税申报表（主表_一般纳税人适用）.xlsx"
db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def analyze_excel():
    print("--- Analysis of Excel File ---")
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return

    try:
        xls = pd.ExcelFile(excel_path)
        print(f"Sheet names: {xls.sheet_names}")
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name, nrows=10) # Read first 10 rows
            print(df.head())
            print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading Excel: {e}")

def analyze_db():
    print("\n--- Analysis of Database Schema ---")
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Show a sample row
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            row = cursor.fetchone()
            print(f"  Sample row: {row}")

        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")

if __name__ == "__main__":
    analyze_excel()
    analyze_db()
