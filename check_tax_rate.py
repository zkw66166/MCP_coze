import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def check_tax_rate():
    conn = sqlite3.connect(db_path)
    query = """
    SELECT 
        total_profit, 
        income_tax_expense,
        (income_tax_expense / total_profit) as effective_rate
    FROM income_statements
    WHERE total_profit > 0
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print("--- Tax Rate Check ---")
    print(df)
    conn.close()

if __name__ == "__main__":
    check_tax_rate()
