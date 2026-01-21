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
                if "aliases" in info and info["aliases"]:
                    mapping[field] = info["aliases"][0]
    
    # Special handling for companies table
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
            "company_scale": "企业规模",
            "credit_code": "统一社会信用代码",
            "taxpayer_type": "纳税人类型",
            "business_term": "营业期限",
            "employee_count": "员工人数",
            "shareholder_info": "股东信息",
            "industry_code": "行业代码",
            "industry_chain_position": "产业链位置",
            "taxpayer_qualification": "纳税人资质",
            "collection_method": "征收方式",
            "tax_credit_rating": "纳税信用等级",
            "operating_status": "经营状态"
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

    # Comprehensive mapping for income_statements (利润表)
    if table_name == "income_statements":
        mapping.update({
            "total_revenue": "营业收入",
            "cost_of_sales": "营业成本",
            "gross_profit": "毛利润",
            "operating_revenue": "营业收入额",
            "operating_costs": "营业成本额",
            "taxes_and_surcharges": "税金及附加",
            "selling_expenses": "销售费用",
            "administrative_expenses": "管理费用",
            "rd_expenses": "研发费用",
            "financial_expenses": "财务费用",
            "interest_expenses": "利息费用",
            "interest_income": "利息收入",
            "other_income": "其他收益",
            "investment_income": "投资收益",
            "fair_value_gains": "公允价值变动收益",
            "credit_impairment_losses": "信用减值损失",
            "asset_impairment_losses": "资产减值损失",
            "asset_disposal_income": "资产处置收益",
            "operating_profit": "营业利润",
            "non_operating_income": "营业外收入",
            "non_operating_expenses": "营业外支出",
            "total_profit": "利润总额",
            "income_tax_expense": "所得税费用",
            "net_profit": "净利润"
        })

    # Comprehensive mapping for balance_sheets (资产负债表)
    if table_name == "balance_sheets":
        mapping.update({
            "cash_and_equivalents": "货币资金",
            "trading_financial_assets": "交易性金融资产",
            "notes_receivable": "应收票据",
            "accounts_receivable": "应收账款",
            "prepayments": "预付账款",
            "other_receivables": "其他应收款",
            "inventory": "存货",
            "contract_assets": "合同资产",
            "current_assets_total": "流动资产合计",
            "long_term_equity_investment": "长期股权投资",
            "fixed_assets": "固定资产",
            "accumulated_depreciation": "累计折旧",
            "construction_in_progress": "在建工程",
            "intangible_assets": "无形资产",
            "accumulated_amortization": "累计摊销",
            "long_term_deferred_expenses": "长期待摊费用",
            "deferred_tax_assets": "递延所得税资产",
            "non_current_assets_total": "非流动资产合计",
            "total_assets": "资产总计",
            "short_term_loans": "短期借款",
            "notes_payable": "应付票据",
            "accounts_payable": "应付账款",
            "contract_liabilities": "合同负债",
            "employee_benefits_payable": "应付职工薪酬",
            "taxes_payable": "应交税费",
            "other_payables": "其他应付款",
            "current_liabilities_total": "流动负债合计",
            "long_term_loans": "长期借款",
            "long_term_payables": "长期应付款",
            "deferred_revenue": "递延收益",
            "deferred_tax_liabilities": "递延所得税负债",
            "non_current_liabilities_total": "非流动负债合计",
            "total_liabilities": "负债合计",
            "paid_in_capital": "实收资本",
            "capital_reserve": "资本公积",
            "surplus_reserve": "盈余公积",
            "undistributed_profit": "未分配利润",
            "total_equity": "所有者权益合计",
            "total_liabilities_and_equity": "负债和所有者权益总计"
        })

    # Comprehensive mapping for tax_returns_vat (增值税申报表)
    if table_name == "tax_returns_vat":
        mapping.update({
            # 一般项目 - 销售额部分
            "gen_sales_taxable_current": "按适用税率计税销售额(本月)",
            "gen_sales_taxable_ytd": "按适用税率计税销售额(累计)",
            "gen_sales_goods_current": "应税货物销售额(本月)",
            "gen_sales_goods_ytd": "应税货物销售额(累计)",
            "gen_sales_service_current": "应税劳务销售额(本月)",
            "gen_sales_service_ytd": "应税劳务销售额(累计)",
            "gen_sales_adjustment_current": "纳税检查调整销售额(本月)",
            "gen_sales_adjustment_ytd": "纳税检查调整销售额(累计)",
            "gen_sales_simple_current": "简易计税销售额(本月)",
            "gen_sales_simple_ytd": "简易计税销售额(累计)",
            "gen_sales_simple_adjustment_current": "简易计税检查调整销售额(本月)",
            "gen_sales_simple_adjustment_ytd": "简易计税检查调整销售额(累计)",
            "gen_sales_export_current": "免抵退出口销售额(本月)",
            "gen_sales_export_ytd": "免抵退出口销售额(累计)",
            "gen_sales_exempt_current": "免税销售额(本月)",
            "gen_sales_exempt_ytd": "免税销售额(累计)",
            "gen_sales_exempt_goods_current": "免税货物销售额(本月)",
            "gen_sales_exempt_goods_ytd": "免税货物销售额(累计)",
            "gen_sales_exempt_service_current": "免税劳务销售额(本月)",
            "gen_sales_exempt_service_ytd": "免税劳务销售额(累计)",
            # 一般项目 - 税款计算部分
            "gen_output_tax_current": "销项税额(本月)",
            "gen_output_tax_ytd": "销项税额(累计)",
            "gen_input_tax_current": "进项税额(本月)",
            "gen_input_tax_ytd": "进项税额(累计)",
            "gen_previous_credit_current": "上期留抵税额(本月)",
            "gen_previous_credit_ytd": "上期留抵税额(累计)",
            "gen_input_tax_transfer_current": "进项税额转出(本月)",
            "gen_input_tax_transfer_ytd": "进项税额转出(累计)",
            "gen_export_refund_current": "免抵退应退税额(本月)",
            "gen_tax_inspection_current": "纳税检查应补税额(本月)",
            "gen_deductible_total_current": "应抵扣税额合计(本月)",
            "gen_actual_deduction_current": "实际抵扣税额(本月)",
            "gen_actual_deduction_ytd": "实际抵扣税额(累计)",
            "gen_tax_payable_current": "应纳税额(本月)",
            "gen_tax_payable_ytd": "应纳税额(累计)",
            "gen_ending_credit_current": "期末留抵税额(本月)",
            "gen_simple_tax_current": "简易计税应纳税额(本月)",
            "gen_simple_tax_ytd": "简易计税应纳税额(累计)",
            "gen_simple_inspection_current": "简易计税检查应补税额(本月)",
            "gen_tax_reduction_current": "应纳税额减征额(本月)",
            "gen_tax_reduction_ytd": "应纳税额减征额(累计)",
            "gen_tax_total_current": "应纳税额合计(本月)",
            "gen_tax_total_ytd": "应纳税额合计(累计)",
            # 一般项目 - 税款缴纳部分
            "gen_opening_unpaid_tax_current": "期初未缴税额(本月)",
            "gen_opening_unpaid_tax_ytd": "期初未缴税额(累计)",
            "gen_export_refund_received_current": "出口专用缴款书退税额(本月)",
            "gen_paid_tax_total_current": "本期已缴税额(本月)",
            "gen_paid_tax_total_ytd": "本期已缴税额(累计)",
            "gen_prepaid_tax_current": "分次预缴税额(本月)",
            "gen_export_prepaid_current": "出口专用缴款书预缴税额(本月)",
            "gen_paid_previous_tax_current": "本期缴纳上期应纳税额(本月)",
            "gen_paid_previous_tax_ytd": "本期缴纳上期应纳税额(累计)",
            "gen_paid_overdue_tax_current": "本期缴纳欠缴税额(本月)",
            "gen_paid_overdue_tax_ytd": "本期缴纳欠缴税额(累计)",
            "gen_ending_unpaid_tax_current": "期末未缴税额(本月)",
            "gen_ending_unpaid_tax_ytd": "期末未缴税额(累计)",
            "gen_overdue_tax_current": "欠缴税额(本月)",
            "gen_tax_payable_refund_current": "本期应补(退)税额(本月)",
            "gen_opening_inspection_unpaid_current": "期初未缴查补税额(本月)",
            "gen_opening_inspection_unpaid_ytd": "期初未缴查补税额(累计)",
            "gen_inspection_paid_current": "本期入库查补税额(本月)",
            "gen_inspection_paid_ytd": "本期入库查补税额(累计)",
            "gen_ending_inspection_unpaid_current": "期末未缴查补税额(本月)",
            "gen_ending_inspection_unpaid_ytd": "期末未缴查补税额(累计)",
            # 即征即退项目 - 销售额部分
            "ref_sales_taxable_current": "即征即退-按适用税率计税销售额(本月)",
            "ref_sales_taxable_ytd": "即征即退-按适用税率计税销售额(累计)",
            "ref_sales_goods_current": "即征即退-应税货物销售额(本月)",
            "ref_sales_goods_ytd": "即征即退-应税货物销售额(累计)",
            "ref_sales_service_current": "即征即退-应税劳务销售额(本月)",
            "ref_sales_service_ytd": "即征即退-应税劳务销售额(累计)",
            "ref_sales_adjustment_current": "即征即退-纳税检查调整销售额(本月)",
            "ref_sales_adjustment_ytd": "即征即退-纳税检查调整销售额(累计)",
            "ref_sales_simple_current": "即征即退-简易计税销售额(本月)",
            "ref_sales_simple_ytd": "即征即退-简易计税销售额(累计)",
            "ref_sales_simple_adjustment_current": "即征即退-简易计税检查调整销售额(本月)",
            "ref_sales_simple_adjustment_ytd": "即征即退-简易计税检查调整销售额(累计)",
            # 即征即退项目 - 税款计算部分
            "ref_output_tax_current": "即征即退-销项税额(本月)",
            "ref_output_tax_ytd": "即征即退-销项税额(累计)",
            "ref_input_tax_current": "即征即退-进项税额(本月)",
            "ref_input_tax_ytd": "即征即退-进项税额(累计)",
            "ref_previous_credit_current": "即征即退-上期留抵税额(本月)",
            "ref_input_tax_transfer_current": "即征即退-进项税额转出(本月)",
            "ref_input_tax_transfer_ytd": "即征即退-进项税额转出(累计)",
            "ref_deductible_total_current": "即征即退-应抵扣税额合计(本月)",
            "ref_actual_deduction_current": "即征即退-实际抵扣税额(本月)",
            "ref_actual_deduction_ytd": "即征即退-实际抵扣税额(累计)",
            "ref_tax_payable_current": "即征即退-应纳税额(本月)",
            "ref_tax_payable_ytd": "即征即退-应纳税额(累计)",
            "ref_ending_credit_current": "即征即退-期末留抵税额(本月)",
            "ref_simple_tax_current": "即征即退-简易计税应纳税额(本月)",
            "ref_simple_tax_ytd": "即征即退-简易计税应纳税额(累计)",
            "ref_tax_reduction_current": "即征即退-应纳税额减征额(本月)",
            "ref_tax_reduction_ytd": "即征即退-应纳税额减征额(累计)",
            "ref_tax_total_current": "即征即退-应纳税额合计(本月)",
            "ref_tax_total_ytd": "即征即退-应纳税额合计(累计)",
            # 即征即退项目 - 税款缴纳部分
            "ref_opening_unpaid_tax_current": "即征即退-期初未缴税额(本月)",
            "ref_opening_unpaid_tax_ytd": "即征即退-期初未缴税额(累计)",
            "ref_paid_tax_total_current": "即征即退-本期已缴税额(本月)",
            "ref_paid_tax_total_ytd": "即征即退-本期已缴税额(累计)",
            "ref_prepaid_tax_current": "即征即退-分次预缴税额(本月)",
            "ref_paid_previous_tax_current": "即征即退-本期缴纳上期应纳税额(本月)",
            "ref_paid_previous_tax_ytd": "即征即退-本期缴纳上期应纳税额(累计)",
            "ref_paid_overdue_tax_current": "即征即退-本期缴纳欠缴税额(本月)",
            "ref_paid_overdue_tax_ytd": "即征即退-本期缴纳欠缴税额(累计)",
            "ref_ending_unpaid_tax_current": "即征即退-期末未缴税额(本月)",
            "ref_ending_unpaid_tax_ytd": "即征即退-期末未缴税额(累计)",
            "ref_overdue_tax_current": "即征即退-欠缴税额(本月)",
            "ref_tax_payable_refund_current": "即征即退-本期应补(退)税额(本月)",
            "ref_actual_refund_current": "即征即退-实际退税额(本月)",
            "ref_actual_refund_ytd": "即征即退-实际退税额(累计)",
            # 附加税费
            "urban_construction_tax_current": "城市维护建设税(本月)",
            "urban_construction_tax_ytd": "城市维护建设税(累计)",
            "education_surcharge_current": "教育费附加(本月)",
            "education_surcharge_ytd": "教育费附加(累计)",
            "local_education_surcharge_current": "地方教育附加(本月)",
            "local_education_surcharge_ytd": "地方教育附加(累计)",
            # 申报信息
            "preparer": "经办人",
            "preparer_id_card": "经办人身份证号",
            "taxpayer_signature": "纳税人签章",
            "signature_date": "签章日期",
            "receiver": "受理人",
            "agent_org": "代理机构签章",
            "agent_org_code": "代理机构统一社会信用代码",
            "tax_authority": "受理税务机关章",
            "acceptance_date": "受理日期"
        })


    # Comprehensive mapping for tax_returns_income (企业所得税申报表)
    if table_name == "tax_returns_income":
        mapping.update({
            "id": "记录唯一标识",
            "company_id": "企业标识",
            "period_year": "申报年度",
            "filing_date": "申报日期",
            "created_at": "创建时间",
            "revenue": "一、营业收入",
            "cost": "营业成本",
            "taxes_and_surcharges": "税金及附加",
            "selling_expenses": "销售费用",
            "administrative_expenses": "管理费用",
            "financial_expenses": "财务费用",
            "operating_profit": "二、营业利润",
            "total_profit": "三、利润总额",
            "taxable_income": "五、应纳税所得额",
            "tax_rate": "税率",
            "nominal_tax": "六、应纳所得税额",
            "tax_reduction": "减免所得税额",
            "tax_payable": "七、应纳税额",
            "final_tax_payable": "十、本年实际应补（退）所得税额"
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
