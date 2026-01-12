#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试发票查询流程"""

from modules.metrics_loader import get_metrics_loader
from modules.financial_query import FinancialQuery

loader = get_metrics_loader()
keywords = loader.get_keywords()

# 检查关键词
test_terms = ['发票', '发票金额', '发票总金额', '金额', '总金额', '卖方', 'seller']
print('=== 关键词匹配检查 ===')
for term in test_terms:
    found = term in keywords or any(term in kw for kw in keywords)
    print(f'  {term}: {"✓" if found else "✗"}')

# 检查问题是否能匹配关键词
questions = [
    '2021-2025年卖方名称为Shenzhen Electronics的发票金额',
    '2021-2025年卖方名称为Shenzhen Electronics的发票总金额',
]

print()
print('=== 问题关键词匹配 ===')
for q in questions:
    has_kw = any(kw in q for kw in keywords)
    print(f'  "{q[:40]}...": {"✓" if has_kw else "✗"}')
    
# 检查发票金额的映射
fq = FinancialQuery()
metrics_map = fq.metrics_map

print()
print('=== metrics_map中的发票相关 ===')
for key, val in metrics_map.items():
    if '发票' in key or 'invoice' in key.lower():
        print(f'  {key} -> {val}')

print()
print('=== 模拟完整查询流程 ===')
# 模拟前端选中公司
selected_company = {'id': 5, 'name': 'ABC有限公司'}
question = '2021-2025年卖方名称为Shenzhen Electronics的发票金额'

print(f'选中公司: {selected_company}')
print(f'问题: {question}')

# Step 1: 关键词检测
has_financial_kw = any(kw in question for kw in keywords)
print(f'\n关键词检测: {"✓ 通过" if has_financial_kw else "✗ 失败"}')

# Step 2: 提取时间和指标
time_range = fq.extract_time_range(question)
metrics = fq.extract_metrics(question)
print(f'时间范围: {time_range}')
print(f'识别指标: {metrics}')

# Step 3: 执行查询
print(f'\n=== 执行查询 ===')
results = fq.execute_query(selected_company['id'], time_range, metrics, question)
print(f'结果数: {len(results)}')
for r in results[:5]:
    print(f'  {r}')
