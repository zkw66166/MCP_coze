"""
企业画像数据库迁移脚本 V2
添加完整的14模块指标支持表结构

新增/修改:
- companies表: 6个新字段
- 10个新表支持各模块指标
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'financial.db')


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_companies_fields(conn):
    """为companies表添加新字段"""
    cursor = conn.cursor()
    
    # 检查现有列
    cursor.execute("PRAGMA table_info(companies)")
    existing_cols = {row['name'] for row in cursor.fetchall()}
    
    new_fields = [
        ("industry_code", "TEXT"),           # 行业代码
        ("industry_chain_position", "TEXT"), # 产业链位置
        ("taxpayer_qualification", "TEXT"),  # 纳税人资格
        ("collection_method", "TEXT"),       # 征收方式
        ("tax_credit_rating", "TEXT"),       # 纳税信用等级
        ("operating_status", "TEXT"),        # 经营状态
    ]
    
    added = []
    for field_name, field_type in new_fields:
        if field_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE companies ADD COLUMN {field_name} {field_type}")
                added.append(field_name)
            except sqlite3.OperationalError as e:
                print(f"  跳过 {field_name}: {e}")
    
    if added:
        print(f"  ✓ companies表新增字段: {', '.join(added)}")
    else:
        print("  ✓ companies表字段已存在")
    
    return len(added)


def create_certifications_table(conn):
    """创建资质认证表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            cert_type TEXT NOT NULL,
            cert_name TEXT NOT NULL,
            cert_level TEXT,
            issue_date TEXT,
            expire_date TEXT,
            status TEXT DEFAULT '有效',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_certifications_company 
        ON company_certifications(company_id)
    ''')
    print("  ✓ company_certifications 表已创建")


def create_employee_structure_table(conn):
    """创建人员结构表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            total_employees INTEGER,
            rd_employees INTEGER,
            sales_employees INTEGER,
            admin_employees INTEGER,
            other_employees INTEGER,
            master_above INTEGER,
            bachelor INTEGER,
            below_bachelor INTEGER,
            total_salary REAL,
            avg_salary REAL,
            social_insurance_coverage REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_employee_structure_company_year 
        ON employee_structure(company_id, period_year)
    ''')
    print("  ✓ employee_structure 表已创建")


def create_rd_innovation_table(conn):
    """创建研发创新表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rd_innovation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            rd_investment REAL,
            rd_investment_ratio REAL,
            patent_total INTEGER,
            patent_invention INTEGER,
            patent_utility INTEGER,
            patent_design INTEGER,
            software_copyright INTEGER,
            new_patents_year INTEGER,
            high_tech_product_ratio REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_rd_innovation_company_year 
        ON rd_innovation(company_id, period_year)
    ''')
    print("  ✓ rd_innovation 表已创建")


def create_cross_border_table(conn):
    """创建跨境业务表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cross_border_business (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            overseas_revenue REAL,
            overseas_revenue_ratio REAL,
            export_sales REAL,
            import_purchase REAL,
            applicable_treaty TEXT,
            overseas_tax_paid REAL,
            overseas_tax_credit REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cross_border_company_year 
        ON cross_border_business(company_id, period_year)
    ''')
    print("  ✓ cross_border_business 表已创建")


def create_bank_relations_table(conn):
    """创建银行关系表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            bank_count INTEGER,
            total_credit_line REAL,
            loan_balance REAL,
            weighted_avg_rate REAL,
            pboc_credit_rating TEXT,
            customs_credit_rating TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bank_relations_company_year 
        ON bank_relations(company_id, period_year)
    ''')
    print("  ✓ bank_relations 表已创建")


