import sqlite3
import os

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def update_schema():
    print(f"Updating schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. vat_returns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vat_returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        period_month INTEGER NOT NULL,
        filing_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, period_year, period_month)
    );
    """)
    print("Created table: vat_returns")

    # 2. vat_return_items (Main body)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vat_return_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER NOT NULL,
        line_no INTEGER,
        item_name TEXT,
        amount_current REAL DEFAULT 0,
        amount_ytd REAL DEFAULT 0,
        refund_current REAL DEFAULT 0,
        refund_ytd REAL DEFAULT 0,
        FOREIGN KEY (return_id) REFERENCES vat_returns(id)
    );
    """)
    print("Created table: vat_return_items")

    # 3. vat_surcharges (Appendix)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vat_surcharges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        return_id INTEGER NOT NULL,
        item_name TEXT,
        tax_payable REAL DEFAULT 0,
        tax_paid_ytd REAL DEFAULT 0,
        FOREIGN KEY (return_id) REFERENCES vat_returns(id)
    );
    """)
    print("Created table: vat_surcharges")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
