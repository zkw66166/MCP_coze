
import sqlite3
import random
import datetime
from decimal import Decimal

DB_PATH = 'database/financial.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_companies():
    # 5: ABC有限公司 (Software - Refund)
    # 8: 123制造厂 (Manufacturing - No Refund)
    # 10: 太空科技公司 (Software - Refund)
    # 11: 环球机械有限公司 (Manufacturing - No Refund)
    return {
        5: {'type': 'software', 'refund': True},
        8: {'type': 'manufacturing', 'refund': False},
        10: {'type': 'software', 'refund': True},
        11: {'type': 'manufacturing', 'refund': False}
    }

def get_quarterly_revenue(conn, company_id, year):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT period_month, operating_revenue 
        FROM income_statements 
        WHERE company_id = ? AND period_year = ? AND period_quarter IS NOT NULL
        ORDER BY period_month
    """, (company_id, year))
    revenue_map = {}
    for month, rev in cursor.fetchall():
        q = (month - 1) // 3 + 1
        revenue_map[q] = float(rev)
    return revenue_map

def get_annual_revenue(conn, company_id, year):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT operating_revenue 
        FROM income_statements 
        WHERE company_id = ? AND period_year = ? AND period_month = 12 AND period_quarter IS NULL
    """, (company_id, year))
    res = cursor.fetchone()
    return float(res[0]) if res else None

def get_inventory(conn, company_id, year, month):
    cursor = conn.cursor()
    # Interpolation logic for inventory
    cursor.execute("SELECT period_month, inventory FROM balance_sheets WHERE company_id = ? AND period_year = ? ORDER BY period_month", (company_id, year))
    rows = cursor.fetchall()
    if not rows:
        return 0.0
    
    # Simple nearest neighbor or just use last known
    # Better: find exact match or closest previous
    last_inv = 0.0
    for m, inv in rows:
        if m == month:
            return float(inv)
        if m < month:
            last_inv = float(inv)
        if m > month and last_inv == 0.0:
            last_inv = float(inv) # use next if no prev
            
    return last_inv

