import sqlite3
import os

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def update_schema():
    print(f"Updating schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. tax_returns_stamp (Quarterly Return Meta)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_returns_stamp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        period_quarter INTEGER NOT NULL,
        filing_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, period_year, period_quarter)
    );
    """)
    print("Created table: tax_returns_stamp")

    # 2. tax_return_stamp_items (Return Body)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_return_stamp_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER NOT NULL,
        tax_category TEXT,       -- e.g. 印花税
        tax_item TEXT,           -- e.g. 买卖合同
        tax_base REAL DEFAULT 0, -- e.g. Revenue
        tax_rate REAL DEFAULT 0, -- e.g. 0.0003
        tax_payable REAL DEFAULT 0,
        tax_reduction REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0, -- Final amount
        FOREIGN KEY (return_id) REFERENCES tax_returns_stamp(id)
    );
    """)
    print("Created table: tax_return_stamp_items")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
