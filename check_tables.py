import sqlite3

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def list_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    conn.close()

if __name__ == "__main__":
    list_tables()
