#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试发票总金额的完整execute_query流程"""

from modules.financial_query import FinancialQuery

fq = FinancialQuery()

# 模拟前端的调用
question = '2021-2025年卖方名称为Shenzhen Electronics的发票总金额'
company_id = 5
time_range = fq.extract_time_range(question)
metrics = fq.extract_metrics(question)

print(f'=== 完整execute_query测试 ===')
print(f'问题: {question}')
print(f'时间范围: {time_range}')
print(f'提取的指标: {metrics}')
print()

# 执行查询 - 传入question以启用复杂条件检测
print('=== 调用 execute_query ===')
results = fq.execute_query(company_id, time_range, metrics, question)

print(f'\n=== 结果 ===')
print(f'结果数: {len(results)}')
for r in results[:5]:
    print(f'  {r}')
