import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.routers.company_profile import get_company_profile

async def main():
    try:
        print("Calling get_company_profile(8, 2024)...")
        result = await get_company_profile(company_id=8, year=2024)
        print("Success!")
        # print(result)
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
