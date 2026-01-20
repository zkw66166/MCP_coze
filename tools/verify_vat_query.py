
import sqlite3
import os

DB_PATH = r'D:\MyProjects\MCP_coze\database\financial.db'

def verify_vat_query():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Try for a known company and year
    company_id = 1
    year = 2024
    
    print(f"Checking VAT for Company {company_id}, Year {year}...")
    
    try:
        cursor.execute('''
            SELECT SUM(gen_tax_payable_current) as vat_amount
            FROM tax_returns_vat
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        vat_row = cursor.fetchone()
        vat_amount = vat_row["vat_amount"] if vat_row and vat_row["vat_amount"] else 0
        print(f"Success! VAT Amount: {vat_amount}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_vat_query()
