
import sqlite3

def check_structure():
    conn = sqlite3.connect('d:/MyProjects/MCP_coze/database/financial.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(income_statements)")
    cols = cursor.fetchall()
    print("Income Statements Columns:")
    for c in cols:
        print(c[1])
    conn.close()

if __name__ == "__main__":
    check_structure()
