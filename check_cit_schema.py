import sqlite3

def check_schema():
    conn = sqlite3.connect('database/financial.db')
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(tax_returns_income)")
        columns = cursor.fetchall()
        if not columns:
            print("Table 'tax_returns_income' does not exist.")
        else:
            print(f"Table 'tax_returns_income' has {len(columns)} columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
