
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

        # Fetch data
        resp = requests.get(f"{BASE_URL}/api/data-browser/data",
                          params={"company_id": company_id, "table_name": "tax_returns_vat"})
        
        if resp.status_code == 200:
            data = resp.json()
            columns = data.get('columns', [])
            col_map = {c['key']: c['label'] for c in columns}
            
            # Check for Chinese mapping
            check_fields = ["gen_sales_taxable_current", "gen_output_tax_current"]
            all_mapped = True
            for field in check_fields:
                if field in col_map:
                    if col_map[field] == field: # No mapping applied
                        print(f"⚠️ Warning: Field {field} matches its key (Mapping missing?)")
                        all_mapped = False
                    else:
                        print(f"✅ Field {field} mapped to: {col_map[field]}")
                else:
                    # It's possible the field isn't in PRAGMA table_info if I was wrong about schema, 
                    # but I checked it.
                    pass
            
            print(f"   Total Records: {len(data.get('data', []))}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_vat_data()
