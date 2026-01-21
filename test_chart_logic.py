
import asyncio
import json

# Mock results similar to what financial_query returns
mock_results_multi = [
    {'metric_name': 'Sales', 'year': 2022, 'quarter': 1, 'value': 100, 'unit': '元'},
    {'metric_name': 'Tax', 'year': 2022, 'quarter': 1, 'value': 10, 'unit': '元'},
    {'metric_name': 'Sales', 'year': 2022, 'quarter': 2, 'value': 110, 'unit': '元'},
    {'metric_name': 'Tax', 'year': 2022, 'quarter': 2, 'value': 11, 'unit': '元'},
     {'metric_name': 'Sales', 'year': 2022, 'quarter': 3, 'value': 120, 'unit': '元'},
    {'metric_name': 'Tax', 'year': 2022, 'quarter': 3, 'value': 12, 'unit': '元'},
]

mock_results_single = [
    {'metric_name': 'Sales', 'year': 2022, 'quarter': 1, 'value': 100, 'unit': '元'},
    {'metric_name': 'Sales', 'year': 2022, 'quarter': 2, 'value': 120, 'unit': '元'},
]

company = {'name': 'Test Corp'}

async def test_chart_logic(results):
    print(f"\nTesting with {len(results)} results...")
    
    # Copy pasted logic from chat.py (simplified for test)
    if len(results) >= 2:
        try:
            # 1. Group Data
            metrics_map = {} 
            all_periods = set()
            
            for r in results:
                m = r['metric_name']
                p = (r['year'], r.get('quarter'))
                all_periods.add(p)
                if m not in metrics_map:
                    metrics_map[m] = {}
                metrics_map[m][p] = r['value']
            
            sorted_periods = sorted(list(all_periods), key=lambda x: (x[0], x[1] or 0))
            labels = []
            for year, quarter in sorted_periods:
                labels.append(f"{year}年" + (f"Q{quarter}" if quarter else ""))
            
            unique_metrics = list(metrics_map.keys())
            print(f"Unique metrics: {unique_metrics}")
            
            if len(unique_metrics) == 1:
                print(">> Path: Single Metric Chart")
                metric = unique_metrics[0]
                values = []
                # ... skipping calculation detail ...
                chart_data = {
                    "chartType": "combo", # simplified
                    "title": f"{company['name']} {metric}趋势对比",
                    "labels": labels,
                     # ...
                }
                print(f"Generated Chart: {json.dumps(chart_data, ensure_ascii=False)}")
                
            else:
                print(">> Path: Multi Metric Chart")
                top_metrics = unique_metrics[:5]
                datasets = []
                for idx, metric in enumerate(top_metrics):
                    data_points = []
                    for p in sorted_periods:
                        val = metrics_map[metric].get(p, 0)
                        data_points.append(val or 0)
                    datasets.append({
                        "type": "line",
                        "label": metric,
                        "data": data_points
                    })
                
                chart_data = {
                    "chartType": "line",
                    "title": f"Comparison ({len(top_metrics)})",
                    "labels": labels,
                    "datasets": datasets
                }
                print(f"Generated Chart: {json.dumps(chart_data, ensure_ascii=False)}")
                
        except Exception as e:
            print(f"Error: {e}")

async def main():
    await test_chart_logic(mock_results_single)
    await test_chart_logic(mock_results_multi)

if __name__ == "__main__":
    asyncio.run(main())