def generate_vat_returns():
    conn = get_connection()
    cursor = conn.cursor()
    
    companies = get_companies()
    clean_ids = ",".join(map(str, companies.keys()))
    print(f"Cleaning data for companies: {clean_ids}")
    cursor.execute(f"DELETE FROM tax_returns_vat WHERE company_id IN ({clean_ids})")
    
    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2026, 1, 31)
    
    for company_id, info in companies.items():
        print(f"Generating data for Company {company_id} ({info['type']})...")
        
        current_date = start_date
        # Running balances
        previous_credit = 0.0      # Col 13 (General)
        previous_ref_credit = 0.0  # (Refund Project equivalent)
        
        # Track previous payment for "Prepaid tax" logic if needed, but simplified here:
        # Assuming last month's tax payable was fully paid.
        
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            quarter = (month - 1) // 3 + 1
            
            # --- 1. Deriving Sales (Row 1) ---
            q_revs = get_quarterly_revenue(conn, company_id, year)
            sales_gen = 0.0
            
            if quarter in q_revs:
                total_q = q_revs[quarter]
                random.seed(f"{company_id}_{year}_{quarter}")
                # Random split 30/30/40 rough
                splits = [0.3 + random.uniform(-0.05, 0.05) for _ in range(2)]
                splits.append(1.0 - sum(splits))
                month_idx = (month - 1) % 3
                sales_gen = total_q * splits[month_idx]
            else:
                # Estimate
                ann_rev = get_annual_revenue(conn, company_id, year)
                if ann_rev:
                    sales_gen = (ann_rev / 12) * (1 + random.uniform(-0.2, 0.2))
                else:
                    sales_gen = 1000000.0 * (1 + random.uniform(-0.1, 0.1)) # Fallback
            
            # Reduce precision noise
            sales_gen = round(sales_gen, 2)
            
            # --- 2. Sales Breakdown (Row 2, 3...) ---
            if info['type'] == 'manufacturing':
                sales_goods = sales_gen * random.uniform(0.95, 1.0)
                sales_service = sales_gen - sales_goods
            else: # software
                # Often mixed sales
                sales_goods = sales_gen * random.uniform(0.1, 0.3) 
                sales_service = sales_gen - sales_goods
            
            # --- 3. Output Tax (Row 11) ---
            output_tax = round(sales_gen * 0.13, 2)
            
            # --- 4. Input Tax (Row 12) ---
            # Target effective tax rate
            target_rate = 0.03 if info['type'] == 'software' else 0.04
            target_payable = sales_gen * target_rate
            
            # Formula: Payable = Output - Input - PrevCredit
            # Input = Output - PrevCredit - TargetPayable
            input_tax = output_tax - previous_credit - target_payable
            
            # Constrain Input Tax
            if input_tax < 0: input_tax = output_tax * 0.5 # fallback
            input_tax = round(input_tax * (1 + random.uniform(-0.05, 0.05)), 2)
            
            # --- 5. Transfers & Adjustments ---
            input_tax_transfer = 0.0 # Row 14
            if random.random() < 0.2: # 20% chance
                 input_tax_transfer = round(input_tax * random.uniform(0.01, 0.05), 2)
            
            # --- 6. General Project Calculations ---
            # Row 18: Actual Deductible = Input(12) + PrevCredit(13) - Transfer(14) ... skipping rare ones
            actual_deduction = round(input_tax + previous_credit - input_tax_transfer, 2)
            
            # Row 19: Payable = Output(11) - ActualDeduction(18)
            # Row 20: Ending Credit
            diff = output_tax - actual_deduction
            if diff >= 0:
                tax_payable = round(diff, 2)
                ending_credit = 0.0
            else:
                tax_payable = 0.0
                ending_credit = round(abs(diff), 2)
            
            # Inventory Check
            inventory = get_inventory(conn, company_id, year, month)
            max_credit = inventory * 0.11
            if ending_credit > max_credit and max_credit > 0:
                 # Adjust input tax down to satisfy constraint
                 excess = ending_credit - max_credit
                 input_tax = round(input_tax - excess, 2)
                 # Recalc
                 actual_deduction = round(input_tax + previous_credit - input_tax_transfer, 2)
                 diff = output_tax - actual_deduction
                 if diff >= 0:
                    tax_payable = round(diff, 2)
                    ending_credit = 0.0
                 else:
                    tax_payable = 0.0
                    ending_credit = round(abs(diff), 2)

            # Row 21: Simple Tax (Usually 0 for general taxpayer, unless generic small specific calc)
            simple_tax = 0.0
            
            # Row 23: Tax Reduction (For poverty/other policies, usually 0)
            tax_reduction = 0.0
            
            # Row 24: Total Payable = 19 + 21 - 23
            tax_total = round(tax_payable + simple_tax - tax_reduction, 2)
            if tax_total < 0: tax_total = 0.0
            
            # Row 25: Opening Unpaid (Assumed 0)
            opening_unpaid = 0.0
            
            # Row 27: Paid this period
            # Assuming we pay the full amount of (Row 24 + 25)
            # Row 30: Pay previous period tax (which is effectively this period's payable if we consider filing time...
            # BUT usually "paid this period" refers to paying "Opening Unpaid + Current Payable"
            # Schema: gen_paid_tax_total_current
            paid_total = round(tax_total + opening_unpaid, 2)
            
            # Row 30: 本期缴纳上期应纳税额 (This usually means paying the tax generated in this period? 
            # OR paying arrears? Usually it equates to Row 24 in standard flow)
            paid_current_period_liability = tax_total 
            
            # Row 32: Ending Unpaid
            ending_unpaid = round(tax_total + opening_unpaid - paid_total, 2)
            
            # --- REFUND PROJECT (Immediate Refund for Software) ---
            ref_data = {}
            if info['refund']:
                 # Simplified: 100% sales are refundable items
                 # Ref Row 1
                 ref_sales = sales_gen 
                 # Ref Row 11
                 ref_output = output_tax
                 # Ref Row 12 (Proportional input tax)
                 # Since 100% sales are refundable, 100% input tax relates to it
                 ref_input = input_tax
                 ref_prev_credit = previous_ref_credit
                 
                 ref_deduction = round(ref_input + ref_prev_credit, 2)
                 ref_diff = ref_output - ref_deduction
                 
                 if ref_diff >= 0:
                     ref_payable = round(ref_diff, 2)
                     ref_ending_credit = 0.0
                 else:
                     ref_payable = 0.0
                     ref_ending_credit = round(abs(ref_diff), 2)
                     
                 # Calculate Refund Amount (Policy: Burden > 3%)
                 # Refund = Payable - (Sales * 3%)
                 burden_limit = round(ref_sales * 0.03, 2)
                 actual_refund = 0.0
                 if ref_payable > burden_limit:
                     actual_refund = round(ref_payable - burden_limit, 2)
                 
                 # Row 28-ish? In DB usually 'ref_actual_refund_current' or similar
                 ref_data = {
                     'ref_sales_taxable_current': ref_sales,
                     'ref_output_tax_current': ref_output,
                     'ref_input_tax_current': ref_input,
                     'ref_tax_payable_current': ref_payable,
                     'ref_actual_refund_current': actual_refund
                 }
                 
                 # IMPORTANT: Refund modifies General Project Payment?
                 # Typically "Immediate Refund" is a separate process or "gen_tax_reduction"
                 # Ideally, we log it in `gen_tax_reduction` if the money is never paid.
                 # BUT usually "Immediate Refund" means Pay -> Apply Refund -> Get Money.
                 # So we keep General Project as normal full payment.
                 
                 previous_ref_credit = ref_ending_credit
            else:
                 ref_data = {
                     'ref_sales_taxable_current': 0,
                     'ref_output_tax_current': 0,
                     'ref_input_tax_current': 0,
                     'ref_tax_payable_current': 0,
                     'ref_actual_refund_current': 0
                 }

            # Insert
            sql = """
                INSERT INTO tax_returns_vat (
                    company_id, period_year, period_month, period_quarter, tax_period,
                    
                    gen_sales_taxable_current, gen_sales_goods_current, gen_sales_service_current,
                    gen_output_tax_current, 
                    gen_input_tax_current, gen_previous_credit_current, gen_input_tax_transfer_current,
                    gen_actual_deduction_current,
                    gen_tax_payable_current, gen_ending_credit_current,
                    
                    gen_tax_reduction_current,
                    gen_tax_total_current, 
                    gen_opening_unpaid_tax_current,
                    gen_paid_tax_total_current,
                    gen_paid_previous_tax_current,
                    gen_ending_unpaid_tax_current,
                    
                    ref_sales_taxable_current,
                    ref_output_tax_current,
                    ref_input_tax_current,
                    ref_tax_payable_current,
                    ref_actual_refund_current,

                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 
                          ?, ?, ?, 
                          ?, 
                          ?, ?, ?, 
                          ?, 
                          ?, ?, 
                          ?, 
                          ?, 
                          ?, 
                          ?, 
                          ?, 
                          ?, 
                          ?, ?, ?, ?, ?, 
                          CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            
            tax_period = f"{year}-{month:02d}"
            
            cursor.execute(sql, (
                company_id, year, month, quarter, tax_period,
                
                sales_gen, sales_goods, sales_service,
                output_tax,
                input_tax, previous_credit, input_tax_transfer,
                actual_deduction,
                tax_payable, ending_credit,
                
                tax_reduction,
                tax_total,
                opening_unpaid,
                paid_total,
                paid_current_period_liability, # using this field for "Row 30"
                ending_unpaid,
                
                ref_data['ref_sales_taxable_current'],
                ref_data['ref_output_tax_current'],
                ref_data['ref_input_tax_current'],
                ref_data['ref_tax_payable_current'],
                ref_data['ref_actual_refund_current']
            ))
            
            previous_credit = ending_credit
            
            # Next month logic
            comp_next_month = month + 1
            comp_next_year = year
            if comp_next_month > 12:
                comp_next_month = 1
                comp_next_year += 1
            current_date = datetime.date(comp_next_year, comp_next_month, 1)

    conn.commit()
    print("Comprehensive VAT Data Generation Complete.")
    conn.close()

if __name__ == "__main__":
    generate_vat_returns()
