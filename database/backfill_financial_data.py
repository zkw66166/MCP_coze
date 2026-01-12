import sqlite3
import random

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def backfill_data():
    print("--- Backfilling Financial Data ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Backfill Income Statements
    print("Backfilling Income Statements...")
    cursor.execute("SELECT id, total_revenue, selling_expenses, administrative_expenses, taxes_and_surcharges, operating_profit FROM income_statements")
    rows = cursor.fetchall()
    
    for row in rows:
        idx, rev, sell, admin, taxes, op_profit = row
        
        # Taxes Breakdown
        # 12% of taxes usually (7+3+2) is surcharges. 
        # But 'taxes_and_surcharges' includes stamp duty, property tax etc.
        # Let's assume:
        # Stamp Duty ~= 0.03% of Rev
        stamp_duty = rev * 0.0003
        # City/Edu/LocalEdu ~= 12% of VAT (which we don't have exactly here, but approximated in prev task)
        # Let's just assign portions of 'taxes_and_surcharges'
        remaining_taxes = taxes - stamp_duty
        if remaining_taxes < 0: remaining_taxes = 0
        
        city_tax = remaining_taxes * 0.5 # Arbitrary split
        edu_tax = remaining_taxes * 0.3
        local_edu = remaining_taxes * 0.2
        
        # Expenses Breakdown
        entertainment = admin * 0.1 # Business hospitality
        research = admin * 0.15 # R&D
        advertising = sell * 0.2 # Ad spend
        
        # Other Income / Losses (Small estimates)
        # Asset Impairment often 0 or small
        impairment = 0 if random.random() > 0.2 else op_profit * 0.01 
        other_inc = 0 if random.random() > 0.2 else op_profit * 0.02
        
        cursor.execute("""
            UPDATE income_statements SET
                city_maintenance_tax = ?,
                education_surcharge = ?,
                local_education_surcharge = ?,
                stamp_duty = ?,
                research_expenses = ?,
                entertainment_expenses = ?,
                advertising_expenses = ?,
                asset_impairment_loss = ?,
                other_income = ?
            WHERE id = ?
        """, (
            round(city_tax, 2), round(edu_tax, 2), round(local_edu, 2), round(stamp_duty, 2),
            round(research, 2), round(entertainment, 2), round(advertising, 2),
            round(impairment, 2), round(other_inc, 2),
            idx
        ))

    # 2. Backfill Balance Sheets
    print("Backfilling Balance Sheets...")
    cursor.execute("SELECT id, accounts_receivable, accounts_payable, fixed_assets, other_receivables, other_non_current_assets FROM balance_sheets")
    rows = cursor.fetchall()
    
    for row in rows:
        idx, ar, ap, fixed, other_rec, other_non_curr = row
        
        # Assets Breakdown
        notes_rec = ar * 0.1 # Some portion as Notes
        contract_assets = 0 # Simplify
        right_of_use = 0
        
        # Liabilities Breakdown
        notes_pay = ap * 0.15
        contract_liab = ap * 0.05
        
        cursor.execute("""
            UPDATE balance_sheets SET
                notes_receivable = ?,
                notes_payable = ?,
                contract_liabilities = ?
            WHERE id = ?
        """, (
            round(notes_rec, 2), 
            round(notes_pay, 2), round(contract_liab, 2),
            idx
        ))

    conn.commit()
    conn.close()
    print("Backfill Complete.")

if __name__ == "__main__":
    backfill_data()
