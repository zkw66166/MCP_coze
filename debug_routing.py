#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试路由问题"""

from modules.intent_classifier import IntentClassifier

classifier = IntentClassifier(use_llm=False)

test_cases = [
    "个人所得税优惠政策有哪些",
    "印花税减免政策有哪些",
]

print("=" * 60)
print("调试路由问题")
print("=" * 60)

for question in test_cases:
    print(f"\n问题: {question}")
    
    # 检查关键词匹配
    question_lower = question.lower()
    matched_keywords = []
    for keyword in classifier.incentive_keywords:
        if keyword in question_lower:
            matched_keywords.append(keyword)
    
    print(f"  匹配的关键词: {matched_keywords}")
    
    # 关键词过滤结果
    keyword_result = classifier._keyword_filter(question)
    print(f"  关键词过滤: {keyword_result}")
    
    # 最终分类结果
    result = classifier.classify(question)
    print(f"  最终结果: {result}")
