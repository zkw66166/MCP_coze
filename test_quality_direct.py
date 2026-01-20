"""
直接测试 DataQualityChecker 模块
"""
import sys
sys.path.insert(0, 'server')

from services.data_quality import DataQualityChecker

db_path = "database/financial.db"
print(f"Testing DataQualityChecker with DB: {db_path}")

try:
    checker = DataQualityChecker(db_path)
    print("✓ DataQualityChecker created successfully")
    
    print("\n1. Testing get_available_periods(5)...")
    periods = checker.get_available_periods(5)
    for table, p_list in periods.items():
        print(f"  {table}: {len(p_list)} periods")
    
    print("\n2. Testing check_all(5)...")
    results = checker.check_all(5)
    
    print(f"\n=== Summary ===")
    summary = results.get('summary', {})
    print(f"  Total Tables: {summary.get('total_tables')}")
    print(f"  Total Periods: {summary.get('total_periods')}")
    print(f"  Total Checks: {summary.get('total_checks')}")
    print(f"  Pass Rate: {summary.get('pass_rate')}%")
    
    print(f"\n=== Results by Table ===")
    for table_key, table_result in results.get('results_by_table', {}).items():
        status = table_result.get('status', 'unknown')
        print(f"  {table_result.get('table_name')}: {status} ({table_result.get('period_count')} periods)")
        
except Exception as e:
    import traceback
    print(f"✗ Error: {e}")
    traceback.print_exc()
