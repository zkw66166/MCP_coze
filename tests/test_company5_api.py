import requests
import json

# 测试公司5, 2023年的完整接口
print("=" * 80)
print("测试完整画像接口 - 公司5, 2023年")
print("=" * 80)

try:
    response = requests.get('http://localhost:8000/api/company-profile/5?year=2023')
    if response.status_code == 200:
        data = response.json()
        
        fs = data.get('financial_summary', {})
        gm = data.get('growth_metrics', {})
        cf = data.get('cash_flow_summary', {})
        inv = data.get('invoice_summary', {})
        
        print(f"\n✅ API返回成功")
        
        print(f"\n[financial_summary 根字段]")
        fields = ['revenue', 'net_profit', 'gross_margin', 'net_margin', 'debt_ratio', 'current_ratio', 'quick_ratio', 'asset_turnover']
        for f in fields:
            print(f"  {f:20}: {fs.get(f)}")
            
        print(f"\n[growth_metrics]")
        for f in ['revenue_growth', 'profit_growth', 'asset_growth']:
            print(f"  {f:20}: {gm.get(f)}")
            
        print(f"\n[cash_flow_summary]")
        for f in ['operating', 'investing', 'financing']:
            print(f"  {f:20}: {cf.get(f)}")
            
        print(f"\n[invoice_summary]")
        for f in ['sales_count', 'purchase_count']:
            print(f"  {f:20}: {inv.get(f)}")
            
    else:
        print(f"❌ API返回失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ 连接失败: {e}")

print("\n" + "=" * 80)
