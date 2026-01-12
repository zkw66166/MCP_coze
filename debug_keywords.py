#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试关键词提取"""

from modules.db_query import TaxIncentiveQuery

q = TaxIncentiveQuery()

# 测试关键词提取
test_questions = [
    "高新技术企业有哪些增值税优惠?",
    "小微企业所得税减免政策",
    "农产品增值税免征"
]

for question in test_questions:
    keywords = q._extract_keywords(question)
    print(f"问题: {question}")
    print(f"提取的关键词: '{keywords}'")
    
    # 直接测试keyword_search
    results = q.keyword_search(keywords, limit=10)
    print(f"keyword_search结果数: {len(results)}")
    
    # 测试用原问题搜索
    results2 = q.keyword_search(question, limit=10)
    print(f"用原问题搜索结果数: {len(results2)}")
    print()
