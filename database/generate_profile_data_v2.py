"""
企业画像示例数据生成脚本 V2
为4家企业生成14个模块的差异化示例数据
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'financial.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_companies(conn):
    """获取所有企业"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies ORDER BY id")
    return cursor.fetchall()


def update_companies_fields(conn, companies):
    """更新companies表新增字段"""
    print("\n[1] 更新企业基本字段...")
    cursor = conn.cursor()
    
    company_profiles = {
        'ABC有限公司': {
            'industry_chain_position': '中游',
            'taxpayer_qualification': '一般纳税人',
            'collection_method': '查账征收',
            'tax_credit_rating': 'A',
            'operating_status': '存续'
        },
        '123制造厂': {
            'industry_chain_position': '上游',
            'taxpayer_qualification': '一般纳税人',
            'collection_method': '查账征收',
            'tax_credit_rating': 'B',
            'operating_status': '存续'
        },
        '太空科技公司': {
            'industry_chain_position': '下游',
            'taxpayer_qualification': '一般纳税人',
            'collection_method': '查账征收',
            'tax_credit_rating': 'A',
            'operating_status': '存续'
        },
        '环球机械有限公司': {
            'industry_chain_position': '中游',
            'taxpayer_qualification': '一般纳税人',
            'collection_method': '查账征收',
            'tax_credit_rating': 'B',
            'operating_status': '存续'
        }
    }
    
    for company in companies:
        profile = company_profiles.get(company['name'], company_profiles['ABC有限公司'])
        cursor.execute('''
            UPDATE companies SET 
                industry_chain_position = ?,
                taxpayer_qualification = ?,
                collection_method = ?,
                tax_credit_rating = ?,
                operating_status = ?
            WHERE id = ?
        ''', (
            profile['industry_chain_position'],
            profile['taxpayer_qualification'],
            profile['collection_method'],
            profile['tax_credit_rating'],
            profile['operating_status'],
            company['id']
        ))
    
    print(f"  ✓ 更新 {len(companies)} 家企业基本字段")


