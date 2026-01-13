
import sys
import unittest
from modules.financial_query import FinancialQuery
from modules.text_to_sql import TextToSQLEngine

# Add project root to path
sys.path.append('d:/MyProjects/MCP_coze')

def debug_sql_generation():
    engine = TextToSQLEngine()
    
    # Test Case 1: Tax Burden (Ratio)
    print("\n--- TEST 1: Tax Burden ---")
    q1 = "2023年增值税税负"
    # Note: We must mock the schema provider or ensure it works locally
    # We will try to run query() directly but we need to see the SQL string.
    # The current engine.query() prints the SQL if successful, but let's be explicit.
    
    # We need to construct the prompt and just print it, OR run a query and inspect logs
    prompt = engine._build_prompt(q1, 1, [2023])
    print(f"PROMPT SENT:\n{prompt}\n")

    # Actually generate SQL (requires LLM API key)
    # Since _generate_sql_from_llm does not exist, we extract the logic from generate_sql method
    # or just use the public .generate_sql() if available?
    # Inspecting source: it has generate_sql(self, question, company_id, ...).
    try:
        # We use the public method generate_sql which returns the SQL string
        system_sql = engine.generate_sql(q1, 1, [2023])
        print(f"GENERATED SQL 1: {system_sql}")
    except Exception as e:
        print(f"Error 1 details: {e}")

    # Test Case 2: Headcount (Snapshot)
    print("\n--- TEST 2: Headcount ---")
    q2 = "2023年销售部人数"
    try:
        system_sql2 = engine.generate_sql(q2, 1, [2023])
        print(f"GENERATED SQL 2: {system_sql2}")
    except Exception as e:
        print(f"Error 2: {e}")

if __name__ == "__main__":
    debug_sql_generation()
