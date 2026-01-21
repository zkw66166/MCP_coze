
import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    
    # Check columns
    cursor.execute("PRAGMA table_info(tax_returns_vat)")
    columns = cursor.fetchall()
    col_names = [c[1] for c in columns]
    print("Columns:", col_names)
    
    if 'period_quarter' in col_names:
        print("\n'period_quarter' exists.")
        # Check distinct values
        cursor.execute("SELECT DISTINCT period_year, period_quarter FROM tax_returns_vat LIMIT 10")
        rows = cursor.fetchall()
        print("\nDistinct Year/Quarter samples:", rows)
    else:
        print("\n'period_quarter' DOES NOT exist.")
        
    # Check data count for 2022-2024
    if 'period_year' in col_names:
        cursor.execute("SELECT period_year, count(*) FROM tax_returns_vat GROUP BY period_year")
        print("\nCount by Year:", cursor.fetchall())

    conn.close()
    
except Exception as e:
    print("Error:", e)
