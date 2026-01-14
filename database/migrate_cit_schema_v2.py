import sqlite3
import os

db_path = r'd:\MyProjects\MCP_coze\database\financial.db'

def migrate_schema():
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add columns to tax_returns_income
    # Columns to add:
    # revenue, cost, taxes_and_surcharges, selling_expenses, administrative_expenses, financial_expenses
    # operating_profit, total_profit, taxable_income, tax_rate, nominal_tax, tax_reduction
    # tax_payable, final_tax_payable
    
    columns = [
        ("revenue", "REAL"),
        ("cost", "REAL"),
        ("taxes_and_surcharges", "REAL"),
        ("selling_expenses", "REAL"),
        ("administrative_expenses", "REAL"),
        ("financial_expenses", "REAL"),
        ("operating_profit", "REAL"),
        ("total_profit", "REAL"),
        ("taxable_income", "REAL"),
        ("tax_rate", "REAL"),
        ("nominal_tax", "REAL"),
        ("tax_reduction", "REAL"),
        ("tax_payable", "REAL"),
        ("final_tax_payable", "REAL")
    ]

    print("Adding columns to tax_returns_income...")
    cursor.execute("PRAGMA table_info(tax_returns_income)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    for col_name, col_type in columns:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE tax_returns_income ADD COLUMN {col_name} {col_type}")
                print(f"  + Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"  ! Error adding {col_name}: {e}")
        else:
            print(f"  = Column exists: {col_name}")

    # 2. Drop tax_return_income_items
    print("Dropping table tax_return_income_items...")
    cursor.execute("DROP TABLE IF EXISTS tax_return_income_items")
    print("  - Table dropped.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_schema()
