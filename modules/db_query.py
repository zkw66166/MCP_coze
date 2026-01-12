#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
税收优惠政策数据库查询模块
功能:
1. 提供多种查询方式(关键词、税种、优惠方式等)
2. 支持全文搜索
3. 结果排序和过滤
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


class TaxIncentiveQuery:
    """税收优惠政策查询类"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # 默认数据库路径
            db_path = Path(__file__).parent.parent / "database" / "tax_incentives.db"
        
        self.db_path = str(db_path)
        self._verify_database()
    
    def _verify_database(self):
        """验证数据库是否存在"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn
    
    def search(self, question: str, limit: int = 50) -> tuple:
        """
        智能搜索:根据问题自动选择最佳查询策略
        
        Args:
            question: 用户问题
            limit: 返回结果数量限制(默认50,增加以返回更多结果)
        
        Returns:
            (查询结果列表, 总数, 查询意图)
        """
        # 提取税种、优惠关键词、实体关键词和查询意图
        tax_type, incentive_keywords, entity_keywords, query_intent = self._extract_tax_and_incentive(question)
        
        results = []
        total_count = 0
        
        # 策略1: 如果提取到税种,使用结构化查询(税种+优惠方式+实体)
        if tax_type:
            # 先查询总数
            total_count = self.count_structured_results(tax_type, entity_keywords)
            # 再查询限定数量的结果
            results = self.structured_search(tax_type, entity_keywords, limit=limit)
            
            if entity_keywords:
                print(f"📊 结构化查询: 税种='{tax_type}', 实体={entity_keywords}, 总数={total_count}条, 返回={len(results)}条")
            else:
                print(f"📊 结构化查询: 税种='{tax_type}', 总数={total_count}条, 返回={len(results)}条")
        
        # 策略2: 如果没有提取到税种,使用关键词搜索
        if not results:
            keywords = self._extract_keywords(question)
            if keywords:
                results = self.keyword_search(keywords, limit=limit)
                total_count = len(results)  # 关键词搜索已限制数量,总数=结果数
                print(f"📊 关键词查询: 关键词='{keywords}', 结果={len(results)}条")
        
        # 策略3: 如果仍然没有结果,使用原问题搜索
        if not results:
            results = self.keyword_search(question, limit=limit)
            total_count = len(results)
            print(f"📊 原问题查询: 结果={len(results)}条")
        
        return results[:limit], total_count, query_intent
    
    def _extract_tax_and_incentive(self, question: str) -> tuple:
        """
        从问题中提取税种、优惠关键词、实体关键词和查询意图
        
        Args:
            question: 用户问题
        
        Returns:
            (税种, 优惠关键词列表, 实体关键词列表, 查询意图)
        """
        # 税种关键词(按长度排序,优先匹配长的)
        tax_types = [
            "城镇土地使用税", "企业所得税", "个人所得税", "土地增值税",
            "增值税", "印花税", "房产税", "消费税", "资源税", "车船税", "契税", "关税"
        ]
        
        # 税种模糊匹配映射(支持缺少"税"字的情况)
        tax_fuzzy_map = {
            "企业所得": "企业所得税",
            "个人所得": "个人所得税",
            "土地增值": "土地增值税",
            "城镇土地使用": "城镇土地使用税",
        }
        
        # 优惠关键词
        incentive_keywords = [
            "优惠", "减免", "免征", "减征", "抵扣", "退税", 
            "补贴", "扶持", "即征即退", "先征后退", "免税", "减税"
        ]
        
        # 核心实体关键词(高频、重要的,用于快速匹配)
        core_entity_keywords = [
            "集成电路", "软件", "高新技术", "小微企业", "小型微利",
            "残疾人", "创业投资", "天使投资"
        ]
        
        # 条件意图关键词(判断用户是否关注优惠条件)
        condition_intent_keywords = [
            "条件", "要求", "认定条件", "优惠条件", "减免条件",
            "资格", "标准", "手续", "资料", "备案", "申请", "流程"
        ]
        
        # 提取税种(精确匹配)
        matched_tax_type = None
        for tax_type in tax_types:
            if tax_type in question:
                matched_tax_type = tax_type
                break
        
        # 如果精确匹配失败,尝试模糊匹配
        if not matched_tax_type:
            for fuzzy_key, full_tax_type in tax_fuzzy_map.items():
                if fuzzy_key in question:
                    matched_tax_type = full_tax_type
                    print(f"🔍 模糊匹配: '{fuzzy_key}' → '{full_tax_type}'")
                    break
        
        # 如果仍然没有匹配,使用DeepSeek推理
        if not matched_tax_type:
            matched_tax_type = self._infer_tax_type_with_llm(question)
            if matched_tax_type:
                print(f"🤖 DeepSeek推理: 税种='{matched_tax_type}'")
        
        # 提取优惠关键词
        matched_incentives = []
        for keyword in incentive_keywords:
            if keyword in question:
                matched_incentives.append(keyword)
        
        # 提取实体关键词(先尝试快速匹配核心关键词)
        matched_entities = []
        for keyword in core_entity_keywords:
            if keyword in question:
                matched_entities.append(keyword)
        
        # 如果没有匹配到核心关键词,使用DeepSeek智能提取优惠项目
        if not matched_entities:
            project_keywords = self._extract_project_keywords_with_llm(question)
            if project_keywords:
                matched_entities = project_keywords
                print(f"🤖 DeepSeek提取优惠项目: {project_keywords}")
        
        # 判断查询意图
        is_condition_focused = any(kw in question for kw in condition_intent_keywords)
        query_intent = "condition" if is_condition_focused else "general"
        
        return matched_tax_type, matched_incentives, matched_entities, query_intent
    
    def _infer_tax_type_with_llm(self, question: str) -> Optional[str]:
        """
        使用DeepSeek推理税种
        
        Args:
            question: 用户问题
        
        Returns:
            推理出的税种,如果无法推理返回None
        """
        try:
            from modules.deepseek_client import DeepSeekClient
            
            deepseek = DeepSeekClient()
            
            prompt = f"""请根据以下问题判断涉及的税种。

问题: {question}

税种列表:
- 增值税
- 企业所得税
- 个人所得税
- 印花税
- 房产税
- 城镇土地使用税
- 消费税
- 土地增值税
- 资源税
- 车船税
- 契税
- 关税

判断规则:
1. 如果问题明确提到税种名称,返回该税种
2. 如果问题涉及"税前扣除"、"加计扣除"、"研发费用",通常是企业所得税
3. 如果问题涉及"专项附加扣除"、"工资薪金"、"劳务报酬",通常是个人所得税
4. 如果问题涉及"进项税"、"销项税"、"抵扣",通常是增值税
5. 如果无法判断,返回"无法判断"

请只返回税种名称或"无法判断",不要有其他内容。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = deepseek.chat_completion(messages, stream=False, temperature=0.3)
            response = response.strip()
            
            # 验证返回的是有效税种
            valid_tax_types = [
                "增值税", "企业所得税", "个人所得税", "印花税", "房产税",
                "城镇土地使用税", "消费税", "土地增值税", "资源税", "车船税", "契税", "关税"
            ]
            
            if response in valid_tax_types:
                return response
            else:
                return None
        
        except Exception as e:
            print(f"⚠️  DeepSeek推理失败: {str(e)}")
            return None
    
    def _extract_project_keywords_with_llm(self, question: str) -> Optional[List[str]]:
        """
        使用DeepSeek智能提取优惠项目关键词
        
        Args:
            question: 用户问题
        
        Returns:
            优惠项目关键词列表,如果无法提取返回None
        """
        try:
            from modules.deepseek_client import DeepSeekClient
            
            deepseek = DeepSeekClient()
            
            prompt = f"""请从以下问题中提取税收优惠相关的项目关键词。

