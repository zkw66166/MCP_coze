import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_tax_regen():
    print("--- Verifying Tax Regeneration ---")
    conn = sqlite3.connect(db_path)
    
    # 1. Row Counts
    # VAT: 4 companies * 13 quarters * 3 months = 156 records
    n_vat = pd.read_sql_query("SELECT count(*) as cnt FROM vat_returns", conn).iloc[0]['cnt']
    print(f"VAT Returns Count: {n_vat} (Expected ~156)")
    
    # Stamp: 4 companies * 13 quarters = 52 records
    n_stamp = pd.read_sql_query("SELECT count(*) as cnt FROM tax_returns_stamp", conn).iloc[0]['cnt']
    print(f"Stamp Returns Count: {n_stamp} (Expected 52)")
    
    # CIT: 4 companies * 3 years (2022-2024) = 12 records
    n_cit = pd.read_sql_query("SELECT count(*) as cnt FROM tax_returns_income", conn).iloc[0]['cnt']
    print(f"CIT Returns Count: {n_cit} (Expected 12)")
    
    # 2. Logic Check (Sample)
    # Check VAT 2025 Q1 existence for one company
    print("\nVAT 2025 Q1 Check (Company 5):")
    df_v25 = pd.read_sql_query("SELECT period_month FROM vat_returns WHERE company_id=5 AND period_year=2025", conn)
    print(f"Months present: {df_v25['period_month'].tolist()}")
    
    conn.close()

if __name__ == "__main__":
    verify_tax_regen()
