#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业画像财务摘要API - 从预加工表读取版本

替换company_profile.py中的get_financial_summary函数
从financial_metrics表读取预计算的指标，而非实时计算
"""

@router.get("/company-profile/{company_id}/financial")
async def get_financial_summary(company_id: int, year: Optional[int] = None) -> Dict[str, Any]:
    """获取财务状况摘要（从预加工表读取）"""
    if year is None:
        year = datetime.now().year
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 从financial_metrics表读取最新季度的预计算指标
        cursor.execute('''
            SELECT *
            FROM financial_metrics
            WHERE company_id = ? AND period_year = ?
            ORDER BY period_quarter DESC
            LIMIT 1
        ''', (company_id, year))
        fm_row = cursor.fetchone()
        
        # 获取基础财务数据（用于显示，非计算）
        cursor.execute('''
            SELECT total_assets, total_liabilities, total_equity
            FROM balance_sheets
            WHERE company_id = ? AND period_year = ?
            ORDER BY period_quarter DESC, period_month DESC
            LIMIT 1
        ''', (company_id, year))
        bs_row = cursor.fetchone()
        
        cursor.execute('''
            SELECT SUM(total_revenue) as revenue, SUM(net_profit) as net_profit,
                   SUM(selling_expenses) as sales_expense, SUM(administrative_expenses) as admin_expense
            FROM income_statements
            WHERE company_id = ? AND period_year = ?
        ''', (company_id, year))
        is_row = cursor.fetchone()
        
        # 构建指标列表（从预加工表读取）
        metrics = []
        
        if fm_row:
            # 盈利能力指标
            if fm_row["gross_profit_margin"] is not None:
                eval_text, eval_color = evaluate_metric("gross_margin", fm_row["gross_profit_margin"])
                metrics.append({
                    "name": "毛利率",
                    "value": round(fm_row["gross_profit_margin"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            if fm_row["net_profit_margin"] is not None:
                eval_text, eval_color = evaluate_metric("net_margin", fm_row["net_profit_margin"])
                metrics.append({
                    "name": "净利率",
                    "value": round(fm_row["net_profit_margin"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 偿债能力指标
            if fm_row["asset_liability_ratio"] is not None:
                eval_text, eval_color = evaluate_metric("asset_liability_ratio", fm_row["asset_liability_ratio"])
                metrics.append({
                    "name": "资产负债率",
                    "value": round(fm_row["asset_liability_ratio"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            if fm_row["current_ratio"] is not None:
                eval_text, eval_color = evaluate_metric("current_ratio", fm_row["current_ratio"])
                metrics.append({
                    "name": "流动比率",
                    "value": round(fm_row["current_ratio"], 2),
                    "unit": "",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            if fm_row["quick_ratio"] is not None:
                eval_text, eval_color = evaluate_metric("quick_ratio", fm_row["quick_ratio"])
                metrics.append({
                    "name": "速动比率",
                    "value": round(fm_row["quick_ratio"], 2),
                    "unit": "",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 运营效率指标
            if fm_row["total_asset_turnover"] is not None:
                metrics.append({
                    "name": "总资产周转率",
                    "value": round(fm_row["total_asset_turnover"], 2),
                    "unit": "次",
                    "evaluation": "良好" if fm_row["total_asset_turnover"] >= 1.0 else "一般",
                    "evaluation_color": "green" if fm_row["total_asset_turnover"] >= 1.0 else "yellow"
                })
            
            if fm_row["receivable_turnover_days"] is not None:
                metrics.append({
                    "name": "应收账款周转天数",
                    "value": round(fm_row["receivable_turnover_days"], 2),
                    "unit": "天",
                    "evaluation": "优秀" if fm_row["receivable_turnover_days"] <= 60 else "一般",
                    "evaluation_color": "green" if fm_row["receivable_turnover_days"] <= 60 else "yellow"
                })
            
            # 成长性指标
            if fm_row["revenue_growth_rate"] is not None:
                eval_text, eval_color = evaluate_growth(fm_row["revenue_growth_rate"])
                metrics.append({
                    "name": "营业收入增长率",
                    "value": round(fm_row["revenue_growth_rate"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            if fm_row["profit_growth_rate"] is not None:
                eval_text, eval_color = evaluate_growth(fm_row["profit_growth_rate"])
                metrics.append({
                    "name": "净利润增长率",
                    "value": round(fm_row["profit_growth_rate"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            if fm_row["asset_growth_rate"] is not None:
                eval_text, eval_color = evaluate_growth(fm_row["asset_growth_rate"])
                metrics.append({
                    "name": "资产增长率",
                    "value": round(fm_row["asset_growth_rate"], 2),
                    "unit": "%",
                    "evaluation": eval_text,
                    "evaluation_color": eval_color
                })
            
            # 成本费用指标（新增）
            if fm_row["sales_expense"] is not None:
                metrics.append({
                    "name": "销售费用",
                    "value": round(fm_row["sales_expense"], 2),
                    "unit": "万元",
                    "evaluation": None,
                    "evaluation_color": None
                })
            
            if fm_row["admin_expense"] is not None:
                metrics.append({
                    "name": "管理费用",
                    "value": round(fm_row["admin_expense"], 2),
                    "unit": "万元",
                    "evaluation": None,
                    "evaluation_color": None
                })
            
            if fm_row["selling_expense_ratio"] is not None:
                metrics.append({
                    "name": "销售费用率",
                    "value": round(fm_row["selling_expense_ratio"], 2),
                    "unit": "%",
                    "evaluation": "合理" if fm_row["selling_expense_ratio"] <= 20 else "偏高",
                    "evaluation_color": "green" if fm_row["selling_expense_ratio"] <= 20 else "yellow"
                })
            
            if fm_row["admin_expense_ratio"] is not None:
                metrics.append({
                    "name": "管理费用率",
                    "value": round(fm_row["admin_expense_ratio"], 2),
                    "unit": "%",
                    "evaluation": "合理" if fm_row["admin_expense_ratio"] <= 15 else "偏高",
                    "evaluation_color": "green" if fm_row["admin_expense_ratio"] <= 15 else "yellow"
                })
            
            # 现金流指标（新增）
            cash_flow_data = {
                "operating": fm_row["operating_cash_flow"] if fm_row["operating_cash_flow"] is not None else 0,
                "investing": fm_row["investing_cash_flow"] if fm_row["investing_cash_flow"] is not None else 0,
                "financing": fm_row["financing_cash_flow"] if fm_row["financing_cash_flow"] is not None else 0,
            }
        else:
            # 如果没有预计算数据，返回空指标列表
            cash_flow_data = {
                "operating": 0,
                "investing": 0,
                "financing": 0,
            }
        
        return {
            "year": year,
            "total_assets": bs_row["total_assets"] if bs_row else 0,
            "total_liabilities": bs_row["total_liabilities"] if bs_row else 0,
            "total_equity": bs_row["total_equity"] if bs_row else 0,
            "revenue": is_row["revenue"] if is_row and is_row["revenue"] else 0,
            "net_profit": is_row["net_profit"] if is_row and is_row["net_profit"] else 0,
            "metrics": metrics,
            "cash_flow": cash_flow_data,  # 新增现金流数据
            "sales_expense": fm_row["sales_expense"] if fm_row and fm_row["sales_expense"] else (is_row["sales_expense"] if is_row else 0),
            "admin_expense": fm_row["admin_expense"] if fm_row and fm_row["admin_expense"] else (is_row["admin_expense"] if is_row else 0),
            "data_source": "precomputed" if fm_row else "realtime",  # 标识数据来源
            "last_updated": fm_row["updated_at"] if fm_row and "updated_at" in dict(fm_row).keys() else None
        }
    finally:
        conn.close()
