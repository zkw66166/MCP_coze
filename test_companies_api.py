import requests
import json

BASE_URL = "http://localhost:8000"

def test_companies():
    print("Testing /companies API...")
    resp = requests.get(f"{BASE_URL}/api/data-browser/companies")
    if resp.status_code != 200:
        print(f"Failed: {resp.status_code}")
        return
    
    data = resp.json()
    print(f"Got {len(data)} companies.")
    if len(data) > 0:
        print("First company sample:", data[0])
        print("Keys:", data[0].keys())

if __name__ == "__main__":
    test_companies()
