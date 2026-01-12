import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_data():
    conn = sqlite3.connect(db_path)
    print("--- Stamp Duty Verification Check ---")

    # 1. Count Records
    count = conn.execute("SELECT COUNT(*) FROM tax_returns_stamp").fetchone()[0]
    print(f"Total Stamp Duty Returns: {count}")
    
    # 2. Check Tax Base vs Revenue and Calculation
    print("\nChecking Calculation Logic:")
    query = """
    SELECT 
        trs.company_id,
        trs.period_year,
        trs.period_quarter,
        trsi.tax_base,
        trsi.tax_amount,
        fin.total_revenue
    FROM tax_returns_stamp trs
    JOIN tax_return_stamp_items trsi ON trs.id = trsi.return_id
    JOIN income_statements fin ON trs.company_id = fin.company_id 
        AND trs.period_year = fin.period_year 
        AND trs.period_quarter = fin.period_quarter
    """
    df = pd.read_sql_query(query, conn)
    
    # Logic: Amount = Base * 0.0003 * 0.5
    # Allow small float diff
    df['expected_amount'] = df['tax_base'] * 0.0003 * 0.5
    df['diff'] = df['tax_amount'] - df['expected_amount']
    df['is_valid_base'] = abs(df['tax_base'] - df['total_revenue']) < 0.1
    df['is_valid_calc'] = abs(df['diff']) < 0.1
    
    print(df[['company_id', 'period_year', 'period_quarter', 'tax_base', 'total_revenue', 'tax_amount', 'expected_amount', 'is_valid_calc']].head())
    
    invalid = df[~(df['is_valid_base'] & df['is_valid_calc'])]
    print(f"\nInvalid Records Found: {len(invalid)}")
    if len(invalid) > 0:
        print(invalid)
    
    conn.close()

if __name__ == "__main__":
    verify_data()
