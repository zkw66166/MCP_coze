import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_data():
    conn = sqlite3.connect(db_path)
    print("--- Verification Check ---")

    # 1. Count Records
    count = conn.execute("SELECT COUNT(*) FROM vat_returns").fetchone()[0]
    print(f"Total VAT Returns: {count}")
    
    # 2. Check Sales vs Revenue Constraint (Quarterly Aggregation)
    print("\nChecking Sales <= Revenue Constraint (Sample 5 Quarters):")
    query = """
    SELECT 
        vr.company_id, 
        vr.period_year, 
        (vr.period_month - 1) / 3 + 1 as quarter,
        SUM(vri.amount_current) as total_sales
    FROM vat_returns vr
    JOIN vat_return_items vri ON vr.id = vri.return_id
    WHERE vri.line_no = 1
    GROUP BY vr.company_id, vr.period_year, quarter
    """
    df_vat = pd.read_sql_query(query, conn)
    
    query_inc = """
    SELECT company_id, period_year, period_quarter as quarter, total_revenue 
    FROM income_statements
    """
    df_inc = pd.read_sql_query(query_inc, conn)
    
    merged = pd.merge(df_vat, df_inc, on=['company_id', 'period_year', 'quarter'], how='inner')
    merged['diff'] = merged['total_revenue'] - merged['total_sales']
    merged['is_valid'] = merged['total_sales'] <= merged['total_revenue'] * 1.01 # Allow 1% tolerance for floating point or small logic mismatch
    
    print(merged[['company_id', 'period_year', 'quarter', 'total_sales', 'total_revenue', 'diff', 'is_valid']].head())
    
    invalid_count = len(merged[~merged['is_valid']])
    print(f"\nInvalid Records Found: {invalid_count}")
    if invalid_count > 0:
        print(merged[~merged['is_valid']])
    
    conn.close()

if __name__ == "__main__":
    verify_data()
