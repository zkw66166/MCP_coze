import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def deep_audit():
    print("--- Deep Audit ---")
    conn = sqlite3.connect(db_path)
    
    # Check 2025 Q1 explicitly
    print("\nChecking 2025 Q1 for Income Statements:")
    df_25q1 = pd.read_sql_query("SELECT * FROM income_statements WHERE period_year=2025 AND period_quarter=1", conn)
    print(df_25q1)
    
    if df_25q1.empty:
        print("ALERT: 2025 Q1 Income Statements are MISSING.")
    else:
        print(f"Found {len(df_25q1)} records for 2025 Q1.")
        print(df_25q1[['company_id', 'total_revenue']])

    # Check Tax Returns Stamp
    print("\nChecking Stamp Duty (Expected 13 quarters/company):")
    df_stamp = pd.read_sql_query("SELECT company_id, count(*) as cnt FROM tax_returns_stamp GROUP BY company_id", conn)
    print(df_stamp)
    
    # Check VAT 2025 Q1 (Months 1, 2, 3)
    print("\nChecking VAT 2025 (Months 1-3):")
    df_vat = pd.read_sql_query("SELECT company_id, period_month, tax_payable FROM vat_returns WHERE period_year=2025", conn)
    print(df_vat)
    
    # Check if we need Quarterly CIT
    # Current CIT table is Annual. User might want Quarterly.
    print("\nCIT Table Structure:")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tax_returns_income)")
    print([c[1] for c in cursor.fetchall()])
    
    conn.close()

if __name__ == "__main__":
    deep_audit()
