import sqlite3

def inspect_tables():
    conn = sqlite3.connect('database/tax_incentives.db')
    cursor = conn.cursor()
    
    print("=== Tables in tax_incentives.db ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
        
    print("\n=== Structure of tax_incentives_fts ===")
    try:
        cursor.execute("PRAGMA table_info(tax_incentives_fts)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Could not inspect FTS structure: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_tables()
