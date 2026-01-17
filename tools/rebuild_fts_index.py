#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FTS索引重建脚本
功能:
1. 检测主表 tax_incentives 与 FTS 索引表的数据差异
2. 自动重建 tax_incentives_fts 及其关联表
3. 对新增记录，调用大模型生成/优化 keywords 字段
4. 容错处理：事务回滚、异常日志

使用方法:
    python tools/rebuild_fts_index.py

执行顺序:
    此脚本应在 update_tax_config.py 之前运行
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 数据库路径
DB_PATH = PROJECT_ROOT / "database" / "tax_incentives.db"
LOG_PATH = PROJECT_ROOT / "tools" / "fts_rebuild.log"

# 记录文件，用于配置更新脚本检测执行顺序
LAST_REBUILD_FILE = PROJECT_ROOT / "tools" / ".fts_last_rebuild"


def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")


def get_main_table_count(cursor) -> int:
    """获取主表记录数"""
    cursor.execute("SELECT COUNT(*) FROM tax_incentives")
    return cursor.fetchone()[0]


def get_fts_table_count(cursor) -> int:
    """获取FTS表记录数"""
    try:
        cursor.execute("SELECT COUNT(*) FROM tax_incentives_fts")
        return cursor.fetchone()[0]
    except sqlite3.OperationalError:
        return -1  # FTS表不存在


def check_fts_sync(conn) -> dict:
    """检查FTS索引是否与主表同步"""
    cursor = conn.cursor()
    
    main_count = get_main_table_count(cursor)
    fts_count = get_fts_table_count(cursor)
    
    return {
        "main_count": main_count,
        "fts_count": fts_count,
        "is_synced": main_count == fts_count,
        "fts_exists": fts_count >= 0
    }


def rebuild_fts_index(conn) -> bool:
    """重建FTS索引"""
    cursor = conn.cursor()
    
    try:
        log("开始重建FTS索引...")
        
        # 1. 删除现有FTS表及关联表
        log("  → 清理现有FTS表...")
        cursor.execute("DROP TABLE IF EXISTS tax_incentives_fts")
        
        # 2. 创建新的FTS5虚拟表
        log("  → 创建FTS5虚拟表...")
        cursor.execute("""
            CREATE VIRTUAL TABLE tax_incentives_fts USING fts5(
                tax_type,
                incentive_items,
                qualification,
                detailed_rules,
                legal_basis,
                explanation,
                keywords,
                content='tax_incentives',
                content_rowid='id'
            )
        """)
        
        # 3. 填充FTS索引
        log("  → 填充FTS索引数据...")
        cursor.execute("""
            INSERT INTO tax_incentives_fts(rowid, tax_type, incentive_items, 
                qualification, detailed_rules, legal_basis, explanation, keywords)
            SELECT id, tax_type, incentive_items, qualification, 
                   detailed_rules, legal_basis, explanation, keywords
            FROM tax_incentives
        """)
        
        conn.commit()
        
        # 4. 验证
        new_count = get_fts_table_count(cursor)
        main_count = get_main_table_count(cursor)
        
        if new_count == main_count:
            log(f"✅ FTS索引重建成功! 共 {new_count} 条记录")
            return True
        else:
            log(f"⚠️ FTS索引记录数({new_count})与主表({main_count})不一致", "WARNING")
            return False
            
    except Exception as e:
        conn.rollback()
        log(f"❌ FTS索引重建失败: {e}", "ERROR")
        return False


def generate_keywords_with_llm(record: dict) -> str:
    """使用大模型生成keywords字段（对于缺少keywords的记录）"""
    try:
        from modules.llm_client import call_deepseek
        
        prompt = f"""请为以下税收优惠政策生成搜索关键词（用空格分隔，不超过10个关键词）：

税种：{record.get('tax_type', '')}
优惠项目：{record.get('incentive_items', '')}
认定条件：{record.get('qualification', '')[:200]}
优惠方式：{record.get('incentive_method', '')}

只返回关键词，不要其他解释。"""

        response = call_deepseek(prompt, max_tokens=100)
        if response:
            # 清理响应
            keywords = response.strip().replace('\n', ' ').replace(',', ' ')
            return keywords
    except Exception as e:
        log(f"  ⚠️ LLM生成keywords失败: {e}", "WARNING")
    
    # 降级：使用字段内容生成基础关键词
    parts = [
        record.get('tax_type', ''),
        record.get('incentive_items', ''),
        record.get('incentive_method', '')
    ]
    return ' '.join(filter(None, parts))


def update_missing_keywords(conn) -> int:
    """更新缺少keywords的记录"""
    cursor = conn.cursor()
    
    # 查找缺少keywords的记录
    cursor.execute("""
        SELECT id, tax_type, incentive_items, qualification, incentive_method
        FROM tax_incentives
        WHERE keywords IS NULL OR keywords = '' OR keywords = 'N/A'
        LIMIT 50
    """)
    
    records = cursor.fetchall()
    if not records:
        log("所有记录均有keywords，无需更新")
        return 0
    
    log(f"发现 {len(records)} 条记录缺少keywords，开始生成...")
    
    updated = 0
    for row in records:
        record = {
            'id': row[0],
            'tax_type': row[1],
            'incentive_items': row[2],
            'qualification': row[3],
            'incentive_method': row[4]
        }
        
        keywords = generate_keywords_with_llm(record)
        
        if keywords:
            cursor.execute(
                "UPDATE tax_incentives SET keywords = ? WHERE id = ?",
                (keywords, record['id'])
            )
            updated += 1
            log(f"  → 已更新 ID={record['id']}: {keywords[:50]}...")
    
    conn.commit()
    log(f"✅ 已更新 {updated} 条记录的keywords")
    return updated


def mark_rebuild_complete():
    """记录重建完成时间（供配置更新脚本检测）"""
    with open(LAST_REBUILD_FILE, 'w') as f:
        f.write(datetime.now().isoformat())
    log(f"已记录重建时间到: {LAST_REBUILD_FILE}")


def main():
    """主函数"""
    print("=" * 60)
    print("FTS索引重建工具")
    print("=" * 60)
    
    # 检查数据库是否存在
    if not DB_PATH.exists():
        log(f"❌ 数据库文件不存在: {DB_PATH}", "ERROR")
        return 1
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # 1. 检查同步状态
        log("检查FTS索引同步状态...")
        status = check_fts_sync(conn)
        log(f"  主表记录数: {status['main_count']}")
        log(f"  FTS记录数: {status['fts_count']}")
        log(f"  是否同步: {'是' if status['is_synced'] else '否'}")
        
        # 2. 如果不同步或FTS不存在，重建索引
        if not status['is_synced'] or not status['fts_exists']:
            log("需要重建FTS索引...")
            if not rebuild_fts_index(conn):
                return 1
        else:
            log("FTS索引已是最新，无需重建")
        
        # 3. 更新缺少keywords的记录
        log("\n检查并更新缺少keywords的记录...")
        update_missing_keywords(conn)
        
        # 4. 如果keywords有更新，需要重新同步FTS
        log("\n再次同步FTS索引...")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tax_incentives_fts(tax_incentives_fts) VALUES('rebuild')")
        conn.commit()
        log("✅ FTS索引已重新同步")
        
        # 5. 记录完成时间
        mark_rebuild_complete()
        
        print("\n" + "=" * 60)
        print("✅ FTS索引重建完成!")
        print("请继续运行: python tools/update_tax_config.py")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        log(f"❌ 执行失败: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