def create_compliance_summary_table(conn):
    """创建合规评估汇总表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            -- 税务合规
            tax_filing_rate REAL,
            tax_payment_rate REAL,
            tax_audit_count INTEGER,
            tax_audit_amount REAL,
            tax_penalty_count INTEGER,
            tax_penalty_amount REAL,
            tax_risk_level TEXT,
            -- 财务合规
            audit_opinion TEXT,
            internal_control_defects INTEGER,
            accounting_standard TEXT,
            -- 经营合规
            env_penalty_count INTEGER,
            safety_incident_count INTEGER,
            quality_penalty_count INTEGER,
            -- 风险评估
            liquidity_risk_level TEXT,
            customer_concentration_risk TEXT,
            supplier_dependency_risk TEXT,
            overall_risk_rating TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_compliance_summary_company_year 
        ON compliance_summary(company_id, period_year)
    ''')
    print("  ✓ compliance_summary 表已创建")


def create_digital_capability_table(conn):
    """创建数字化能力表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_capability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            erp_coverage REAL,
            finance_system_coverage REAL,
            tax_system_coverage REAL,
            finance_data_quality TEXT,
            tax_data_quality TEXT,
            system_integration TEXT,
            data_completeness REAL,
            process_automation REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_digital_capability_company_year 
        ON digital_capability(company_id, period_year)
    ''')
    print("  ✓ digital_capability 表已创建")


def create_esg_indicators_table(conn):
    """创建ESG指标表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            env_investment_ratio REAL,
            energy_saving_investment REAL,
            charity_donation REAL,
            disability_employment_ratio REAL,
            info_disclosure_level TEXT,
            related_party_review TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            UNIQUE(company_id, period_year)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_esg_indicators_company_year 
        ON esg_indicators(company_id, period_year)
    ''')
    print("  ✓ esg_indicators 表已创建")


def create_policy_eligibility_table(conn):
    """创建政策匹配表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policy_eligibility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            policy_name TEXT NOT NULL,
            eligibility_status TEXT,
            eligibility_detail TEXT,
            benefit_amount REAL,
            expire_date TEXT,
            alert_level TEXT,
            missing_conditions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_policy_eligibility_company_year 
        ON policy_eligibility(company_id, period_year)
    ''')
    print("  ✓ policy_eligibility 表已创建")


def create_special_business_table(conn):
    """创建特殊业务表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS special_business (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            business_type TEXT NOT NULL,
            business_revenue REAL,
            revenue_ratio REAL,
            value_added_rate REAL,
            tax_refund_amount REAL,
            cert_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_special_business_company_year 
        ON special_business(company_id, period_year)
    ''')
    print("  ✓ special_business 表已创建")


def run_migration():
    """执行全部迁移"""
    print("\n" + "="*60)
    print("企业画像数据库迁移 V2")
    print("="*60)
    
    conn = get_connection()
    
    try:
        print("\n[1/11] 更新 companies 表字段...")
        add_companies_fields(conn)
        
        print("\n[2/11] 创建 company_certifications 表...")
        create_certifications_table(conn)
        
        print("\n[3/11] 创建 employee_structure 表...")
        create_employee_structure_table(conn)
        
        print("\n[4/11] 创建 rd_innovation 表...")
        create_rd_innovation_table(conn)
        
        print("\n[5/11] 创建 cross_border_business 表...")
        create_cross_border_table(conn)
        
        print("\n[6/11] 创建 bank_relations 表...")
        create_bank_relations_table(conn)
        
        print("\n[7/11] 创建 compliance_summary 表...")
        create_compliance_summary_table(conn)
        
        print("\n[8/11] 创建 digital_capability 表...")
        create_digital_capability_table(conn)
        
        print("\n[9/11] 创建 esg_indicators 表...")
        create_esg_indicators_table(conn)
        
        print("\n[10/11] 创建 policy_eligibility 表...")
        create_policy_eligibility_table(conn)
        
        print("\n[11/11] 创建 special_business 表...")
        create_special_business_table(conn)
        
        conn.commit()
        print("\n" + "="*60)
        print("✓ 数据库迁移完成!")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ 迁移失败: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
