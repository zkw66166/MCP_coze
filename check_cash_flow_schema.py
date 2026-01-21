import sqlite3

def check_schema():
    conn = sqlite3.connect('financial.db')
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(cash_flow_statements)")
        columns = cursor.fetchall()
        if not columns:
            print("Table 'cash_flow_statements' does not exist or has no columns.")
        else:
            print(f"Table 'cash_flow_statements' has {len(columns)} columns.")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
