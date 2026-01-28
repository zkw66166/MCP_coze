#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试修改后的意图识别"""

from modules.intent_classifier import IntentClassifier

classifier = IntentClassifier(use_llm=False)

test_cases = [
    "增值税优惠政策有哪些",
    "高新技术企业有哪些增值税优惠?",
    "小微企业所得税减免政策",
    "农产品增值税免征",
    "研发费用加计扣除",
    "两免三减半政策",
    "减半征收",
    "税收优惠",
    "退税政策",
    "什么是增值税专用发票?",
    "如何进行税务申报?",
    "增值税的计算公式",
]

print("=" * 60)
print("意图识别测试(修改后)")
print("=" * 60)

for question in test_cases:
    result = classifier.classify(question)
    keyword_result = classifier._keyword_filter(question)
    print(f"\n问题: {question}")
    print(f"  关键词过滤: {keyword_result}")
    print(f"  最终结果: {result}")
