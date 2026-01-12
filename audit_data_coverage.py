import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def audit_data():
    print("--- Auditing Data Coverage ---")
    conn = sqlite3.connect(db_path)
    
    # 1. Get Companies
    companies = pd.read_sql_query("SELECT id, name FROM companies", conn)
    print(f"Companies ({len(companies)}):")
    print(companies)
    
    # 2. Define Expected Periods (2022 Q1 - 2025 Q1)
    years = [2022, 2023, 2024]
    quarters = [1, 2, 3, 4]
    expected_periods = [(y, q) for y in years for q in quarters] + [(2025, 1)]
    print(f"\nExpected Quarters: {len(expected_periods)}")
    
    # 3. Check Income Statements
    print("\n--- Income Statements Coverage ---")
    df_inc = pd.read_sql_query("SELECT company_id, period_year, period_quarter FROM income_statements", conn)
    df_inc['exists'] = 1
    
    # Cross join expected
    missing_inc = []
    for _, comp in companies.iterrows():
        cid = comp['id']
        for y, q in expected_periods:
            match = df_inc[(df_inc['company_id'] == cid) & (df_inc['period_year'] == y) & (df_inc['period_quarter'] == q)]
            if match.empty:
                missing_inc.append((cid, y, q))
                
    if missing_inc:
        print(f"MISSING Income Statements ({len(missing_inc)}):")
        print(missing_inc[:10])
    else:
        print("Income Statements: COMPLETE")

    # 4. Check VAT Returns (Monthly) -> Aggregate to check coverage roughly coverage
    print("\n--- VAT Returns Coverage (Monthly) ---")
    # Expected months: 2022-01 to 2025-03
    df_vat = pd.read_sql_query("SELECT company_id, period_year, period_month FROM vat_returns", conn)
    missing_vat = []
    # Just check counts per quarter or something? 
    # Let's check specific months
    for _, comp in companies.iterrows():
        cid = comp['id']
        for y, q in expected_periods:
            months = [(q-1)*3 + i for i in range(1, 4)]
            for m in months:
                match = df_vat[(df_vat['company_id'] == cid) & (df_vat['period_year'] == y) & (df_vat['period_month'] == m)]
                if match.empty:
                    missing_vat.append((cid, y, m))
    
    if missing_vat:
        print(f"MISSING VAT Returns ({len(missing_vat)}):")
        print(missing_vat[:10])
    else:
        print("VAT Returns: COMPLETE")

    # 5. Check CIT (Annual) -> Actually user said "Tax Returns coverage missing", CIT is annual usually but can be quarterly prepaid?
    # Our table is `tax_returns_income` (Annual).
    # If user wants 2022-2025, we assume 2022, 2023, 2024 annuals. 2025 not due.
    # OR maybe they expect Quarterly prepayment returns? The Excel was "Annual". 
    # Let's check Annuals for 22, 23, 24.
    print("\n--- CIT Returns Coverage (Annual) ---")
    df_cit = pd.read_sql_query("SELECT company_id, period_year FROM tax_returns_income", conn)
    missing_cit = []
    for _, comp in companies.iterrows():
        cid = comp['id']
        for y in [2022, 2023, 2024]:
            match = df_cit[(df_cit['company_id'] == cid) & (df_cit['period_year'] == y)]
            if match.empty:
                missing_cit.append((cid, y))
    
    if missing_cit:
        print(f"MISSING CIT Returns ({len(missing_cit)}):")
        print(missing_cit)
    else:
        print("CIT Returns: COMPLETE")

    conn.close()

if __name__ == "__main__":
    audit_data()
