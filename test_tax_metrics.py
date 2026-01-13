#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试税收指标提取问题"""

from modules.metrics_loader import get_metrics_loader
from modules.financial_query import FinancialQuery

loader = get_metrics_loader()
fq = FinancialQuery()

# 测试问题
question = '2021-2026印花税、增值税、企业所得税'

print(f'=== 问题: {question} ===\n')

# 1. 检查metrics_map中是否有匹配
print('=== Step 1: 指标提取 ===')
metrics = fq.extract_metrics(question)
print(f'提取到的指标: {metrics}')

# 2. 检查所有的key
print('\n=== Step 2: 关键词包含检查 ===')
all_metrics = list(fq.metrics_map.keys()) + list(fq.formulas.keys())
sorted_metrics = sorted(set(all_metrics), key=len, reverse=True)

test_terms = ['印花税', '增值税', '企业所得税', '所得税', '所到税']
found_terms = []
for term in test_terms:
    if term in all_metrics:
        print(f'  ✓ "{term}" 在配置中存在')
        found_terms.append(term)
    else:
        print(f'  ✗ "{term}" 不在配置中')

# 3. 检查是否有包含关系导致的问题
print('\n=== Step 3: 可能的匹配干扰 ===')
for metric_name in sorted_metrics:
    if metric_name in question:
        print(f'  匹配到: {metric_name} (长度: {len(metric_name)})')

