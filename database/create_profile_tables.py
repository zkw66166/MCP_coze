"""
企业画像数据库表创建脚本
创建企业画像功能所需的所有新表和字段
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'financial.db')

def create_profile_tables():
    """创建企业画像相关表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 结构化股东表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shareholders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            shareholder_name TEXT NOT NULL,
            shareholder_type TEXT,  -- '自然人'/'法人'/'国有'
            share_ratio REAL,       -- 持股比例 (0-100)
            share_amount REAL,      -- 出资金额(万元)
            is_actual_controller INTEGER DEFAULT 0,  -- 是否实际控制人
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: shareholders (股东信息)")
    
    # 2. 对外投资表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            invested_company_name TEXT NOT NULL,
            investment_ratio REAL,    -- 投资比例 (0-100)
            investment_type TEXT,     -- '控股'/'参股'
            investment_amount REAL,   -- 投资金额(万元)
            investment_date TEXT,     -- 投资日期
            invested_industry TEXT,   -- 被投资企业行业
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: investments (对外投资)")
    
    # 3. 风险信息表 (支持外部数据导入)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            risk_type TEXT NOT NULL,  -- 'lawsuit'诉讼/'execution'被执行/'dishonest'失信/
                                      -- 'penalty'行政处罚/'tax_violation'税务违法/
                                      -- 'overdue_tax'欠税/'equity_freeze'股权冻结/'abnormal'经营异常
            risk_title TEXT,          -- 风险标题
            risk_detail TEXT,         -- 风险详情
            risk_amount REAL,         -- 涉及金额
            risk_date TEXT,           -- 发生日期
            risk_status TEXT,         -- 状态: 进行中/已结案/已解除
            risk_source TEXT,         -- 数据来源
            case_number TEXT,         -- 案件编号
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: risk_info (风险信息)")
    
    # 4. 行业基准数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS industry_benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            industry_code TEXT NOT NULL,
            industry_name TEXT,
            metric_name TEXT NOT NULL,  -- 指标名称
            metric_code TEXT,           -- 指标代码
            avg_value REAL,             -- 行业平均值
            top_quartile REAL,          -- 上四分位数(优秀)
            bottom_quartile REAL,       -- 下四分位数(较差)
            year INTEGER,
            data_source TEXT,           -- 数据来源
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 创建表: industry_benchmarks (行业基准)")
    
    # 5. 客户分析汇总表 (从发票数据聚合)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_tax_id TEXT,
            customer_region TEXT,       -- 客户地区
            customer_industry TEXT,     -- 客户行业(可从工商信息补充)
            total_sales REAL,           -- 销售总额
            invoice_count INTEGER,      -- 发票数量
            first_deal_date TEXT,       -- 首次交易日期
            last_deal_date TEXT,        -- 最近交易日期
            is_new INTEGER DEFAULT 0,   -- 是否新客户
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: customer_analysis (客户分析)")
    
    # 6. 供应商分析汇总表 (从发票数据聚合)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            supplier_tax_id TEXT,
            supplier_region TEXT,       -- 供应商地区
            supplier_industry TEXT,     -- 供应商行业
            total_purchase REAL,        -- 采购总额
            invoice_count INTEGER,      -- 发票数量
            first_deal_date TEXT,       -- 首次交易日期
            last_deal_date TEXT,        -- 最近交易日期
            is_new INTEGER DEFAULT 0,   -- 是否新供应商
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: supplier_analysis (供应商分析)")
    
    # 7. 关联方信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            related_company_name TEXT NOT NULL,
            relation_type TEXT,         -- '股权关联'/'管理层关联'/'亲属关联'
            relation_detail TEXT,       -- 关联关系描述
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: related_parties (关联方)")
    
    # 8. 关联交易表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            related_party_name TEXT NOT NULL,
            transaction_type TEXT,      -- 'sales'销售/'purchase'采购
            transaction_amount REAL,    -- 交易金额
            market_price_amount REAL,   -- 市场公允价格
            is_fair_price INTEGER DEFAULT 1,  -- 定价是否公允
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: related_transactions (关联交易)")
    
    # 9. 企业画像评价汇总表 (存储计算后的评价结果)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            period_year INTEGER NOT NULL,
            category TEXT NOT NULL,     -- 评价类别
            metric_name TEXT NOT NULL,  -- 指标名称
            metric_value REAL,          -- 指标值
            evaluation TEXT,            -- 评价: 优秀/领先/稳健/一般/较差/集中/分散等
            evaluation_color TEXT,      -- 评价颜色: green/blue/yellow/red
            industry_rank INTEGER,      -- 行业排名
            percentile REAL,            -- 行业百分位
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    print("✓ 创建表: profile_evaluations (画像评价)")
    
    # 修改 companies 表, 添加新字段
    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN credit_code TEXT")
        print("✓ 添加字段: companies.credit_code (统一社会信用代码)")
    except sqlite3.OperationalError:
        print("- 字段已存在: companies.credit_code")
    
    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN taxpayer_type TEXT DEFAULT '一般纳税人'")
        print("✓ 添加字段: companies.taxpayer_type (纳税人资格)")
    except sqlite3.OperationalError:
        print("- 字段已存在: companies.taxpayer_type")
    
    conn.commit()
    conn.close()
    print("\n✅ 企业画像数据库表创建完成!")


def create_indexes():
    """创建索引提升查询性能"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    indexes = [
        ("idx_shareholders_company", "shareholders", "company_id"),
        ("idx_investments_company", "investments", "company_id"),
        ("idx_risk_info_company", "risk_info", "company_id"),
        ("idx_risk_info_type", "risk_info", "risk_type"),
        ("idx_customer_analysis_company_year", "customer_analysis", "company_id, period_year"),
        ("idx_supplier_analysis_company_year", "supplier_analysis", "company_id, period_year"),
        ("idx_related_parties_company", "related_parties", "company_id"),
        ("idx_related_transactions_company", "related_transactions", "company_id"),
        ("idx_profile_evaluations_company", "profile_evaluations", "company_id, period_year"),
        ("idx_industry_benchmarks_code", "industry_benchmarks", "industry_code, year"),
    ]
    
    for idx_name, table, columns in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns})")
            print(f"✓ 创建索引: {idx_name}")
        except sqlite3.OperationalError as e:
            print(f"- 索引创建跳过: {idx_name} ({e})")
    
    conn.commit()
    conn.close()
    print("\n✅ 索引创建完成!")


if __name__ == "__main__":
    print("=" * 50)
    print("企业画像数据库表创建脚本")
    print("=" * 50)
    create_profile_tables()
    print()
    create_indexes()
