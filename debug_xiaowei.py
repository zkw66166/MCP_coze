#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本：分析小微企业优惠查询问题
"""

import sqlite3
from pathlib import Path

# 数据库路径
db_path = Path(__file__).parent / "database" / "tax_incentives.db"

print("=" * 80)
print("税收优惠数据库分析 - 小微企业优惠查询问题调试")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. 查看数据库表结构
print("\n【1. 数据库表结构】")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"数据库表: {[t[0] for t in tables]}")

# 2. 查看tax_incentives表结构
print("\n【2. tax_incentives表字段】")
cursor.execute("PRAGMA table_info(tax_incentives)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]:2}. {col[1]:25} [{col[2]:10}]")

# 3. 统计税种分布
print("\n【3. 税种分布】")
cursor.execute("SELECT tax_type, COUNT(*) as cnt FROM tax_incentives GROUP BY tax_type ORDER BY cnt DESC")
for row in cursor.fetchall():
    print(f"  {row[0]:20}: {row[1]:4} 条")

# 4. 搜索包含"小微"关键词的记录
print("\n【4. 包含'小微'关键词的记录】")
search_fields = ['incentive_items', 'qualification', 'detailed_rules', 'keywords', 'incentive_method', 'explanation']
all_xiaowei_records = []

for field in search_fields:
    cursor.execute(f"SELECT id, tax_type, incentive_items, incentive_method, {field} as matched_field FROM tax_incentives WHERE {field} LIKE '%小微%'")
    results = cursor.fetchall()
    if results:
        print(f"\n  ▶ 在 {field} 字段找到 {len(results)} 条记录:")
        for row in results:
            print(f"    ID={row[0]:3}, 税种={row[1]:12}, 项目={row[2][:40] if row[2] else 'N/A'}...")
            all_xiaowei_records.append(dict(row))

print(f"\n  总计：包含'小微'的记录共 {len(all_xiaowei_records)} 条")

# 5. 搜索包含"小型微利"关键词的记录
print("\n【5. 包含'小型微利'关键词的记录】")
for field in search_fields:
    cursor.execute(f"SELECT id, tax_type, incentive_items, incentive_method, {field} as matched_field FROM tax_incentives WHERE {field} LIKE '%小型微利%'")
    results = cursor.fetchall()
    if results:
        print(f"\n  ▶ 在 {field} 字段找到 {len(results)} 条记录:")
        for row in results:
            print(f"    ID={row[0]:3}, 税种={row[1]:12}, 项目={row[2][:40] if row[2] else 'N/A'}...")

# 6. 模拟"小微企业优惠有哪些"的查询逻辑
print("\n【6. 模拟查询:'小微企业优惠有哪些'】")
question = "小微企业优惠有哪些"

# 检查是否包含税种
tax_types = [
    "城镇土地使用税", "企业所得税", "个人所得税", "土地增值税",
    "增值税", "印花税", "房产税", "消费税", "资源税", "车船税", "契税", "关税"
]
matched_tax = None
for tax in tax_types:
    if tax in question:
        matched_tax = tax
        break
print(f"  税种识别: {matched_tax if matched_tax else '未识别到税种'}")

# 检查是否匹配核心实体关键词
core_entity_keywords = [
    "集成电路", "软件", "高新技术", "小微企业", "小型微利",
    "残疾人", "创业投资", "天使投资"
]
matched_entities = [kw for kw in core_entity_keywords if kw in question]
print(f"  实体关键词: {matched_entities if matched_entities else '未识别'}")

# 7. 当没有税种但有实体关键词时的查询逻辑分析
print("\n【7. 当前查询逻辑分析】")
print("  问题: '小微企业优惠有哪些'")
print(f"  - 税种识别结果: {matched_tax}")
print(f"  - 实体关键词: {matched_entities}")
print("\n  当前代码逻辑:")
print("  1. _extract_tax_and_incentive() 提取税种和实体关键词")
print("  2. 如果提取到税种 → structured_search(tax_type, entity_keywords)")
print("  3. 如果没有税种 → keyword_search()")
print("")
print("  问题分析:")
print("  - 问题中没有明确税种,所以不会进入 structured_search")
print("  - 虽然识别到'小微企业'实体关键词,但因为没有税种,会进入 keyword_search")
print("  - keyword_search 使用 _extract_keywords() 提取关键词")

# 8. 查看_extract_keywords会返回什么
print("\n【8. _extract_keywords 逻辑模拟】")
# 税种关键词
tax_kw = ["增值税", "企业所得税", "个人所得税", "印花税", "房产税", 
             "城镇土地使用税", "消费税", "土地增值税", "资源税", "车船税", "契税"]
# 优惠关键词
incentive_kw = ["优惠", "减免", "免征", "减征", "抵扣", "退税", 
                     "补贴", "扶持", "即征即退", "先征后退", "免税", "减税"]
# 实体关键词
entity_kw = ["高新技术", "小微企业", "农业", "科技", "研发", 
                      "软件", "集成电路", "节能", "环保", "残疾人"]

extracted = []
for kw in tax_kw + incentive_kw + entity_kw:
    if kw in question:
        extracted.append(kw)

print(f"  问题: {question}")
print(f"  _extract_keywords 返回: {' '.join(list(set(extracted)))}")

# 9. 验证keyword_search能否找到小微企业相关数据
print("\n【9. keyword_search 结果验证】")
keywords = ' '.join(list(set(extracted)))
print(f"  搜索关键词: '{keywords}'")

# 分割关键词
keyword_list = keywords.split()
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
    SELECT * FROM tax_incentives
    WHERE {where_clause}
    LIMIT 50
"""
params.append(50)
# 去掉最后一个limit参数
params = params[:-1]
query = f"""
    SELECT id, tax_type, incentive_items, incentive_method 
    FROM tax_incentives
    WHERE {where_clause}
    LIMIT 50
"""

cursor.execute(query, params)
results = cursor.fetchall()
print(f"  找到 {len(results)} 条记录")

# 分析结果中包含"小微"的记录数
xiaowei_count = 0
for row in results:
    # 检查各字段是否包含小微
    item = row[2] if row[2] else ""
    method = row[3] if row[3] else ""
    if "小微" in item or "小微" in method:
        xiaowei_count += 1
        print(f"    ✓ ID={row[0]:3}, 税种={row[1]:12}, 项目={row[2][:35]}...")

print(f"\n  结果中包含'小微'的记录: {xiaowei_count} 条")

# 10. 检查所有"小微企业"相关的完整数据
print("\n【10. 所有小微企业相关政策详情】")
cursor.execute("""
    SELECT id, tax_type, incentive_items, incentive_method, qualification, keywords
    FROM tax_incentives 
    WHERE incentive_items LIKE '%小微%' 
       OR qualification LIKE '%小微%'
       OR detailed_rules LIKE '%小微%'
       OR keywords LIKE '%小微%'
       OR incentive_method LIKE '%小微%'
       OR explanation LIKE '%小微%'
    ORDER BY tax_type
""")
all_results = cursor.fetchall()
print(f"  小微企业相关政策总数: {len(all_results)} 条")
for row in all_results:
    print(f"\n  ID={row[0]:3} [{row[1]:12}]")
    print(f"    项目: {row[2] if row[2] else 'N/A'}")
    print(f"    优惠方式: {row[3] if row[3] else 'N/A'}")
    print(f"    资格条件: {row[4][:60] if row[4] else 'N/A'}...")
    print(f"    关键词: {row[5] if row[5] else 'N/A'}")

conn.close()

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
