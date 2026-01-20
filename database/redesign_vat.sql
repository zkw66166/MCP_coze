-- Redesign of VAT Returns Table (Refined)
-- Purpose: Replace Key-Value structure with Wide Table for efficiency.
-- Changes:
-- 1. Rename to vat_return_fact
-- 2. Add metadata columns
-- 3. Drop old tables

-- Drop the temporary table if it was created in previous step
DROP TABLE IF EXISTS fact_vat_returns;
DROP TABLE IF EXISTS vat_return_fact; -- Ensure clean slate

-- Create the new table with correct name and columns
CREATE TABLE vat_return_fact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    
    -- Period Dimension
    period_year INTEGER NOT NULL,
    period_month INTEGER NOT NULL,
    period_quarter INTEGER NOT NULL,
    tax_period VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    
    filing_date DATE,
    
    -- ========================================
    -- General Project - Sales (一般项目 - 销售额)
    -- ========================================
    gen_sales_taxable_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_taxable_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_goods_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_goods_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_service_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_service_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_adjustment_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_adjustment_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_simple_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_simple_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_simple_adjustment_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_simple_adjustment_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_export_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_export_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_goods_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_goods_ytd DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_service_current DECIMAL(18,2) DEFAULT 0,
    gen_sales_exempt_service_ytd DECIMAL(18,2) DEFAULT 0,
    
    -- ========================================
    -- General Project - Tax Calculation (一般项目 - 税款计算)
    -- ========================================
    gen_output_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_output_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_input_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_input_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_previous_credit_current DECIMAL(18,2) DEFAULT 0,
    gen_previous_credit_ytd DECIMAL(18,2) DEFAULT 0,
    gen_input_tax_transfer_current DECIMAL(18,2) DEFAULT 0,
    gen_input_tax_transfer_ytd DECIMAL(18,2) DEFAULT 0,
    gen_export_refund_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_inspection_current DECIMAL(18,2) DEFAULT 0,
    gen_deductible_total_current DECIMAL(18,2) DEFAULT 0,
    gen_actual_deduction_current DECIMAL(18,2) DEFAULT 0,
    gen_actual_deduction_ytd DECIMAL(18,2) DEFAULT 0,
    gen_tax_payable_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_payable_ytd DECIMAL(18,2) DEFAULT 0,
    gen_ending_credit_current DECIMAL(18,2) DEFAULT 0,
    gen_simple_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_simple_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_simple_inspection_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_reduction_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_reduction_ytd DECIMAL(18,2) DEFAULT 0,
    gen_tax_total_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_total_ytd DECIMAL(18,2) DEFAULT 0,
    
    -- ========================================
    -- General Project - Tax Payment (一般项目 - 税款缴纳)
    -- ========================================
    gen_opening_unpaid_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_opening_unpaid_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_export_refund_received_current DECIMAL(18,2) DEFAULT 0,
    gen_paid_tax_total_current DECIMAL(18,2) DEFAULT 0,
    gen_paid_tax_total_ytd DECIMAL(18,2) DEFAULT 0,
    gen_prepaid_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_export_prepaid_current DECIMAL(18,2) DEFAULT 0,
    gen_paid_previous_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_paid_previous_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_paid_overdue_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_paid_overdue_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_ending_unpaid_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_ending_unpaid_tax_ytd DECIMAL(18,2) DEFAULT 0,
    gen_overdue_tax_current DECIMAL(18,2) DEFAULT 0,
    gen_tax_payable_refund_current DECIMAL(18,2) DEFAULT 0,
    gen_opening_inspection_unpaid_current DECIMAL(18,2) DEFAULT 0,
    gen_opening_inspection_unpaid_ytd DECIMAL(18,2) DEFAULT 0,
    gen_inspection_paid_current DECIMAL(18,2) DEFAULT 0,
    gen_inspection_paid_ytd DECIMAL(18,2) DEFAULT 0,
    gen_ending_inspection_unpaid_current DECIMAL(18,2) DEFAULT 0,
    gen_ending_inspection_unpaid_ytd DECIMAL(18,2) DEFAULT 0,
    
    -- ========================================
    -- Refunds on Levy (Immediate Refund) Project (即征即退项目)
    -- ========================================
    ref_sales_taxable_current DECIMAL(18,2) DEFAULT 0,
    ref_sales_taxable_ytd DECIMAL(18,2) DEFAULT 0,
    ref_output_tax_current DECIMAL(18,2) DEFAULT 0,
    ref_output_tax_ytd DECIMAL(18,2) DEFAULT 0,
    ref_input_tax_current DECIMAL(18,2) DEFAULT 0,
    ref_input_tax_ytd DECIMAL(18,2) DEFAULT 0,
    ref_tax_payable_current DECIMAL(18,2) DEFAULT 0,
    ref_tax_payable_ytd DECIMAL(18,2) DEFAULT 0,
    ref_tax_total_current DECIMAL(18,2) DEFAULT 0,
    ref_tax_total_ytd DECIMAL(18,2) DEFAULT 0,
    ref_actual_refund_current DECIMAL(18,2) DEFAULT 0,
    ref_actual_refund_ytd DECIMAL(18,2) DEFAULT 0,
    
    -- ========================================
    -- Surcharges (附加税费)
    -- ========================================
    urban_construction_tax_current DECIMAL(18,2) DEFAULT 0,
    urban_construction_tax_ytd DECIMAL(18,2) DEFAULT 0,
    education_surcharge_current DECIMAL(18,2) DEFAULT 0,
    education_surcharge_ytd DECIMAL(18,2) DEFAULT 0,
    local_education_surcharge_current DECIMAL(18,2) DEFAULT 0,
    local_education_surcharge_ytd DECIMAL(18,2) DEFAULT 0,

    -- ========================================
    -- Metadata (New additions)
    -- ========================================
    preparer VARCHAR(50),                              -- 经办人
    preparer_id_card VARCHAR(18),                      -- 经办人身份证号
    taxpayer_signature VARCHAR(200),                   -- 纳税人（签章）
    signature_date DATE,                               -- 签章日期
    receiver VARCHAR(50),                              -- 受理人
    agent_org VARCHAR(200),                            -- 代理机构签章
    agent_org_code VARCHAR(18),                        -- 代理机构统一社会信用代码
    tax_authority VARCHAR(200),                        -- 受理税务机关（章）
    acceptance_date DATE,                              -- 受理日期

    -- Standard Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(company_id, period_year, period_month)
);

CREATE INDEX IF NOT EXISTS idx_vat_return_fact_company_period ON vat_return_fact(company_id, period_year, period_month);
CREATE INDEX IF NOT EXISTS idx_vat_return_fact_filing_date ON vat_return_fact(filing_date);

-- Drop old tables
DROP TABLE IF EXISTS vat_returns;
DROP TABLE IF EXISTS vat_return_items;
DROP TABLE IF EXISTS vat_surcharges;
