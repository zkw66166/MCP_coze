#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业画像 API 路由
提供企业画像数据查询接口
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'database', 'financial.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# 数据模型
# =============================================================================

class BasicInfo(BaseModel):
    """基本信息"""
    company_name: str
    legal_person: Optional[str] = None
    registered_capital: Optional[float] = None
    establishment_date: Optional[str] = None
    company_type: Optional[str] = None
    address: Optional[str] = None
    business_scope: Optional[str] = None
    industry: Optional[str] = None
    credit_code: Optional[str] = None
    taxpayer_type: Optional[str] = None
    employee_count: Optional[int] = None


class Shareholder(BaseModel):
    """股东信息"""
    name: str
    shareholder_type: Optional[str] = None
    share_ratio: float
    share_amount: Optional[float] = None
    is_actual_controller: bool = False


class Investment(BaseModel):
    """对外投资"""
    invested_company_name: str
    investment_ratio: float
    investment_type: Optional[str] = None
    investment_amount: Optional[float] = None
    investment_date: Optional[str] = None
    invested_industry: Optional[str] = None


class RiskInfo(BaseModel):
    """风险信息"""
    risk_type: str
    risk_title: Optional[str] = None
    risk_detail: Optional[str] = None
    risk_amount: Optional[float] = None
    risk_date: Optional[str] = None
    risk_status: Optional[str] = None


class FinancialMetric(BaseModel):
    """财务指标"""
    name: str
    value: float
    unit: str = ""
    evaluation: Optional[str] = None
    evaluation_color: Optional[str] = None


class CustomerInfo(BaseModel):
    """客户信息"""
    customer_name: str
    total_sales: float
    invoice_count: int
    share_ratio: float = 0  # 占比


class SupplierInfo(BaseModel):
    """供应商信息"""
    supplier_name: str
    total_purchase: float
    invoice_count: int
    share_ratio: float = 0  # 占比


# =============================================================================
# API 端点
# =============================================================================

