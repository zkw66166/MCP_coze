import requests
import json

BASE_URL = "http://localhost:8000"

def test_income_statement():
    print("Testing income_statements data...")
    
    # 1. Get Company
    resp = requests.get(f"{BASE_URL}/api/data-browser/companies")
    if resp.status_code != 200 or not resp.json():
        print("No companies.")
        return
    company_id = resp.json()[0]['id']
    
    # 2. Get Data
    resp = requests.get(f"{BASE_URL}/api/data-browser/data", 
                        params={"company_id": company_id, "table_name": "income_statements"})
    
    if resp.status_code == 200:
        data = resp.json()
        rows = data['data']
        if not rows:
            print("No data for income_statements.")
            return

        row = rows[0]
        # Check for key fields used in Raw View
        required_fields = [
            "total_revenue", "cost_of_sales", "taxes_and_surcharges", 
            "selling_expenses", "administrative_expenses", "financial_expenses",
            "operating_profit", "total_profit", "income_tax_expense", "net_profit"
        ]
        
        missing = [f for f in required_fields if f not in row]
        if missing:
            print(f"❌ Missing fields in response: {missing}")
        else:
            print("✅ All required fields present.")
            print(f"Sample Revenue: {row.get('total_revenue')}")
            
    else:
        print(f"Failed to get data: {resp.text}")

if __name__ == "__main__":
    try:
        test_income_statement()
    except Exception as e:
        print(f"Error: {e}")
