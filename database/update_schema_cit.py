import sqlite3
import os

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def update_schema():
    print(f"Updating schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. tax_returns_income (Annual Return Meta)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_returns_income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        filing_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, period_year)
    );
    """)
    print("Created table: tax_returns_income")

    # 2. tax_return_income_items (Return Body)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_return_income_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER NOT NULL,
        line_no INTEGER,
        item_name TEXT,
        amount REAL DEFAULT 0,
        FOREIGN KEY (return_id) REFERENCES tax_returns_income(id)
    );
    """)
    print("Created table: tax_return_income_items")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