问题: {question}

项目类型包括:
- 产品: 如粮食、油页岩、软件产品、集成电路等
- 服务: 如会议展览、婚姻介绍、文化服务、工程监理等
- 行业: 如出版、科研、农业、医疗等
- 企业类型: 如高新技术企业、小微企业、残疾人企业等
- 事项: 如资产损失、补贴收入、保险赔款、残疾人就业等
- 地区: 如海南、前海、西藏等

要求:
1. 只提取与税收优惠直接相关的项目关键词
2. 每个关键词2-6个字,尽量简洁
3. 最多返回3个关键词
4. 如果问题中没有明确的项目,返回"无"
5. 只返回关键词,用逗号分隔,不要其他内容

示例:
问题: 粮食企业有哪些增值税优惠?
返回: 粮食

问题: 会议展览服务有哪些优惠政策?
返回: 会议展览

问题: 海南自贸港企业所得税优惠
返回: 海南

请直接返回关键词或"无"。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = deepseek.chat_completion(messages, stream=False, temperature=0.3)
            response = response.strip()
            
            # 解析返回结果
            if response and response != "无" and response != "无法提取":
                # 分割关键词
                keywords = [kw.strip() for kw in response.split(',') if kw.strip()]
                # 过滤掉过长的关键词(可能是错误)
                keywords = [kw for kw in keywords if 2 <= len(kw) <= 10]
                return keywords if keywords else None
            else:
                return None
        
        except Exception as e:
            print(f"⚠️  DeepSeek提取优惠项目失败: {str(e)}")
            return None
    
    def structured_search(self, tax_type: str, entity_keywords: List[str] = None, limit: int = 50) -> List[Dict]:
        """
        结构化查询:税种精确匹配 + 优惠方式包含特定关键词 + 实体关键词过滤
        
        Args:
            tax_type: 税种(如"增值税"、"个人所得税")
            entity_keywords: 实体关键词列表(如["集成电路", "软件"])
            limit: 返回结果数量限制
        
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 优惠方式关键词(数据库中所有可能的值)
        incentive_methods = [
            "减征", "免征", "不征", "暂免", "减半", "退税",
            "即征即退", "先征后退", "先征后返", "免税", "减税",
            "减免", "抵扣", "补贴", "扶持", "优惠"
        ]
        
        # 构建优惠方式OR条件
        method_conditions = " OR ".join(["incentive_method LIKE ?" for _ in incentive_methods])
        method_params = [f"%{method}%" for method in incentive_methods]
        
        # 基础查询条件
        params = [tax_type] + method_params
        
        # 如果有实体关键词,增加实体过滤条件
        if entity_keywords:
            # 在多个字段中搜索实体关键词(增加incentive_method字段)
            entity_conditions = []
            for entity in entity_keywords:
                entity_conditions.append("""(
                    project_name LIKE ? 
                    OR detailed_rules LIKE ? 
                    OR qualification LIKE ?
                    OR incentive_method LIKE ?
                )""")
                params.extend([f"%{entity}%", f"%{entity}%", f"%{entity}%", f"%{entity}%"])
            
            entity_clause = " OR ".join(entity_conditions)
            
            # 移除优惠方式条件限制(因为实体关键词可能就是优惠方式)
            query = f"""
                SELECT * FROM tax_incentives
                WHERE tax_type = ?
                AND ({entity_clause})
                LIMIT ?
            """
            # 重新构建params(移除method_params)
            params = [tax_type]
            for entity in entity_keywords:
                params.extend([f"%{entity}%", f"%{entity}%", f"%{entity}%", f"%{entity}%"])
            params.append(limit)
        else:
            query = f"""
                SELECT * FROM tax_incentives
                WHERE tax_type = ?
                AND ({method_conditions})
                LIMIT ?
            """
            params.append(limit)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def count_structured_results(self, tax_type: str, entity_keywords: List[str] = None) -> int:
        """
        统计结构化查询的总数(不限制limit)
        
        Args:
            tax_type: 税种(如"增值税"、"个人所得税")
            entity_keywords: 实体关键词列表(如["集成电路", "软件"])
        
        Returns:
            总记录数
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 优惠方式关键词(与structured_search保持一致)
        incentive_methods = [
            "减征", "免征", "不征", "暂免", "减半", "退税",
            "即征即退", "先征后退", "先征后返", "免税", "减税",
            "减免", "抵扣", "补贴", "扶持", "优惠"
        ]
        
        # 构建优惠方式OR条件
        method_conditions = " OR ".join(["incentive_method LIKE ?" for _ in incentive_methods])
        method_params = [f"%{method}%" for method in incentive_methods]
        
        # 基础查询参数
        params = [tax_type] + method_params
        
        # 如果有实体关键词,增加实体过滤条件(与structured_search保持一致)
        if entity_keywords:
            entity_conditions = []
            for entity in entity_keywords:
                entity_conditions.append("""(
                    project_name LIKE ? 
                    OR detailed_rules LIKE ? 
                    OR qualification LIKE ?
                    OR incentive_method LIKE ?
                )""")
            
            entity_clause = " OR ".join(entity_conditions)
            
            # 移除优惠方式条件限制(因为实体关键词可能就是优惠方式)
            query = f"""
                SELECT COUNT(*) FROM tax_incentives
                WHERE tax_type = ?
                AND ({entity_clause})
            """
            # 重新构建params
            params = [tax_type]
            for entity in entity_keywords:
                params.extend([f"%{entity}%", f"%{entity}%", f"%{entity}%", f"%{entity}%"])
        else:
            query = f"""
                SELECT COUNT(*) FROM tax_incentives
                WHERE tax_type = ?
                AND ({method_conditions})
            """
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def _extract_keywords(self, question: str) -> str:
        """
        从问题中提取关键词(用于关键词搜索)
        
        Args:
            question: 用户问题
        
        Returns:
            关键词字符串
        """
        # 税种关键词
        tax_types = ["增值税", "企业所得税", "个人所得税", "印花税", "房产税", 
                     "城镇土地使用税", "消费税", "土地增值税", "资源税", "车船税", "契税"]
        
        # 优惠关键词
        incentive_keywords = ["优惠", "减免", "免征", "减征", "抵扣", "退税", 
                             "补贴", "扶持", "即征即退", "先征后退", "免税", "减税"]
        
        # 行业/企业类型关键词
        entity_keywords = ["高新技术", "小微企业", "农业", "科技", "研发", 
                          "软件", "集成电路", "节能", "环保", "残疾人"]
        
        keywords = []
        
        # 提取税种
        for tax_type in tax_types:
            if tax_type in question:
                keywords.append(tax_type)
        
        # 提取优惠关键词
        for keyword in incentive_keywords:
            if keyword in question:
                keywords.append(keyword)
        
        # 提取行业/企业类型
        for keyword in entity_keywords:
            if keyword in question:
                keywords.append(keyword)
        
        # 如果提取到关键词,返回组合;否则返回原问题
        if keywords:
            # 去重并返回
            return ' '.join(list(set(keywords)))
        else:
            # 返回原问题用于搜索
            return question
    
    def fulltext_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        全文搜索
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 使用FTS5全文搜索
            cursor.execute("""
                SELECT t.* 
                FROM tax_incentives t
                JOIN tax_incentives_fts fts ON t.id = fts.rowid
                WHERE tax_incentives_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
        
        except sqlite3.OperationalError as e:
            # 如果FTS搜索失败,降级到LIKE搜索
            print(f"⚠️  全文搜索失败: {e}, 使用关键词搜索")
            return self.keyword_search(query, limit)
        
        finally:
            conn.close()
    
    def keyword_search(self, keywords: str, limit: int = 50) -> List[Dict]:
        """
        关键词搜索(使用LIKE)
        
        Args:
            keywords: 搜索关键词(可以是空格分隔的多个关键词)
            limit: 返回结果数量限制
        
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 将关键词分割成列表
        keyword_list = keywords.split()
        
        if not keyword_list:
            conn.close()
            return []
        
        # 构建OR查询条件
        conditions = []
        params = []
        
        for keyword in keyword_list:
            like_pattern = f"%{keyword}%"
            # 每个关键词在多个字段中搜索
            conditions.append("""(
                tax_type LIKE ? OR
                project_name LIKE ? OR
                qualification LIKE ? OR
                detailed_rules LIKE ? OR
                keywords LIKE ? OR
                explanation LIKE ? OR
                incentive_method LIKE ? OR
                legal_basis LIKE ?
            )""")
            # 每个关键词需要8个参数(对应8个字段)
            params.extend([like_pattern] * 8)
        
        # 组合所有条件(OR连接)
        where_clause = " OR ".join(conditions)
        
        query = f"""
            SELECT * FROM tax_incentives
            WHERE {where_clause}
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def search_by_tax_type(self, tax_type: str, limit: int = 10) -> List[Dict]:
        """
        按税种搜索
        
        Args:
            tax_type: 税种名称
            limit: 返回结果数量限制
        
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tax_incentives
            WHERE tax_type = ?
            LIMIT ?
        """, (tax_type, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def search_by_incentive_method(self, method: str, limit: int = 10) -> List[Dict]:
        """
        按优惠方式搜索
        
        Args:
            method: 优惠方式
            limit: 返回结果数量限制
        
        Returns:
            查询结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tax_incentives
            WHERE incentive_method LIKE ?
            LIMIT ?
        """, (f"%{method}%", limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_by_id(self, policy_id: int) -> Optional[Dict]:
        """
        根据ID获取政策详情
        
        Args:
            policy_id: 政策ID
        
        Returns:
            政策详情字典,如果不存在返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tax_incentives WHERE id = ?", (policy_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM tax_incentives")
        stats['total_count'] = cursor.fetchone()[0]
        
        # 按税种统计
        cursor.execute("""
            SELECT tax_type, COUNT(*) as count 
            FROM tax_incentives 
            GROUP BY tax_type 
            ORDER BY count DESC
        """)
        stats['by_tax_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 按优惠方式统计
        cursor.execute("""
            SELECT incentive_method, COUNT(*) as count 
            FROM tax_incentives 
            WHERE incentive_method IS NOT NULL
            GROUP BY incentive_method 
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['by_incentive_method'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return stats


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("税收优惠政策数据库查询测试")
    print("=" * 60)
    
    query = TaxIncentiveQuery()
    
    # 测试1: 统计信息
    print("\n【测试1: 数据库统计】")
    stats = query.get_statistics()
    print(f"  总记录数: {stats['total_count']}")
    print(f"  税种数量: {len(stats['by_tax_type'])}")
    print(f"  优惠方式数量: {len(stats['by_incentive_method'])}")
    
    # 测试2: 智能搜索
    print("\n【测试2: 智能搜索】")
    test_questions = [
        "高新技术企业有哪些增值税优惠?",
        "小微企业所得税减免政策",
        "农产品增值税免征"
    ]
    
    for q in test_questions:
        print(f"\n  问题: {q}")
        results = query.search(q, limit=3)
        print(f"  找到 {len(results)} 条结果:")
        for idx, r in enumerate(results, 1):
            print(f"    {idx}. [{r['tax_type']}] {r['project_name']} - {r['incentive_method']}")
    
    # 测试3: 按税种搜索
    print("\n【测试3: 按税种搜索】")
    results = query.search_by_tax_type("增值税", limit=5)
    print(f"  增值税优惠政策: {len(results)} 条")
    for idx, r in enumerate(results[:3], 1):
        print(f"    {idx}. {r['project_name']}")
    
    # 测试4: 按优惠方式搜索
    print("\n【测试4: 按优惠方式搜索】")
    results = query.search_by_incentive_method("免征", limit=5)
    print(f"  免征类优惠: {len(results)} 条")
    for idx, r in enumerate(results[:3], 1):
        print(f"    {idx}. [{r['tax_type']}] {r['project_name']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
