import sqlite3
import pandas as pd
import random

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def regenerate_taxes():
    print("--- Regenerating Tax Returns ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Clear Tables
    tables = [
        "vat_returns", "vat_return_items", "vat_surcharges",
        "tax_returns_income", "tax_return_income_items",
        "tax_returns_stamp", "tax_return_stamp_items"
    ]
    for t in tables:
        cursor.execute(f"DELETE FROM {t}")
    print("Cleared existing tax returns.")

    # 2. Get Companies
    cursor.execute("SELECT id FROM companies")
    companies = [r[0] for r in cursor.fetchall()]
    
    # 3. Get Income Statements
    query = """
    SELECT company_id, period_year, period_quarter, total_revenue, operating_costs, 
           taxes_and_surcharges, income_tax_expense, total_profit
    FROM income_statements
    ORDER BY company_id, period_year, period_quarter
    """
    df_inc = pd.read_sql_query(query, conn)
    
    for comp_id in companies:
        comp_data = df_inc[df_inc['company_id'] == comp_id]
        
        # --- VAT (Monthly) ---
        for _, row in comp_data.iterrows():
            year = row['period_year']
            q = row['period_quarter']
            rev = row['total_revenue']
            cost = row['operating_costs']
            
            # Interpolate to 3 months
            # Random split approx 30/30/40
            splits = [random.uniform(0.3, 0.4) for _ in range(2)]
            s3 = 1 - sum(splits)
            splits.append(s3)
            random.shuffle(splits)
            
            months = [(q-1)*3 + i for i in range(1, 4)]
            
            for i, m in enumerate(months):
                monthly_rev = rev * splits[i]
                monthly_cost = cost * splits[i]
                
                # Logic: Sales = Revenue / 1.13 approx (assuming Revenue includes tax? No, standard IncStmt is Excl Tax)
                # Usually Revenue in IncStmt IS Excl Tax.
                # So Sales Amount = Revenue.
                sales_amt = monthly_rev
                output_tax = sales_amt * 0.13
                
                # Input Deductible?
                # Cost usually Excl Tax.
                input_amt = monthly_cost
                input_tax = input_amt * 0.09 # Blend of 13% and 6% and 0%
                
                tax_payable = max(0, output_tax - input_tax)
                
                # Insert Header
                cursor.execute("""
                    INSERT INTO vat_returns (company_id, period_year, period_month, filing_date)
                    VALUES (?, ?, ?, ?)
                """, (comp_id, year, int(m), f"{year}-{int(m):02d}-15"))
                vat_id = cursor.lastrowid
                
                # Insert Items (Simplified Main Flow)
                # Schema: return_id, item_name, amount_current, amount_ytd...
                
                # Sales
                cursor.execute("INSERT INTO vat_return_items (return_id, item_name, amount_current) VALUES (?, ?, ?)", 
                               (vat_id, "按适用税率计税销售额", round(sales_amt, 2)))
                cursor.execute("INSERT INTO vat_return_items (return_id, item_name, amount_current) VALUES (?, ?, ?)", 
                               (vat_id, "销项税额", round(output_tax, 2)))
                cursor.execute("INSERT INTO vat_return_items (return_id, item_name, amount_current) VALUES (?, ?, ?)", 
                               (vat_id, "进项税额", round(input_tax, 2)))
                cursor.execute("INSERT INTO vat_return_items (return_id, item_name, amount_current) VALUES (?, ?, ?)", 
                               (vat_id, "应纳税额", round(tax_payable, 2)))

        # --- CIT (Annual) ---
        # Aggregate 2022, 2023, 2024. 2025 incomplete.
        for year in [2022, 2023, 2024]:
            yr_data = comp_data[comp_data['period_year'] == year]
            if yr_data.empty: continue
            
            total_rev = yr_data['total_revenue'].sum()
            total_cost = yr_data['operating_costs'].sum()
            total_profit = yr_data['total_profit'].sum()
            tax_expense = yr_data['income_tax_expense'].sum()
            
            # Insert Header
            cursor.execute("""
                INSERT INTO tax_returns_income (company_id, period_year, filing_date)
                VALUES (?, ?, ?)
            """, (comp_id, year, f"{year+1}-05-31"))
            cit_id = cursor.lastrowid
            
            # Insert Items
            # Schema: return_id, item_name, amount
            items = [
                ("营业收入", total_rev),
                ("营业成本", total_cost),
                ("利润总额", total_profit),
                ("应纳税所得额", total_profit), 
                ("应纳所得税额", tax_expense)
            ]
            for name, val in items:
                cursor.execute("INSERT INTO tax_return_income_items (return_id, item_name, amount) VALUES (?, ?, ?)",
                               (cit_id, name, round(val, 2)))

        # --- Stamp Duty (Quarterly) ---
        for _, row in comp_data.iterrows():
            year = row['period_year']
            q = row['period_quarter']
            rev = row['total_revenue']
            
            # Sales Contract
            tax_base = rev
            tax_rate = 0.0003
            reduction = tax_base * tax_rate * 0.5
            tax_payable = tax_base * tax_rate
            tax_final = tax_payable - reduction
            
            # Insert Header
            cursor.execute("""
                INSERT INTO tax_returns_stamp (company_id, period_year, period_quarter, filing_date)
                VALUES (?, ?, ?, ?)
            """, (comp_id, year, q, f"{year}-Q{q}"))
            stamp_id = cursor.lastrowid
            
            # Insert Item
            # Schema: return_id, tax_category, tax_item, tax_base, tax_rate, tax_payable, tax_reduction, tax_amount
            cursor.execute("""
                INSERT INTO tax_return_stamp_items (
                    return_id, tax_category, tax_item, tax_base, tax_rate, 
                    tax_payable, tax_reduction, tax_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stamp_id, "买卖合同", "购销合同", round(tax_base, 2), tax_rate, 
                round(tax_payable, 2), round(reduction, 2), round(tax_final, 2)
            ))

    conn.commit()
    conn.close()
    print("Regeneration Complete.")

if __name__ == "__main__":
    regenerate_taxes()
