import pandas as pd
import os

excel_path = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\财务报表\现金流量表.xlsx"

def analyze_cash_flow():
    print("--- Analyzing Cash Flow Excel ---")
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return

    try:
        # Read first few rows to understand structure
        df = pd.read_excel(excel_path)
        print(df.head(40).to_string())
        
        # Identify key columns. Usually "项目" (Item) and "金额" (Amount)
        # Based on typical CAS format, it might be:
        # Item | Current Amount | Previous Amount
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    analyze_cash_flow()
