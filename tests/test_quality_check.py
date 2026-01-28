"""
Test script for data quality check API
"""
import requests
import json

BASE_URL = "http://localhost:8188"

def test_quality_check(company_id=5):
    url = f"{BASE_URL}/api/data-management/quality-check"
    if company_id:
        url += f"?company_id={company_id}"
    
    print(f"Testing: POST {url}")
    try:
        response = requests.post(url)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✓ Response Status: {response.status_code}")
        print(f"\n=== Summary ===")
        summary = data.get('summary', {})
        print(f"  Company ID: {data.get('company_id')}")
        print(f"  Total Tables: {summary.get('total_tables')}")
        print(f"  Total Periods: {summary.get('total_periods')}")
        print(f"  Total Checks: {summary.get('total_checks')}")
        print(f"  Passed: {summary.get('passed_checks')}")
        print(f"  Failed: {summary.get('failed_checks')}")
        print(f"  Pass Rate: {summary.get('pass_rate')}%")
        
        print(f"\n=== Results by Table ===")
        for table_key, table_result in data.get('results_by_table', {}).items():
            status = table_result.get('status', 'unknown')
            status_icon = '✓' if status == 'pass' else '✗' if status == 'fail' else '-'
            print(f"\n{status_icon} {table_result.get('table_name')} ({table_key})")
            print(f"    Periods: {table_result.get('period_count')}, Status: {status}")
            
            # Show first few period results
            periods = table_result.get('periods', [])[:3]
            for p in periods:
                p_status = '✓' if p['status'] == 'pass' else '✗' if p['status'] == 'fail' else '-'
                print(f"      {p_status} {p['period']}: {p['status']} ({p.get('passed_checks', 0)}/{p.get('total_checks', 0)} passed)")
            if len(table_result.get('periods', [])) > 3:
                print(f"      ... and {len(table_result.get('periods', [])) - 3} more periods")
        
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to server. Make sure the backend is running on port 8188.")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_quality_check(5)
