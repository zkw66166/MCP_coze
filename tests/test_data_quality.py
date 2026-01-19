
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.services.data_quality import DataQualityChecker

def test_quality_checker():
    # Use real DB
    db_path = "D:\\MyProjects\\MCP_coze\\database\\financial.db"
    
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    checker = DataQualityChecker(db_path)
    
    # Test for Company 5, Year 2022, Month 3 (Data seen in inspection)
    print("Running Quality Check for Company 5 (2022-03)...")
    results = checker.check_all(5, 2022, 3)
    
    for category, res in results.items():
        print(f"\n--- {category.upper()} ---")
        if res.get('status') == 'skip':
            print(f"SKIPPED: {res.get('message')}")
            continue
            
        print(f"Status: {res['status']} (Passed: {res['passed_checks']}/{res['total_checks']})")
        for detail in res['details']:
            status_icon = "✅" if detail['status'] == 'pass' else "❌"
            msg = f"{status_icon} {detail['check']}"
            if detail['status'] == 'fail':
                 msg += f" | Expected: {detail.get('expected')}, Actual: {detail.get('actual')}"
            print(msg)

if __name__ == "__main__":
    test_quality_checker()
