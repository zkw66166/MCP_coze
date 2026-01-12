import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def check_granularity():
    conn = sqlite3.connect(db_path)
    try:
        # Check if we have monthly data
        df = pd.read_sql_query("SELECT period_year, period_month, COUNT(*) as count FROM income_statements GROUP BY period_year, period_month", conn)
        print(df)
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

if __name__ == "__main__":
    check_granularity()