def generate_certifications(conn, companies):
    """生成资质认证数据"""
    print("\n[2] 生成资质认证数据...")
    cursor = conn.cursor()
    
    # 清除旧数据
    cursor.execute("DELETE FROM company_certifications")
    
    cert_templates = {
        'ABC有限公司': [
            ('高新技术', '高新技术企业认定', '国家级', '2023-11-15', '2026-11-14', '有效'),
            ('软件企业', '软件企业认定', '国家级', '2024-03-01', '2027-02-28', '有效'),
            ('专精特新', '专精特新企业', '市级', '2023-12-01', '2025-11-30', '有效'),
        ],
        '123制造厂': [
            ('ISO认证', 'ISO9001质量管理', '国际级', '2022-06-15', '2025-06-14', '有效'),
        ],
        '太空科技公司': [
            ('高新技术', '高新技术企业认定', '国家级', '2024-01-10', '2027-01-09', '有效'),
            ('知识产权', '国家知识产权优势企业', '国家级', '2023-08-20', '2026-08-19', '有效'),
            ('专精特新', '专精特新小巨人', '国家级', '2024-02-01', '2027-01-31', '有效'),
        ],
        '环球机械有限公司': [
            ('AEO认证', '海关高级认证企业', '国家级', '2023-05-01', '2026-04-30', '有效'),
            ('ISO认证', 'ISO14001环境管理', '国际级', '2022-09-10', '2025-09-09', '有效'),
        ]
    }
    
    count = 0
    for company in companies:
        certs = cert_templates.get(company['name'], [])
        for cert in certs:
            cursor.execute('''
                INSERT INTO company_certifications 
                (company_id, cert_type, cert_name, cert_level, issue_date, expire_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company['id'], *cert))
            count += 1
    
    print(f"  ✓ 生成 {count} 条资质认证记录")


def generate_employee_structure(conn, companies):
    """生成人员结构数据"""
    print("\n[3] 生成人员结构数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM employee_structure")
    
    profiles = {
        'ABC有限公司': {'total': 156, 'rd_ratio': 0.50, 'master_ratio': 0.22, 'salary_per': 12.1},
        '123制造厂': {'total': 280, 'rd_ratio': 0.15, 'master_ratio': 0.08, 'salary_per': 8.5},
        '太空科技公司': {'total': 85, 'rd_ratio': 0.65, 'master_ratio': 0.35, 'salary_per': 18.5},
        '环球机械有限公司': {'total': 120, 'rd_ratio': 0.12, 'master_ratio': 0.10, 'salary_per': 9.2},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            total = int(p['total'] * (1 + (year - 2022) * 0.05))
            rd = int(total * p['rd_ratio'])
            sales = int(total * 0.18)
            admin = int(total * 0.16)
            other = total - rd - sales - admin
            
            master = int(total * p['master_ratio'])
            bachelor = int(total * 0.50)
            below = total - master - bachelor
            
            total_salary = total * p['salary_per'] * (1 + (year - 2022) * 0.08)
            
            cursor.execute('''
                INSERT OR REPLACE INTO employee_structure 
                (company_id, period_year, total_employees, rd_employees, sales_employees,
                 admin_employees, other_employees, master_above, bachelor, below_bachelor,
                 total_salary, avg_salary, social_insurance_coverage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year, total, rd, sales, admin, other,
                master, bachelor, below, total_salary, p['salary_per'], 100.0
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条人员结构记录")


def generate_rd_innovation(conn, companies):
    """生成研发创新数据"""
    print("\n[4] 生成研发创新数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM rd_innovation")
    
    profiles = {
        'ABC有限公司': {'rd_ratio': 6.5, 'patent': 35, 'invention': 12, 'sw': 25, 'ht_ratio': 78},
        '123制造厂': {'rd_ratio': 2.5, 'patent': 8, 'invention': 2, 'sw': 3, 'ht_ratio': 25},
        '太空科技公司': {'rd_ratio': 12.0, 'patent': 58, 'invention': 28, 'sw': 42, 'ht_ratio': 92},
        '环球机械有限公司': {'rd_ratio': 3.2, 'patent': 12, 'invention': 4, 'sw': 5, 'ht_ratio': 35},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            growth = 1 + (year - 2022) * 0.15
            patent_total = int(p['patent'] * growth)
            patent_inv = int(p['invention'] * growth)
            
            # 假设从income_statements获取营收计算研发投入
            cursor.execute('''
                SELECT SUM(total_revenue) as revenue FROM income_statements
                WHERE company_id = ? AND period_year = ?
            ''', (company['id'], year))
            row = cursor.fetchone()
            revenue = row['revenue'] if row and row['revenue'] else 10000000
            
            rd_investment = revenue * p['rd_ratio'] / 100
            
            cursor.execute('''
                INSERT OR REPLACE INTO rd_innovation
                (company_id, period_year, rd_investment, rd_investment_ratio,
                 patent_total, patent_invention, patent_utility, patent_design,
                 software_copyright, new_patents_year, high_tech_product_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year, rd_investment, p['rd_ratio'],
                patent_total, patent_inv, patent_total - patent_inv - 2, 2,
                int(p['sw'] * growth), int(patent_total * 0.2), p['ht_ratio']
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条研发创新记录")


def generate_cross_border(conn, companies):
    """生成跨境业务数据"""
    print("\n[5] 生成跨境业务数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cross_border_business")
    
    # 只有环球机械有明显跨境业务
    profiles = {
        'ABC有限公司': {'ratio': 0.075, 'treaty': '中美税收协定'},
        '123制造厂': {'ratio': 0.02, 'treaty': None},
        '太空科技公司': {'ratio': 0.05, 'treaty': '中英税收协定'},
        '环球机械有限公司': {'ratio': 0.25, 'treaty': '中德税收协定'},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            cursor.execute('''
                SELECT SUM(total_revenue) as revenue FROM income_statements
                WHERE company_id = ? AND period_year = ?
            ''', (company['id'], year))
            row = cursor.fetchone()
            revenue = row['revenue'] if row and row['revenue'] else 10000000
            
            overseas = revenue * p['ratio']
            tax_paid = overseas * 0.05 if p['treaty'] else 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO cross_border_business
                (company_id, period_year, overseas_revenue, overseas_revenue_ratio,
                 export_sales, import_purchase, applicable_treaty,
                 overseas_tax_paid, overseas_tax_credit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year, overseas, p['ratio'] * 100,
                overseas, overseas * 0.3, p['treaty'],
                tax_paid, tax_paid
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条跨境业务记录")


def generate_bank_relations(conn, companies):
    """生成银行关系数据"""
    print("\n[6] 生成银行关系数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM bank_relations")
    
    profiles = {
        'ABC有限公司': {'banks': 5, 'credit': 2500, 'rate': 4.85, 'pboc': 'AA', 'customs': '一般信用'},
        '123制造厂': {'banks': 3, 'credit': 1500, 'rate': 5.20, 'pboc': 'A', 'customs': '一般信用'},
        '太空科技公司': {'banks': 4, 'credit': 3000, 'rate': 4.50, 'pboc': 'AAA', 'customs': None},
        '环球机械有限公司': {'banks': 6, 'credit': 2000, 'rate': 5.00, 'pboc': 'A', 'customs': '高级认证'},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            loan_balance = p['credit'] * 0.52 * (1 + (year - 2022) * 0.1)
            
            cursor.execute('''
                INSERT OR REPLACE INTO bank_relations
                (company_id, period_year, bank_count, total_credit_line,
                 loan_balance, weighted_avg_rate, pboc_credit_rating, customs_credit_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year, p['banks'], p['credit'] * 10000,
                loan_balance * 10000, p['rate'], p['pboc'], p['customs']
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条银行关系记录")


def generate_compliance_summary(conn, companies):
    """生成合规评估汇总数据"""
    print("\n[7] 生成合规评估数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM compliance_summary")
    
    profiles = {
        'ABC有限公司': {
            'tax_filing': 100, 'tax_payment': 100, 'audit_count': 0, 'audit_amount': 0,
            'penalty_count': 0, 'penalty_amount': 0, 'tax_risk': '低',
            'audit_opinion': '标准无保留意见', 'control_defects': 0, 'accounting': '优',
            'env_penalty': 0, 'safety_incident': 0, 'quality_penalty': 0,
            'liquidity_risk': '低', 'customer_risk': '低', 'supplier_risk': '中', 'overall': 'B'
        },
        '123制造厂': {
            'tax_filing': 98, 'tax_payment': 95, 'audit_count': 1, 'audit_amount': 5000,
            'penalty_count': 0, 'penalty_amount': 0, 'tax_risk': '中',
            'audit_opinion': '标准无保留意见', 'control_defects': 1, 'accounting': '良',
            'env_penalty': 1, 'safety_incident': 0, 'quality_penalty': 0,
            'liquidity_risk': '中', 'customer_risk': '中', 'supplier_risk': '中', 'overall': 'C'
        },
        '太空科技公司': {
            'tax_filing': 100, 'tax_payment': 100, 'audit_count': 0, 'audit_amount': 0,
            'penalty_count': 0, 'penalty_amount': 0, 'tax_risk': '低',
            'audit_opinion': '标准无保留意见', 'control_defects': 0, 'accounting': '优',
            'env_penalty': 0, 'safety_incident': 0, 'quality_penalty': 0,
            'liquidity_risk': '低', 'customer_risk': '中', 'supplier_risk': '低', 'overall': 'A'
        },
        '环球机械有限公司': {
            'tax_filing': 100, 'tax_payment': 98, 'audit_count': 0, 'audit_amount': 0,
            'penalty_count': 0, 'penalty_amount': 0, 'tax_risk': '低',
            'audit_opinion': '标准无保留意见', 'control_defects': 0, 'accounting': '良',
            'env_penalty': 0, 'safety_incident': 0, 'quality_penalty': 0,
            'liquidity_risk': '中', 'customer_risk': '高', 'supplier_risk': '高', 'overall': 'C'
        },
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            cursor.execute('''
                INSERT OR REPLACE INTO compliance_summary
                (company_id, period_year, tax_filing_rate, tax_payment_rate,
                 tax_audit_count, tax_audit_amount, tax_penalty_count, tax_penalty_amount,
                 tax_risk_level, audit_opinion, internal_control_defects, accounting_standard,
                 env_penalty_count, safety_incident_count, quality_penalty_count,
                 liquidity_risk_level, customer_concentration_risk, supplier_dependency_risk,
                 overall_risk_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year,
                p['tax_filing'], p['tax_payment'], p['audit_count'], p['audit_amount'],
                p['penalty_count'], p['penalty_amount'], p['tax_risk'],
                p['audit_opinion'], p['control_defects'], p['accounting'],
                p['env_penalty'], p['safety_incident'], p['quality_penalty'],
                p['liquidity_risk'], p['customer_risk'], p['supplier_risk'], p['overall']
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条合规评估记录")


def generate_digital_capability(conn, companies):
    """生成数字化能力数据"""
    print("\n[8] 生成数字化能力数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM digital_capability")
    
    profiles = {
        'ABC有限公司': {'erp': 95, 'fin': 100, 'tax': 100, 'fin_q': '优', 'tax_q': '优', 'integ': '高', 'complete': 96, 'auto': 78},
        '123制造厂': {'erp': 75, 'fin': 90, 'tax': 95, 'fin_q': '良', 'tax_q': '良', 'integ': '中', 'complete': 82, 'auto': 55},
        '太空科技公司': {'erp': 98, 'fin': 100, 'tax': 100, 'fin_q': '优', 'tax_q': '优', 'integ': '高', 'complete': 98, 'auto': 92},
        '环球机械有限公司': {'erp': 85, 'fin': 95, 'tax': 100, 'fin_q': '良', 'tax_q': '优', 'integ': '中', 'complete': 88, 'auto': 65},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            cursor.execute('''
                INSERT OR REPLACE INTO digital_capability
                (company_id, period_year, erp_coverage, finance_system_coverage,
                 tax_system_coverage, finance_data_quality, tax_data_quality,
                 system_integration, data_completeness, process_automation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year,
                p['erp'], p['fin'], p['tax'], p['fin_q'], p['tax_q'],
                p['integ'], p['complete'], p['auto']
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条数字化能力记录")


def generate_esg_indicators(conn, companies):
    """生成ESG指标数据"""
    print("\n[9] 生成ESG指标数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM esg_indicators")
    
    profiles = {
        'ABC有限公司': {'env': 1.2, 'energy': 45, 'charity': 15, 'disability': 1.8, 'disclosure': '高', 'review': '高'},
        '123制造厂': {'env': 2.5, 'energy': 120, 'charity': 8, 'disability': 2.0, 'disclosure': '中', 'review': '中'},
        '太空科技公司': {'env': 0.8, 'energy': 25, 'charity': 30, 'disability': 1.5, 'disclosure': '高', 'review': '高'},
        '环球机械有限公司': {'env': 1.8, 'energy': 85, 'charity': 10, 'disability': 1.6, 'disclosure': '中', 'review': '高'},
    }
    
    count = 0
    for company in companies:
        p = profiles.get(company['name'], profiles['ABC有限公司'])
        for year in [2022, 2023, 2024]:
            cursor.execute('''
                INSERT OR REPLACE INTO esg_indicators
                (company_id, period_year, env_investment_ratio, energy_saving_investment,
                 charity_donation, disability_employment_ratio,
                 info_disclosure_level, related_party_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company['id'], year,
                p['env'], p['energy'] * 10000, p['charity'] * 10000, p['disability'],
                p['disclosure'], p['review']
            ))
            count += 1
    
    print(f"  ✓ 生成 {count} 条ESG指标记录")


def generate_policy_eligibility(conn, companies):
    """生成政策匹配数据"""
    print("\n[10] 生成政策匹配数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM policy_eligibility")
    
    policies_template = {
        'ABC有限公司': [
            ('高新技术企业15%税率', '符合', '研发占比6.5%，高新产品78%', 365000, '2026-11-14', '中', '需提前6个月准备复审'),
            ('软件产品增值税即征即退', '享受中', '软件产品增值率35%', 900000, '2027-02-28', None, None),
            ('研发费用加计扣除200%', '享受中', '符合科技型中小企业条件', 4960000, None, None, None),
        ],
        '123制造厂': [
            ('小微企业所得税优惠', '不符合', '资产总额超标', 0, None, None, '资产总额超过5000万'),
            ('研发费用加计扣除100%', '享受中', '符合基本条件', 500000, None, None, None),
        ],
        '太空科技公司': [
            ('高新技术企业15%税率', '符合', '研发占比12%，专利58项', 580000, '2027-01-09', None, None),
            ('专精特新小巨人扶持', '享受中', '国家级认定', 500000, '2027-01-31', None, None),
            ('研发费用加计扣除200%', '享受中', '符合科技型中小企业', 8500000, None, None, None),
        ],
        '环球机械有限公司': [
            ('AEO高级认证优惠', '享受中', '通关便利化', 200000, '2026-04-30', None, None),
            ('研发费用加计扣除100%', '享受中', '符合基本条件', 800000, None, None, None),
        ],
    }
    
    count = 0
    for company in companies:
        policies = policies_template.get(company['name'], [])
        for year in [2024]:  # 政策匹配通常只需当年
            for policy in policies:
                cursor.execute('''
                    INSERT INTO policy_eligibility
                    (company_id, period_year, policy_name, eligibility_status,
                     eligibility_detail, benefit_amount, expire_date,
                     alert_level, missing_conditions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (company['id'], year, *policy))
                count += 1
    
    print(f"  ✓ 生成 {count} 条政策匹配记录")


def generate_special_business(conn, companies):
    """生成特殊业务数据"""
    print("\n[11] 生成特殊业务数据...")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM special_business")
    
    business_template = {
        'ABC有限公司': [
            ('软件', 22800000, 60, 35, 900000, '双软企业'),
            ('技术服务', 15200000, 40, 45, 0, None),
        ],
        '123制造厂': [
            ('制造', 45000000, 90, 15, 0, None),
            ('加工', 5000000, 10, 12, 0, None),
        ],
        '太空科技公司': [
            ('软件', 35000000, 70, 42, 1500000, '双软企业'),
            ('航天服务', 15000000, 30, 55, 0, '航天资质'),
        ],
        '环球机械有限公司': [
            ('机械制造', 28000000, 70, 18, 0, None),
            ('出口贸易', 12000000, 30, 12, 0, 'AEO认证'),
        ],
    }
    
    count = 0
    for company in companies:
        businesses = business_template.get(company['name'], [])
        for year in [2022, 2023, 2024]:
            for biz in businesses:
                growth = 1 + (year - 2022) * 0.15
                cursor.execute('''
                    INSERT INTO special_business
                    (company_id, period_year, business_type, business_revenue,
                     revenue_ratio, value_added_rate, tax_refund_amount, cert_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    company['id'], year, biz[0], biz[1] * growth,
                    biz[2], biz[3], biz[4] * growth, biz[5]
                ))
                count += 1
    
    print(f"  ✓ 生成 {count} 条特殊业务记录")


def run_generation():
    """执行数据生成"""
    print("\n" + "="*60)
    print("企业画像示例数据生成 V2")
    print("="*60)
    
    conn = get_connection()
    
    try:
        companies = get_companies(conn)
        print(f"\n找到 {len(companies)} 家企业:")
        for c in companies:
            print(f"  - {c['name']} (ID: {c['id']})")
        
        update_companies_fields(conn, companies)
        generate_certifications(conn, companies)
        generate_employee_structure(conn, companies)
        generate_rd_innovation(conn, companies)
        generate_cross_border(conn, companies)
        generate_bank_relations(conn, companies)
        generate_compliance_summary(conn, companies)
        generate_digital_capability(conn, companies)
        generate_esg_indicators(conn, companies)
        generate_policy_eligibility(conn, companies)
        generate_special_business(conn, companies)
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✓ 示例数据生成完成!")
        print("="*60)
        
        # 统计
        print("\n数据统计:")
        tables = [
            'company_certifications', 'employee_structure', 'rd_innovation',
            'cross_border_business', 'bank_relations', 'compliance_summary',
            'digital_capability', 'esg_indicators', 'policy_eligibility', 'special_business'
        ]
        cursor = conn.cursor()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_generation()
