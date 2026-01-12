#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试税种提取"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

test_cases = [
    "企业所得优惠政策有哪些",  # 缺少"税"字
    "企业所得税优惠政策有哪些",
    "个人所得优惠政策",  # 缺少"税"字
    "个人所得税优惠政策",
]

for question in test_cases:
    tax_type, incentives = q._extract_tax_and_incentive(question)
    print(f"问题: {question}")
    print(f"  提取税种: {tax_type}\n")
