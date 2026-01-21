
import sqlite3
import json
import os

def check_tables():
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='view';")
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    print(f"Tables/Views found: {len(table_names)}")
    if 'tax_returns_vat' in table_names:
        print("✅ tax_returns_vat exists")
    else:
        print("❌ tax_returns_vat MISSING")
        
    if 'vat_return_fact' in table_names:
        print("✅ vat_return_fact exists")
    else:
        print("❌ vat_return_fact MISSING")
    
    # Check data in tax_returns_vat if exists
    if 'tax_returns_vat' in table_names:
        try:
            cursor.execute("SELECT period_year, period_quarter, COUNT(*) FROM tax_returns_vat GROUP BY period_year, period_quarter")
            rows = cursor.fetchall()
            print("\nData in tax_returns_vat:")
            for r in rows:
                print(f"  {r[0]} Q{r[1]}: {r[2]} rows")
        except Exception as e:
            print(f"Error querying tax_returns_vat: {e}")

    conn.close()

def check_config():
    try:
        with open('config/metrics_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        tables = config.get('tables', {})
        found = False
        for t_name, t_info in tables.items():
            fields = t_info.get('fields', {})
            for f_name, f_info in fields.items():
                aliases = f_info.get('aliases', [])
                if '一般项目应纳税额' in aliases:
                    print(f"\n✅ Found '一般项目应纳税额' in table '{t_name}', field '{f_name}'")
                    found = True
                    return
        
        if not found:
            print("\n❌ '一般项目应纳税额' NOT found in metrics_config.json aliases")
            
    except Exception as e:
        print(f"Error reading config: {e}")

if __name__ == "__main__":
    check_tables()
    check_config()
