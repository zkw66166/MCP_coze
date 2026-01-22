#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增指标计算功能
验证 financial_metrics 表的新字段是否正确计算
"""

import sqlite3
import os
import sys

# 添加父目录到路径以导入 calculate_metrics
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.calculate_metrics import calculate_metrics_for_period, save_metrics

DB_PATH = 'database/financial.db'  # 使用相对路径

def test_single_company_calculation():
    """测试单个企业的指标计算"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取第一家有数据的企业
    cursor.execute('''
        SELECT DISTINCT company_id FROM income_statements
        LIMIT 1
    ''')
    result = cursor.fetchone()
    if not result:
        print("❌ 数据库中没有利润表数据")
        conn.close()
        return False
    
    company_id = result['company_id']
    
    # 获取该企业的基本信息
    cursor.execute('SELECT name FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    company_name = company['name'] if company else f"企业{company_id}"
    
    # 获取该企业最近的数据期间
    cursor.execute('''
        SELECT period_year, period_quarter
        FROM income_statements
        WHERE company_id = ?
        ORDER BY period_year DESC, period_quarter DESC
        LIMIT 1
    ''', (company_id,))
    period = cursor.fetchone()
    
    if not period:
        print(f"❌ 企业 {company_name} 没有可用数据")
        conn.close()
        return False
    
    year = period['period_year']
    quarter = period['period_quarter']
    
    conn.close()
    
    print("=" * 70)
    print(f"测试企业画像指标计算")
    print("=" * 70)
    print(f"企业: {company_name} (ID: {company_id})")
    print(f"期间: {year}年 Q{quarter}")
    print("-" * 70)
    
    # 执行计算
    print("\n🔄 开始计算指标...")
    metrics = calculate_metrics_for_period(company_id, year, quarter)
    
    if not metrics:
        print("❌ 计算失败 - 数据不足")
        return False
    
    print("✅ 计算成功\n")
    
    # 显示新增指标
    print("=" * 70)
    print("新增指标计算结果")
    print("=" * 70)
    
    new_indicators = [
        ('sales_expense', '销售费用', '万元'),
        ('admin_expense', '管理费用', '万元'),
        ('operating_cash_flow', '经营活动现金流', '万元'),
        ('investing_cash_flow', '投资活动现金流', '万元'),
        ('financing_cash_flow', '筹资活动现金流', '万元'),
        ('sales_invoice_count', '销售发票数量', '张'),
        ('purchase_invoice_count', '采购发票数量', '张'),
        ('customer_concentration', '客户集中度(TOP5)', '%'),
        ('supplier_concentration', '供应商集中度(TOP5)', '%'),
    ]
    
    for key, label, unit in new_indicators:
        value = metrics.get(key)
        if value is not None:
            print(f"  ✓ {label:25s}: {value:>12} {unit}")
        else:
            print(f"  - {label:25s}: {'未计算':>12} (数据不足)")
    
    # 保存到数据库
    print("\n🔄 保存指标到数据库...")
    save_metrics(metrics)
    print("✅ 保存成功")
    
    # 验证数据库中的数据
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM financial_metrics
        WHERE company_id = ? AND period_year = ? AND period_quarter = ?
    ''', (company_id, year, quarter))
    
    saved = cursor.fetchone()
    conn.close()
    
    if saved:
        print("\n✅ 数据库验证通过")
        print(f"   记录ID: {saved['id']}")
        print(f"   总指标数: {len([k for k in dict(saved).keys() if saved[k] is not None])} 个")
        
        # 检查新增字段是否有值
        new_fields_with_data = sum(1 for key, _, _ in new_indicators if saved[key] is not None)
        print(f"   新增字段有数据: {new_fields_with_data}/{len(new_indicators)} 个")
        
        return True
    else:
        print("\n❌ 数据库验证失败 - 未找到保存的记录")
        return False


def show_all_indicators():
    """显示所有已计算的指标类型"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT company_id) as companies,
               MIN(period_year) as min_year,
               MAX(period_year) as max_year
        FROM financial_metrics
    ''')
    stats = cursor.fetchone()
    
    print("\n" + "=" * 70)
    print("财务指标表统计")
    print("=" * 70)
    print(f"总记录数: {stats[0]}")
    print(f"企业数: {stats[1]}")
    print(f"年份范围: {stats[2]} - {stats[3]}")
    
    conn.close()


if __name__ == "__main__":
    success = test_single_company_calculation()
    
    if success:
        show_all_indicators()
        print("\n" + "=" * 70)
        print("✅ 测试通过 - 新增指标计算功能正常")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        sys.exit(1)
