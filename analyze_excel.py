import pandas as pd
import os

excel_path = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\增值税申报表（主表_一般纳税人适用）.xlsx"

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
            # Read first few rows to understand where the header is
            df = pd.read_excel(xls, sheet_name=sheet_name, nrows=20, header=None) 
            print(df.to_string())
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    analyze_excel()
