import requests
import json

# 测试API返回
response = requests.get('http://localhost:8000/api/company-profile/8/financial?year=2024')
print(f"Status: {response.status_code}")
print(f"\n完整响应 JSON:")
data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

print(f"\n关键字段检查:")
print(f"  sales_expense: {data.get('sales_expense')}")
print(f"  admin_expense: {data.get('admin_expense')}")
print(f"  cash_flow: {data.get('cash_flow')}")
print(f"  data_source: {data.get('data_source')}")
print(f"\n指标数量: {len(data.get('metrics', []))}")
for i, m in enumerate(data.get('metrics', [])[:5], 1):
    print(f"  {i}. {m.get('name')}: {m.get('value')} {m.get('unit', '')}")
