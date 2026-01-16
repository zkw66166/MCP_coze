#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本：完整模拟"小微企业优惠有哪些"的查询流程
"""

import sqlite3
from pathlib import Path

# 数据库路径
db_path = Path(__file__).parent / "database" / "tax_incentives.db"

print("=" * 80)
print("完整模拟查询: '小微企业优惠有哪些'")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

question = "小微企业优惠有哪些"

# ====== 1. _extract_tax_and_incentive 逻辑 ======
print("\n【1. _extract_tax_and_incentive 提取结果】")

tax_types = [
    "城镇土地使用税", "企业所得税", "个人所得税", "土地增值税",
    "增值税", "印花税", "房产税", "消费税", "资源税", "车船税", "契税", "关税"
]
tax_fuzzy_map = {
    "企业所得": "企业所得税",
    "个人所得": "个人所得税",
    "土地增值": "土地增值税",
    "城镇土地使用": "城镇土地使用税",
}
core_entity_keywords = [
    "集成电路", "软件", "高新技术", "小微企业", "小型微利",
    "残疾人", "创业投资", "天使投资"
]

# 提取税种
matched_tax_type = None
for tax_type in tax_types:
    if tax_type in question:
        matched_tax_type = tax_type
        break
if not matched_tax_type:
    for fuzzy_key, full_tax_type in tax_fuzzy_map.items():
        if fuzzy_key in question:
            matched_tax_type = full_tax_type
            break

# 提取实体关键词
matched_entities = [kw for kw in core_entity_keywords if kw in question]

print(f"  税种: {matched_tax_type}")
print(f"  实体关键词: {matched_entities}")

# ====== 2. search 方法逻辑 ======
print("\n【2. search 方法逻辑分析】")
print("  if tax_type:  # 如果有税种")
print("      → structured_search(tax_type, entity_keywords)")
print("  else:         # 没有税种")
print("      → keyword_search()")
print("")
print(f"  当前: tax_type = {matched_tax_type}")
print(f"  → 由于没有税种,进入 keyword_search 分支")

# ====== 3. keyword_search 逻辑 ======
print("\n【3. keyword_search 逻辑】")

# _extract_keywords 提取
tax_kw = ["增值税", "企业所得税", "个人所得税", "印花税", "房产税", 
         "城镇土地使用税", "消费税", "土地增值税", "资源税", "车船税", "契税"]
incentive_kw = ["优惠", "减免", "免征", "减征", "抵扣", "退税", 
                "补贴", "扶持", "即征即退", "先征后退", "免税", "减税"]
entity_kw = ["高新技术", "小微企业", "农业", "科技", "研发", 
             "软件", "集成电路", "节能", "环保", "残疾人"]

extracted_keywords = []
for kw in tax_kw + incentive_kw + entity_kw:
    if kw in question:
        extracted_keywords.append(kw)

keywords_str = ' '.join(list(set(extracted_keywords)))
print(f"  _extract_keywords 返回: '{keywords_str}'")

# keyword_search 查询
keyword_list = keywords_str.split()
print(f"  分割后的关键词列表: {keyword_list}")

# 构建 OR 条件（问题所在！）
print("\n  SQL条件构建 (OR 连接):")
for kw in keyword_list:
    print(f"    - '{kw}' 匹配 tax_type/incentive_items/qualification/.../legal_basis")

print("\n  ⚠️ 问题分析:")
print("  关键词 '优惠' 和 '小微企业' 用 OR 连接")
print("  → '优惠'会匹配大量无关记录 (所有含'优惠'的政策)")
print("  → '小微企业'只能匹配少量记录")
print("  → OR 的结果是大量含'优惠'但不含'小微'的记录")

# 验证
print("\n【4. 验证 OR 查询结果】")

# 模拟 keyword_search 的 OR 查询
conditions = []
params = []
for keyword in keyword_list:
    like_pattern = f"%{keyword}%"
    conditions.append("""(
        tax_type LIKE ? OR
        incentive_items LIKE ? OR
        qualification LIKE ? OR
        detailed_rules LIKE ? OR
        keywords LIKE ? OR
        explanation LIKE ? OR
        incentive_method LIKE ? OR
        legal_basis LIKE ?
    )""")
    params.extend([like_pattern] * 8)

where_clause = " OR ".join(conditions)
query = f"""
    SELECT id, tax_type, incentive_items, incentive_method 
    FROM tax_incentives
    WHERE {where_clause}
    LIMIT 20
