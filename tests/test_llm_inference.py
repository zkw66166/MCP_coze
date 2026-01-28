#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试DeepSeek税种推理"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    "税前扣除有哪些优惠规定",  # 应推理为企业所得税
    "专项附加扣除有哪些",  # 应推理为个人所得税
    "进项税抵扣政策",  # 应推理为增值税
    "研发费用加计扣除",  # 应推理为企业所得税
]

print("=" * 60)
print("测试DeepSeek税种推理")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    tax_type, incentives = q._extract_tax_and_incentive(question)
    print(f"  提取税种: {tax_type}")
    
    if tax_type:
        results = q.search(question, limit=5)
        print(f"  查询结果: {len(results)}条")
