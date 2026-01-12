#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扩展financial.db数据库
- 创建financial_metrics表(预计算指标)
- 创建company_aliases表(企业别名)
- 初始化企业别名数据
"""

import sqlite3
from datetime import datetime

DB_PATH = 'database/financial.db'

def create_tables():
    """创建新表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 创建预计算财务指标表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        period_year INTEGER NOT NULL,
        period_quarter INTEGER,
        period_month INTEGER,
        
        -- 盈利能力指标
        operating_profit_margin REAL,    -- 营业利润率(%)
        net_profit_margin REAL,          -- 净利率(%)
        gross_profit_margin REAL,        -- 毛利率(%)
        roa REAL,                        -- 总资产收益率(%)
        roe REAL,                        -- 净资产收益率(%)
        
        -- 偿债能力指标
        asset_liability_ratio REAL,      -- 资产负债率(%)
        current_ratio REAL,              -- 流动比率
        quick_ratio REAL,                -- 速动比率
        interest_coverage_ratio REAL,    -- 利息保障倍数
        
        -- 运营效率指标
        total_asset_turnover REAL,       -- 总资产周转率(次/年)
        inventory_turnover REAL,         -- 存货周转率(次/年)
        inventory_turnover_days REAL,    -- 存货周转天数
        receivable_turnover REAL,        -- 应收账款周转率(次/年)
        receivable_turnover_days REAL,   -- 应收账款周转天数
        payable_turnover REAL,           -- 应付账款周转率(次/年)
        payable_turnover_days REAL,      -- 应付账款周转天数
        cash_cycle REAL,                 -- 现金周期(天)
        
        -- 成长能力指标
        revenue_growth_rate REAL,        -- 营收增长率(%)
        profit_growth_rate REAL,         -- 净利润增长率(%)
        asset_growth_rate REAL,          -- 总资产增长率(%)
        
        -- 成本费用指标
        selling_expense_ratio REAL,      -- 销售费用率(%)
        admin_expense_ratio REAL,        -- 管理费用率(%)
        period_expense_ratio REAL,       -- 期间费用率(%)
        
        -- 税务指标
        vat_burden_rate REAL,            -- 增值税税负率(%)
        income_tax_burden_rate REAL,     -- 所得税税负率(%)
        total_tax_burden_rate REAL,      -- 综合税负率(%)
        
        -- 元数据
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (company_id) REFERENCES companies(id),
        UNIQUE(company_id, period_year, period_quarter, period_month)
    )
    ''')
    
    # 2. 创建企业别名表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS company_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        alias TEXT NOT NULL,
        alias_type TEXT DEFAULT 'short_name',  -- short_name/former_name/pinyin/custom
        is_primary INTEGER DEFAULT 0,           -- 是否主要别名
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (company_id) REFERENCES companies(id),
        UNIQUE(alias)
    )
    ''')
    
    # 3. 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_company ON financial_metrics(company_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_period ON financial_metrics(period_year, period_quarter)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aliases_alias ON company_aliases(alias)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aliases_company ON company_aliases(company_id)')
    
    conn.commit()
    print("✅ 表创建成功: financial_metrics, company_aliases")
    
    conn.close()

def init_company_aliases():
    """初始化企业别名数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有企业
    cursor.execute('SELECT id, name FROM companies')
    companies = cursor.fetchall()
    
    for company_id, name in companies:
        aliases = []
        
        # 生成别名
        # 1. 去掉"有限公司"后缀
        short1 = name.replace('有限公司', '').replace('有限责任公司', '').strip()
        if short1 and short1 != name:
            aliases.append((short1, 'short_name'))
        
        # 2. 去掉"公司"后缀
        short2 = name.replace('公司', '').strip()
        if short2 and short2 != name and short2 != short1:
            aliases.append((short2, 'short_name'))
        
        # 3. 去掉地区前缀(如果有)
        # 4. 提取核心名称(如ABC、123)
        core_names = []
        if 'ABC' in name:
            core_names.extend(['ABC', 'ABC公司'])
        if '123' in name:
            core_names.extend(['123', '123制造'])
        
        for core in core_names:
            aliases.append((core, 'short_name'))
        
        # 插入别名
        for alias, alias_type in aliases:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO company_aliases (company_id, alias, alias_type)
                    VALUES (?, ?, ?)
                ''', (company_id, alias, alias_type))
            except Exception as e:
                print(f"  跳过别名 '{alias}': {e}")
    
    conn.commit()
    
    # 显示结果
    cursor.execute('SELECT c.name, a.alias FROM company_aliases a JOIN companies c ON a.company_id = c.id')
    results = cursor.fetchall()
    print(f"\n✅ 企业别名初始化完成,共 {len(results)} 条:")
    for name, alias in results:
        print(f"  {name} → {alias}")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("扩展financial.db数据库")
    print("=" * 60)
    
    create_tables()
    init_company_aliases()
    
    print("\n✅ 数据库扩展完成!")
