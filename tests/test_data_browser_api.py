
from fastapi.testclient import TestClient
from server.main import app
import unittest
import sys

client = TestClient(app)

class TestDataBrowserAPI(unittest.TestCase):
    def test_get_tables(self):
        response = client.get("/api/data-browser/tables")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        table_names = [t['name'] for t in data]
        self.assertIn("balance_sheets", table_names)
        self.assertIn("companies", table_names)

    def test_get_companies(self):
        response = client.get("/api/data-browser/companies")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Assuming there's at least one company in the DB
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])

    def test_get_periods_and_data(self):
        # 1. Get a company ID
        companies_resp = client.get("/api/data-browser/companies")
        if companies_resp.status_code != 200 or len(companies_resp.json()) == 0:
            print("No companies found, skipping data tests")
            return
        
        company_id = companies_resp.json()[0]['id']
        
        # 2. Get Periods for balance_sheets
        periods_resp = client.get(f"/api/data-browser/periods?company_id={company_id}&table_name=balance_sheets")
        self.assertEqual(periods_resp.status_code, 200)
        periods = periods_resp.json()
        
        # 3. Get Data (No pagination)
        params = {"company_id": company_id, "table_name": "balance_sheets"}
        if len(periods) > 0:
            params["period"] = periods[0]
            
        data_resp = client.get("/api/data-browser/data", params=params)
        self.assertEqual(data_resp.status_code, 200)
        result = data_resp.json()
        
        self.assertIn("columns", result)
        self.assertIn("data", result)
        self.assertIn("total", result)
        
        # Verify column structure
        self.assertTrue(len(result["columns"]) > 0)
        self.assertIn("key", result["columns"][0])
        self.assertIn("label", result["columns"][0])
        
        # Verify data map
        labels = [c['label'] for c in result["columns"]]
        print(f"Sample columns: {labels[:5]}")

if __name__ == "__main__":
    unittest.main()
