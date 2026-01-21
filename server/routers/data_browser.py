from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import sqlite3
import os
import json
from datetime import datetime

router = APIRouter(
    prefix="/api/data-browser",
    tags=["data-browser"]
)

# 1. 数据库路径配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'database', 'financial.db')
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'config', 'metrics_config.json')

# 2. 表配置定义
SUPPORTED_TABLES = {
    "companies": "工商登记信息",
    "balance_sheets": "资产负债表",
    "income_statements": "利润表",
    "cash_flow_statements": "现金流量表",
    "account_balances": "科目余额表",
    "tax_returns_vat": "增值税申报表",
    "tax_returns_income": "企业所得税申报表",
    "tax_returns_stamp": "印花税申报表",
    "invoices": "发票数据"
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_metrics_config():
    """Load metrics config for column mapping"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metrics config: {e}")
        return {}

def get_column_mapping(table_name: str) -> Dict[str, str]:
    """Get Chinese name mapping for columns"""
    config = load_metrics_config()
    mapping = {}
    
    # Base mapping for common fields
    common_mapping = {
        "id": "ID",
        "company_id": "企业ID",
        "period_year": "年份",
        "period_month": "月份",
        "period_quarter": "季度",
        "period": "期间",
        "created_at": "创建时间",
        "updated_at": "更新时间",
        "filing_date": "申报日期",
        "report_date": "报告日期",
        "start_date": "开始日期",
        "end_date": "结束日期"
    }
    mapping.update(common_mapping)

    # Table specific mapping from config
    if "tables" in config and table_name in config["tables"]:
        table_config = config["tables"][table_name]
        if "fields" in table_config:
            for field, info in table_config["fields"].items():
                # Use the first alias or the field name
                if "aliases" in info and info["aliases"]:
                    mapping[field] = info["aliases"][0]
    
    # Special handling for companies table (not in metrics_config usually)
    if table_name == "companies":
        mapping.update({
            "name": "企业名称",
            "tax_code": "纳税人识别号",
            "company_type": "企业类型",
            "legal_person": "法人代表",
            "registered_capital": "注册资本",
            "establishment_date": "成立日期",
            "address": "注册地址",
            "business_scope": "经营范围",
            "industry": "所属行业",
            "company_scale": "企业规模"
        })
        
    # Special handling for invoices
    if table_name == "invoices":
        mapping.update({
            "invoice_code": "发票代码",
            "invoice_number": "发票号码",
            "issue_date": "开票日期",
            "buyer_name": "购买方名称",
            "buyer_tax_id": "购买方税号",
            "seller_name": "销售方名称",
            "seller_tax_id": "销售方税号",
            "amount_excluding_tax": "不含税金额",
            "tax_amount": "税额",
            "total_amount": "价税合计",
            "invoice_type": "发票类型",
            "item_name": "货物或应税劳务名称"
        })

    # Special handling for tax_returns_vat
    if table_name == "tax_returns_vat":
        mapping.update({
            "tax_period": "税款所属期",
            "gen_sales_taxable_current": "本期销售额",
            "gen_sales_taxable_ytd": "累计销售额",
            "gen_output_tax_current": "本期销项税额",
            "gen_output_tax_ytd": "累计销项税额",
            "gen_input_tax_current": "本期进项税额",
            "gen_input_tax_ytd": "累计进项税额",
            "gen_tax_payable_current": "本期应纳税额",
            "gen_tax_payable_ytd": "累计应纳税额",
            "gen_paid_tax_total_current": "本期已缴税额",
            "gen_paid_tax_total_ytd": "累计已缴税额"
        })

    return mapping

@router.get("/tables")
async def get_tables():
    """获取所有支持的数据表"""
    return [{"name": k, "label": v} for k, v in SUPPORTED_TABLES.items()]

@router.get("/companies")
async def get_companies():
    """获取所有企业列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM companies ORDER BY id")
        companies = [dict(row) for row in cursor.fetchall()]
        return companies
    finally:
        conn.close()

@router.get("/periods")
async def get_periods(company_id: int, table_name: str):
    """获取指定表的数据期间列表"""
    if table_name not in SUPPORTED_TABLES:
        raise HTTPException(status_code=400, detail="Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if table has period columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row['name'] for row in cursor.fetchall()]
        
        periods = []
        if 'period' in columns:
            cursor.execute(f"SELECT DISTINCT period FROM {table_name} WHERE company_id = ? ORDER BY period DESC", (company_id,))
            periods = [row['period'] for row in cursor.fetchall()]
        elif 'period_year' in columns:
            # Construct period based on available columns
            # For tax_returns_vat, we explicitly want monthly first if available
            if table_name == 'tax_returns_vat' and 'period_month' in columns:
                 cursor.execute(f"""
                    SELECT DISTINCT period_year, period_month 
                    FROM {table_name} 
                    WHERE company_id = ? 
                    ORDER BY period_year DESC, period_month DESC
                """, (company_id,))
                 rows = cursor.fetchall()
                 periods = [f"{row['period_year']}年{row['period_month']}月" for row in rows]
            elif 'period_quarter' in columns:
                cursor.execute(f"""
                    SELECT DISTINCT period_year, period_quarter 
                    FROM {table_name} 
                    WHERE company_id = ? 
                    ORDER BY period_year DESC, period_quarter DESC
                """, (company_id,))
                rows = cursor.fetchall()
                periods = [f"{row['period_year']}年Q{row['period_quarter']}" for row in rows]
            elif 'period_month' in columns:
                cursor.execute(f"""
                    SELECT DISTINCT period_year, period_month 
                    FROM {table_name} 
                    WHERE company_id = ? 
                    ORDER BY period_year DESC, period_month DESC
                """, (company_id,))
                rows = cursor.fetchall()
                periods = [f"{row['period_year']}年{row['period_month']}月" for row in rows]
            else:
                cursor.execute(f"SELECT DISTINCT period_year FROM {table_name} WHERE company_id = ? ORDER BY period_year DESC", (company_id,))
                periods = [f"{row['period_year']}年" for row in cursor.fetchall()]
        
        return periods
    except Exception as e:
        print(f"Error getting periods: {e}")
        return []
    finally:
        conn.close()

@router.get("/data")
async def get_table_data(
    company_id: int, 
    table_name: str, 
    period: Optional[str] = None
):
    """获取表数据 (不分页)"""
    if table_name not in SUPPORTED_TABLES:
        raise HTTPException(status_code=400, detail="Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Get Columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row['name'] for row in cursor.fetchall()]
        
        # 2. Get Chinese Mapping
        mapping = get_column_mapping(table_name)
        
        # 3. Build Column Headers
        column_headers = []
        for col in columns:
            column_headers.append({
                "key": col,
                "label": mapping.get(col, col) # Fallback to original name if no mapping
            })

        # 4. Query Data
        query = f"SELECT * FROM {table_name} WHERE company_id = ?"
        params = [company_id]
        
        if period:
            # Parse period string back to conditions
            # Simple heuristic based on format
            if 'Q' in period: # 2022年Q1
                try:
                    year = period.split('年')[0]
                    quarter = period.split('Q')[1]
                    query += " AND period_year = ? AND period_quarter = ?"
                    params.extend([year, quarter])
                except:
                    pass
            elif '月' in period: # 2022年1月
                try:
                    year = period.split('年')[0]
                    month = period.split('月')[0].split('年')[1]
                    query += " AND period_year = ? AND period_month = ?"
                    params.extend([year, month])
                except:
                    pass
            elif '年' in period: # 2022年
                 try:
                    year = period.split('年')[0]
                    query += " AND period_year = ?"
                    params.extend([year])
                 except:
                    pass
            else:
                 # Try exact match on 'period' column if it exists
                 if 'period' in columns:
                     query += " AND period = ?"
                     params.append(period)

        # Order by logical time if possible
        order_clause = ""
        if 'period_year' in columns:
             order_clause = " ORDER BY period_year DESC"
             if 'period_month' in columns:
                 order_clause += ", period_month DESC"
             elif 'period_quarter' in columns:
                 order_clause += ", period_quarter DESC"
        elif 'issue_date' in columns:
            order_clause = " ORDER BY issue_date DESC"
        elif 'created_at' in columns:
            order_clause = " ORDER BY created_at DESC"
            
        query += order_clause

        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]

        # 5. Post-processing
        # For tax_returns_vat, calculate start_date and end_date if not present
        if table_name == 'tax_returns_vat':
            import calendar
            for row in rows:
                # Calculate dates if period fields exist
                if 'period_year' in row and 'period_month' in row and row['period_year'] and row['period_month']:
                    try:
                        year = int(row['period_year'])
                        month = int(row['period_month'])
                        # Month range
                        _, last_day = calendar.monthrange(year, month)
                        row['start_date'] = f"{year}年{month}月1日"
                        row['end_date'] = f"{year}年{month}月{last_day}日"
                    except:
                        pass
                # Or fallback to tax_period if it exists but usually its a string like "2024-01-01"
        
        return {
            "columns": column_headers,
            "data": rows,
            "total": len(rows)
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
