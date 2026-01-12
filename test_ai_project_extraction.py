#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试DeepSeek智能提取优惠项目"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    "粮食企业有哪些增值税优惠?",
    "会议展览服务有哪些优惠政策?",
    "海南自贸港企业所得税优惠",
    "油页岩有什么税收优惠?",
    "残疾人就业有哪些优惠?",
    "集成电路企业有哪些优惠政策",  # 核心关键词,不需要AI
]

print("=" * 60)
print("测试DeepSeek智能提取优惠项目")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    
    results, total_count, query_intent = q.search(question, limit=10)
    
    print(f"总数: {total_count}条")
    print(f"返回: {len(results)}条")
    
    if results:
        print("前3条:")
        for i, r in enumerate(results[:3], 1):
            print(f"  {i}. {r['project_name'][:50]}")
