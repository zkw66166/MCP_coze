import sqlite3
import pandas as pd

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def generate_cash_flow():
    print("--- Generating Cash Flow Data ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get Companies
    cursor.execute("SELECT id FROM companies")
    companies = [r[0] for r in cursor.fetchall()]
    
    # Clear old data
    cursor.execute("DELETE FROM cash_flow_statements")
    
    for comp_id in companies:
        # Get Balance Sheets (sorted by time)
        bs_query = """
        SELECT period_year, period_quarter, cash_and_equivalents, 
               accounts_receivable, inventory, accounts_payable, 
               fixed_assets, short_term_loans, long_term_loans,
               total_assets, total_liabilities
        FROM balance_sheets 
        WHERE company_id = ?
        ORDER BY period_year, period_quarter
        """
        df_bs = pd.read_sql_query(bs_query, conn, params=(comp_id,))
        
        # Get Income Statements
        is_query = """
        SELECT period_year, period_quarter, total_revenue, operating_costs, 
               selling_expenses, administrative_expenses, financial_expenses,
               taxes_and_surcharges, income_tax_expense, net_profit
        FROM income_statements
        WHERE company_id = ?
        ORDER BY period_year, period_quarter
        """
        df_is = pd.read_sql_query(is_query, conn, params=(comp_id,))
        
        # Merge on period
        df = pd.merge(df_bs, df_is, on=['period_year', 'period_quarter'], how='inner')
        
        # Calculate changes (diff with prev row)
        # Shift 1 to get prev
        df['prev_cash'] = df['cash_and_equivalents'].shift(1).fillna(df['cash_and_equivalents'] * 0.9) # Assume 10% growth if no prev
        df['d_cash'] = df['cash_and_equivalents'] - df['prev_cash']
        
        df['d_ar'] = df['accounts_receivable'] - df['accounts_receivable'].shift(1).fillna(df['accounts_receivable'])
        df['d_inv'] = df['inventory'] - df['inventory'].shift(1).fillna(df['inventory'])
        df['d_ap'] = df['accounts_payable'] - df['accounts_payable'].shift(1).fillna(df['accounts_payable'])
        df['d_fixed'] = df['fixed_assets'] - df['fixed_assets'].shift(1).fillna(df['fixed_assets'])
        df['d_loans'] = (df['short_term_loans'] + df['long_term_loans']) - (df['short_term_loans'] + df['long_term_loans']).shift(1).fillna(0)
        
        for index, row in df.iterrows():
            # Operating
            # Cash Received = Revenue + d_AR (inverse: if AR up, cash not received, so - d_AR)
            # Actually: Cash = Revenue - ChangeInAR
            # If AR increased (d_ar > 0), confirmed Revenue > Cash Received -> Cash = Rev - d_AR. Correct.
            cash_rec_goods = row['total_revenue'] * 1.13 - row['d_ar'] # Approx VAT 13%
            if cash_rec_goods < 0: cash_rec_goods = 0
            
            cash_paid_goods = row['operating_costs'] * 1.13 + row['d_inv'] - row['d_ap'] 
            if cash_paid_goods < 0: cash_paid_goods = 0
            
            cash_paid_empl = (row['selling_expenses'] + row['administrative_expenses']) * 0.5 # Assume 50% is labor
            cash_paid_tax = row['taxes_and_surcharges'] + row['income_tax_expense']
            
            sub_op_in = cash_rec_goods
            sub_op_out = cash_paid_goods + cash_paid_empl + cash_paid_tax
            net_op_initial = sub_op_in - sub_op_out
            
            # Investing
            # Capex
            cash_paid_asset = max(0, row['d_fixed']) # If fixed assets grew, we paid cash
            cash_rec_disposal = max(0, -row['d_fixed']) # If shrank, maybe disposal (or dep, ignore dep for now simplicity)
            
            net_inv = cash_rec_disposal - cash_paid_asset
            
            # Financing
            # Debt
            cash_rec_borrow = max(0, row['d_loans'])
            cash_paid_debt = max(0, -row['d_loans'])
            cash_paid_int = row['financial_expenses']
            
            net_fin = cash_rec_borrow - cash_paid_debt - cash_paid_int
            
            # Reconciliation Plug
            # Target Delta = d_cash
            # Calculated Delta = NetOp + NetInv + NetFin
            # Gap goes to "Other Operating"
            calc_delta = net_op_initial + net_inv + net_fin
            gap = row['d_cash'] - calc_delta
            
            # Adjust Operating
            # If gap positive (Cash increase > Calc), implies we received more or paid less. Add to "Received Other"
            # If gap negative (Cash increase < Calc), implies we paid more. Add to "Paid Other"
            
            cash_rec_other_op = 0
            cash_paid_other_op = 0
            
            if gap > 0:
                cash_rec_other_op = gap
            else:
                cash_paid_other_op = -gap
                
            # Recalculate Net Op
            sub_op_in += cash_rec_other_op
            sub_op_out += cash_paid_other_op
            net_op = sub_op_in - sub_op_out
            
            # Final check
            final_delta = net_op + net_inv + net_fin
            
            # Insert
            cursor.execute("""
                INSERT INTO cash_flow_statements (
                    company_id, period_year, period_quarter,
                    cash_received_goods_services, cash_received_other_operating, subtotal_operate_inflow,
                    cash_paid_goods_services, cash_paid_employees, cash_paid_taxes, cash_paid_other_operating, subtotal_operate_outflow,
                    net_cash_operating,
                    
                    cash_received_asset_disposal, subtotal_invest_inflow,
                    cash_paid_asset_acquisition, subtotal_invest_outflow,
                    net_cash_investing,
                    
                    cash_received_borrowings, subtotal_finance_inflow,
                    cash_paid_debt_repayment, cash_paid_interest_dividends, subtotal_finance_outflow,
                    net_cash_financing,
                    
                    net_increase_cash, cash_beginning, cash_ending
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comp_id, row['period_year'], row['period_quarter'],
                round(cash_rec_goods, 2), round(cash_rec_other_op, 2), round(sub_op_in, 2),
                round(cash_paid_goods, 2), round(cash_paid_empl, 2), round(cash_paid_tax, 2), round(cash_paid_other_op, 2), round(sub_op_out, 2),
                round(net_op, 2),
                
                round(cash_rec_disposal, 2), round(cash_rec_disposal, 2),
                round(cash_paid_asset, 2), round(cash_paid_asset, 2),
                round(net_inv, 2),
                
                round(cash_rec_borrow, 2), round(cash_rec_borrow, 2),
                round(cash_paid_debt, 2), round(cash_paid_int, 2), round(cash_paid_debt + cash_paid_int, 2),
                round(net_fin, 2),
                
                round(final_delta, 2), round(row['prev_cash'], 2), round(row['cash_and_equivalents'], 2)
            ))
            
    conn.commit()
    conn.close()
    print("Cash Flow Generation Complete.")

if __name__ == "__main__":
    generate_cash_flow()
