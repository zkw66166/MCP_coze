
import sqlite3
import pandas as pd

db_path = "D:\\MyProjects\\MCP_coze\\financial.db"
tables = [
    "subject_balance", 
    "balance_sheet", 
    "income_statements", 
    "cash_flow_statements", 
    "vat_returns", 
    "tax_returns_income", 
    "tax_returns_stamp"
]

def inspect_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open("schema_details.txt", "w", encoding="utf-8") as f:
        for table in tables:
            f.write(f"\n--- Table: {table} ---\n")
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                f.write(f"Columns: {', '.join(col_names)}\n")
                
                # Get a sample row to see data types/content roughly
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                row = cursor.fetchone()
                f.write(f"Sample: {row}\n")
            except Exception as e:
                f.write(f"Error reading {table}: {e}\n")
    
    conn.close()
    print("Schema inspection complete. Check schema_details.txt")

if __name__ == "__main__":
    inspect_schema()