@router.get("/company-profile/{company_id}")
async def get_company_profile(company_id: int, year: Optional[int] = None):
    """
    获取完整企业画像数据
    """
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        # 获取各部分数据
        basic = await get_basic_info(company_id)
        shareholders = await get_shareholders(company_id)
        investments = await get_investments(company_id)
        financial = await get_financial_summary(company_id, year)
        tax = await get_tax_summary(company_id, year)
        invoice = await get_invoice_summary(company_id, year)
        customers = await get_top_customers(company_id, year)
        suppliers = await get_top_suppliers(company_id, year)
        risks = await get_risk_info(company_id)
        growth = await get_growth_metrics(company_id, year)
        cash_flow = await get_cash_flow_summary(company_id, year)
        
        return {
            "company_id": company_id,
            "year": year,
            "basic_info": basic,
            "shareholders": shareholders,
            "investments": investments,
            "financial_summary": financial,
            "tax_summary": tax,
            "invoice_summary": invoice,
            "top_customers": customers,
            "top_suppliers": suppliers,
            "risk_info": risks,
            "growth_metrics": growth,
            "cash_flow_summary": cash_flow
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/basic")
async def get_basic_info(company_id: int) -> Dict[str, Any]:
    """获取企业基本信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, legal_person, registered_capital, establishment_date,
                   company_type, address, business_scope, industry, 
                   credit_code, taxpayer_type, employee_count, tax_code,
                   shareholder_info
            FROM companies WHERE id = ?
        ''', (company_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="企业不存在")
        
        return {
            "company_name": row["name"],
            "legal_person": row["legal_person"],
            "registered_capital": row["registered_capital"],
            "establishment_date": row["establishment_date"],
            "company_type": row["company_type"],
            "address": row["address"],
            "business_scope": row["business_scope"],
            "industry": row["industry"],
            "credit_code": row["credit_code"] or row["tax_code"],
            "taxpayer_type": row["taxpayer_type"] or "一般纳税人",
            "employee_count": row["employee_count"],
            "shareholder_info_text": row["shareholder_info"]
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/shareholders")
async def get_shareholders(company_id: int) -> List[Dict[str, Any]]:
    """获取股东信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT shareholder_name, shareholder_type, share_ratio, 
                   share_amount, is_actual_controller
            FROM shareholders 
            WHERE company_id = ?
            ORDER BY share_ratio DESC
        ''', (company_id,))
        
        shareholders = []
        for row in cursor.fetchall():
            shareholders.append({
                "name": row["shareholder_name"],
                "shareholder_type": row["shareholder_type"],
                "share_ratio": row["share_ratio"],
                "share_amount": row["share_amount"],
                "is_actual_controller": bool(row["is_actual_controller"])
            })
        
        return shareholders
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/investments")
async def get_investments(company_id: int) -> List[Dict[str, Any]]:
    """获取对外投资信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT invested_company_name, investment_ratio, investment_type,
                   investment_amount, investment_date, invested_industry
            FROM investments 
            WHERE company_id = ?
            ORDER BY investment_ratio DESC
        ''', (company_id,))
        
        investments = []
        for row in cursor.fetchall():
            investments.append({
                "invested_company_name": row["invested_company_name"],
                "investment_ratio": row["investment_ratio"],
                "investment_type": row["investment_type"],
                "investment_amount": row["investment_amount"],
                "investment_date": row["investment_date"],
                "invested_industry": row["invested_industry"]
            })
        
        # 统计
        controlling = sum(1 for i in investments if i["investment_type"] == "控股")
        participating = sum(1 for i in investments if i["investment_type"] == "参股")
        
        return {
            "investments": investments,
            "total_count": len(investments),
            "controlling_count": controlling,
            "participating_count": participating
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/financial")
async def get_financial_summary(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取财务状况摘要"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取最新的资产负债表数据
        cursor.execute('''
            SELECT total_assets, total_liabilities, total_equity,
                   current_assets_total, current_liabilities_total,
                   inventory, accounts_receivable, cash_and_equivalents
            FROM balance_sheets
            WHERE company_id = ? AND period_year = ?
            ORDER BY period_quarter DESC, period_month DESC
            LIMIT 1
        ''', (company_id, year))
        bs_row = cursor.fetchone()
        
        # 获取利润表数据（年度汇总）
        cursor.execute('''
            SELECT SUM(total_revenue) as revenue, 
                   SUM(cost_of_sales) as cost,
                   SUM(gross_profit) as gross_profit,
                   SUM(total_profit) as total_profit,
                   SUM(net_profit) as net_profit
            FROM income_statements
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        is_row = cursor.fetchone()
        
        # 计算财务指标
        metrics = []
        
        if bs_row:
            total_assets = bs_row["total_assets"] or 0
            total_liabilities = bs_row["total_liabilities"] or 0
            total_equity = bs_row["total_equity"] or 0
            current_assets = bs_row["current_assets_total"] or 0
            current_liabilities = bs_row["current_liabilities_total"] or 0
            inventory = bs_row["inventory"] or 0
            
            # 资产负债率
            if total_assets > 0:
                ratio = total_liabilities / total_assets * 100
                eval_text, eval_color = evaluate_metric("asset_liability_ratio", ratio)
                metrics.append({
                    "name": "资产负债率",
                    "value": round(ratio, 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 流动比率
            if current_liabilities > 0:
                ratio = current_assets / current_liabilities
                eval_text, eval_color = evaluate_metric("current_ratio", ratio)
                metrics.append({
                    "name": "流动比率",
                    "value": round(ratio, 2),
                    "unit": "",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 速动比率
            if current_liabilities > 0:
                ratio = (current_assets - inventory) / current_liabilities
                eval_text, eval_color = evaluate_metric("quick_ratio", ratio)
                metrics.append({
                    "name": "速动比率",
                    "value": round(ratio, 2),
                    "unit": "",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
        
        if is_row and is_row["revenue"]:
            revenue = is_row["revenue"] or 0
            cost = is_row["cost"] or 0
            gross_profit = is_row["gross_profit"] or 0
            net_profit = is_row["net_profit"] or 0
            
            # 毛利率
            if revenue > 0:
                ratio = gross_profit / revenue * 100
                eval_text, eval_color = evaluate_metric("gross_margin", ratio)
                metrics.append({
                    "name": "毛利率",
                    "value": round(ratio, 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 净利率
            if revenue > 0:
                ratio = net_profit / revenue * 100
                eval_text, eval_color = evaluate_metric("net_margin", ratio)
                metrics.append({
                    "name": "净利率",
                    "value": round(ratio, 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # ROE
            if bs_row and bs_row["total_equity"] and bs_row["total_equity"] > 0:
                ratio = net_profit / bs_row["total_equity"] * 100
                eval_text, eval_color = evaluate_metric("roe", ratio)
                metrics.append({
                    "name": "净资产收益率(ROE)",
                    "value": round(ratio, 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # ROA
            if bs_row and bs_row["total_assets"] and bs_row["total_assets"] > 0:
                ratio = net_profit / bs_row["total_assets"] * 100
                eval_text, eval_color = evaluate_metric("roa", ratio)
                metrics.append({
                    "name": "总资产收益率(ROA)",
                    "value": round(ratio, 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
        
        return {
            "year": year,
            "total_assets": bs_row["total_assets"] if bs_row else 0,
            "total_liabilities": bs_row["total_liabilities"] if bs_row else 0,
            "total_equity": bs_row["total_equity"] if bs_row else 0,
            "revenue": is_row["revenue"] if is_row else 0,
            "net_profit": is_row["net_profit"] if is_row else 0,
            "metrics": metrics
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/tax")
async def get_tax_summary(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取税务情况摘要"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取增值税数据
        cursor.execute('''
            SELECT SUM(vi.amount_current) as vat_amount
            FROM vat_returns vr
            JOIN vat_return_items vi ON vr.id = vi.return_id
            WHERE vr.company_id = ? AND vr.period_year = ?
            AND vi.item_name LIKE '%应纳税额%'
        ''', (company_id, year))
        vat_row = cursor.fetchone()
        vat_amount = vat_row["vat_amount"] if vat_row and vat_row["vat_amount"] else 0
        
        # 获取企业所得税数据
        cursor.execute('''
            SELECT SUM(tax_payable) as cit_amount
            FROM tax_returns_income
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        cit_row = cursor.fetchone()
        cit_amount = cit_row["cit_amount"] if cit_row and cit_row["cit_amount"] else 0
        
        # 获取营业收入用于计算税负率
        cursor.execute('''
            SELECT SUM(total_revenue) as revenue
            FROM income_statements
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        rev_row = cursor.fetchone()
        revenue = rev_row["revenue"] if rev_row and rev_row["revenue"] else 0
        
        # 计算税负率
        vat_burden_rate = (vat_amount / revenue * 100) if revenue > 0 else 0
        cit_burden_rate = (cit_amount / revenue * 100) if revenue > 0 else 0
        total_burden_rate = vat_burden_rate + cit_burden_rate
        
        # 评价
        vat_eval, vat_color = evaluate_metric("vat_burden", vat_burden_rate)
        cit_eval, cit_color = evaluate_metric("cit_burden", cit_burden_rate)
        total_eval, total_color = evaluate_metric("total_tax_burden", total_burden_rate)
        
        return {
            "year": year,
            "vat_amount": round(vat_amount, 2),
            "cit_amount": round(cit_amount, 2),
            "total_tax": round(vat_amount + cit_amount, 2),
            "vat_burden_rate": round(vat_burden_rate, 2),
            "cit_burden_rate": round(cit_burden_rate, 2),
            "total_burden_rate": round(total_burden_rate, 2),
            "evaluations": {
                "vat": {"text": vat_eval, "color": vat_color},
                "cit": {"text": cit_eval, "color": cit_color},
                "total": {"text": total_eval, "color": total_color}
            }
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/invoice")
async def get_invoice_summary(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取发票数据摘要"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 销售发票统计
        cursor.execute('''
            SELECT COUNT(*) as count, SUM(amount_excluding_tax) as amount
            FROM invoices
            WHERE company_id = ? AND period_year = ? AND invoice_type = 'OUTPUT'
        ''', (company_id, year))
        sales_row = cursor.fetchone()
        
        # 采购发票统计
        cursor.execute('''
            SELECT COUNT(*) as count, SUM(amount_excluding_tax) as amount
            FROM invoices
            WHERE company_id = ? AND period_year = ? AND invoice_type = 'INPUT'
        ''', (company_id, year))
        purchase_row = cursor.fetchone()
        
        sales_count = sales_row["count"] if sales_row else 0
        sales_amount = sales_row["amount"] if sales_row and sales_row["amount"] else 0
        purchase_count = purchase_row["count"] if purchase_row else 0
        purchase_amount = purchase_row["amount"] if purchase_row and purchase_row["amount"] else 0
        
        # 平均单票金额
        avg_sales = sales_amount / sales_count if sales_count > 0 else 0
        avg_purchase = purchase_amount / purchase_count if purchase_count > 0 else 0
        
        return {
            "year": year,
            "sales_invoice_count": sales_count,
            "sales_invoice_amount": round(sales_amount, 2),
            "purchase_invoice_count": purchase_count,
            "purchase_invoice_amount": round(purchase_amount, 2),
            "avg_sales_amount": round(avg_sales, 2),
            "avg_purchase_amount": round(avg_purchase, 2)
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/customers")
async def get_top_customers(company_id: int, year: Optional[int] = None, 
                            top_n: int = 5) -> Dict[str, Any]:
    """获取TOP客户分析"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取客户总销售额
        cursor.execute('''
            SELECT SUM(total_sales) as total
            FROM customer_analysis
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        total_row = cursor.fetchone()
        total_sales = total_row["total"] if total_row and total_row["total"] else 0
        
        # 获取TOP客户
        cursor.execute('''
            SELECT customer_name, total_sales, invoice_count
            FROM customer_analysis
            WHERE company_id = ? AND period_year = ?
            ORDER BY total_sales DESC
            LIMIT ?
        ''', (company_id, year, top_n))
        
        customers = []
        top_total = 0
        for row in cursor.fetchall():
            share = (row["total_sales"] / total_sales * 100) if total_sales > 0 else 0
            top_total += row["total_sales"]
            customers.append({
                "customer_name": row["customer_name"],
                "total_sales": round(row["total_sales"], 2),
                "invoice_count": row["invoice_count"],
                "share_ratio": round(share, 2)
            })
        
        # 客户集中度
        concentration = (top_total / total_sales * 100) if total_sales > 0 else 0
        conc_eval, conc_color = evaluate_concentration(concentration)
        
        # 客户总数
        cursor.execute('''
            SELECT COUNT(*) as count FROM customer_analysis
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        count_row = cursor.fetchone()
        customer_count = count_row["count"] if count_row else 0
        
        return {
            "year": year,
            "customer_count": customer_count,
            "top_customers": customers,
            "top_n": top_n,
            "top_concentration": round(concentration, 2),
            "concentration_evaluation": conc_eval,
            "concentration_color": conc_color
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/suppliers")
async def get_top_suppliers(company_id: int, year: Optional[int] = None,
                            top_n: int = 5) -> Dict[str, Any]:
    """获取TOP供应商分析"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取供应商总采购额
        cursor.execute('''
            SELECT SUM(total_purchase) as total
            FROM supplier_analysis
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        total_row = cursor.fetchone()
        total_purchase = total_row["total"] if total_row and total_row["total"] else 0
        
        # 获取TOP供应商
        cursor.execute('''
            SELECT supplier_name, total_purchase, invoice_count
            FROM supplier_analysis
            WHERE company_id = ? AND period_year = ?
            ORDER BY total_purchase DESC
            LIMIT ?
        ''', (company_id, year, top_n))
        
        suppliers = []
        top_total = 0
        for row in cursor.fetchall():
            share = (row["total_purchase"] / total_purchase * 100) if total_purchase > 0 else 0
            top_total += row["total_purchase"]
            suppliers.append({
                "supplier_name": row["supplier_name"],
                "total_purchase": round(row["total_purchase"], 2),
                "invoice_count": row["invoice_count"],
                "share_ratio": round(share, 2)
            })
        
        # 供应商集中度
        concentration = (top_total / total_purchase * 100) if total_purchase > 0 else 0
        conc_eval, conc_color = evaluate_concentration(concentration)
        
        # 供应商总数
        cursor.execute('''
            SELECT COUNT(*) as count FROM supplier_analysis
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        count_row = cursor.fetchone()
        supplier_count = count_row["count"] if count_row else 0
        
        return {
            "year": year,
            "supplier_count": supplier_count,
            "top_suppliers": suppliers,
            "top_n": top_n,
            "top_concentration": round(concentration, 2),
            "concentration_evaluation": conc_eval,
            "concentration_color": conc_color
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/risks")
async def get_risk_info(company_id: int) -> Dict[str, Any]:
    """获取风险信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT risk_type, risk_title, risk_detail, risk_amount, 
                   risk_date, risk_status, case_number
            FROM risk_info
            WHERE company_id = ?
            ORDER BY risk_date DESC
        ''', (company_id,))
        
        risks = []
        risk_counts = {}
        for row in cursor.fetchall():
            risk_type = row["risk_type"]
            risk_counts[risk_type] = risk_counts.get(risk_type, 0) + 1
            risks.append({
                "risk_type": risk_type,
                "risk_type_name": get_risk_type_name(risk_type),
                "risk_title": row["risk_title"],
                "risk_detail": row["risk_detail"],
                "risk_amount": row["risk_amount"],
                "risk_date": row["risk_date"],
                "risk_status": row["risk_status"],
                "case_number": row["case_number"]
            })
        
        # 风险等级评估
        total_risks = len(risks)
        if total_risks == 0:
            risk_level = "低"
            risk_color = "green"
        elif total_risks <= 2:
            risk_level = "中"
            risk_color = "yellow"
        else:
            risk_level = "高"
            risk_color = "red"
        
        return {
            "total_count": total_risks,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "risk_counts": risk_counts,
            "risks": risks
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/growth")
async def get_growth_metrics(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取成长性指标"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取当年和上年营收
        cursor.execute('''
            SELECT period_year, SUM(total_revenue) as revenue, SUM(net_profit) as profit
            FROM income_statements
            WHERE company_id = ? AND period_year IN (?, ?)
            GROUP BY period_year
        ''', (company_id, year, year - 1))
        
        # Convert sqlite3.Row objects to regular dicts
        data = {}
        for row in cursor.fetchall():
            data[row["period_year"]] = {
                "revenue": row["revenue"],
                "profit": row["profit"]
            }
        
        current = data.get(year, {})
        previous = data.get(year - 1, {})
        
        current_revenue = current.get("revenue", 0) or 0
        previous_revenue = previous.get("revenue", 0) or 0
        current_profit = current.get("profit", 0) or 0
        previous_profit = previous.get("profit", 0) or 0
        
        # 计算增长率
        revenue_growth = ((current_revenue - previous_revenue) / previous_revenue * 100 
                          if previous_revenue and previous_revenue > 0 else 0)
        profit_growth = ((current_profit - previous_profit) / abs(previous_profit) * 100 
                         if previous_profit and previous_profit != 0 else 0)
        
        rev_eval, rev_color = evaluate_growth(revenue_growth)
        profit_eval, profit_color = evaluate_growth(profit_growth)
        
        return {
            "year": year,
            "current_revenue": round(current_revenue, 2) if current_revenue else 0,
            "previous_revenue": round(previous_revenue, 2) if previous_revenue else 0,
            "revenue_growth_rate": round(revenue_growth, 2),
            "revenue_evaluation": rev_eval,
            "revenue_color": rev_color,
            "current_profit": round(current_profit, 2) if current_profit else 0,
            "previous_profit": round(previous_profit, 2) if previous_profit else 0,
            "profit_growth_rate": round(profit_growth, 2),
            "profit_evaluation": profit_eval,
            "profit_color": profit_color
        }
    finally:
        conn.close()


@router.get("/company-profile/{company_id}/cashflow")
async def get_cash_flow_summary(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取现金流摘要"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(net_cash_operating) as operating,
                   SUM(net_cash_investing) as investing,
                   SUM(net_cash_financing) as financing,
                   SUM(net_increase_cash) as net_increase
            FROM cash_flow_statements
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        
        row = cursor.fetchone()
        
        operating = row["operating"] if row and row["operating"] else 0
        investing = row["investing"] if row and row["investing"] else 0
        financing = row["financing"] if row and row["financing"] else 0
        net_increase = row["net_increase"] if row and row["net_increase"] else 0
        
        # 经营现金流评价
        op_eval, op_color = ("正向", "green") if operating > 0 else ("负向", "red")
        
        return {
            "year": year,
            "operating_cash_flow": round(operating, 2),
            "investing_cash_flow": round(investing, 2),
            "financing_cash_flow": round(financing, 2),
            "net_increase": round(net_increase, 2),
            "operating_evaluation": op_eval,
            "operating_color": op_color
        }
    finally:
        conn.close()


# =============================================================================
# 辅助函数
# =============================================================================

def evaluate_metric(metric_type: str, value: float) -> tuple:
    """评估指标并返回评价文本和颜色"""
    evaluations = {
        "asset_liability_ratio": [
            (40, "优秀", "green"),
            (60, "稳健", "blue"),
            (80, "偏高", "yellow"),
            (100, "风险", "red")
        ],
        "current_ratio": [
            (2.0, "优秀", "green"),
            (1.5, "稳健", "blue"),
            (1.0, "一般", "yellow"),
            (0, "风险", "red")
        ],
        "quick_ratio": [
            (1.5, "优秀", "green"),
            (1.0, "稳健", "blue"),
            (0.5, "一般", "yellow"),
            (0, "风险", "red")
        ],
        "gross_margin": [
            (40, "优秀", "green"),
            (25, "良好", "blue"),
            (15, "一般", "yellow"),
            (0, "较低", "red")
        ],
        "net_margin": [
            (15, "优秀", "green"),
            (8, "良好", "blue"),
            (3, "一般", "yellow"),
            (0, "较低", "red")
        ],
        "roe": [
            (15, "优秀", "green"),
            (10, "良好", "blue"),
            (5, "一般", "yellow"),
            (0, "较低", "red")
        ],
        "roa": [
            (10, "优秀", "green"),
            (5, "良好", "blue"),
            (2, "一般", "yellow"),
            (0, "较低", "red")
        ],
        "vat_burden": [
            (2, "较低", "green"),
            (5, "适中", "blue"),
            (8, "偏高", "yellow"),
            (100, "过高", "red")
        ],
        "cit_burden": [
            (1, "较低", "green"),
            (3, "适中", "blue"),
            (5, "偏高", "yellow"),
            (100, "过高", "red")
        ],
        "total_tax_burden": [
            (3, "较低", "green"),
            (8, "适中", "blue"),
            (12, "偏高", "yellow"),
            (100, "过高", "red")
        ]
    }
    
    thresholds = evaluations.get(metric_type, [])
    
    # 对于比率类指标，值越低越好的特殊处理
    if metric_type in ["asset_liability_ratio", "vat_burden", "cit_burden", "total_tax_burden"]:
        for threshold, text, color in thresholds:
            if value <= threshold:
                return (text, color)
        return ("风险", "red")
    else:
        # 值越高越好
        for threshold, text, color in reversed(thresholds):
            if value >= threshold:
                return (text, color)
        return ("较低", "red")


def evaluate_concentration(concentration: float) -> tuple:
    """评估集中度"""
    if concentration < 30:
        return ("分散", "green")
    elif concentration < 50:
        return ("适中", "blue")
    elif concentration < 70:
        return ("较集中", "yellow")
    else:
        return ("高度集中", "red")


def evaluate_growth(growth_rate: float) -> tuple:
    """评估增长率"""
    if growth_rate >= 30:
        return ("高速增长", "green")
    elif growth_rate >= 10:
        return ("稳定增长", "blue")
    elif growth_rate >= 0:
        return ("平稳", "yellow")
    else:
        return ("下降", "red")


def get_risk_type_name(risk_type: str) -> str:
    """获取风险类型中文名称"""
    names = {
        "lawsuit": "诉讼信息",
        "execution": "被执行信息",
        "dishonest": "失信信息",
        "penalty": "行政处罚",
        "tax_violation": "税务违法",
        "overdue_tax": "欠税信息",
        "equity_freeze": "股权冻结",
        "abnormal": "经营异常"
    }
    return names.get(risk_type, risk_type)
