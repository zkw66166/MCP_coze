#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试多指标图表生成逻辑
"""

import asyncio
import json

# Mock results similar to what financial_query returns
mock_results_multi = [
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 1, 'value': 10000000, 'unit': '元'},
    {'metric_name': '净利润', 'year': 2022, 'quarter': 1, 'value': 1000000, 'unit': '元'},
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 2, 'value': 12000000, 'unit': '元'},
    {'metric_name': '净利润', 'year': 2022, 'quarter': 2, 'value': 1200000, 'unit': '元'},
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 3, 'value': 15000000, 'unit': '元'},
    {'metric_name': '净利润', 'year': 2022, 'quarter': 3, 'value': 1500000, 'unit': '元'},
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 4, 'value': 18000000, 'unit': '元'},
    {'metric_name': '净利润', 'year': 2022, 'quarter': 4, 'value': 1600000, 'unit': '元'},
]

mock_results_single = [
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 1, 'value': 10000000, 'unit': '元'},
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 2, 'value': 12000000, 'unit': '元'},
    {'metric_name': '营业收入', 'year': 2022, 'quarter': 3, 'value': 15000000, 'unit': '元'},
]

company = {'name': '测试公司', 'id': 1}


async def test_chart_logic(results, test_name):
    """测试图表生成逻辑"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"{'='*60}")
    print(f"数据条数: {len(results)}")
    
    if len(results) >= 2:
        try:
            # 1. 整理数据：按 metric 分组
            metrics_map = {}
            all_periods = set()
            
            for r in results:
                m = r['metric_name']
                p = (r['year'], r.get('quarter'))
                all_periods.add(p)
                if m not in metrics_map:
                    metrics_map[m] = {}
                metrics_map[m][p] = r['value']
            
            # 排序 periods
            sorted_periods = sorted(list(all_periods), key=lambda x: (x[0], x[1] or 0))
            labels = []
            for year, quarter in sorted_periods:
                labels.append(f"{year}年" + (f"Q{quarter}" if quarter else ""))
            
            unique_metrics = list(metrics_map.keys())
            print(f"指标数量: {len(unique_metrics)}")
            print(f"指标列表: {unique_metrics}")
            print(f"时间标签: {labels}")
            
            # 2. 决策：单指标 vs 多指标
            if len(unique_metrics) == 1:
                print("\n>>> 路径: 单指标图表 (Combo Chart)")
                metric = unique_metrics[0]
                values = []
                growth_rates = []
                
                prev_val = None
                for p in sorted_periods:
                    val = metrics_map[metric].get(p)
                    values.append(val or 0)
                    
                    if prev_val is not None and prev_val != 0 and val is not None:
                        growth_pct = ((val - prev_val) / abs(prev_val)) * 100
                        growth_rates.append(round(growth_pct, 2))
                    else:
                        growth_rates.append(None)
                    
                    prev_val = val
                
                print(f"原始值: {values}")
                print(f"增长率: {growth_rates}")
                
            else:
                print("\n>>> 路径: 多指标图表 (双图表)")
                top_metrics = unique_metrics[:5]
                
                colors = [
                    "rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)", 
                    "rgba(255, 206, 86, 1)", "rgba(75, 192, 192, 1)", 
                    "rgba(153, 102, 255, 1)"
                ]
                
                # === 图表1: 绝对值对比 ===
                print("\n--- 图表1: 绝对值对比 (柱状图) ---")
                
                colors = [
                    "rgba(54, 162, 235, 0.8)", "rgba(255, 99, 132, 0.8)", 
                    "rgba(255, 206, 86, 0.8)", "rgba(75, 192, 192, 0.8)", 
                    "rgba(153, 102, 255, 0.8)"
                ]
                
                border_colors = [
                    "rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)", 
                    "rgba(255, 206, 86, 1)", "rgba(75, 192, 192, 1)", 
                    "rgba(153, 102, 255, 1)"
                ]
                
                value_datasets = []
                for idx, metric in enumerate(top_metrics):
                    data_points = []
                    for p in sorted_periods:
                        val = metrics_map[metric].get(p, 0)
                        data_points.append(val or 0)
                    
                    print(f"{metric}: {data_points}")
                    
                    value_datasets.append({
                        "type": "bar",
                        "label": metric,
                        "data": data_points,
                        "backgroundColor": colors[idx % len(colors)],
                        "borderColor": border_colors[idx % len(border_colors)],
                        "borderWidth": 1
                    })
                
                chart1_data = {
                    "chartType": "bar",
                    "title": f"{company['name']} 指标绝对值对比 ({len(top_metrics)}/{len(unique_metrics)})",
                    "labels": labels,
                    "datasets": value_datasets
                }
                print(f"\n图表1数据: {json.dumps(chart1_data, ensure_ascii=False, indent=2)}")
                
                # === 图表2: 增长率对比 ===
                print("\n--- 图表2: 增长率对比 (柱状图) ---")
                growth_datasets = []
                for idx, metric in enumerate(top_metrics):
                    growth_rates = []
                    prev_val = None
                    
                    for p in sorted_periods:
                        val = metrics_map[metric].get(p)
                        
                        if prev_val is not None and prev_val != 0 and val is not None:
                            growth_pct = ((val - prev_val) / abs(prev_val)) * 100
                            growth_rates.append(round(growth_pct, 2))
                        else:
                            growth_rates.append(None)
                        
                        prev_val = val
                    
                    print(f"{metric} 增长率: {growth_rates}")
                    
                    growth_datasets.append({
                        "type": "bar",
                        "label": metric,
                        "data": growth_rates,
                        "backgroundColor": colors[idx % len(colors)],
                        "borderColor": border_colors[idx % len(border_colors)],
                        "borderWidth": 1
                    })
                
                chart2_data = {
                    "chartType": "bar",
                    "title": f"{company['name']} 指标增长率对比 (%) ({len(top_metrics)}/{len(unique_metrics)})",
                    "labels": labels,
                    "datasets": growth_datasets,
                    "options": {
                        "scales": {
                            "y": {
                                "ticks": {
                                    "callback": "function(value) { return value + '%'; }"
                                }
                            }
                        }
                    }
                }
                print(f"\n图表2数据: {json.dumps(chart2_data, ensure_ascii=False, indent=2)}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """运行测试"""
    await test_chart_logic(mock_results_single, "单指标多期查询")
    await test_chart_logic(mock_results_multi, "多指标多期查询")
    
    print(f"\n{'='*60}")
    print("✅ 测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
