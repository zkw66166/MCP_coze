#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试动态指标计算(利润率等)"""

from modules.financial_query import FinancialQuery

q = FinancialQuery()

test_cases = [
    "ABC公司2023年利润率是多少",  # 利润率(公式库)
    "太空科技2023年净利润率",     # 净利润率(公式库)
    "环球机械2023年毛利率",       # 毛利率(预计算)
    "123制造2024年Q1销售额",     # 销售额(原始数据)
]

print("=" * 60)
print("测试动态指标计算")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    
    results, company, status = q.search(question)
    
    if status == "company_not_found":
        print("❌ 未找到企业")
    elif status == "no_data" or not results:
        print(f"📊 {company['name']} 暂无相关数据")
    else:
        print(q.format_results(results, company))
