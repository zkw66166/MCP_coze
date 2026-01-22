import sqlite3
import os
import pandas as pd

# Path to database
DB_PATH = os.path.join('database', 'financial.db')

def inspect_data(company_id, year):
    conn = sqlite3.connect(DB_PATH)
    try:
        print(f"--- Inspecting Data for Company ID: {company_id}, Year: {year} ---")

        # 1. Check Companies Table
        print("\n[1. Companies Table]")
        df_comp = pd.read_sql_query(f"SELECT id, name FROM companies WHERE id = {company_id}", conn)
        print(df_comp)

        # 2. Check Financial Metrics (Q4 check)
        print("\n[2. Financial Metrics]")
        df_fm = pd.read_sql_query(f"SELECT period_year, period_quarter, asset_liability_ratio, revenue_growth_rate FROM financial_metrics WHERE company_id = {company_id} AND period_year = {year}", conn)
        print(df_fm)
        if df_fm.empty:
            print("  ! No financial_metrics found.")
        elif not any(df_fm['period_quarter'] == 4):
            print("  ! No Q4 data in financial_metrics. Profile relies on Q4 for stock metrics.")

        # 3. Check Balance Sheets (Raw Data)
        print("\n[3. Balance Sheets]")
        df_bs = pd.read_sql_query(f"SELECT period_year, period_quarter, total_assets FROM balance_sheets WHERE company_id = {company_id} AND period_year = {year}", conn)
        print(df_bs)

        # 4. Check Income Statements (Raw Data)
        print("\n[4. Income Statements]")
        df_is = pd.read_sql_query(f"SELECT period_year, period_quarter, total_revenue, net_profit FROM income_statements WHERE company_id = {company_id} AND period_year = {year}", conn)
        print(df_is)

        # 5. Check Tax Returns VAT
        print("\n[5. Tax Returns VAT]")
        try:
            df_vat = pd.read_sql_query(f"SELECT period_year, period_month, gen_tax_payable_current FROM tax_returns_vat WHERE company_id = {company_id} AND period_year = {year}", conn)
            print(df_vat)
        except Exception as e:
            print(f"  Error reading tax_returns_vat: {e}")

        # 6. Check Invoices
        print("\n[6. Invoices]")
        df_inv = pd.read_sql_query(f"SELECT COUNT(*) as count, invoice_type FROM invoices WHERE company_id = {company_id} AND period_year = {year} GROUP BY invoice_type", conn)
        print(df_inv)

        # 7. Check Customer Analysis
        print("\n[7. Customer Analysis]")
        df_cust = pd.read_sql_query(f"SELECT customer_name, total_sales FROM customer_analysis WHERE company_id = {company_id} AND period_year = {year} LIMIT 5", conn)
        print(df_cust)

        # 8. Check Supplier Analysis
        print("\n[8. Supplier Analysis]")
        df_supp = pd.read_sql_query(f"SELECT supplier_name, total_purchase FROM supplier_analysis WHERE company_id = {company_id} AND period_year = {year} LIMIT 5", conn)
        print(df_supp)

    finally:
        conn.close()

if __name__ == "__main__":
    inspect_data(8, 2024)
