
import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def reproduce():
    # Mock results as described by user: 2022 Q1 - 2024 Q4
    results = []
    years = [2022, 2023, 2024]
    quarters = [1, 2, 3, 4]
    
    for y in years:
        for q in quarters:
            results.append({
                'metric_name': '一般项目应纳税额',
                'year': y,
                'quarter': q,
                'value': 1000 + (y-2022)*400 + q*100, # Dummy increasing values
                'unit': '元'
            })
            
    print(f"\nResults count: {len(results)}")
    
    # Mock company
    company = {'id': 1, 'name': '测试公司'}

    # 2. Simulate stream_financial_response logic for chart generation
    print("\n--- Simulating Chart Generation ---")
    if len(results) >= 2:
        metrics_map = {} 
        all_periods = set()
        
        for r in results:
            m = r['metric_name']
            p = (r['year'], r.get('quarter'))
            all_periods.add(p)
            if m not in metrics_map:
                metrics_map[m] = {}
            metrics_map[m][p] = r['value']
        
        # Sort logic from chat.py
        sorted_periods = sorted(list(all_periods), key=lambda x: (x[0], x[1] or 0))
        print(f"Sorted Periods ({len(sorted_periods)}): {sorted_periods}")
        
        unique_metrics = list(metrics_map.keys())
        # print(f"Unique Metrics: {unique_metrics}")
        
        if len(unique_metrics) == 1:
            metric = unique_metrics[0]
            values = []
            growth_amounts = []
            growth_rates = []
            
            prev_val = None
            for p in sorted_periods:
                val = metrics_map[metric].get(p)
                values.append(val or 0)
                
                if prev_val is not None and prev_val != 0 and val is not None:
                    growth = val - prev_val
                    growth_pct = (growth / abs(prev_val)) * 100
                    growth_wan = growth / 10000 if abs(growth) >= 10000 else growth
                    growth_amounts.append(round(growth_wan, 2))
                    growth_rates.append(round(growth_pct, 2))
                else:
                    growth_amounts.append(None)
                    growth_rates.append(None)
                
                prev_val = val
            
            print(f"Values ({len(values)}): {values}")
            print(f"Growth Rates ({len(growth_rates)}): {growth_rates}")
            
            # Label generation
            labels = []
            for year, quarter in sorted_periods:
                labels.append(f"{year}年" + (f"Q{quarter}" if quarter else ""))
            print(f"Labels ({len(labels)}): {labels}")

if __name__ == "__main__":
    asyncio.run(reproduce())
