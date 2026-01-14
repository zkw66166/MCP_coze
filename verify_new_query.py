from modules.financial_query import FinancialQuery
import sys

# Initialize
fq = FinancialQuery()
fq.reload_config()

print("--- Testing CIT Queries with New Schema ---")
questions = [
    "2023年太空科技公司的应纳税所得额是多少",
    "2023年太空科技公司的实际应纳所得税额",
    "太空科技2023年企业所得税营业收入",
    "太空科技2023年应纳所得税额"
]

for q in questions:
    print(f"\nQ: {q}")
    results, company, status = fq.search(q)
    print(f"Status: {status}")
    if results:
        for r in results:
            print(f"  - {r['metric_name']}: {r['value']} {r['unit']} (Year: {r['year']})")
    else:
        print("  No results found.")
