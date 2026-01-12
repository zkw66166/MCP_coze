import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_cit_data():
    conn = sqlite3.connect(db_path)
    print("--- CIT Verification Check ---")

    # 1. Count Records
    count = conn.execute("SELECT COUNT(*) FROM tax_returns_income").fetchone()[0]
    print(f"Total CIT Returns: {count}")
    
    # 2. Check Tax Payable vs Annual Tax Expense
    print("\nChecking Tax Payable consistency:")
    query = """
    SELECT 
        tri.company_id,
        tri.period_year,
        trii.amount as tax_return_payable
    FROM tax_returns_income tri
    JOIN tax_return_income_items trii ON tri.id = trii.return_id
    WHERE trii.line_no = 31 -- 实际应纳所得税额
    """
    df_cit = pd.read_sql_query(query, conn)
    
    query_fin = """
    SELECT 
        company_id,
        period_year,
        SUM(income_tax_expense) as annual_tax_expense
    FROM income_statements
    GROUP BY company_id, period_year
    """
    df_fin = pd.read_sql_query(query_fin, conn)
    
    merged = pd.merge(df_cit, df_fin, on=['company_id', 'period_year'])
    merged['diff'] = merged['tax_return_payable'] - merged['annual_tax_expense']
    merged['is_exact'] = abs(merged['diff']) < 0.01
    
    print(merged.head())
    
    invalid = merged[~merged['is_exact']]
    print(f"\nDiscrepancies Found: {len(invalid)}")
    if len(invalid) > 0:
        print(invalid)
    
    conn.close()

if __name__ == "__main__":
    verify_cit_data()
