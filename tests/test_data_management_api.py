
# import pytest (removed)
from fastapi.testclient import TestClient
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app

client = TestClient(app)

def test_data_management_stats_multi():
    """Test fetching multi-company stats (no company_id param)"""
    response = client.get("/api/data-management/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert "summary" in data
    assert "companies" in data
    assert "mapping_synonyms" in data
    assert "quality_checks" in data # This might be empty if no companies, but key should exist
    
    # Verify synonyms are present
    assert len(data['mapping_synonyms']) > 0
    assert data['mapping_synonyms'][0]['standard'] == "Balance Sheet"

def test_data_management_stats_single():
    """Test fetching single-company stats (with company_id param)"""
    # First get a valid company ID
    companies_resp = client.get("/api/companies")
    if companies_resp.status_code == 200 and len(companies_resp.json()) > 0:
        company_id = companies_resp.json()[0]['id']
        
        response = client.get(f"/api/data-management/stats?company_id={company_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Structure check
        assert "summary" in data
        assert "companies" in data # Should be a list with 1 item
        assert len(data['companies']) == 1
        assert data['companies'][0]['id'] == company_id

if __name__ == "__main__":
    # Manually run tests if executed properly
    try:
        test_data_management_stats_multi()
        print("test_data_management_stats_multi PASSED")
        test_data_management_stats_single()
        print("test_data_management_stats_single PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
