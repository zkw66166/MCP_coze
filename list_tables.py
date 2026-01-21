import sqlite3

def list_tables():
    try:
        conn = sqlite3.connect('database/financial.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(tables)} tables:")
        if 'cash_flow_statements' in tables:
            print(" -> cash_flow_statements FOUND")
        else:
            print(" -> cash_flow_statements NOT FOUND")
        for t in tables:
            print(f"  - {t}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
