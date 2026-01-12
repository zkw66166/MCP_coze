#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
税收优惠政策数据库初始化脚本
功能:
1. 创建增强版数据库表结构(包含扩展字段)
2. 创建全文搜索索引
3. 从Excel导入现有数据
4. 数据验证和统计
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "tax_incentives.db"
EXCEL_PATH = Path(__file__).parent.parent / "data_source" / "税收优惠政策一览表(coze).xlsx"


def create_database():
    """创建数据库和表结构"""
    print("📦 开始创建数据库...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建主表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tax_incentives (
        -- 主键
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        -- Excel现有字段
        serial_number INTEGER,             -- 序号
        tax_type TEXT NOT NULL,            -- 税种(增值税、企业所得税等)
        project_name TEXT,                 -- 优惠项目
        qualification TEXT,                -- 优惠认定条件
        incentive_method TEXT,             -- 税收优惠方式(免征、减征等)
        detailed_rules TEXT,               -- 具体优惠规定
        legal_basis TEXT,                  -- 法律依据
        special_notes TEXT,                -- 特殊事项
        explanation TEXT,                  -- 相关解释
        
        -- 扩展字段(支持后续数据完善)
        effective_date TEXT,               -- 有效期开始日期(YYYY-MM-DD)
        expiry_date TEXT,                  -- 有效期结束日期(YYYY-MM-DD)
        applicable_region TEXT,            -- 适用地区(全国/省份/城市)
        policy_status TEXT DEFAULT 'active', -- 政策状态(active/expired/suspended)
        industry_scope TEXT,               -- 适用行业范围
        enterprise_type TEXT,              -- 适用企业类型(小微/高新/一般等)
        discount_rate TEXT,                -- 优惠比例/税率
        application_process TEXT,          -- 申请流程说明
        required_documents TEXT,           -- 所需材料清单
        
        -- 元数据
        data_source TEXT DEFAULT 'excel',  -- 数据来源
        data_quality INTEGER DEFAULT 1,    -- 数据完整度(1-5, 1=仅基础字段)
        last_verified_date TEXT,           -- 最后核验日期
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- 索引字段
        keywords TEXT,                     -- 关键词(用于快速检索)
        tags TEXT                          -- 标签(JSON数组)
    )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tax_type ON tax_incentives(tax_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incentive_method ON tax_incentives(incentive_method)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_policy_status ON tax_incentives(policy_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_applicable_region ON tax_incentives(applicable_region)")
    
    # 创建全文搜索虚拟表
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS tax_incentives_fts USING fts5(
        tax_type,
        project_name,
        qualification,
        detailed_rules,
        legal_basis,
        explanation,
        keywords,
        content='tax_incentives',
        content_rowid='id'
    )
    """)
    
    # 创建触发器:自动更新全文搜索索引
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS tax_incentives_ai AFTER INSERT ON tax_incentives BEGIN
        INSERT INTO tax_incentives_fts(rowid, tax_type, project_name, qualification, detailed_rules, legal_basis, explanation, keywords)
        VALUES (new.id, new.tax_type, new.project_name, new.qualification, new.detailed_rules, new.legal_basis, new.explanation, new.keywords);
    END
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS tax_incentives_ad AFTER DELETE ON tax_incentives BEGIN
        DELETE FROM tax_incentives_fts WHERE rowid = old.id;
    END
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS tax_incentives_au AFTER UPDATE ON tax_incentives BEGIN
        DELETE FROM tax_incentives_fts WHERE rowid = old.id;
        INSERT INTO tax_incentives_fts(rowid, tax_type, project_name, qualification, detailed_rules, legal_basis, explanation, keywords)
        VALUES (new.id, new.tax_type, new.project_name, new.qualification, new.detailed_rules, new.legal_basis, new.explanation, new.keywords);
    END
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库创建成功!")


def generate_keywords(row):
    """生成关键词用于快速检索"""
    keywords = []
    
    # 税种关键词
    if pd.notna(row['税种']):
        keywords.append(row['税种'])
    
    # 优惠方式关键词
    if pd.notna(row['税收优惠方式']):
        method = str(row['税收优惠方式'])
        if '免征' in method:
            keywords.extend(['免征', '免税', '优惠'])
        if '减征' in method or '减免' in method:
            keywords.extend(['减征', '减免', '优惠'])
        if '抵扣' in method:
            keywords.extend(['抵扣', '优惠'])
    
    # 项目名称关键词
    if pd.notna(row['优惠项目']):
        keywords.append(str(row['优惠项目']))
    
    return ' '.join(set(keywords))


def import_excel_data():
    """从Excel导入数据"""
    print(f"\n📥 开始导入Excel数据: {EXCEL_PATH}")
    
    if not EXCEL_PATH.exists():
        print(f"❌ Excel文件不存在: {EXCEL_PATH}")
        return
    
    # 读取Excel
    df = pd.read_excel(EXCEL_PATH)
    print(f"📊 读取到 {len(df)} 条记录")
    
    # 字段映射
    field_mapping = {
        '序号': 'serial_number',
        '税种': 'tax_type',
        '优惠项目': 'project_name',
        '优惠认定条件': 'qualification',
        '税收优惠方式': 'incentive_method',
        '具体优惠规定': 'detailed_rules',
        '法律依据': 'legal_basis',
        '特殊事项': 'special_notes',
        '相关解释': 'explanation'
    }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空现有数据(如果需要重新导入)
    cursor.execute("DELETE FROM tax_incentives")
    
    imported_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        # 跳过税种为空的行
        if pd.isna(row['税种']):
            skipped_count += 1
            continue
        
        # 生成关键词
        keywords = generate_keywords(row)
        
        # 准备插入数据
        insert_data = {
            'serial_number': int(row['序号']) if pd.notna(row['序号']) else None,
            'tax_type': str(row['税种']) if pd.notna(row['税种']) else None,
            'project_name': str(row['优惠项目']) if pd.notna(row['优惠项目']) else None,
            'qualification': str(row['优惠认定条件']) if pd.notna(row['优惠认定条件']) else None,
            'incentive_method': str(row['税收优惠方式']) if pd.notna(row['税收优惠方式']) else None,
            'detailed_rules': str(row['具体优惠规定']) if pd.notna(row['具体优惠规定']) else None,
            'legal_basis': str(row['法律依据']) if pd.notna(row['法律依据']) else None,
            'special_notes': str(row['特殊事项']) if pd.notna(row['特殊事项']) else None,
            'explanation': str(row['相关解释']) if pd.notna(row['相关解释']) else None,
            'keywords': keywords,
            'data_source': 'excel',
            'data_quality': 1  # 仅基础字段,质量等级1
        }
        
        # 插入数据
        cursor.execute("""
            INSERT INTO tax_incentives (
                serial_number, tax_type, project_name, qualification,
                incentive_method, detailed_rules, legal_basis, special_notes,
                explanation, keywords, data_source, data_quality
            ) VALUES (
                :serial_number, :tax_type, :project_name, :qualification,
                :incentive_method, :detailed_rules, :legal_basis, :special_notes,
                :explanation, :keywords, :data_source, :data_quality
            )
        """, insert_data)
        
        imported_count += 1
        
        if (imported_count % 100) == 0:
            print(f"  已导入 {imported_count} 条...")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据导入完成!")
    print(f"  - 成功导入: {imported_count} 条")
    print(f"  - 跳过记录: {skipped_count} 条")


def verify_database():
    """验证数据库"""
    print("\n🔍 验证数据库...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 统计总记录数
    cursor.execute("SELECT COUNT(*) FROM tax_incentives")
    total_count = cursor.fetchone()[0]
    print(f"  总记录数: {total_count}")
    
    # 按税种统计
    cursor.execute("""
        SELECT tax_type, COUNT(*) as count 
        FROM tax_incentives 
        GROUP BY tax_type 
        ORDER BY count DESC
    """)
    print("\n  按税种统计:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} 条")
    
    # 按优惠方式统计
    cursor.execute("""
        SELECT incentive_method, COUNT(*) as count 
        FROM tax_incentives 
        WHERE incentive_method IS NOT NULL
        GROUP BY incentive_method 
        ORDER BY count DESC
        LIMIT 10
    """)
    print("\n  按优惠方式统计(前10):")
    for row in cursor.fetchall():
        method = row[0][:30] + '...' if len(row[0]) > 30 else row[0]
        print(f"    {method}: {row[1]} 条")
    
    # 测试全文搜索
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tax_incentives_fts 
        WHERE tax_incentives_fts MATCH '增值税'
    """)
    search_count = cursor.fetchone()[0]
    print(f"\n  全文搜索测试('增值税'): {search_count} 条")
    
    conn.close()
    print("\n✅ 数据库验证完成!")


def main():
    """主函数"""
    print("=" * 60)
    print("税收优惠政策数据库初始化")
    print("=" * 60)
    
    # 创建database目录
    DB_PATH.parent.mkdir(exist_ok=True)
    
    # 检查数据库是否已存在
    if DB_PATH.exists():
        response = input(f"\n⚠️  数据库已存在: {DB_PATH}\n是否重新创建? (y/n): ")
        if response.lower() != 'y':
            print("❌ 取消操作")
            return
        os.remove(DB_PATH)
        print("🗑️  已删除旧数据库")
    
    # 执行初始化
    create_database()
    import_excel_data()
    verify_database()
    
    print("\n" + "=" * 60)
    print(f"✅ 初始化完成! 数据库路径: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
