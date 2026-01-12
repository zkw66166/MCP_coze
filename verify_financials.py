import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_financials():
    print("--- Financial Data Verification ---")
    conn = sqlite3.connect(db_path)
    
    # 1. Check Cash Flow Consistency
    print("Checking Cash Flow vs Balance Sheet Delta:")
    query = """
    SELECT company_id, period_year, period_quarter, net_increase_cash, cash_beginning, cash_ending,
           (cash_ending - cash_beginning) as bs_delta
    FROM cash_flow_statements
    """
    df = pd.read_sql_query(query, conn)
    df['diff'] = df['net_increase_cash'] - df['bs_delta']
    df['is_consistent'] = abs(df['diff']) < 0.01
    
    print(df.head())
    print("Inconsistent Rows:", len(df[~df['is_consistent']]))
    
    # 2. Check New Columns Population
    print("\nChecking New Columns Population:")
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(research_expenses), AVG(advertising_expenses) FROM income_statements")
    print("Avg Research/Ads:", cursor.fetchone())
    
    cursor.execute("SELECT AVG(notes_receivable), AVG(notes_payable) FROM balance_sheets")
    print("Avg Notes Rec/Pay:", cursor.fetchone())
    
    conn.close()

if __name__ == "__main__":
    verify_financials()
