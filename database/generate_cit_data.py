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
    cursor.execute("DELETE FROM tax_return_income_items")
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
            # we just set reduction to 0 and let payable be nominal? Or allow negative reduction (additional tax)?
            # Let's align exactly to the Financial Statement by forcing the reduction math.
            
            # Insert Return Header
            filing_date_obj = datetime.date(year + 1, 5, 31) # Annual filing by May 31 next year
            filing_txt = filing_date_obj.strftime("%Y-%m-%d")
            
            cursor.execute("""
                INSERT INTO tax_returns_income (company_id, period_year, filing_date)
                VALUES (?, ?, ?)
            """, (company_id, year, filing_txt))
            return_id = cursor.lastrowid
            
            # Insert Return Items
            # Mapping based on "A100000主表" row numbers roughly
            items = [
                (1, "一、营业收入", revenue),
                (2, "减：营业成本", costs),
                (3, "减：税金及附加", taxes),
                (4, "减：销售费用", selling),
                (5, "减：管理费用", admin),
                (6, "减：财务费用", fin_exp),
                (10, "二、营业利润", op_profit),
                (13, "三、利润总额", total_profit),
                (23, "五、应纳税所得额", taxable_income),
                (24, "税率（25%）", standard_tax_rate),
                (25, "六、应纳所得税额", nominal_tax),
                (26, "减：减免所得税额", tax_reduction), # Using this line to bridge the gap
                (28, "七、应纳税额", nominal_tax - tax_reduction), # Should equal actual_tax
                (31, "八、实际应纳所得税额", actual_tax)
            ]
            
            for item in items:
                l_no, name, val = item
                cursor.execute("""
                    INSERT INTO tax_return_income_items (return_id, line_no, item_name, amount)
                    VALUES (?, ?, ?, ?)
                """, (return_id, l_no, name, round(val, 2)))
                
    conn.commit()
    conn.close()
    print("CIT Data Generation Complete.")

if __name__ == "__main__":
    generate_cit_data()