"""

cursor.execute(query, params)
results = cursor.fetchall()

print(f"  OR 查询结果: {len(results)} 条")

# 统计匹配情况
match_youhui_only = 0
match_xiaowei = 0
for row in results:
    item = row[2] if row[2] else ""
    method = row[3] if row[3] else ""
    kws_field = ""
    cursor.execute("SELECT keywords FROM tax_incentives WHERE id = ?", (row[0],))
    kw_row = cursor.fetchone()
    if kw_row:
        kws_field = kw_row[0] if kw_row[0] else ""
    
    has_xiaowei = "小微" in item or "小微" in method or "小微" in kws_field
    has_youhui = "优惠" in item or "优惠" in method or "优惠" in kws_field
    
    if has_xiaowei:
        match_xiaowei += 1
    if has_youhui and not has_xiaowei:
        match_youhui_only += 1

print(f"  - 仅匹配'优惠'的记录: {match_youhui_only} 条")
print(f"  - 匹配'小微'的记录: {match_xiaowei} 条")

# ====== 5. 解决方案分析 ======
print("\n【5. 问题根因和解决方案】")
print("")
print("  ❌ 问题根因:")
print("    1. 问题中没有税种 → 不进入 structured_search")
print("    2. keyword_search 用 OR 连接多个关键词")
print("    3. '优惠'是高频词,匹配大量无关政策")
print("    4. 结果被'优惠'相关的政策稀释,'小微企业'相关政策排不到前面")
print("")
print("  ✅ 解决方案:")
print("    方案1: 当没有税种但有实体关键词时,实体关键词使用 AND 约束")
print("    方案2: structured_search 应该接受 tax_type=None 的情况")
print("    方案3: 当识别到'小微企业'等实体时,应跨所有税种搜索包含该实体的政策")

# ====== 6. 验证正确查询 ======
print("\n【6. 验证正确的查询方式】")

# 方案: 使用 AND 连接实体关键词
print("  使用 AND 连接 '优惠' + '小微企业':")
cursor.execute("""
    SELECT id, tax_type, incentive_items, incentive_method 
    FROM tax_incentives
    WHERE (
        incentive_items LIKE '%小微%' 
        OR qualification LIKE '%小微%' 
        OR detailed_rules LIKE '%小微%'
        OR keywords LIKE '%小微%'
        OR incentive_method LIKE '%小微%'
        OR explanation LIKE '%小微%'
    )
    ORDER BY id
""")
correct_results = cursor.fetchall()
print(f"  结果: {len(correct_results)} 条")
for row in correct_results:
    print(f"    ID={row[0]:3}, 税种={row[1]:12}, 项目={row[2] if row[2] else 'N/A'}")

# ====== 7. 还要检查"小型微利企业"相关政策 ======
print("\n【7. 检查'小型微利企业'相关政策】")
cursor.execute("""
    SELECT id, tax_type, incentive_items, incentive_method 
    FROM tax_incentives
    WHERE (
        incentive_items LIKE '%小型微利%' 
        OR qualification LIKE '%小型微利%' 
        OR detailed_rules LIKE '%小型微利%'
        OR keywords LIKE '%小型微利%'
    )
    ORDER BY id
""")
xiaoxing_results = cursor.fetchall()
print(f"  '小型微利'相关政策: {len(xiaoxing_results)} 条")
for row in xiaoxing_results:
    print(f"    ID={row[0]:3}, 税种={row[1]:12}, 项目={row[2] if row[2] else 'N/A'}")

conn.close()

print("\n" + "=" * 80)
print("分析结论:")
print("  问题: 当用户询问'小微企业优惠有哪些'时,由于没有指定税种,")
print("        系统进入 keyword_search,使用 OR 连接'优惠'和'小微企业'。")
print("        '优惠'关键词匹配了大量无关数据,稀释了'小微企业'相关结果。")
print("")
print("  建议修复:")
print("    1. 当有实体关键词(如'小微企业')但没有税种时,")
print("       应该优先搜索包含该实体的政策(跨所有税种)")
print("    2. 修改 search() 方法,在没有税种但有实体关键词时,")
print("       调用新的跨税种实体搜索方法")
print("=" * 80)
