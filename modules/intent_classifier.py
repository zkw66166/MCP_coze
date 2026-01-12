#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
意图识别模块
功能:
1. 快速关键词过滤
2. DeepSeek智能分类
3. 多层判断提高准确率
"""

from typing import Optional
from modules.deepseek_client import DeepSeekClient


class IntentClassifier:
    """意图分类器"""
    
    def __init__(self, use_llm: bool = True):
        """
        初始化意图分类器
        
        Args:
            use_llm: 是否使用LLM进行二次确认(默认True)
        """
        self.use_llm = use_llm
        if use_llm:
            self.deepseek = DeepSeekClient()
        
        # 税收优惠关键词(扩展列表)
        self.incentive_keywords = [
            "优惠", "减免", "免征", "减征", "抵扣", "退税", 
            "补贴", "扶持", "即征即退", "先征后退", "先征后返",
            "免税", "减税", "税收优惠", "优惠政策", "优惠条件",
            "优惠比例", "优惠税率", "税收减免", "税收扶持",
            "减半征收", "减半", "两免三减半", "三免三减半",
            "免", "减", "返还", "返税", "加计扣除", "加计",
            "税收政策", "税收支持", "税惠"
        ]
        
        # 税种关键词
        self.tax_type_keywords = [
            "增值税", "企业所得税", "个人所得税", "印花税", 
            "房产税", "城镇土地使用税", "消费税", "土地增值税", 
            "资源税", "车船税", "契税", "关税"
        ]
        
        # 排除关键词(明确不是税收优惠的问题)
        # 注意:这些关键词只在没有优惠关键词时才排除
        self.exclude_keywords = [
            "发票", "申报流程", "缴纳流程", "登记流程",
            "什么是", "定义", "概念", "计算公式"
        ]
        
        # === 新增:最优先路由到财务数据库的关键词 ===
        # 当问题包含税种关键词 + 以下关键词时,最优先路由到财务数据库
        self.financial_db_priority_keywords = [
            "多少", "是多少", "数据", "金额", "查询", 
            "增长", "增减", "增加", "减少", 
            "变动", "改变", "变化", "趋势", "情况"
        ]
        
        # === 新增:知识库优先关键词(即使包含优惠关键词也优先路由到知识库) ===
        self.knowledge_base_priority_keywords = [
            "指南", "指引", "操作", "申报", "申请", "备案", "管理", 
            "办理", "注销", "注册", "登记注册", "注册登记", 
            "认定", "扣缴", "目录", "汇编", "流程", "怎么办",
            "如何办", "怎样办", "程序", "步骤", "手续", "享受"
        ]
        
        # === V2.0: 从 MetricsLoader 动态加载财务数据关键词 ===
        self._financial_data_keywords_cache = None
        
        # 财务数据请求关键词
        self.data_request_keywords = [
            "多少", "是多少", "数据", "金额", "输出", "列出",
            "查询", "显示", "告诉我", "计算"
        ]
        
        # 企业名称缓存(从数据库加载)
        self._company_names_cache = None
    
    @property
    def financial_data_keywords(self):
        """V2.0: 动态加载财务数据关键词(从配置文件)"""
        if self._financial_data_keywords_cache is None:
            try:
                from modules.metrics_loader import get_metrics_loader
                loader = get_metrics_loader()
                self._financial_data_keywords_cache = loader.get_keywords()
            except Exception as e:
                print(f"⚠️  加载财务数据关键词失败,使用基础关键词: {e}")
                # 基础关键词作为后备
                self._financial_data_keywords_cache = [
                    "销售额", "收入", "利润", "资产", "负债", "费用", "成本",
                    "毛利率", "净利率", "ROA", "ROE", "周转率", "税负率"
                ]
        return self._financial_data_keywords_cache
    
    def _load_company_names(self):
        """加载企业名称和别名"""
        if self._company_names_cache is None:
            try:
                import sqlite3
                conn = sqlite3.connect('database/financial.db')
                cursor = conn.cursor()
                
                # 加载企业名称
                cursor.execute('SELECT name FROM companies')
                names = [row[0] for row in cursor.fetchall()]
                
                # 加载别名
                cursor.execute('SELECT alias FROM company_aliases')
                aliases = [row[0] for row in cursor.fetchall()]
                
                self._company_names_cache = names + aliases
                conn.close()
            except:
                self._company_names_cache = []
        
        return self._company_names_cache
    
    def _should_route_to_knowledge_base(self, question: str) -> bool:
        """检查是否应该优先路由到知识库"""
        return any(kw in question for kw in self.knowledge_base_priority_keywords)
    
    def _should_priority_route_to_financial_db(self, question: str) -> bool:
        """
        检查是否应该最优先路由到财务数据库
        
        条件(满足任一即可):
        1. 问题包含时间区间表述(如"2022-2023")
        2. 问题包含税种关键词 + 财务数据库优先关键词(如"增值税多少")
        3. 问题包含财务数据关键词 + 财务数据库优先关键词(如"收入变化")
        """
        import re
        
        # 条件1: 检查是否包含时间区间表述
        # 支持多种格式: "2022-2023", "21-23", "2021-24", "23年"
        # 模式1: 4位数-4位数 (如 2022-2023)
        pattern_4_4 = r'\d{4}[—\-~至到]\d{4}'
        # 模式2: 2位数-2位数 (如 21-23)
        pattern_2_2 = r'(?<!\d)\d{2}[—\-~至到]\d{2}(?!\d)'
        # 模式3: 4位数-2位数 (如 2021-24)
        pattern_4_2 = r'\d{4}[—\-~至到]\d{2}(?!\d)'
        # 模式4: 2位数年 (如 23年)
        pattern_2_year = r'(?<!\d)\d{2}年'
        
        has_time_range = bool(
            re.search(pattern_4_4, question) or
            re.search(pattern_2_2, question) or
            re.search(pattern_4_2, question) or
            re.search(pattern_2_year, question)
        )
        if has_time_range:
            return True
        
        # 条件2: 检查是否包含税种关键词 + 财务数据库优先关键词
        has_tax_type = any(kw in question for kw in self.tax_type_keywords)
        has_financial_priority = any(kw in question for kw in self.financial_db_priority_keywords)
        
        if has_tax_type and has_financial_priority:
            return True
        
        # 条件3: 检查是否包含财务数据关键词 + 财务数据库优先关键词
        # 例如:"收入变化" "利润趋势" 等
        has_financial_keyword = any(kw in question for kw in self.financial_data_keywords)
        
        if has_financial_keyword and has_financial_priority:
            return True
        
        return False
    
    def classify(self, question: str) -> str:
        """
        分类用户问题
        
        Args:
            question: 用户问题
        
        Returns:
            "financial_data" - 企业财务数据查询
            "tax_incentive" - 税收优惠政策查询
            "other" - 其他问题(路由到知识库)
        """
        # 第-2层（最高优先级）: 检查是否应该最优先路由到财务数据库
        # 当问题包含税种关键词 + 财务数据库优先关键词时,优先路由到财务数据库
        if self._should_priority_route_to_financial_db(question):
            print(f"💰 检测到财务数据库优先关键词,路由到财务数据库")
            return "financial_data"
        
        # 第-1层: 检查知识库优先关键词
        # 包含"办理、申报、指南"等关键词时,即使有"优惠"也优先路由到知识库
        if self._should_route_to_knowledge_base(question):
            print(f"📚 检测到知识库优先关键词,路由到知识库")
            return "other"
        
        # 第0层: 检查企业财务数据查询
        if self._is_financial_data_query(question):
            return "financial_data"
        
        # 第一层: 快速关键词过滤(税收优惠)
        keyword_result = self._keyword_filter(question)
        
        # 只要包含优惠关键词,优先路由到本地数据库
        if keyword_result == "tax_incentive":
            return "tax_incentive"
        
        # 明确排除的问题
        if keyword_result == "exclude":
            return "other"
        
        # 不确定的情况,使用LLM判断
        if self.use_llm:
            llm_result = self._llm_classify(question)
            return llm_result
        else:
            # 不使用LLM时,默认返回other(保守策略)
            return "other"
    
    def _is_financial_data_query(self, question: str) -> bool:
        """
        判断是否为企业财务数据查询
        
        条件:
        1. 包含企业名称(或别名)
        2. 包含财务数据关键词
        3. 包含数据请求关键词(可选,但增加置信度)
        """
        # 加载企业名称
        company_names = self._load_company_names()
        
        # 检查是否包含企业名称
        has_company = any(name in question for name in company_names if name)
        
        if not has_company:
            return False
        
        # 检查是否包含财务数据关键词
        has_financial = any(kw in question for kw in self.financial_data_keywords)
        
        # 检查是否包含数据请求关键词
        has_data_request = any(kw in question for kw in self.data_request_keywords)
        
        # 必须同时包含企业名称和财务关键词
        return has_company and (has_financial or has_data_request)
    
    def _keyword_filter(self, question: str) -> str:
        """
        关键词快速过滤
        
        Args:
            question: 用户问题
        
        Returns:
            "tax_incentive": 强匹配税收优惠
            "exclude": 明确排除
            "uncertain": 不确定
        """
        question_lower = question.lower()
        
        # 优先检查税收优惠关键词
        incentive_count = sum(1 for k in self.incentive_keywords if k in question_lower)
        
        # 只要包含任何优惠关键词,就路由到本地数据库
        if incentive_count >= 1:
            return "tax_incentive"
        
        # 检查排除关键词(仅在没有优惠关键词时)
        for keyword in self.exclude_keywords:
            if keyword in question_lower:
                return "exclude"
        
        # 其他情况不确定
        return "uncertain"
    
    def _llm_classify(self, question: str) -> str:
        """
        使用DeepSeek进行智能分类
        
        Args:
            question: 用户问题
        
        Returns:
            "tax_incentive" 或 "other"
        """
        try:
            return self.deepseek.classify_intent(question)
        except Exception as e:
            print(f"⚠️  LLM分类失败: {str(e)}, 默认返回other")
            return "other"
    
    def get_confidence(self, question: str) -> float:
        """
        获取分类置信度
        
        Args:
            question: 用户问题
        
        Returns:
            置信度(0-1)
        """
        keyword_result = self._keyword_filter(question)
        
        if keyword_result == "exclude":
            return 0.9  # 高置信度排除
        elif keyword_result == "tax_incentive":
            return 0.85  # 高置信度匹配
        else:
            return 0.5  # 不确定


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("意图识别模块测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        # 税收优惠相关
        ("高新技术企业有哪些增值税优惠?", "tax_incentive"),
        ("小微企业所得税减免政策是什么?", "tax_incentive"),
        ("农产品增值税免征条件", "tax_incentive"),
        ("研发费用加计扣除比例", "tax_incentive"),
        ("出口退税政策", "tax_incentive"),
        
        # 其他税法问题
        ("什么是增值税专用发票?", "other"),
        ("如何进行税务申报?", "other"),
        ("增值税的计算公式是什么?", "other"),
        ("发票丢失怎么办?", "other"),
        ("税务登记流程", "other"),
        
        # 边界情况
        ("增值税", "uncertain"),
        ("税收优惠", "tax_incentive"),
        ("如何申请税收优惠?", "uncertain"),
    ]
    
    # 测试1: 仅关键词过滤
    print("\n【测试1: 仅关键词过滤】")
    classifier_no_llm = IntentClassifier(use_llm=False)
    
    for question, expected in test_cases:
        result = classifier_no_llm.classify(question)
        confidence = classifier_no_llm.get_confidence(question)
        status = "✅" if result == expected or expected == "uncertain" else "❌"
        print(f"{status} {question}")
        print(f"   预期: {expected}, 结果: {result}, 置信度: {confidence:.2f}\n")
    
    # 测试2: 关键词 + LLM
    print("\n【测试2: 关键词 + LLM智能分类】")
    classifier_with_llm = IntentClassifier(use_llm=True)
    
    important_cases = [
        ("高新技术企业有哪些增值税优惠?", "tax_incentive"),
        ("什么是增值税专用发票?", "other"),
        ("如何申请税收优惠?", "uncertain"),
        ("小微企业税收减免政策", "tax_incentive"),
    ]
    
    for question, expected in important_cases:
        result = classifier_with_llm.classify(question)
        confidence = classifier_with_llm.get_confidence(question)
        status = "✅" if result == expected or expected == "uncertain" else "❌"
        print(f"{status} {question}")
        print(f"   预期: {expected}, 结果: {result}, 置信度: {confidence:.2f}\n")
    
    print("=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
