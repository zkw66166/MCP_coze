#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查增值税额的映射和查询结果"""

from modules.metrics_loader import get_metrics_loader
from modules.financial_query import FinancialQuery

loader = get_metrics_loader()
fq = FinancialQuery()

question = '2021-2026印花税额、增值税额、企业所得税额'
company_id = 5 # Assuming company 5 as before, or I'll pick one that has data

print(f'=== 问题: {question} ===')
metrics = fq.extract_metrics(question)
print(f'提取指标: {metrics}')

print('\n=== 指标映射 ===')
for m in metrics:
    if m in fq.metrics_map:
        print(f'{m} -> {fq.metrics_map[m]}')
    elif m in fq.formulas:
        print(f'{m} -> Formula: {fq.formulas[m]}')
    else:
        print(f'{m} -> Not Found')

print('\n=== 执行查询 (Company ID: 5) ===')
# 模拟查询
time_range = fq.extract_time_range(question)
curr_metrics = metrics
results = fq.execute_query(company_id, time_range, curr_metrics, question)

print(f'返回记录数: {len(results)}')

# 分析结果数据 - 检查是否有 quarter=0 或 None 的年度汇总数据
print('\n=== 数据分析 ===')
vat_metric = '增值税额' # Or whatever matches
found_vat = False
for m in metrics:
    if '增值税' in m:
        vat_metric = m
        found_vat = True
        break

if found_vat:
    print(f'检查指标: {vat_metric}')
    yearly_data = {}
    quarterly_data = {}
    
    for r in results:
        if r['metric_name'] != vat_metric:
            continue
            
        y = r['year']
        q = r.get('quarter')
        v = r.get('value', 0)
        
        if not q: # Yearly record
            yearly_data[y] = v
            print(f'  Year {y} Total: {v}')
        else:
            if y not in quarterly_data: quarterly_data[y] = []
            quarterly_data[y].append((q, v))
            print(f'  Year {y} Q{q}: {v}')
            
    # Check consistency
    print('\n=== 一致性检查 ===')
    for y, q_vals in quarterly_data.items():
        q_sum = sum(v for _, v in q_vals)
        y_total = yearly_data.get(y, 'Missing')
        print(f'Year {y}: Sum of Quarters = {q_sum}, Yearly Record = {y_total}')
        
else:
    print('没有找到增值税相关指标结果')
