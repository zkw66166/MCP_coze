import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def deep_audit():
    print("--- Deep Audit V2 ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check VAT Schema
    cursor.execute("PRAGMA table_info(vat_returns)")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"VAT Returns Columns: {cols}")
    
    # Check VAT 2025 Q1
    # Assuming 'tax_amount' or similar? Or 'vat_payable'?
    # Let's inspect columns first.
    
    # 2. Check CIT Schema and Data
    print("\nCIT Table Columns:")
    cursor.execute("PRAGMA table_info(tax_returns_income)")
    print([c[1] for c in cursor.fetchall()])
    
    print("CIT Years Present:")
    df_cit = pd.read_sql_query("SELECT company_id, period_year FROM tax_returns_income", conn)
    print(df_cit.groupby('company_id')['period_year'].unique())
    
    # 3. Check for specific gaps in VAT
    # Assume distinct Y/M
    df_vat = pd.read_sql_query("SELECT company_id, period_year, period_month FROM vat_returns ORDER BY company_id, period_year, period_month", conn)
    # Check if 2025-01, 02, 03 exist for all
    for cid in [5, 8, 10, 11]:
        months = df_vat[(df_vat['company_id'] == cid) & (df_vat['period_year'] == 2025)]['period_month'].tolist()
        print(f"Company {cid} 2025 Months: {months}")

    conn.close()

if __name__ == "__main__":
    deep_audit()
