import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def get_db_info():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Income Statements Schema ---")
    cursor.execute("PRAGMA table_info(income_statements)")
    for col in cursor.fetchall():
        print(col)
        
    print("\n--- Data Range ---")
    # Check periods in income_statements
    try:
        df = pd.read_sql_query("SELECT DISTINCT year, quarter FROM income_statements ORDER BY year, quarter", conn)
        print(df)
    except Exception as e:
        print(f"Error querying periods: {e}")
        
    conn.close()

if __name__ == "__main__":
    get_db_info()
