-- Create VAT Views (Corrected)
-- Table is already named tax_returns_vat

-- Create Summary View
DROP VIEW IF EXISTS v_vat_summary;
CREATE VIEW v_vat_summary AS
SELECT 
    c.tax_code AS taxpayer_id,
    c.name AS company_name,
    c.industry,
    f.tax_period,
    f.period_year AS year,
    f.period_month AS month,
    f.period_quarter AS quarter,
    f.gen_sales_taxable_current,
    f.gen_tax_payable_current,
    f.gen_tax_total_current,
    f.urban_construction_tax_current,
    f.education_surcharge_current,
    f.local_education_surcharge_current,
    f.filing_date
FROM tax_returns_vat f
JOIN companies c ON f.company_id = c.id;

-- Create Annual Summary View
DROP VIEW IF EXISTS v_vat_annual_summary;
CREATE VIEW v_vat_annual_summary AS
SELECT 
    c.tax_code AS taxpayer_id,
    c.name AS company_name,
    c.industry,
    f.period_year AS year,
    SUM(f.gen_sales_taxable_current) as total_sales,
    SUM(f.gen_tax_total_current) as total_tax,
    SUM(f.urban_construction_tax_current) as total_urban_tax,
    SUM(f.education_surcharge_current) as total_education_surcharge,
    COUNT(*) as return_count
FROM tax_returns_vat f
JOIN companies c ON f.company_id = c.id
GROUP BY c.tax_code, c.name, c.industry, f.period_year;
