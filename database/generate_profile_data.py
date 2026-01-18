"""
企业画像示例数据生成脚本
为4户企业生成差异化的示例数据用于演示
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'financial.db')

# 企业特征定位
COMPANY_PROFILES = {
    5: {  # ABC有限公司
        'name': 'ABC有限公司',
        'type': '成熟稳健型',
        'gross_margin': 0.35,
        'growth_rate': 0.08,
        'customer_concentration': 'low',
        'risk_level': 'low',
        'taxpayer_type': '一般纳税人',
        'credit_code': '91330200MA2KXXXXXX'
    },
    8: {  # 123制造厂
        'name': '123制造厂',
        'type': '规模化制造型',
        'gross_margin': 0.15,
        'growth_rate': 0.05,
        'customer_concentration': 'medium',
        'risk_level': 'medium',
        'taxpayer_type': '一般纳税人',
        'credit_code': '91330200MA2KYYYYYY'
    },
    10: {  # 太空科技公司
        'name': '太空科技公司',
        'type': '高成长科技型',
        'gross_margin': 0.45,
        'growth_rate': 0.50,
        'customer_concentration': 'high',
        'risk_level': 'low',
        'taxpayer_type': '一般纳税人',
        'credit_code': '91310115MA2KZZZZZZ'
    },
    11: {  # 环球机械有限公司
        'name': '环球机械有限公司',
        'type': '传统制造型',
        'gross_margin': 0.25,
        'growth_rate': 0.03,
        'customer_concentration': 'high',
        'risk_level': 'medium',
        'taxpayer_type': '一般纳税人',
        'credit_code': '91330100MA2KWWWWWW'
    }
}


def generate_shareholders(cursor):
    """生成股东数据"""
    print("生成股东数据...")
    
    shareholders_data = {
        5: [  # ABC有限公司 - 分散股权
            ('ABC控股集团', '法人', 55.0, 110.0, 1),
            ('吴明', '自然人', 25.0, 50.0, 0),
            ('张华投资', '法人', 12.0, 24.0, 0),
            ('员工持股平台', '法人', 8.0, 16.0, 0),
        ],
        8: [  # 123制造厂 - 国有控股
            ('国有资产管理公司', '国有', 60.0, 0.0, 1),
            ('制造业发展基金', '法人', 25.0, 0.0, 0),
            ('管理层持股', '自然人', 15.0, 0.0, 0),
        ],
        10: [  # 太空科技公司 - 创始人控股
            ('TSE控股集团', '法人', 55.0, 110.0, 1),
            ('吴明', '自然人', 30.0, 60.0, 0),
            ('天使投资基金', '法人', 15.0, 30.0, 0),
        ],
        11: [  # 环球机械 - 家族企业
            ('环球控股集团', '法人', 45.0, 360.0, 0),
            ('李环球', '自然人', 25.0, 200.0, 1),
            ('SOE国资', '国有', 30.0, 240.0, 0),
        ]
    }
    
    for company_id, shareholders in shareholders_data.items():
        for name, s_type, ratio, amount, is_controller in shareholders:
            cursor.execute('''
                INSERT INTO shareholders (company_id, shareholder_name, shareholder_type, 
                    share_ratio, share_amount, is_actual_controller)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_id, name, s_type, ratio, amount, is_controller))
    
    print(f"  ✓ 插入 {sum(len(v) for v in shareholders_data.values())} 条股东记录")


def generate_investments(cursor):
    """生成对外投资数据"""
    print("生成对外投资数据...")
    
    investments_data = {
        5: [  # ABC有限公司
            ('ABC科技子公司', 100.0, '控股', 500.0, '2020-03-15', '软件开发'),
            ('华东销售公司', 80.0, '控股', 200.0, '2021-06-20', '贸易'),
            ('供应链金融公司', 30.0, '参股', 100.0, '2022-01-10', '金融服务'),
        ],
        8: [  # 123制造厂
            ('精密零部件厂', 100.0, '控股', 300.0, '2019-08-01', '制造业'),
            ('物流运输公司', 51.0, '控股', 150.0, '2021-03-15', '物流'),
        ],
        10: [  # 太空科技公司
            ('AI研究院', 100.0, '控股', 1000.0, '2022-06-01', '研发'),
            ('云计算子公司', 70.0, '控股', 500.0, '2023-01-15', '云服务'),
            ('数据中心公司', 40.0, '参股', 200.0, '2023-06-01', '数据服务'),
            ('智能硬件公司', 25.0, '参股', 100.0, '2024-01-01', '硬件制造'),
        ],
        11: [  # 环球机械
            ('环球铸造厂', 100.0, '控股', 400.0, '2018-05-01', '制造业'),
            ('机械销售公司', 60.0, '控股', 120.0, '2020-09-15', '贸易'),
        ]
    }
    
    for company_id, investments in investments_data.items():
        for name, ratio, inv_type, amount, date, industry in investments:
            cursor.execute('''
                INSERT INTO investments (company_id, invested_company_name, investment_ratio,
                    investment_type, investment_amount, investment_date, invested_industry)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, name, ratio, inv_type, amount, date, industry))
    
    print(f"  ✓ 插入 {sum(len(v) for v in investments_data.values())} 条对外投资记录")


def generate_risk_info(cursor):
    """生成风险信息数据"""
    print("生成风险信息数据...")
    
    risk_data = {
        5: [],  # ABC有限公司 - 低风险，无风险记录
        8: [  # 123制造厂 - 中等风险
            ('lawsuit', '合同纠纷案', '与供应商的货款纠纷', 50000.0, '2024-03-15', '已结案', '裁判文书网', '(2024)浙01民初1234号'),
            ('penalty', '环保处罚', '废水排放超标', 20000.0, '2023-08-20', '已结案', '信用中国', 'HJ2023-0820'),
        ],
        10: [  # 太空科技公司 - 低风险
            ('lawsuit', '知识产权纠纷', '专利侵权诉讼(原告)', 0.0, '2024-06-01', '进行中', '裁判文书网', '(2024)沪01知民初567号'),
        ],
        11: [  # 环球机械 - 中等风险
            ('lawsuit', '劳动争议', '员工工伤赔偿', 80000.0, '2023-11-10', '已结案', '裁判文书网', '(2023)浙01民终890号'),
            ('execution', '被执行记录', '货款执行', 150000.0, '2022-05-20', '已结案', '执行信息公开网', '(2022)浙01执123号'),
            ('abnormal', '经营异常', '未按期公示年报', 0.0, '2021-07-01', '已解除', '企业信用信息公示系统', None),
        ]
    }
    
    for company_id, risks in risk_data.items():
        for risk_type, title, detail, amount, date, status, source, case_no in risks:
            cursor.execute('''
                INSERT INTO risk_info (company_id, risk_type, risk_title, risk_detail,
                    risk_amount, risk_date, risk_status, risk_source, case_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, risk_type, title, detail, amount, date, status, source, case_no))
    
    total = sum(len(v) for v in risk_data.values())
    print(f"  ✓ 插入 {total} 条风险记录")


def generate_industry_benchmarks(cursor):
    """生成行业基准数据"""
    print("生成行业基准数据...")
    
    # 行业代码: 3011-软件和信息技术服务业, 3511-通用设备制造业
    benchmarks = [
        # 软件行业基准 (3011)
        ('3011', '软件和信息技术服务业', 'gross_margin', 'gross_margin', 0.45, 0.55, 0.35, 2024, '行业研究报告'),
        ('3011', '软件和信息技术服务业', 'net_margin', 'net_margin', 0.15, 0.25, 0.08, 2024, '行业研究报告'),
        ('3011', '软件和信息技术服务业', 'roe', 'roe', 0.12, 0.20, 0.05, 2024, '行业研究报告'),
        ('3011', '软件和信息技术服务业', 'asset_liability_ratio', 'asset_liability_ratio', 0.40, 0.30, 0.55, 2024, '行业研究报告'),
        ('3011', '软件和信息技术服务业', 'revenue_growth', 'revenue_growth', 0.20, 0.35, 0.08, 2024, '行业研究报告'),
        
        # 制造业基准 (3511)
        ('3511', '通用设备制造业', 'gross_margin', 'gross_margin', 0.22, 0.30, 0.15, 2024, '行业研究报告'),
        ('3511', '通用设备制造业', 'net_margin', 'net_margin', 0.06, 0.10, 0.03, 2024, '行业研究报告'),
        ('3511', '通用设备制造业', 'roe', 'roe', 0.08, 0.12, 0.04, 2024, '行业研究报告'),
        ('3511', '通用设备制造业', 'asset_liability_ratio', 'asset_liability_ratio', 0.55, 0.45, 0.65, 2024, '行业研究报告'),
        ('3511', '通用设备制造业', 'revenue_growth', 'revenue_growth', 0.08, 0.15, 0.02, 2024, '行业研究报告'),
        ('3511', '通用设备制造业', 'inventory_turnover', 'inventory_turnover', 4.5, 6.0, 3.0, 2024, '行业研究报告'),
    ]
    
    for code, name, metric, metric_code, avg, top, bottom, year, source in benchmarks:
        cursor.execute('''
            INSERT INTO industry_benchmarks (industry_code, industry_name, metric_name,
                metric_code, avg_value, top_quartile, bottom_quartile, year, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (code, name, metric, metric_code, avg, top, bottom, year, source))
    
    print(f"  ✓ 插入 {len(benchmarks)} 条行业基准记录")


def generate_related_parties(cursor):
    """生成关联方数据"""
    print("生成关联方数据...")
    
    related_data = {
        5: [
            ('ABC控股集团', '股权关联', '控股股东'),
            ('华东销售公司', '股权关联', '子公司'),
            ('吴明个人企业', '管理层关联', '法人代表关联'),
        ],
        8: [
            ('国有资产管理公司', '股权关联', '控股股东'),
            ('精密零部件厂', '股权关联', '子公司'),
        ],
        10: [
            ('TSE控股集团', '股权关联', '控股股东'),
            ('AI研究院', '股权关联', '子公司'),
            ('云计算子公司', '股权关联', '子公司'),
        ],
        11: [
            ('环球控股集团', '股权关联', '控股股东'),
            ('环球铸造厂', '股权关联', '子公司'),
            ('李环球家族企业', '亲属关联', '实控人关联企业'),
        ]
    }
    
    for company_id, parties in related_data.items():
        for name, rel_type, detail in parties:
            cursor.execute('''
                INSERT INTO related_parties (company_id, related_company_name, 
                    relation_type, relation_detail)
                VALUES (?, ?, ?, ?)
            ''', (company_id, name, rel_type, detail))
    
    print(f"  ✓ 插入 {sum(len(v) for v in related_data.values())} 条关联方记录")


def generate_related_transactions(cursor):
    """生成关联交易数据"""
    print("生成关联交易数据...")
    
    transactions = []
    
    for company_id in [5, 8, 10, 11]:
        for year in [2023, 2024, 2025]:
            # 销售给关联方
            sales_amount = random.uniform(100000, 500000)
            transactions.append((
                company_id, year, f'关联方销售-{company_id}', 'sales',
                sales_amount, sales_amount * 1.02, 1
            ))
            # 从关联方采购
            purchase_amount = random.uniform(80000, 400000)
            transactions.append((
                company_id, year, f'关联方采购-{company_id}', 'purchase',
                purchase_amount, purchase_amount * 0.98, 1
            ))
    
    for t in transactions:
        cursor.execute('''
            INSERT INTO related_transactions (company_id, period_year, related_party_name,
                transaction_type, transaction_amount, market_price_amount, is_fair_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', t)
    
    print(f"  ✓ 插入 {len(transactions)} 条关联交易记录")


def update_company_info(cursor):
    """更新公司基本信息"""
    print("更新公司基本信息...")
    
    for company_id, profile in COMPANY_PROFILES.items():
        cursor.execute('''
            UPDATE companies 
            SET credit_code = ?, taxpayer_type = ?
            WHERE id = ?
        ''', (profile['credit_code'], profile['taxpayer_type'], company_id))
    
    print(f"  ✓ 更新 {len(COMPANY_PROFILES)} 家公司信息")


def generate_customer_analysis(cursor):
    """从发票数据生成客户分析汇总"""
    print("生成客户分析数据...")
    
    # 先清空现有数据
    cursor.execute("DELETE FROM customer_analysis")
    
    # 从发票表聚合客户数据 (OUTPUT = 销售发票，buyer_name = 客户)
    cursor.execute('''
        INSERT INTO customer_analysis (company_id, period_year, customer_name, customer_tax_id,
            total_sales, invoice_count, first_deal_date, last_deal_date)
        SELECT 
            company_id,
            period_year,
            buyer_name,
            buyer_tax_id,
            SUM(amount_excluding_tax) as total_sales,
            COUNT(*) as invoice_count,
            MIN(issue_date) as first_deal_date,
            MAX(issue_date) as last_deal_date
        FROM invoices
        WHERE invoice_type = 'OUTPUT' AND buyer_name IS NOT NULL AND buyer_name != ''
        GROUP BY company_id, period_year, buyer_name, buyer_tax_id
    ''')
    
    count = cursor.rowcount
    print(f"  ✓ 生成 {count} 条客户分析记录")


def generate_supplier_analysis(cursor):
    """从发票数据生成供应商分析汇总"""
    print("生成供应商分析数据...")
    
    # 先清空现有数据
    cursor.execute("DELETE FROM supplier_analysis")
    
    # 从发票表聚合供应商数据 (INPUT = 采购发票，seller_name = 供应商)
    cursor.execute('''
        INSERT INTO supplier_analysis (company_id, period_year, supplier_name, supplier_tax_id,
            total_purchase, invoice_count, first_deal_date, last_deal_date)
        SELECT 
            company_id,
            period_year,
            seller_name,
            seller_tax_id,
            SUM(amount_excluding_tax) as total_purchase,
            COUNT(*) as invoice_count,
            MIN(issue_date) as first_deal_date,
            MAX(issue_date) as last_deal_date
        FROM invoices
        WHERE invoice_type = 'INPUT' AND seller_name IS NOT NULL AND seller_name != ''
        GROUP BY company_id, period_year, seller_name, seller_tax_id
    ''')
    
    count = cursor.rowcount
    print(f"  ✓ 生成 {count} 条供应商分析记录")


def main():
    """主函数"""
    print("=" * 50)
    print("企业画像示例数据生成脚本")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 清空已有数据（如果有）
        print("\n清理旧数据...")
        tables = ['shareholders', 'investments', 'risk_info', 'industry_benchmarks',
                  'related_parties', 'related_transactions']
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  - 清空表: {table}")
        
        print("\n生成新数据...")
        update_company_info(cursor)
        generate_shareholders(cursor)
        generate_investments(cursor)
        generate_risk_info(cursor)
        generate_industry_benchmarks(cursor)
        generate_related_parties(cursor)
        generate_related_transactions(cursor)
        generate_customer_analysis(cursor)
        generate_supplier_analysis(cursor)
        
        conn.commit()
        print("\n" + "=" * 50)
        print("✅ 示例数据生成完成!")
        print("=" * 50)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 错误: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
