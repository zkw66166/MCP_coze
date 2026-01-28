import requests
import json

# 测试年度汇总API
print("=" * 80)
print("测试年度汇总API - 公司8, 2024年")
print("=" * 80)

response = requests.get('http://localhost:8000/api/company-profile/8/financial?year=2024')
data = response.json()

print(f"\n✅ API返回成功 (status: {response.status_code})")
print(f"\n数据来源: {data.get('data_source')}")
print(f"更新时间: {data.get('last_updated')}")

print(f"\n=== 流量指标（应为全年汇总） ===")
print(f"  销售费用:   {data.get('selling_expense')/10000:.0f} 万元  (预期: ~3103万)")
print(f"  管理费用:   {data.get('admin_expense')/10000:.0f} 万元  (预期: ~2365万)")
print(f"  发票数量:")
inv = data.get('invoice_summary', {})
print(f"    销售发票: {inv.get('sales_count')} 张  (预期: ~2787张, 4季度汇总)")
print(f"    采购发票: {inv.get('purchase_count')} 张  (预期: ~3585张)")

print(f"\n现金流（全年累计）:")
cf = data.get('cash_flow', {})
print(f"  经营活动: {cf.get('operating')/10000:.0f} 万")
print(f"  投资活动: {cf.get('investing')/10000:.0f} 万")  
print(f"  筹资活动: {cf.get('financing')/10000:.0f} 万")

print(f"\n=== 比率指标 ===")
print(f"指标数量: {len(data.get('metrics', []))}")
for i, m in enumerate(data.get('metrics', [])[:8], 1):
    print(f"  {i}. {m.get('name')}: {m.get('value')}{m.get('unit', '')} - {m.get('evaluation', 'N/A')}")

print("\n" + "=" * 80)
