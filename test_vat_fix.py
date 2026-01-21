
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_vat_data():
    print("Testing VAT Data Retrieval...")
    
    # 1. Get Tables to confirm tax_returns_vat is there
    print("\n1. Testing /api/data-browser/tables")
    try:
        resp = requests.get(f"{BASE_URL}/api/data-browser/tables")
        if resp.status_code == 200:
            tables = resp.json()
            table_dict = {t['name']: t['label'] for t in tables}
            if "tax_returns_vat" in table_dict:
                print("✅ Success: tax_returns_vat found in tables")
            else:
                print("❌ Failed: tax_returns_vat NOT found in tables")
                print(f"   Available tables: {list(table_dict.keys())}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # 2. Get Data for tax_returns_vat
    print("\n2. Testing /api/data-browser/data for tax_returns_vat")
    try:
        # Get first company
        comp_resp = requests.get(f"{BASE_URL}/api/data-browser/companies")
        if comp_resp.status_code != 200 or not comp_resp.json():
            print("Skipping data test: No companies found")
            return
        company_id = comp_resp.json()[0]['id']
        
        # Test get_periods
        print("\n   Testing /api/data-browser/periods")
        per_resp = requests.get(f"{BASE_URL}/api/data-browser/periods", 
                              params={"company_id": company_id, "table_name": "tax_returns_vat"})
        if per_resp.status_code == 200:
            periods = per_resp.json()
            if periods:
                print(f"   ✅ Periods found: {periods[:3]}...")
                if "月" in periods[0] and "Q" not in periods[0]:
                     print("   ✅ Valid Monthly Period Format")
                else:
                     print(f"   ⚠️ Warning: Unexpected format: {periods[0]}")
            else:
                 print("   ⚠️ No periods found")
        else:
             print(f"   ❌ Failed to get periods: {per_resp.status_code}")

        # Fetch data
        resp = requests.get(f"{BASE_URL}/api/data-browser/data",
                          params={"company_id": company_id, "table_name": "tax_returns_vat"})
        
        if resp.status_code == 200:
            data = resp.json()
            # print(data.keys())
            rows = data.get('data', [])
            if rows:
                first_row = rows[0]
                if 'start_date' in first_row and 'end_date' in first_row:
                    print(f"   ✅ Dynamic Date Calculation: {first_row.get('start_date')} - {first_row.get('end_date')}")
                else:
                    print("   ❌ Missing start_date or end_date in row data")
            
            print(f"   Total Records: {len(data.get('data', []))}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_vat_data()
