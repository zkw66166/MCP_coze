import pandas as pd
import sqlite3
import os

excel_path = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\企业所得税申报表（基础表+主表）.xlsx"
db_path = r"D:\MyProjects\MCP_coze\database\financial.db"

def analyze_excel():
    print("--- Analysis of Excel File ---")
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return

    try:
        xls = pd.ExcelFile(excel_path)
        print(f"Sheet names: {xls.sheet_names}")
        for sheet_name in xls.sheet_names:
            print(f"\nSheet: {sheet_name}")
            # Read first few rows to understand structure
            df = pd.read_excel(xls, sheet_name=sheet_name, nrows=35) 
            print(df.head(35).to_string()) # Print more rows to see the main table structure
    except Exception as e:
        print(f"Error reading Excel: {e}")

def check_db_nature():
    print("\n--- Checking Income Statement Data Nature (Discrete vs Cumulative) ---")
    conn = sqlite3.connect(db_path)
    # Check one company's revenue trend for 2022
    query = """
    SELECT period_year, period_quarter, total_revenue 
    FROM income_statements 
    WHERE company_id = (SELECT id FROM companies LIMIT 1) AND period_year = 2022
    ORDER BY period_quarter
    """
    df = pd.read_sql_query(query, conn)
    print(df)
    
    # logic check: if Q4 >> Q1+Q2+Q3, it might be cumulative. 
    # if Q1 ~ Q2 ~ Q3 ~ Q4, it is discrete.
    conn.close()

if __name__ == "__main__":
    analyze_excel()
    check_db_nature()
