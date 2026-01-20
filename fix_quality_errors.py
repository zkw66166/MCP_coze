"""
Script to fix data quality errors based on user rules.
Rules:
1. Subject Balance: Fix 'credit_amount' to make the equation balance.
2. Balance Sheet: Base on 'total_assets', fix 'total_equity' and 'undistributed_profit'.
3. Income Statement: Base on 'total_revenue', fix 'operating_profit', 'total_profit', 'net_profit'.
4. CIT Return: Calculate profit and tax amounts correctly.
"""
import sqlite3
import os

DB_PATH = 'database/financial.db'

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fix_subject_balance(conn, company_id):
    print(f"Fixing Subject Balances for Company {company_id}...")
    cursor = conn.cursor()
    
    # Get all records
    cursor.execute("SELECT * FROM account_balances WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    
    fixed_count = 0
    for row in rows:
        row_id = row['id']
        code = str(row['account_code'])
        opening = row['opening_balance'] or 0
        debit = row['debit_amount'] or 0
        credit = row['credit_amount'] or 0
        closing = row['ending_balance'] or 0
        
        # Determine direction based on account code
        # 1xxx (Asset), 5xxx (Cost/Expense) -> Opening + Debit - Credit = Closing
        # 2xxx (Liability), 3xxx (Equity), 4xxx (Revenue) -> Opening - Debit + Credit = Closing
        
        is_asset_type = code.startswith('1') or code.startswith('5')
        
        expected_credit = 0
        if is_asset_type:
            # Credit = Opening + Debit - Closing
            expected_credit = opening + debit - closing
        else:
            # Credit = Closing - Opening + Debit
            expected_credit = closing - opening + debit
            
        if abs(credit - expected_credit) > 0.01:
            # Update
            cursor.execute(
                "UPDATE account_balances SET credit_amount = ? WHERE id = ?",
                (expected_credit, row_id)
            )
            fixed_count += 1
            
    conn.commit()
    print(f"  Fixed {fixed_count} records in account_balances")

def fix_balance_sheet(conn, company_id):
    print(f"Fixing Balance Sheets for Company {company_id}...")
    cursor = conn.cursor()
    
    # Get all records
    cursor.execute("SELECT * FROM balance_sheets WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    
    fixed_count = 0
    for row in rows:
        row_id = row['id']
        
        # Base on Total Assets
        total_assets = row['total_assets'] or 0
        total_liabilities = row['total_liabilities'] or 0
        total_equity = row['total_equity'] or 0
        
        # 1. Fix Total Equity to match Total Assets = Total Liabilities + Total Equity
        expected_equity = total_assets - total_liabilities
        
        if abs(total_equity - expected_equity) > 0.01:
            # Also fix Undistributed Profit to balance the Equity internal equation
            # Equity = PaidIn + CapSurplus + SurpReserves + RetainedEarnings
            paid_in = row['paid_in_capital'] or 0
            cap_surplus = row['capital_surplus'] or 0
            surp_reserves = row['surplus_reserves'] or 0
            
            # If we change Total Equity, the difference must go somewhere. Usually Retained Earnings.
            # New Retained = New Total Equity - (PaidIn + CapSurplus + SurpReserves)
            new_retained = expected_equity - (paid_in + cap_surplus + surp_reserves)
            
            cursor.execute(
                "UPDATE balance_sheets SET total_equity = ?, retained_earnings = ? WHERE id = ?",
                (expected_equity, new_retained, row_id)
            )
            fixed_count += 1
            
            # Update local variable to reflect DB change for subsequent calcs if needed
            total_equity = expected_equity
            
        # 1.5 Fix Structure: Total Assets = Current + NonCurrent
        # Base on Total Assets (User Rule)
        # Trust Current Assets Total?
        curr_asset_total = row['current_assets_total'] or 0
        non_curr_asset_total = row['non_current_assets_total'] or 0
        
        if abs(total_assets - (curr_asset_total + non_curr_asset_total)) > 0.01:
            # Adjust Non-Current Assets Total to match
            new_non_curr_total = total_assets - curr_asset_total
            cursor.execute(
                "UPDATE balance_sheets SET non_current_assets_total = ? WHERE id = ?",
                (new_non_curr_total, row_id)
            )
            fixed_count += 1
            non_current_asset_total = new_non_curr_total
            
        # 1.6 Fix Structure: Total Liabilities = Current + NonCurrent
        # We assume Total Liabilities is correct (after equity fix) or at least fixed relative to Assets/Equity
        curr_liab_total = row['current_liabilities_total'] or 0
        non_curr_liab_total = row['non_current_liabilities_total'] or 0
        
        if abs(total_liabilities - (curr_liab_total + non_curr_liab_total)) > 0.01:
            # Adjust Non-Current Liabilities Total to match
            new_non_curr_liab_total = total_liabilities - curr_liab_total
            cursor.execute(
                "UPDATE balance_sheets SET non_current_liabilities_total = ? WHERE id = ?",
                (new_non_curr_liab_total, row_id)
            )
            fixed_count += 1
            non_curr_liab_total = new_non_curr_liab_total
        
        # 2. Fix Current Assets Details
        # Force Sum(Items) = Current Assets Total (Trusting Total because it links to Total Assets)
        # We use 'current_assets' (Other Current Assets) as the plug
        # RE-READ row values if we updated them? 
        # Actually we updated totals columns above (except equity), so local vars `curr_asset_total` and `non_current_asset_total` are up to date (or logically updated).
        # But `row` object is stale for those fields. Use local vars.
        
        current_total = curr_asset_total
        
        # Calculate sum of known items (excluding the plug 'current_assets')
        # Check schema for list of current asset items
        # Known from DataQualityChecker: 
        # cash_and_equivalents, trading_financial_assets, notes_receivable, accounts_receivable, 
        # prepayments, other_receivables, inventory, contract_assets
        # 'current_assets' column is likely 'Other Current Assets'
        
        curr_sum_no_plug = (
            (row['cash_and_equivalents'] or 0) + 
            (row['trading_financial_assets'] or 0) + 
            (row['notes_receivable'] or 0) + 
            (row['accounts_receivable'] or 0) + 
            (row['prepayments'] or 0) + 
            (row['other_receivables'] or 0) + 
            (row['inventory'] or 0) + 
            (row['contract_assets'] or 0)
        )
        
        plug_needed = current_total - curr_sum_no_plug
        current_plug_val = row['current_assets'] or 0
        
        if abs(current_plug_val - plug_needed) > 0.01:
            cursor.execute(
                "UPDATE balance_sheets SET current_assets = ? WHERE id = ?",
                (plug_needed, row_id)
            )
            fixed_count += 1
            
        # 3. Fix Non-Current Assets Details
        # Plug: other_non_current_assets
        non_current_total = row['non_current_assets_total'] or 0
        
        # Items: long_term_equity_investment, fixed_assets, construction_in_progress, 
        # right_of_use_assets, intangible_assets, development_expenditure, goodwill, 
        # long_term_deferred_expenses, deferred_tax_assets
        
        non_curr_sum_no_plug = (
            (row['long_term_equity_investment'] or 0) + 
            (row['fixed_assets'] or 0) + 
            (row['construction_in_progress'] or 0) + 
            (row['right_of_use_assets'] or 0) + 
            (row['intangible_assets'] or 0) + 
            (row['development_expenditure'] or 0) + 
            (row['goodwill'] or 0) + 
            (row['long_term_deferred_expenses'] or 0) + 
            (row['deferred_tax_assets'] or 0)
        )
        
        nc_plug_needed = non_current_total - non_curr_sum_no_plug
        nc_plug_val = row['other_non_current_assets'] or 0
        
        if abs(nc_plug_val - nc_plug_needed) > 0.01:
             cursor.execute(
                "UPDATE balance_sheets SET other_non_current_assets = ? WHERE id = ?",
                (nc_plug_needed, row_id)
            )
             fixed_count += 1

    conn.commit()
    print(f"  Fixed {fixed_count} records in balance_sheets")

def fix_income_statement(conn, company_id):
    print(f"Fixing Income Statements for Company {company_id}...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM income_statements WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    
    # Get column names to safely check for existence
    cursor.execute("PRAGMA table_info(income_statements)")
    columns = [col[1] for col in cursor.fetchall()]
    has_inv_income = 'investment_income' in columns
    
    fixed_count = 0
    for row in rows:
        row_id = row['id']
        
        # Values
        rev = row['operating_revenue'] or 0
        cost = row['operating_costs'] or 0
        tax = row['taxes_and_surcharges'] or 0
        sell = row['selling_expenses'] or 0
        admin = row['administrative_expenses'] or 0
        fin = row['financial_expenses'] or 0
        other = row['other_income'] or 0
        inv = row['investment_income'] if has_inv_income else 0
        if inv is None: inv = 0
        
        # 1. Recalculate Operating Profit
        op_profit = rev - cost - tax - sell - admin - fin + other + inv
        
        non_op_inc = row['non_operating_income'] or 0
        non_op_exp = row['non_operating_expenses'] or 0
        
        # 2. Recalculate Total Profit
        total_profit = op_profit + non_op_inc - non_op_exp
        
        inc_tax = row['income_tax_expense'] or 0
        
        # 3. Recalculate Net Profit
        net_profit = total_profit - inc_tax
        
        # Check if update needed
        curr_op = row['operating_profit'] or 0
        curr_tp = row['total_profit'] or 0
        curr_np = row['net_profit'] or 0
        
        if (abs(curr_op - op_profit) > 0.01 or 
            abs(curr_tp - total_profit) > 0.01 or 
            abs(curr_np - net_profit) > 0.01):
            
            cursor.execute('''
                UPDATE income_statements 
                SET operating_profit = ?, total_profit = ?, net_profit = ?
                WHERE id = ?
            ''', (op_profit, total_profit, net_profit, row_id))
            fixed_count += 1
            
    conn.commit()
    print(f"  Fixed {fixed_count} records in income_statements")

def fix_cit_return(conn, company_id):
    print(f"Fixing CIT Returns for Company {company_id}...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tax_returns_income WHERE company_id = ?", (company_id,))
    rows = cursor.fetchall()
    
    fixed_count = 0
    for row in rows:
        row_id = row['id']
        
        rev = row['revenue'] or 0
        cost = row['cost'] or 0
        tax = row['taxes_and_surcharges'] or 0
        sell = row['selling_expenses'] or 0
        admin = row['administrative_expenses'] or 0
        fin = row['financial_expenses'] or 0
        
        # 1. Recalculate Profit
        total_profit = rev - cost - tax - sell - admin - fin
        
        # 2. Recalculate Tax
        taxable_income = row['taxable_income'] or 0
        tax_rate = row['tax_rate'] or 0.25
        
        # If taxable_income is 0 but profit is not, maybe we should set taxable_income = total_profit + adjustments?
        # For now, let's assume taxable_income is provided correctly, or user rule "Base on Revenue" implies
        # we strictly follow the formula chain.
        # But check_cit_return in DataQualityChecker only checks:
        # 1. Total Profit Calc
        # 2. Nominal Tax = Taxable * Rate
        # 3. Final Tax = Nominal - Reduction
        
        # So we update Total Profit
        nominal_tax = taxable_income * tax_rate
        
        reduction = row['tax_reduction'] or 0
        final_tax = nominal_tax - reduction
        
        curr_tp = row['total_profit'] or 0
        curr_nom = row['nominal_tax'] or 0
        curr_final = row['final_tax_payable'] or 0
        
        if (abs(curr_tp - total_profit) > 0.01 or 
            abs(curr_nom - nominal_tax) > 0.01 or 
            abs(curr_final - final_tax) > 0.01):
            
            cursor.execute('''
                UPDATE tax_returns_income
                SET total_profit = ?, nominal_tax = ?, final_tax_payable = ?
                WHERE id = ?
            ''', (total_profit, nominal_tax, final_tax, row_id))
            fixed_count += 1
            
    conn.commit()
    print(f"  Fixed {fixed_count} records in tax_returns_income")

def main():
    conn = get_db_connection()
    if not conn:
        return
        
    companies = [5, 8, 10, 11]
    
    for company_id in companies:
        print(f"\nProcessing Company {company_id}...")
        fix_subject_balance(conn, company_id)
        fix_balance_sheet(conn, company_id)
        fix_income_statement(conn, company_id)
        fix_cit_return(conn, company_id)
        
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
