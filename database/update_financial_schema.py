import sqlite3

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def update_schema():
    print(f"Updating schema for: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # helper to add column safely
    def add_column(table, col_name, col_type="REAL DEFAULT 0"):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"Column {col_name} already exists in {table}, skipping.")
            else:
                print(f"Error adding {col_name} to {table}: {e}")

    # 1. Update income_statements
    inc_cols = [
        "consumption_tax", "city_maintenance_tax", "education_surcharge", "local_education_surcharge",
        "resource_tax", "land_appreciation_tax", "property_tax", "stamp_duty", "other_taxes",
        "research_expenses", "entertainment_expenses", "advertising_expenses",
        "asset_impairment_loss", "credit_impairment_loss", "asset_disposal_income", 
        "other_income", "govt_grants"
    ]
    for col in inc_cols:
        add_column("income_statements", col)

    # 2. Update balance_sheets
    bal_cols = [
        # Assets
        "notes_receivable", "contract_assets", "right_of_use_assets", 
        "construction_in_progress", "development_expenditure", "long_term_deferred_expenses",
        "goodwill", "deferred_tax_assets", "other_non_current_assets",
        # Liabilities
        "notes_payable", "contract_liabilities", "lease_liabilities", 
        "long_term_payables", "deferred_revenue", "deferred_tax_liabilities",
        "estimated_liabilities"
    ]
    for col in bal_cols:
        add_column("balance_sheets", col)

    # 3. Create cash_flow_statements
    # Dropping if exists to ensure clean state with correct schema? 
    # Or just CREATE IF NOT EXISTS. Let's do CREATE IF NOT EXISTS.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cash_flow_statements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        period_quarter INTEGER NOT NULL,
        period_month INTEGER DEFAULT 0, -- For monthly generated data
        
        -- Operating Activities
        cash_received_goods_services REAL DEFAULT 0,
        cash_received_tax_refunds REAL DEFAULT 0,
        cash_received_other_operating REAL DEFAULT 0,
        subtotal_operate_inflow REAL DEFAULT 0,
        
        cash_paid_goods_services REAL DEFAULT 0,
        cash_paid_employees REAL DEFAULT 0,
        cash_paid_taxes REAL DEFAULT 0,
        cash_paid_other_operating REAL DEFAULT 0,
        subtotal_operate_outflow REAL DEFAULT 0,
        
        net_cash_operating REAL DEFAULT 0,
        
        -- Investing Activities
        cash_received_investment_disposal REAL DEFAULT 0,
        cash_received_investment_return REAL DEFAULT 0,
        cash_received_asset_disposal REAL DEFAULT 0,
        subtotal_invest_inflow REAL DEFAULT 0,
        
        cash_paid_asset_acquisition REAL DEFAULT 0,
        cash_paid_investments REAL DEFAULT 0,
        subtotal_invest_outflow REAL DEFAULT 0,
        
        net_cash_investing REAL DEFAULT 0,
        
        -- Financing Activities
        cash_received_borrowings REAL DEFAULT 0,
        cash_received_capital_contribution REAL DEFAULT 0,
        subtotal_finance_inflow REAL DEFAULT 0,
        
        cash_paid_debt_repayment REAL DEFAULT 0,
        cash_paid_interest_dividends REAL DEFAULT 0,
        subtotal_finance_outflow REAL DEFAULT 0,
        
        net_cash_financing REAL DEFAULT 0,
        
        -- Summary
        exchange_rate_effect REAL DEFAULT 0,
        net_increase_cash REAL DEFAULT 0,
        cash_beginning REAL DEFAULT 0,
        cash_ending REAL DEFAULT 0,
        
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, period_year, period_quarter, period_month)
    );
    """)
    print("Created table: cash_flow_statements")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
