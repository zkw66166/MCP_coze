import sqlite3
import datetime

DB_PATH = 'database/financial.db'

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting schema update for tax_returns_income...")

    # 1. Rename existing table to backup
    try:
        cursor.execute("ALTER TABLE tax_returns_income RENAME TO tax_returns_income_backup_v2")
        print("Renamed existing table to tax_returns_income_backup_v2")
    except sqlite3.OperationalError:
        print("Table tax_returns_income might not exist, skipping rename.")

    # 2. Create new table
    print("Creating new tax_returns_income table...")
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tax_returns_income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        period_year INTEGER,
        filing_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        -- Rows 1-22
        revenue REAL, -- 1. 营业收入
        cost REAL, -- 2. 营业成本
        taxes_and_surcharges REAL, -- 3. 税金及附加
        selling_expenses REAL, -- 4. 销售费用
        administrative_expenses REAL, -- 5. 管理费用
        research_expenses REAL, -- 6. 研发费用
        financial_expenses REAL, -- 7. 财务费用
        other_income REAL, -- 8. 其他收益
        investment_income REAL, -- 9. 投资收益
        hedge_income REAL, -- 10. 净敞口套期收益
        fair_value_change_income REAL, -- 11. 公允价值变动收益
        credit_impairment_loss REAL, -- 12. 信用减值损失
        asset_impairment_loss REAL, -- 13. 资产减值损失
        asset_disposal_income REAL, -- 14. 资产处置收益
        operating_profit REAL, -- 15. 营业利润
        non_operating_revenue REAL, -- 16. 营业外收入
        non_operating_expense REAL, -- 17. 营业外支出
        total_profit REAL, -- 18. 利润总额
        overseas_income REAL, -- 19. 境外所得
        tax_adjustment_increase REAL, -- 20. 纳税调整增加额
        tax_adjustment_decrease REAL, -- 21. 纳税调整减少额
        tax_incentive_deduction REAL, -- 22. 免税、减计收入及加计扣除
        
        -- Rows 22.1, 22.2
        tax_incentive_deduction_item_1 REAL, -- 22.1 (免税、减计收入及加计扣除-优惠事项1)
        tax_incentive_deduction_item_2 REAL, -- 22.2 (免税、减计收入及加计扣除-优惠事项2)
        
        -- Rows 23-31
        overseas_income_offset_loss REAL, -- 23. 境外应税所得抵减境内亏损
        adjusted_taxable_income REAL, -- 24. 纳税调整后所得
        income_reduction REAL, -- 25. 所得减免
        loss_carryforward REAL, -- 26. 弥补以前年度亏损
        deductible_taxable_income REAL, -- 27. 抵扣应纳税所得额
        taxable_income REAL, -- 28. 应纳税所得额
        tax_rate REAL, -- 29. 税率
        nominal_tax REAL, -- 30. 应纳所得税额
        tax_reduction REAL, -- 31. 减免所得税额
        
        -- Rows 31.1, 31.2
        tax_reduction_item_1 REAL, -- 31.1 (减免所得税额-优惠事项1)
        tax_reduction_item_2 REAL, -- 31.2 (减免所得税额-优惠事项2)
        
        -- Rows 32-49
        tax_credit REAL, -- 32. 抵免所得税额
        tax_payable REAL, -- 33. 应纳税额
        overseas_tax_payable REAL, -- 34. 境外所得应纳所得税额
        overseas_tax_credit REAL, -- 35. 境外所得抵免所得税额
        actual_tax_payable REAL, -- 36. 实际应纳所得税额
        prepaid_tax REAL, -- 37. 本年累计预缴所得税额
        annual_tax_payable REAL, -- 38. 本年应补（退）所得税额
        
        head_office_allocated_tax_payable REAL, -- 39. 总机构分摊本年应补（退）所得税额
        finance_centralized_allocated_tax_payable REAL, -- 40. 财政集中分配本年应补（退）所得税额
        head_office_prod_dept_allocated_tax_payable REAL, -- 41. 总机构主体生产经营部门分摊本年应补（退）所得税额
        ethnic_region_local_share_reduction REAL, -- 42. 民族自治地区企业所得税地方分享部分
        inspection_supplementary_tax REAL, -- 43. 稽查查补（退）所得税额
        special_tax_adjustment_supplementary_tax REAL, -- 44. 特别纳税调整补（退）所得税额
        final_actual_tax_payable REAL -- 45. 本年实际应补（退）所得税额
    )
    """
    cursor.execute(create_table_sql)

    # 3. Create Indexes
    print("Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tax_returns_income_company_period ON tax_returns_income(company_id, period_year)")
    
    # 4. Migrate data (Attempt to copy matching columns)
    # We explicitly map old columns to new ones if they exist
    print("Migrating data from backup...")
    try:
        # Get columns of backup table
        cursor.execute("PRAGMA table_info(tax_returns_income_backup_v2)")
        backup_columns = [row[1] for row in cursor.fetchall()]
        
        # Define mapping: New Column -> Old Column (only where they match exactly or logic implies)
        # Old table columns:
        # revenue, cost, taxes_and_surcharges, selling_expenses, administrative_expenses, financial_expenses,
        # operating_profit, total_profit, taxable_income, tax_rate, nominal_tax, tax_reduction, tax_payable, final_tax_payable
        
        # final_tax_payable in old table seems to map to 'annual_tax_payable' (Row 38) as it was the last calculated field.
        
        column_mapping = {
            'company_id': 'company_id',
            'period_year': 'period_year',
            'filing_date': 'filing_date',
            'created_at': 'created_at',
            'revenue': 'revenue',
            'cost': 'cost',
            'taxes_and_surcharges': 'taxes_and_surcharges',
            'selling_expenses': 'selling_expenses',
            'administrative_expenses': 'administrative_expenses',
            'financial_expenses': 'financial_expenses',
            'operating_profit': 'operating_profit',
            'total_profit': 'total_profit',
            'taxable_income': 'taxable_income',
            'tax_rate': 'tax_rate',
            'nominal_tax': 'nominal_tax',
            'tax_reduction': 'tax_reduction',
            'tax_payable': 'tax_payable',
            # 'final_tax_payable' (new Row 38/45?) -> 'final_tax_payable' (old).
            # In old schema, final_tax_payable was likely "本年应补（退）所得税额".
            # Let's map it to annual_tax_payable (Row 38).
            'annual_tax_payable': 'final_tax_payable'
        }
        
        # Construct INSERT SELECT statement
        # Only select columns that exist in backup
        valid_cols = []
        select_cols = []
        
        for new_col, old_col in column_mapping.items():
            if old_col in backup_columns:
                valid_cols.append(new_col)
                select_cols.append(old_col)
        
        if valid_cols:
            sql = f"""
            INSERT INTO tax_returns_income ({', '.join(valid_cols)})
            SELECT {', '.join(select_cols)}
            FROM tax_returns_income_backup_v2
            """
            cursor.execute(sql)
            print(f"Migrated {cursor.rowcount} rows.")
        else:
            print("No matching columns to migrate.")

    except Exception as e:
        print(f"Migration warning: {e}")

    conn.commit()
    conn.close()
    print("Schema update completed successfully.")

if __name__ == "__main__":
    update_schema()
