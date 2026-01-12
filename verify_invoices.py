import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def verify_invoice_totals():
    print("--- Verifying Invoice Constraints ---")
    conn = sqlite3.connect(db_path)
    
    # 1. Output vs Revenue
    print("\nConstraint 1: Output Invoices <= Revenue")
    query_out = """
    SELECT 
        i.company_id, i.period_year, i.period_month, 
        SUM(i.amount_excluding_tax) as output_inv,
        inc.operating_revenue
    FROM invoices i
    JOIN income_statements inc 
        ON i.company_id = inc.company_id 
        AND i.period_year = inc.period_year 
        AND i.period_month = inc.period_month
    WHERE i.invoice_type = 'OUTPUT'
    GROUP BY i.company_id, i.period_year, i.period_month
    """
    df_out = pd.read_sql_query(query_out, conn)
    df_out['diff'] = df_out['operating_revenue'] - df_out['output_inv']
    df_out['is_valid'] = df_out['output_inv'] <= df_out['operating_revenue'] * 1.001 # Tolerance
    
    print(df_out[['company_id', 'period_year', 'period_month', 'output_inv', 'operating_revenue', 'diff', 'is_valid']].head())
    print("Invalid Output Rows:", len(df_out[~df_out['is_valid']]))
    
    # 2. Input vs Costs
    print("\nConstraint 2: Input Invoices ~= Costs")
    query_in = """
    SELECT 
        i.company_id, i.period_year, i.period_month, 
        SUM(i.amount_excluding_tax) as input_inv,
        inc.operating_costs
    FROM invoices i
    JOIN income_statements inc 
        ON i.company_id = inc.company_id 
        AND i.period_year = inc.period_year 
        AND i.period_month = inc.period_month
    WHERE i.invoice_type = 'INPUT'
    GROUP BY i.company_id, i.period_year, i.period_month
    """
    df_in = pd.read_sql_query(query_in, conn)
    df_in['ratio'] = df_in['input_inv'] / df_in['operating_costs']
    df_in['is_close'] = (df_in['ratio'] >= 0.8) & (df_in['ratio'] <= 1.2) # Allow 20% variance
    
    print(df_in[['company_id', 'period_year', 'period_month', 'input_inv', 'operating_costs', 'ratio', 'is_close']].head())
    print("Outliers Input Rows:", len(df_in[~df_in['is_close']]))
    
    conn.close()

if __name__ == "__main__":
    verify_invoice_totals()
