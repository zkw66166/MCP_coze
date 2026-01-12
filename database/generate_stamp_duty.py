import sqlite3
import datetime

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def get_companies(cursor):
    cursor.execute("SELECT id FROM companies")
    return [row[0] for row in cursor.fetchall()]

def get_quarterly_revenue(cursor, company_id):
    query = """
    SELECT period_year, period_quarter, total_revenue
    FROM income_statements
    WHERE company_id = ?
    ORDER BY period_year, period_quarter
    """
    cursor.execute(query, (company_id,))
    return cursor.fetchall()

def generate_stamp_duty():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("DELETE FROM tax_return_stamp_items")
    cursor.execute("DELETE FROM tax_returns_stamp")
    conn.commit()

    companies = get_companies(cursor)
    print(f"Generating Stamp Duty data for {len(companies)} companies...")

    for company_id in companies:
        revenues = get_quarterly_revenue(cursor, company_id)
        
        for row in revenues:
            year, quarter, revenue = row
            
            # Logic:
            # 1. Tax Base = Revenue (Assuming all revenue is from Sales Contracts "买卖合同")
            tax_base = revenue
            
            # 2. Rate = 0.03% (0.0003)
            rate = 0.0003
            
            # 3. Tax Payable = Base * Rate
            payable = tax_base * rate
            
            # 4. Reduction = 50% (Small Micro Enterprise Policy "六税两费"减免)
            reduction = payable * 0.5
            
            # 5. Final Amount
            final_tax = payable - reduction
            
            # Insert Return Header
            # Quarterly filing: usually by 15th of next month after quarter end
            # Q1: Apr 15, Q2: Jul 15, Q3: Oct 15, Q4: Jan 15 (next year)
            if quarter == 4:
                filing_year = year + 1
                filing_month = 1
            else:
                filing_year = year
                filing_month = quarter * 3 + 1
            
            filing_date_obj = datetime.date(filing_year, filing_month, 15)
            filing_txt = filing_date_obj.strftime("%Y-%m-%d")
            
            cursor.execute("""
                INSERT INTO tax_returns_stamp (company_id, period_year, period_quarter, filing_date)
                VALUES (?, ?, ?, ?)
            """, (company_id, year, quarter, filing_txt))
            return_id = cursor.lastrowid
            
            # Insert Return Items
            cursor.execute("""
                INSERT INTO tax_return_stamp_items (
                    return_id, tax_category, tax_item, 
                    tax_base, tax_rate, tax_payable, tax_reduction, tax_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (return_id, "印花税", "买卖合同", round(tax_base, 2), rate, round(payable, 2), round(reduction, 2), round(final_tax, 2)))
                
    conn.commit()
    conn.close()
    print("Stamp Duty Data Generation Complete.")

if __name__ == "__main__":
    generate_stamp_duty()
