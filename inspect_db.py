import sqlite3

conn = sqlite3.connect('database/financial.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("=== Tables ===")
for t in tables:
    print(f"  {t[0]}")

# Check available periods by company for key tables
print("\n=== Available Periods by Table ===")
key_tables = ['balance_sheets', 'income_statements', 'cash_flow_statements', 
              'vat_returns', 'tax_returns_income', 'tax_returns_stamp', 'account_balances']

for table in key_tables:
    try:
        cursor.execute(f"SELECT DISTINCT company_id, period_year, period_month FROM {table} ORDER BY company_id, period_year, period_month")
        rows = cursor.fetchall()
        print(f"\n{table}:")
        company_periods = {}
        for r in rows:
            cid, year, month = r
            if cid not in company_periods:
                company_periods[cid] = []
            company_periods[cid].append(f"{year}Q{(month-1)//3+1}" if month else f"{year}")
        for cid, periods in company_periods.items():
            print(f"  Company {cid}: {periods}")
    except Exception as e:
        # Try without period_month
        try:
            cursor.execute(f"SELECT DISTINCT company_id, period_year FROM {table} ORDER BY company_id, period_year")
            rows = cursor.fetchall()
            print(f"\n{table} (no month):")
            company_periods = {}
            for r in rows:
                cid, year = r
                if cid not in company_periods:
                    company_periods[cid] = []
                company_periods[cid].append(str(year))
            for cid, periods in company_periods.items():
                print(f"  Company {cid}: {periods}")
        except Exception as e2:
            print(f"\n{table}: Error - {e2}")

conn.close()
