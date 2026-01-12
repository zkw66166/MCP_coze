#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""深度调试发票总金额查询"""

from modules.metrics_loader import get_metrics_loader
from modules.financial_query import FinancialQuery
import re

loader = get_metrics_loader()
fq = FinancialQuery()

# 测试问题
question = '2021-2025年卖方名称为Shenzhen Electronics的发票总金额'

print(f'=== 问题: {question} ===\n')

# 1. 检查metrics_map中是否有匹配
print('=== Step 1: 指标提取 ===')
metrics_map = fq.metrics_map
metrics = fq.extract_metrics(question)
print(f'提取到的指标: {metrics}')

# 2. 查看是哪些关键词匹配到了
print('\n=== Step 2: 关键词匹配详情 ===')
all_metrics = list(fq.metrics_map.keys()) + list(fq.formulas.keys())
sorted_metrics = sorted(set(all_metrics), key=len, reverse=True)

for metric_name in sorted_metrics:
    if metric_name in question:
        if metric_name in fq.metrics_map:
            print(f'  ✓ "{metric_name}" -> metrics_map: {fq.metrics_map[metric_name]}')
        elif metric_name in fq.formulas:
            print(f'  ✓ "{metric_name}" -> formulas')

# 3. 检查复杂条件模式
print('\n=== Step 3: 复杂条件检测 ===')
complex_condition_patterns = [
    r'[卖买]方名称[为是]', r'seller_name', r'buyer_name',
    r'发票类型[为是]', r'invoice_type',
    r'税目[为是]', r'类别[为是]',
]
for pattern in complex_condition_patterns:
    if re.search(pattern, question):
        print(f'  ✓ 匹配复杂条件模式: {pattern}')

# 4. 检查提取的指标映射
print('\n=== Step 4: 第一个指标的映射详情 ===')
if metrics:
    first_metric = metrics[0]
    if first_metric in fq.metrics_map:
        table, field = fq.metrics_map[first_metric]
        print(f'  指标: {first_metric}')
        print(f'  表: {table}')
        print(f'  字段: {field}')
        print(f'  是item_query: {table.startswith("__item_query__")}')
    else:
        print(f'  指标 "{first_metric}" 不在metrics_map中')

# 5. 检查发票相关的keywords
print('\n=== Step 5: 发票相关关键词 ===')
keywords = loader.get_keywords()
for kw in keywords:
    if '发票' in kw or '总金额' in kw:
        print(f'  - {kw}')

# 6. 模拟execute_query的复杂条件检测
print('\n=== Step 6: 模拟execute_query流程 ===')
company_id = 5
time_range = {'years': [2021, 2022, 2023, 2024, 2025], 'year': 2021, 'is_full_year': True}

has_complex_condition = False
for pattern in complex_condition_patterns:
    if re.search(pattern, question):
        has_complex_condition = True
        break

print(f'检测到复杂条件: {has_complex_condition}')

if has_complex_condition:
    print('✓ 应该使用Text-to-SQL')
else:
    print('✗ 不会使用Text-to-SQL，走常规策略')
    
# 7. 检查为什么会提取到营业收入
print('\n=== Step 7: 为什么提取到营业收入 ===')
# 检查default逻辑
print('extract_metrics 的默认值逻辑:')
print("  如果没有找到具体指标，默认返回 ['营业收入', '净利润']")
print(f'  当前提取结果: {metrics}')
if '营业收入' in metrics and '营业收入' not in question:
    print('  ⚠️  警告: 营业收入是默认值，不是从问题中提取的!')
