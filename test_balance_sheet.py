import requests
import json

BASE_URL = "http://localhost:8000"

def test_balance_sheet():
    print("Testing balance_sheets data...")
    
    # 1. Get Company
    resp = requests.get(f"{BASE_URL}/api/data-browser/companies")
    if resp.status_code != 200 or not resp.json():
        print("No companies.")
        return
    company_id = resp.json()[0]['id']
    
    # 2. Get Data
    resp = requests.get(f"{BASE_URL}/api/data-browser/data", 
                        params={"company_id": company_id, "table_name": "balance_sheets"})
    
    if resp.status_code == 200:
        data = resp.json()
        rows = data['data']
        if not rows:
            print("No data for balance_sheets.")
            return

        row = rows[0]
        # Check for key fields used in Raw View
        required_fields = [
            "cash_and_equivalents", "short_term_loans", 
            "notes_payable", "accounts_payable", "contract_liabilities",
            "prepayments", "inventory", "total_assets", "total_liabilities", "total_equity"
        ]
        
        missing = [f for f in required_fields if f not in row]
        if missing:
            print(f"❌ Missing fields in response: {missing}")
        else:
            print("✅ All check fields present.")
            print(f"Sample Total Assets: {row.get('total_assets')}")
            
    else:
        print(f"Failed to get data: {resp.text}")

if __name__ == "__main__":
    try:
        test_balance_sheet()
    except Exception as e:
        print(f"Error: {e}")
