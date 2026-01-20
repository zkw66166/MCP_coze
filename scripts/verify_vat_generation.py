
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = 'database/financial.db'

def verify_data():
    conn = sqlite3.connect(DB_PATH)
    
    print("=== VAT Comprehensive Data Verification ===")
    
    # 1. Formula Check: Row 19 = 11 - 18
    # gen_tax_payable_current = gen_output_tax_current - gen_actual_deduction_current
    # (Note: Logic is Max(0, ...), so check if positive matches)
    print("\n[Formula Check: Row 19 = 11 - 18]")
    sql_f1 = """
        SELECT count(*) as fail_count 
        FROM tax_returns_vat 
        WHERE gen_tax_payable_current > 0 
          AND ABS(gen_tax_payable_current - (gen_output_tax_current - gen_actual_deduction_current)) > 0.02
    """
    fails = pd.read_sql(sql_f1, conn).iloc[0]['fail_count']
    print(f"Formula Violations (Payable > 0): {fails}")
    
    # 2. Formula Check: Row 18 = 12 + 13 - 14
    # gen_actual_deduction = gen_input_tax + gen_previous_credit - gen_input_tax_transfer
    print("\n[Formula Check: Row 18 = 12 + 13 - 14]")
    sql_f2 = """
        SELECT count(*) as fail_count
        FROM tax_returns_vat
        WHERE ABS(gen_actual_deduction_current - (gen_input_tax_current + gen_previous_credit_current - gen_input_tax_transfer_current)) > 0.02
    """
    fails = pd.read_sql(sql_f2, conn).iloc[0]['fail_count']
    print(f"Formula Violations (Actual Deduction): {fails}")
    
    # 3. Completeness of New Fields
    print("\n[Field Completeness]")
    # Check if 'gen_sales_goods_current' or 'gen_sales_service_current' are populated
    df_comp = pd.read_sql("""
        SELECT 
            SUM(CASE WHEN gen_sales_goods_current > 0 THEN 1 ELSE 0 END) as goods_rows,
            SUM(CASE WHEN gen_sales_service_current > 0 THEN 1 ELSE 0 END) as service_rows,
            SUM(CASE WHEN gen_input_tax_transfer_current > 0 THEN 1 ELSE 0 END) as transfer_rows
        FROM tax_returns_vat
    """, conn)
    print(df_comp)
    
    # 4. Refund Logic Check
    print("\n[Refund Logic]")
    # Software companies (5, 10) should have 'ref_actual_refund_current' data
    # Manufacturing (8, 11) should have all 0
    df_ref = pd.read_sql("""
        SELECT company_id, 
               SUM(ref_actual_refund_current) as total_refund,
               SUM(ref_sales_taxable_current) as total_ref_sales
        FROM tax_returns_vat
        GROUP BY company_id
    """, conn)
    print(df_ref)
    
    conn.close()

if __name__ == "__main__":
    verify_data()
