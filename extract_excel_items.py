import pandas as pd
import os
import glob

# Use glob to find the files to avoid character encoding issues with exact paths if possible
base_dir = r"D:\MyProjects\MCP_coze\data_source\财务数据库数据源模版\财务报表"

def extract_items():
    print("--- Extracting Items from Excel ---")
    
    # helper to find file
    def find_file(name_part):
        pattern = os.path.join(base_dir, f"*{name_part}*.xlsx")
        files = glob.glob(pattern)
        return files[0] if files else None

    # 1. Income Statement
    f = find_file("利润表")
    if f:
        print(f"\nProcessing: {os.path.basename(f)}")
        try:
            # Skip header rows to get to data. Usually header is complex. 
            # Looking at previous output, row 1 (index) had "项目". So data starts row 2.
            df = pd.read_excel(f, skiprows=1) 
            # Column 0 seems to be "项目" based on prev output
            items = df.iloc[:, 0].dropna().tolist()
            print(f"Items found ({len(items)}):")
            for i in items:
                print(f" - {i}")
        except Exception as e:
            print(f"Error: {e}")

    # 2. Balance Sheet
    f = find_file("资产负债表")
    if f:
        print(f"\nProcessing: {os.path.basename(f)}")
        try:
            df = pd.read_excel(f, skiprows=1)
            # Balance sheet usually has Left (Assets) and Right (Liabilities)
            # Col 0: Assets Item, Col 4: Liabilities Item (check previous output or guess)
            # Prev output: 
            # 0: 资产
            # 4: 负债及所有者权益
            col0_items = df.iloc[:, 0].dropna().tolist()
            col4_items = df.iloc[:, 4].dropna().tolist() # Adjust index if needed
            print(f"Assets Items ({len(col0_items)}):")
            for i in col0_items:
                print(f" - {i}")
            print(f"Liabilities Items ({len(col4_items)}):")
            for i in col4_items:
                print(f" - {i}")
        except Exception as e:
            print(f"Error: {e}")

    # 3. Cash Flow
    f = find_file("现金流量表")
    if f:
        print(f"\nProcessing: {os.path.basename(f)}")
        try:
            df = pd.read_excel(f, skiprows=1) # Adjust skiprows likely
            # Col 0 is likely item
            items = df.iloc[:, 0].dropna().tolist()
            print(f"Items found ({len(items)}):")
            for i in items:
                print(f" - {i}")
        except Exception as e:
            print(f"Error: {e}")
            
    # 4. Account Balances
    f = find_file("科目余额表")
    if f:
        print(f"\nProcessing: {os.path.basename(f)}")
        try:
            # Row 0 is header: 科目代码 科目名称 ...
            df = pd.read_excel(f)
            print(f"Columns: {df.columns.tolist()}")
            # We just need to ensure we have these columns in DB
        except Exception as e:
             print(f"Error: {e}")

if __name__ == "__main__":
    extract_items()
