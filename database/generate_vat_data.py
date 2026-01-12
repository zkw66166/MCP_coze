import sqlite3
import random
import datetime

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def get_companies(cursor):
    cursor.execute("SELECT id FROM companies")
    return [row[0] for row in cursor.fetchall()]

def get_income_statements(cursor, company_id):
    # Fetch quarterly statements
    cursor.execute("""
        SELECT period_year, period_quarter, total_revenue, taxes_and_surcharges, report_date
        FROM income_statements
        WHERE company_id = ?
        ORDER BY period_year, period_quarter
    """, (company_id,))
    return cursor.fetchall()

def generate_vat_returns():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data for idempotency
    cursor.execute("DELETE FROM vat_surcharges")
    cursor.execute("DELETE FROM vat_return_items")
    cursor.execute("DELETE FROM vat_returns")
    conn.commit()

    companies = get_companies(cursor)
    print(f"Found {len(companies)} companies. Generating data...")

    for company_id in companies:
        statements = get_income_statements(cursor, company_id)
        
        ytd_revenue = 0
        ytd_output_tax = 0
        ytd_input_tax = 0
        ytd_payable = 0
        ytd_city_tax = 0
        ytd_edu_tax = 0
        ytd_local_edu_tax = 0

        current_year = 0

        for stmt in statements:
            year, quarter, total_rev, taxes_surcharges, report_date = stmt
            
            if year != current_year:
                # Reset YTD at start of year
                ytd_revenue = 0
                ytd_output_tax = 0
                ytd_input_tax = 0
                ytd_payable = 0
                ytd_city_tax = 0
                ytd_edu_tax = 0
                ytd_local_edu_tax = 0
                current_year = year

            # Distribute quarterly values to 3 months with some randomness
            # We want month1 + month2 + month3 approx equals Quarter items
            # But strictly: sum(VAT Sales) <= Total Revenue
            
            # Base distribution (approx 1/3 each month)
            factors = [random.uniform(0.9, 1.1) for _ in range(3)]
            total_factor = sum(factors)
            normalized_factors = [f / total_factor for f in factors]

            # Monthly target revenues
            monthly_revs = [total_rev * f for f in normalized_factors]
            monthly_surcharges = [taxes_surcharges * f for f in normalized_factors]

            months = [(quarter - 1) * 3 + i for i in range(1, 4)]
            
            for i, month in enumerate(months):
                rev = monthly_revs[i]
                surcharge_total = monthly_surcharges[i] # City(7) + Edu(3) + Local(2) = 12% of VAT Payable
                
                # Infer VAT Payable from Surcharges
                # Surcharges = VAT_Payable * 12%
                # So VAT_Payable = Surcharges / 0.12
                # Handle edge case where surcharge is 0
                if surcharge_total > 0:
                    vat_payable = surcharge_total / 0.12
                else:
                    vat_payable = 0

                # Infer Output Tax from Revenue
                # Sales * 13% = Output Tax
                # Sales should be <= Revenue (Revenue usually excludes VAT, but includes other things)
                # Let's assume most Revenue is taxable Sales.
                sales = rev * 0.95 # Leave some buffer
                output_tax = sales * 0.13
                
                # Adjust Input Tax to match the calculated VAT Payable
                # Payable = Output - Input  =>  Input = Output - Payable
                input_tax = output_tax - vat_payable
                
                if input_tax < 0:
                    # If input tax is negative, it means Output < Payable, which is weird if inferred this way.
                    # It implies Surcharges are high relative to Revenue-based Output.
                    # Adjust Output up to cover it? Or reduce Payable?
                    # Let's clap Input to 0 and adjust Payable to Output
                    input_tax = 0
                    vat_payable = output_tax 
                    # Recalculate surcharges based on new payable
                    surcharge_total = vat_payable * 0.12

                # Calculate specific surcharges
                city_tax = vat_payable * 0.07
                edu_tax = vat_payable * 0.03
                local_edu_tax = vat_payable * 0.02

                # Validating: Sales <= Revenue check (already ensured by 0.95 factor)
                
                # --- Insert Data ---
                
                # 1. vat_returns
                filing_date_obj = datetime.date(year, month, 15) # Approx 15th of next month? Or current month? usually next month.
                # Just use formatted string
                filing_txt = filing_date_obj.strftime("%Y-%m-%d")
                
                cursor.execute("""
                    INSERT INTO vat_returns (company_id, period_year, period_month, filing_date)
                    VALUES (?, ?, ?, ?)
                """, (company_id, year, month, filing_txt))
                return_id = cursor.lastrowid
                
                # Update YTDs
                ytd_revenue += sales
                ytd_output_tax += output_tax
                ytd_input_tax += input_tax
                ytd_payable += vat_payable
                ytd_city_tax += city_tax
                ytd_edu_tax += edu_tax
                ytd_local_edu_tax += local_edu_tax

                # 2. vat_return_items
                items = [
                     # Line 1: Sales
                    (1, "（一）按适用税率计税销售额", sales, ytd_revenue, 0, 0),
                    (2, "其中：应税货物销售额", sales, ytd_revenue, 0, 0), # Simplified: all is goods
                     # Line 11: Output Tax
                    (11, "销项税额", output_tax, ytd_output_tax, 0, 0),
                     # Line 12: Input Tax
                    (12, "进项税额", input_tax, ytd_input_tax, 0, 0),
                     # Line 17: Total Deductible
                    (17, "应抵扣税额合计", input_tax, 0, 0, 0), # YTD not applicable usually here or same
                     # Line 18: Actual Deducted
                    (18, "实际抵扣税额", input_tax, 0, 0, 0),
                     # Line 19: Tax Payable
                    (19, "应纳税额", vat_payable, ytd_payable, 0, 0)
                ]
                
                for item in items:
                    l_no, name, curr, ytd, ref_curr, ref_ytd = item
                    cursor.execute("""
                        INSERT INTO vat_return_items (return_id, line_no, item_name, amount_current, amount_ytd, refund_current, refund_ytd)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (return_id, l_no, name, round(curr, 2), round(ytd, 2), round(ref_curr, 2), round(ref_ytd, 2)))

                # 3. vat_surcharges
                s_items = [
                    ("城市维护建设税", city_tax, ytd_city_tax),
                    ("教育费附加", edu_tax, ytd_edu_tax),
                    ("地方教育附加", local_edu_tax, ytd_local_edu_tax)
                ]
                
                for s_item in s_items:
                    name, curr, ytd = s_item
                    cursor.execute("""
                        INSERT INTO vat_surcharges (return_id, item_name, tax_payable, tax_paid_ytd)
                        VALUES (?, ?, ?, ?)
                    """, (return_id, name, round(curr, 2), round(ytd, 2)))

    conn.commit()
    conn.close()
    print("VAT Data Generation Complete.")

if __name__ == "__main__":
    generate_vat_returns()
