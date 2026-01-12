import sqlite3

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def update_schema():
    print(f"Updating Invoice Schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop old tables if exist
    cursor.execute("DROP TABLE IF EXISTS invoice_data") # Drop the old summary table
    cursor.execute("DROP TABLE IF EXISTS invoices")
    print("Dropped old invoice tables.")

    # Create new invoices table
    # Unified table for both Input and Output
    cursor.execute("""
    CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        invoice_type TEXT NOT NULL, -- 'INPUT' or 'OUTPUT'
        
        -- Identity
        invoice_code TEXT,
        invoice_number TEXT,
        digital_number TEXT,
        
        -- Parties
        seller_name TEXT,
        seller_tax_id TEXT,
        buyer_name TEXT,
        buyer_tax_id TEXT,
        
        -- Financials
        amount_excluding_tax REAL DEFAULT 0,
        tax_rate REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0,
        total_amount REAL DEFAULT 0,
        
        -- Details
        issue_date TEXT,
        item_name TEXT,
        quantity REAL DEFAULT 1,
        unit_price REAL DEFAULT 0,
        spec TEXT, -- Specification
        unit TEXT, -- Unit
        
        -- Meta
        period_year INTEGER,
        period_month INTEGER,
        invoice_category TEXT DEFAULT 'General', -- e.g. Special VAT, General
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("Created new table: invoices")

    conn.commit()
    conn.close()
    print("Invoice Schema update complete.")

if __name__ == "__main__":
    update_schema()
