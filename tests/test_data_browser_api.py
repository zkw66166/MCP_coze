
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_data_browser_api():
    print("Testing Data Browser API...")
    
    # 1. Test Tables List
    print("\n1. Testing /api/data-browser/tables")
    try:
        resp = requests.get(f"{BASE_URL}/api/data-browser/tables")
        if resp.status_code == 200:
            tables = resp.json()
            print(f"✅ Success: Retrieved {len(tables)} tables")
            print(f"   Tables: {[t['name'] for t in tables]}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # 2. Test Companies List
    print("\n2. Testing /api/data-browser/companies")
    company_id = None
    try:
        resp = requests.get(f"{BASE_URL}/api/data-browser/companies")
        if resp.status_code == 200:
            companies = resp.json()
            print(f"✅ Success: Retrieved {len(companies)} companies")
            if companies:
                company_id = companies[0]['id']
                print(f"   Using Company ID: {company_id} for next tests")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    if not company_id:
        print("Skipping remaining tests due to no company ID")
        return

    # 3. Test Periods List
    print("\n3. Testing /api/data-browser/periods")
    try:
        # Test for balance_sheets
        table_name = "balance_sheets"
        resp = requests.get(f"{BASE_URL}/api/data-browser/periods", 
                          params={"company_id": company_id, "table_name": table_name})
        if resp.status_code == 200:
            periods = resp.json()
            print(f"✅ Success: Retrieved {len(periods)} periods for {table_name}")
            print(f"   Sample periods: {periods[:3]}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # 4. Test Data Retrieval
    print("\n4. Testing /api/data-browser/data")
    try:
        # Test getting all data for balance_sheets
        table_name = "balance_sheets"
        resp = requests.get(f"{BASE_URL}/api/data-browser/data",
                          params={"company_id": company_id, "table_name": table_name})
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Success: Retrieved data structure")
            print(f"   Columns (Chinese): {data.get('columns', [])[:5]}...")
            print(f"   Total Records: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"   Sample Record: {list(data['data'][0].values())[:5]}...")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_data_browser_api()
