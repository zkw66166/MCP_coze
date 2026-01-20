
import sqlite3

def inspect_db():
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    relevant_tables = ['v_vat_summary', 'v_vat_annual_summary']
    print("Inspecting VAT Views:")
    for table_name in relevant_tables:
        print(f"\n--- {table_name} ---")
        # For views we can treat them like tables for pragma table_info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if not columns:
            print("  (Table not found or empty schema)")
            continue
        for col in columns:
            # cid, name, type, notnull, dflt_value, pk
            print(f"  {col[1]} ({col[2]})")
    conn.close()

if __name__ == "__main__":
    inspect_db()
