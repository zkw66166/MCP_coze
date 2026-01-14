import sqlite3
import datetime

db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def get_companies(cursor):
    cursor.execute("SELECT id FROM companies")
    return [row[0] for row in cursor.fetchall()]

def get_annual_financials(cursor, company_id):
    # Sum quarterly data to get annual totals
    query = """
    SELECT 
        period_year,
        SUM(operating_revenue) as revenue,
        SUM(operating_costs) as costs,
        SUM(taxes_and_surcharges) as taxes,
        SUM(selling_expenses) as selling,
        SUM(administrative_expenses) as admin,
        SUM(financial_expenses) as fin_exp,
        SUM(operating_profit) as op_profit,
        SUM(total_profit) as total_profit,
        SUM(income_tax_expense) as tax_expense
    FROM income_statements
    WHERE company_id = ?
    GROUP BY period_year
    """
    cursor.execute(query, (company_id,))
    return cursor.fetchall()

def generate_cit_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old data
    # cursor.execute("DELETE FROM tax_return_income_items") # Table migrated
    cursor.execute("DELETE FROM tax_returns_income")
    conn.commit()

    companies = get_companies(cursor)
    print(f"Generating CIT data for {len(companies)} companies...")

    for company_id in companies:
        annual_data = get_annual_financials(cursor, company_id)
        
        for row in annual_data:
            year, revenue, costs, taxes, selling, admin, fin_exp, op_profit, total_profit, actual_tax_expense = row
            
            # Logic:
            # 1. Taxable Income = Total Profit (Simplify: no adjustments)
            taxable_income = total_profit
            
            # 2. Standard Tax = Taxable * 25%
            standard_tax_rate = 0.25
            nominal_tax = taxable_income * standard_tax_rate
            
            # 3. Actual Tax (Target) = From DB (~15%)
            actual_tax = actual_tax_expense
            
            # 4. Reduction needed
            tax_reduction = nominal_tax - actual_tax
            
            # If reduction is negative (Actual > Standard), which is rare but possible if mistakes exist,
            # we align exactly to the Financial Statement.
            
            tax_payable = nominal_tax - tax_reduction
            final_tax_payable = actual_tax

            # Insert Return (Flattened)
            filing_date_obj = datetime.date(year + 1, 5, 31) # Annual filing by May 31 next year
            filing_txt = filing_date_obj.strftime("%Y-%m-%d")
            
            cursor.execute("""
                INSERT INTO tax_returns_income (
                    company_id, period_year, filing_date,
                    revenue, cost, taxes_and_surcharges, 
                    selling_expenses, administrative_expenses, financial_expenses,
                    operating_profit, total_profit, 
                    taxable_income, tax_rate, nominal_tax, 
                    tax_reduction, tax_payable, final_tax_payable
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, year, filing_txt,
                revenue, costs, taxes,
                selling, admin, fin_exp,
                op_profit, total_profit,
                taxable_income, standard_tax_rate, nominal_tax,
                tax_reduction, tax_payable, final_tax_payable
            ))
                
    conn.commit()
    conn.close()
    print("CIT Data Generation Complete (Flattened Schema).")

if __name__ == "__main__":
    generate_cit_data()
