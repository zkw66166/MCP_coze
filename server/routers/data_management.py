from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import sqlite3
import os
from datetime import datetime

router = APIRouter(
    prefix="/api/data-management",
    tags=["data-management"]
)

# 数据库路径 - 使用绝对路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'database', 'financial.db')

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/stats")
async def get_data_management_stats(company_id: Optional[int] = None):
    """
    Get statistics for Data Management page.
    If company_id is provided, returns stats for that specific company (Single Enterprise mode).
    If company_id is None, returns aggregated stats for all companies (Multi Enterprise mode).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Company Information
        if company_id:
            cursor.execute("SELECT id, name, tax_code FROM companies WHERE id = ?", (company_id,))
            company = cursor.fetchone()
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            companies_list = [dict(company)]
        else:
            cursor.execute("SELECT id, name, tax_code FROM companies")
            companies_list = [dict(row) for row in cursor.fetchall()]

        company_ids = [c['id'] for c in companies_list]
        
        if not company_ids:
             return {
                "summary": {
                    "subject_count": 0,
                    "report_count": 0,
                    "period_count": 0,
                    "completeness": 0
                },
                "companies": [],
                "quality_checks": [],
                "mapping_synonyms": _get_mapping_synonyms(), # Always return synonyms
                "update_frequency": _get_update_frequency()
            }

        ids_placeholder = ','.join(['?'] * len(company_ids))

        # 2. Statistics Calculation
        
        # Subject Count (Financial Metrics / Balance Sheet Items)
        # Using financial_metrics columns as a proxy for standardized subjects
        # Or count distinct items from appropriate tables if available. 
        # For simplicity and speed, we'll use a fixed number + potentially dynamic count if applicable.
        # Let's count columns in financial_metrics as "Standardized Subjects"
        subject_count = 30 # Base count of standard metrics
        
        # Report Quantity (Count of rows in main tables)
        tables_to_count = [
            'balance_sheet', 'income_statements', 'cash_flow_statements', 
            'tax_returns_income', 'vat_returns', 'tax_returns_stamp', 'invoices'
        ]
        
        total_reports = 0
        for table in tables_to_count:
            # Check if table exists first to avoid errors
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                if company_id:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE company_id = ?", (company_id,))
                else:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_reports += cursor.fetchone()[0]

        # Data Period (Months)
        # Check distinct YYYY-MM from valid tables
        period_count = 0
        if company_id:
            cursor.execute(f"SELECT COUNT(DISTINCT period_year || '-' || period_month) FROM financial_metrics WHERE company_id = ?", (company_id,))
        else:
            cursor.execute(f"SELECT COUNT(DISTINCT period_year || '-' || period_month) FROM financial_metrics")
        period_count = cursor.fetchone()[0]

        # Completeness (Simple Logic: having Metric data / Expected periods)
        # This is a mock calculation for Phase 1 based on available data
        completeness = 95.0 if total_reports > 0 else 0.0

        # 3. Quality Checks (Mock logic based on real data existence)
        quality_checks = _generate_quality_checks(cursor, company_ids)

        # 4. Companies Detailed Status (for Multi-Company View)
        companies_status = []
        if not company_id:
            for comp in companies_list:
                cid = comp['id']
                # Quick stats for this company
                cursor.execute("SELECT COUNT(*) FROM financial_metrics WHERE company_id = ?", (cid,))
                has_metrics = cursor.fetchone()[0] > 0
                
                status = "Data Complete" if has_metrics else "Incomplete"
                companies_status.append({
                    "id": cid,
                    "name": comp['name'],
                    "taxCode": comp['tax_code'],
                    "status": status,
                    "lastUpdate": datetime.now().strftime("%Y-%m-%d"), # Mock for now
                    "dataTypes": ["Financial Statements", "Tax Returns"],
                    "completeness": 95 if has_metrics else 40,
                    "issues": 0 if has_metrics else 2
                })

        conn.close()

        return {
            "summary": {
                "subject_count": subject_count,
                "report_count": total_reports,
                "period_count": period_count,
                "completeness": completeness
            },
            "companies": companies_status,
            "quality_checks": quality_checks,
            "mapping_synonyms": _get_mapping_synonyms(),
            "update_frequency": [
                {"source": "资产负债表", "frequency": "月度", "last_update": "2024-12-15"},
                {"source": "利润表", "frequency": "月度", "last_update": "2024-12-15"},
                {"source": "现金流量表", "frequency": "月度", "last_update": "2024-12-15"},
                {"source": "增值税申报表", "frequency": "月度", "last_update": "2024-12-15"},
                {"source": "企业所得税申报表", "frequency": "季度", "last_update": "2024-10-20"},
                {"source": "印花税申报表", "frequency": "季度", "last_update": "2024-10-20"},
                {"source": "科目余额表", "frequency": "月度", "last_update": "2024-12-15"}
            ]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quality-check")
async def check_data_quality(
    company_id: Optional[int] = Query(None, description="Company ID")
):
    """
    执行数据质量检查
    自动遍历所选企业的所有期间和所有表
    """
    try:
        from ..services.data_quality import DataQualityChecker
        checker = DataQualityChecker(DB_PATH)
        
        # If no company selected, default to company 5 for testing
        target_company = company_id if company_id else 5
        
        results = checker.check_all(target_company)
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def _get_mapping_synonyms():
    """
    Return the hardcoded synonyms for Smart Data Mapping.
    """
    return [
        {"standard": "Balance Sheet", "synonyms": ["Statement of Financial Position"], "status": "Mapped", "match": 100},
        {"standard": "Income Statement", "synonyms": ["Profit and Loss Statement"], "status": "Mapped", "match": 100},
        {"standard": "Subject Balance Sheet", "synonyms": ["Trial Balance", "General Ledger Summary"], "status": "Mapped", "match": 95},
        {"standard": "Invoices", "synonyms": ["FaPiao", "VAT Invoices"], "status": "Mapped", "match": 100},
        {"standard": "CIT Return", "synonyms": ["Corporate Income Tax Return", "A100000"], "status": "Mapped", "match": 100},
        {"standard": "VAT Return", "synonyms": ["Value Added Tax Return"], "status": "Mapped", "match": 100},
        {"standard": "Stamp Duty", "synonyms": ["Stamp Tax Declaration"], "status": "Mapped", "match": 90}
    ]

def _get_update_frequency():
    """
    Return static update frequency configuration.
    """
    return [
        {"source": "Financial Statements", "frequency": "Real-time", "last": "5 mins ago", "status": "Normal"},
        {"source": "Subject Balance Sheet", "frequency": "Daily", "last": "2 hours ago", "status": "Normal"},
        {"source": "Tax Returns", "frequency": "Monthly", "last": "1 day ago", "status": "Normal"},
        {"source": "Invoices", "frequency": "Daily", "last": "1 day ago", "status": "Delayed"},
        {"source": "Other Tax Data", "frequency": "Weekly", "last": "2 days ago", "status": "Normal"},
        {"source": "Registration Info", "frequency": "Manual", "last": "7 days ago", "status": "Pending"},
        {"source": "Bank Statements", "frequency": "Manual", "last": "3 days ago", "status": "Pending"}
    ]

def _generate_quality_checks(cursor, company_ids):
    """
    Generate quality check results based on DB content.
    """
    checks = []
    
    # Return 7 Placeholder checks for the initial view
    categories = [
        ("Subject Balance Sheet", "科目余额表", "Pending"),
        ("Balance Sheet", "资产负债表", "Pending"),
        ("Income Statement", "利润表", "Pending"),
        ("Cash Flow Statement", "现金流量表", "Pending"),
        ("VAT Return", "增值税申报表", "Pending"),
        ("CIT Return", "企业所得税申报表", "Pending"),
        ("Stamp Duty Return", "印花税申报表", "Pending")
    ]
    
    for en, cn, status in categories:
        checks.append({
            "category": en,
            "check": cn,
            "status": status,
            "details": "Click check to verify",
            "color": "gray"
        })

    return checks
