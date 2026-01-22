#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扩展 financial_metrics 表结构
添加企业画像所需的缺失指标字段
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'financial.db')

def extend_financial_metrics_table():
    """为 financial_metrics 表添加新字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 定义要添加的字段
    new_columns = [
        # 成本费用指标（绝对值）
        ("sales_expense", "REAL", "销售费用（万元）"),
        ("admin_expense", "REAL", "管理费用（万元）"),
        
        # 现金流指标
        ("operating_cash_flow", "REAL", "经营活动现金流（万元）"),
        ("investing_cash_flow", "REAL", "投资活动现金流（万元）"),
        ("financing_cash_flow", "REAL", "筹资活动现金流（万元）"),
        
        # 业务运营指标
        ("sales_invoice_count", "INTEGER", "销售发票数量"),
        ("purchase_invoice_count", "INTEGER", "采购发票数量"),
        ("customer_concentration", "REAL", "客户集中度-TOP5占比(%)"),
        ("supplier_concentration", "REAL", "供应商集中度-TOP5占比(%)"),
        
        # 元数据字段
        ("calculated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP", "计算时间"),
        ("data_version", "TEXT DEFAULT 'v1.0'", "数据版本"),
        ("data_quality_score", "REAL", "数据质量评分(0-100)"),
    ]
    
    print("=" * 60)
    print("扩展 financial_metrics 表结构")
    print("=" * 60)
    
    added_count = 0
    skipped_count = 0
    
    for column_name, column_type, description in new_columns:
        try:
            sql = f"ALTER TABLE financial_metrics ADD COLUMN {column_name} {column_type}"
            cursor.execute(sql)
            print(f"✓ 添加字段: {column_name:30s} ({description})")
            added_count += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"- 字段已存在: {column_name:30s} ({description})")
                skipped_count += 1
            else:
                print(f"✗ 添加失败: {column_name:30s} - {e}")
    
    conn.commit()
    
    # 验证表结构
    cursor.execute("PRAGMA table_info(financial_metrics)")
    columns = cursor.fetchall()
    total_columns = len(columns)
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ 表结构扩展完成")
    print(f"   新增字段: {added_count} 个")
    print(f"   已存在字段: {skipped_count} 个")
    print(f"   表总字段数: {total_columns} 个")
    print("=" * 60)
    
    return added_count, skipped_count, total_columns


def verify_table_structure():
    """验证表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("验证 financial_metrics 表结构")
    print("=" * 60)
    
    cursor.execute("PRAGMA table_info(financial_metrics)")
    columns = cursor.fetchall()
    
    print(f"\n表字段列表（共 {len(columns)} 个）：")
    print(f"{'序号':<6} {'字段名':<35} {'类型':<15} {'可空':<6} {'默认值'}")
    print("-" * 80)
    
    for col in columns:
        cid, name, col_type, notnull, default_val, pk = col
        nullable = "NOT NULL" if notnull else "NULL"
        default = default_val if default_val else ""
        print(f"{cid+1:<6} {name:<35} {col_type:<15} {nullable:<6} {default}")
    
    conn.close()


if __name__ == "__main__":
    # 执行表结构扩展
    extend_financial_metrics_table()
    
    # 验证表结构
    verify_table_structure()
