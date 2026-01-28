#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试意图识别(财务数据/税收优惠/其他)"""

from modules.intent_classifier import IntentClassifier

classifier = IntentClassifier(use_llm=False)  # 仅关键词测试

test_cases = [
    # 企业财务数据查询
    ("ABC公司2023年销售额是多少", "financial_data"),
    ("123制造厂2024年第一季度毛利率", "financial_data"),
    ("太空科技公司的净利润", "financial_data"),
    ("环球机械2023年存货周转率", "financial_data"),
    ("ABC企业资产负债率多少", "financial_data"),
    
    # 税收优惠政策查询
    ("高新技术企业有哪些增值税优惠?", "tax_incentive"),
    ("小微企业所得税减免政策", "tax_incentive"),
    ("研发费用加计扣除", "tax_incentive"),
    ("集成电路企业优惠政策", "tax_incentive"),
    
    # 其他问题(应路由到Coze)
    ("什么是增值税专用发票?", "other"),
    ("如何进行税务申报?", "other"),
    ("发票丢失怎么办?", "other"),
]

print("=" * 60)
print("测试三分类意图识别")
print("=" * 60)

correct = 0
total = len(test_cases)

for question, expected in test_cases:
    result = classifier.classify(question)
    status = "✅" if result == expected else "❌"
    if result == expected:
        correct += 1
    print(f"{status} {question}")
    print(f"   预期: {expected}, 结果: {result}")
    print()

print(f"准确率: {correct}/{total} = {correct/total*100:.1f}%")
