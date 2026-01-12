import sqlite3
import random
import datetime

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def get_companies(cursor):
    cursor.execute("SELECT id, name, tax_code FROM companies")
    return cursor.fetchall() # [(id, name, tax_code)]

def get_monthly_financials(cursor, company_id):
    # Fetch Revenue (Output target) and Costs (Input target)
    # Using 'operating_revenue' and 'operating_costs'
    query = """
    SELECT period_year, period_month, operating_revenue, operating_costs
    FROM income_statements
    WHERE company_id = ?
    ORDER BY period_year, period_month
    """
    cursor.execute(query, (company_id,))
    return cursor.fetchall()

def generate_invoice_data():
    print("--- Generating Invoice Data ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if companies have tax_code populated, if not backfill dummy
    companies = get_companies(cursor)
    
    # Dummy counter parties
    suppliers = [
        ("Shanghai Tech Supply Co.", "91310115MA1K4HD67J"),
        ("Beijing Services Ltd.", "910101016726879178"),
        ("Shenzhen Electronics", "91440300699068972M"),
        ("Guangzhou Consulting", "91440101MA59K34F21")
    ]
    customers = [
        ("Client A Corp", "91310120MAC2A6RL5D"),
        ("Client B Ltd", "91320507MA21C04U89"),
        ("Client C Inc", "91310118MA1JNAYW7B"),
        ("Client D Group", "913101106854614311")
    ]
    
    invoice_cnt = 0
    
    for comp in companies:
        comp_id, comp_name, comp_tax = comp
        rows = get_monthly_financials(cursor, comp_id)
        
        for row in rows:
            year, month, revenue, costs = row
            if not month: continue # Skip if bad data
            
            # --- Output Invoices (Sales) ---
            # Target: ~95-100% of Revenue
            target_output = revenue * random.uniform(0.95, 1.0)
            generated = 0
            
            while generated < target_output:
                # Random amount for single invoice
                remaining = target_output - generated
                if remaining < 1000:
                    amount = remaining
                else:
                    amount = random.uniform(1000, min(remaining, 50000))
                
                if amount < 0.01: break
                
                generated += amount
                
                cust_name, cust_tax = random.choice(customers)
                day = random.randint(1, 28)
                date_str = f"{year}-{month:02d}-{day:02d}"
                
                # Insert
                cursor.execute("""
                    INSERT INTO invoices (
                        company_id, invoice_type, 
                        seller_name, seller_tax_id, 
                        buyer_name, buyer_tax_id,
                        amount_excluding_tax, tax_rate, tax_amount, total_amount,
                        issue_date, item_name, period_year, period_month, invoice_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp_id, 'OUTPUT',
                    comp_name, comp_tax,
                    cust_name, cust_tax,
                    round(amount, 2), 0.13, round(amount*0.13, 2), round(amount*1.13, 2),
                    date_str, "Technical Services", year, month, 'General Invoice'
                ))
                invoice_cnt += 1
                
            # --- Input Invoices (Costs) ---
            # Target: ~90-110% of Costs
            target_input = costs * random.uniform(0.9, 1.1)
            generated_in = 0
            
            while generated_in < target_input:
                remaining = target_input - generated_in
                if remaining < 1000:
                    amount = remaining
                else:
                    amount = random.uniform(1000, min(remaining, 30000))

                if amount < 0.01: break
                
                generated_in += amount
                
                supp_name, supp_tax = random.choice(suppliers)
                day = random.randint(1, 28)
                date_str = f"{year}-{month:02d}-{day:02d}"
                
                cursor.execute("""
                    INSERT INTO invoices (
                        company_id, invoice_type, 
                        seller_name, seller_tax_id, 
                        buyer_name, buyer_tax_id,
                        amount_excluding_tax, tax_rate, tax_amount, total_amount,
                        issue_date, item_name, period_year, period_month, invoice_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp_id, 'INPUT',
                    supp_name, supp_tax,
                    comp_name, comp_tax,
                    round(amount, 2), 0.06, round(amount*0.06, 2), round(amount*1.06, 2),
                    date_str, "Consulting Fee", year, month, 'Special VAT Invoice'
                ))
                invoice_cnt += 1

    conn.commit()
    conn.close()
    print(f"Generated {invoice_cnt} invoices.")

if __name__ == "__main__":
    generate_invoice_data()
