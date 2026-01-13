
import sqlite3
import pandas as pd

def check_metrics_data():
    conn = sqlite3.connect('d:/MyProjects/MCP_coze/database/financial.db')
    
    # Check vat_burden_rate for 2023
    print("\n--- VAT_BURDEN_RATE (2023, Company 1) ---")
    try:
        df = pd.read_sql_query("SELECT period_year, period_quarter, vat_burden_rate FROM financial_metrics WHERE company_id=1 AND period_year=2023", conn)
        print(df)
    except Exception as e:
        print(e)
        
    conn.close()

if __name__ == "__main__":
    check_metrics_data()
