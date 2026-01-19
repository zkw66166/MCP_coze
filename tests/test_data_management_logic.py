
import sys
import os
import asyncio

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.routers.data_management import get_data_management_stats

async def test_logic():
    print("Testing Multi-Company Stats (Logic Only)...")
    stats = await get_data_management_stats(company_id=None)
    
    assert "summary" in stats
    print(f"Summary: {stats['summary']}")
    assert stats['summary']['report_count'] >= 0
    
    assert "companies" in stats
    print(f"Companies Count: {len(stats['companies'])}")
    
    assert "mapping_synonyms" in stats
    print(f"Synonyms Count: {len(stats['mapping_synonyms'])}")
    assert stats['mapping_synonyms'][0]['standard'] == "Balance Sheet"

    print("\nTesting Single-Company Stats (Logic Only)...")
    # Get a company ID first - hardcoded logic or dynamic if possible
    # We will try to fetch stats for company_id=1 (assuming it exists, or just check logic handles not found)
    # Actually, the function requires a valid ID or it might fail if we don't have one? 
    # Let's check logic: if company_id is provided, it tries to fetch name. 
    # Let's try to get ID from the multi-response first.
    
    if len(stats['companies']) > 0:
        cid = stats['companies'][0]['id']
        single_stats = await get_data_management_stats(company_id=cid)
        print(f"Single Stats for ID {cid}: {single_stats['summary']}")
        assert len(single_stats['companies']) == 1
        assert single_stats['companies'][0]['id'] == cid
    else:
        print("No companies found in DB to test single mode.")

if __name__ == "__main__":
    try:
        asyncio.run(test_logic())
        print("\nALL LOGIC TESTS PASSED")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
