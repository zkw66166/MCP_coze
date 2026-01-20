
import sqlite3
from typing import Dict, List, Any, Tuple
import logging

class DataQualityChecker:
    """
    数据质量检查器
    按企业、按期间、按表进行数据质量检测
    """
    
    # 表配置：表名 -> (中文名, 期间类型)
    TABLE_CONFIG = {
        'subject_balance': ('科目余额表', 'monthly', 'account_balances'),
        'balance_sheet': ('资产负债表', 'monthly', 'balance_sheets'),
        'income_statement': ('利润表', 'monthly', 'income_statements'),
        'cash_flow': ('现金流量表', 'monthly', 'cash_flow_statements'),
        'vat_return': ('增值税申报表', 'monthly', 'vat_returns'),
        'cit_return': ('企业所得税申报表', 'quarterly', 'tax_returns_income'),
        'stamp_duty': ('印花税申报表', 'quarterly', 'tax_returns_stamp'),
    }

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_available_periods(self, company_id: int) -> Dict[str, List[Tuple[int, int]]]:
        """
        获取指定企业在各表中的可用期间
        返回: { table_key: [(year, month), ...] }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        periods = {}
        
        for table_key, (cn_name, period_type, db_table) in self.TABLE_CONFIG.items():
            try:
                if period_type == 'monthly':
                    cursor.execute(f"""
                        SELECT DISTINCT period_year, period_month 
                        FROM {db_table} 
                        WHERE company_id = ? 
                        ORDER BY period_year, period_month
                    """, (company_id,))
                    periods[table_key] = [(r[0], r[1]) for r in cursor.fetchall()]
                else:  # quarterly/yearly - period_month可能不存在或用于不同用途
                    # 先检查是否有period_month字段
                    cursor.execute(f"PRAGMA table_info({db_table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if 'period_month' in columns:
                        cursor.execute(f"""
                            SELECT DISTINCT period_year, period_month 
                            FROM {db_table} 
                            WHERE company_id = ? 
                            ORDER BY period_year, period_month
                        """, (company_id,))
                        periods[table_key] = [(r[0], r[1] if r[1] else 0) for r in cursor.fetchall()]
                    else:
                        cursor.execute(f"""
                            SELECT DISTINCT period_year 
                            FROM {db_table} 
                            WHERE company_id = ? 
                            ORDER BY period_year
                        """, (company_id,))
                        periods[table_key] = [(r[0], 0) for r in cursor.fetchall()]
            except Exception as e:
                logging.warning(f"Error getting periods for {db_table}: {e}")
                periods[table_key] = []
        
        conn.close()
        return periods

    def check_all(self, company_id: int) -> Dict[str, Any]:
        """
        对指定企业执行全面数据质量检查
        遍历所有可用期间和所有表
        """
        # 获取所有可用期间
        all_periods = self.get_available_periods(company_id)
        
        results_by_table = {}
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        
        for table_key, (cn_name, period_type, db_table) in self.TABLE_CONFIG.items():
            periods = all_periods.get(table_key, [])
            period_results = []
            
            for year, month in periods:
                # 调用对应的检查方法
                check_method = getattr(self, f'check_{table_key}', None)
                if check_method:
                    if period_type == 'monthly':
                        result = check_method(company_id, year, month)
                    else:
                        result = check_method(company_id, year)
                    
                    # 格式化期间显示
                    if month and month > 0:
                        quarter = (month - 1) // 3 + 1
                        period_str = f"{year}Q{quarter}"
                    else:
                        period_str = str(year)
                    
                    # 统计
                    checks_in_period = result.get('total_checks', 0)
                    passed_in_period = result.get('passed_checks', 0)
                    total_checks += checks_in_period
                    passed_checks += passed_in_period
                    failed_checks += (checks_in_period - passed_in_period)
                    
                    period_results.append({
                        'period': period_str,
                        'year': year,
                        'month': month,
                        'status': result.get('status', 'skip'),
                        'message': result.get('message', ''),
                        'total_checks': checks_in_period,
                        'passed_checks': passed_in_period,
                        'details': result.get('details', [])
                    })
            
            # 计算表级别的总体状态
            if not period_results:
                table_status = 'skip'
            elif all(p['status'] == 'pass' for p in period_results):
                table_status = 'pass'
            elif all(p['status'] == 'skip' for p in period_results):
                table_status = 'skip'
            else:
                table_status = 'fail'
            
            results_by_table[table_key] = {
                'table_name': cn_name,
                'db_table': db_table,
                'period_count': len(period_results),
                'status': table_status,
                'periods': period_results
            }
        
        return {
            'company_id': company_id,
            'summary': {
                'total_tables': len(self.TABLE_CONFIG),
                'total_periods': sum(len(all_periods.get(k, [])) for k in self.TABLE_CONFIG.keys()),
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'pass_rate': round(passed_checks / total_checks * 100, 1) if total_checks > 0 else 0
            },
            'results_by_table': results_by_table
        }

    def _get_row(self, table: str, company_id: int, period_year: int, period_month: int = None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否有period_month列
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        query = f"SELECT * FROM {table} WHERE company_id = ? AND period_year = ?"
        params = [company_id, period_year]
        
        if period_month is not None and period_month > 0 and 'period_month' in columns:
            query += " AND period_month = ?"
            params.append(period_month)
             
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return row
    
    def _create_result(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates checks into a standard result format"""
        passed_count = sum(1 for c in checks if c['status'] == 'pass')
        total_count = len(checks)
        return {
            'total_checks': total_count,
            'passed_checks': passed_count,
            'status': 'pass' if passed_count == total_count else 'fail',
            'details': checks
        }

    def check_subject_balance(self, company_id, year, month):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM account_balances WHERE company_id = ? AND period_year = ? AND period_month = ?",
            (company_id, year, month)
        )
        rows = cursor.fetchall()
        conn.close()

        checks = []
        if not rows:
            return {'status': 'skip', 'message': '无数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}

        # Check 1: Balance Logic Per Row
        for row in rows:
            opening = row['opening_balance'] or 0
            debit = row['debit_amount'] or 0
            credit = row['credit_amount'] or 0
            closing = row['ending_balance'] or 0
            
            # Try both directions
            calc1 = opening + debit - credit
            calc2 = opening - debit + credit
            
            valid = False
            if abs(calc1 - closing) < 0.01: valid = True
            elif abs(calc2 - closing) < 0.01: valid = True
            
            if not valid:
                checks.append({
                    'check': f"科目 {row['account_code']} 余额勾稽",
                    'status': 'fail',
                    'message': f"期初({opening}) + 借方({debit}) - 贷方({credit}) ≠ 期末({closing})",
                    'expected': calc1,
                    'actual': closing
                })

        if not checks:
            checks.append({'check': '科目余额内部勾稽', 'status': 'pass', 'message': '所有科目勾稽正确'})
            
        return self._create_result(checks)

    def check_balance_sheet(self, company_id, year, month):
        row = self._get_row('balance_sheets', company_id, year, month)
        if not row: 
            return {'status': 'skip', 'message': '无数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}
        
        checks = []
        
        def val(key): 
            try:
                return row[key] or 0
            except:
                return 0
                
        def check_eq(name, left, right, tolerance=0.01):
            if abs(left - right) < tolerance:
                checks.append({'check': name, 'status': 'pass', 'message': '一致'})
            else:
                checks.append({'check': name, 'status': 'fail', 'message': f"差异: {left - right:.2f}", 'expected': right, 'actual': left})

        # 1. 资产=负债+权益
        check_eq("资产=负债+权益", val('total_assets'), val('total_liabilities') + val('total_equity'))
        
        # 2. 资产结构
        check_eq("资产结构", val('total_assets'), val('current_assets_total') + val('non_current_assets_total'))
        
        # 3. 负债结构
        check_eq("负债结构", val('total_liabilities'), val('current_liabilities_total') + val('non_current_liabilities_total'))
        
        # 4. 流动资产明细
        ca_calc = (val('cash_and_equivalents') + val('trading_financial_assets') + val('accounts_receivable') + 
                  val('prepayments') + val('other_receivables') + val('inventory') + val('notes_receivable') + 
                  val('contract_assets') + val('current_assets'))
        check_eq("流动资产明细", val('current_assets_total'), ca_calc, tolerance=1000)
        
        # 5. 非流动资产明细
        nca_calc = (val('long_term_equity_investment') + val('fixed_assets') + val('construction_in_progress') + 
                   val('intangible_assets') + val('goodwill') + val('long_term_deferred_expenses') + 
                   val('deferred_tax_assets') + val('other_non_current_assets'))
        check_eq("非流动资产明细", val('non_current_assets_total'), nca_calc, tolerance=1000)

        return self._create_result(checks)

    def check_income_statement(self, company_id, year, month):
        row = self._get_row('income_statements', company_id, year, month)
        if not row: 
            return {'status': 'skip', 'message': '无数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}
        
        checks = []
        def val(key): 
            try:
                return row[key] or 0
            except:
                return 0
                
        def check_eq(name, left, right, tolerance=0.01):
            if abs(left - right) < tolerance:
                checks.append({'check': name, 'status': 'pass', 'message': '一致'})
            else:
                checks.append({'check': name, 'status': 'fail', 'message': f"差异: {left - right:.2f}", 'expected': right, 'actual': left})

        # 1. 营业利润
        op_calc = (val('operating_revenue') - val('operating_costs') - val('taxes_and_surcharges') - 
                   val('selling_expenses') - val('administrative_expenses') - val('financial_expenses') + 
                   val('other_income') + val('investment_income'))
        check_eq("营业利润计算", val('operating_profit'), op_calc, tolerance=1.0)
        
        # 2. 利润总额
        tp_calc = val('operating_profit') + val('non_operating_income') - val('non_operating_expenses')
        check_eq("利润总额计算", val('total_profit'), tp_calc, tolerance=1.0)
        
        # 3. 净利润
        np_calc = val('total_profit') - val('income_tax_expense')
        check_eq("净利润计算", val('net_profit'), np_calc, tolerance=1.0)
        
        return self._create_result(checks)

    def check_cash_flow(self, company_id, year, month=None):
        row = self._get_row('cash_flow_statements', company_id, year, month)
        if not row: 
            return {'status': 'skip', 'message': '无数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}
        
        checks = []
        def val(key): 
            try:
                return row[key] or 0
            except:
                return 0
                
        def check_eq(name, left, right, tolerance=0.01):
            if abs(left - right) < tolerance:
                checks.append({'check': name, 'status': 'pass', 'message': '一致'})
            else:
                checks.append({'check': name, 'status': 'fail', 'message': f"差异: {left - right:.2f}", 'expected': right, 'actual': left})

        # 1. 经营活动净额
        check_eq("经营活动净额", val('net_cash_operating'), val('subtotal_operate_inflow') - val('subtotal_operate_outflow'))
        
        # 2. 投资活动净额
        check_eq("投资活动净额", val('net_cash_investing'), val('subtotal_invest_inflow') - val('subtotal_invest_outflow'))
        
        # 3. 筹资活动净额
        check_eq("筹资活动净额", val('net_cash_financing'), val('subtotal_finance_inflow') - val('subtotal_finance_outflow'))
        
        # 4. 现金净增加额
        check_eq("现金净增加额", val('net_increase_cash'), 
                 val('net_cash_operating') + val('net_cash_investing') + val('net_cash_financing') + val('exchange_rate_effect'))
        
        # 5. 期末现金
        check_eq("期末现金余额", val('cash_ending'), val('cash_beginning') + val('net_increase_cash'))
        
        return self._create_result(checks)

    def check_vat_return(self, company_id, year, month):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM vat_returns WHERE company_id=? AND period_year=? AND period_month=?", (company_id, year, month))
        ret = cur.fetchone()
        
        if not ret:
            conn.close()
            return {'status': 'skip', 'message': '无申报数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}
            
        ret_id = ret['id']
        cur.execute("SELECT * FROM vat_return_items WHERE return_id=?", (ret_id,))
        items = cur.fetchall()
        conn.close()
        
        item_map = {item['item_name']: (item['amount_current'] or 0) for item in items}
        
        checks = []
        
        # 查找关键项目
        output = 0
        input_tax = 0
        payable = 0
        
        for k, v in item_map.items():
            if "销项" in k and "税额" in k: output = v
            if "进项" in k and "税额" in k and "转出" not in k: input_tax = v
            if "应纳税额" in k and "合计" not in k: payable = v
            
        if output and input_tax:
            expected = output - input_tax
            if abs(payable - expected) < 1.0:
                checks.append({'check': '增值税进销项勾稽', 'status': 'pass', 'message': f"应纳税额 {payable} ≈ 销项 {output} - 进项 {input_tax}"})
            else:
                checks.append({'check': '增值税进销项勾稽', 'status': 'fail', 'message': f"应纳税额 {payable} ≠ 销项 {output} - 进项 {input_tax}", 'expected': expected, 'actual': payable})

        if not checks:
            checks.append({'check': '增值税基本结构', 'status': 'pass', 'message': '申报表结构完整'})

        return self._create_result(checks)

    def check_cit_return(self, company_id, year):
        row = self._get_row('tax_returns_income', company_id, year)
        if not row: 
            return {'status': 'skip', 'message': '无数据', 'details': [], 'total_checks': 0, 'passed_checks': 0}
        
        checks = []
        def val(key): 
            try:
                return row[key] or 0
            except:
                return 0
                
        def check_eq(name, left, right, tolerance=1.0):
            if abs(left - right) < tolerance:
                checks.append({'check': name, 'status': 'pass', 'message': '一致'})
            else:
                checks.append({'check': name, 'status': 'fail', 'message': f"差异: {left - right:.2f}", 'expected': right, 'actual': left})
            
        # 1. 利润总额
        profit_calc = (val('revenue') - val('cost') - val('taxes_and_surcharges') - 
                       val('selling_expenses') - val('administrative_expenses') - val('financial_expenses'))
        check_eq("利润总额计算", val('total_profit'), profit_calc)
        
        # 2. 应纳税额
        check_eq("应纳税额计算", val('nominal_tax'), val('taxable_income') * val('tax_rate'))
        
        # 3. 实际应纳税额
        check_eq("实际应纳税额", val('final_tax_payable'), val('nominal_tax') - val('tax_reduction'))
        
        return self._create_result(checks)

    def check_stamp_duty(self, company_id, year):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM tax_returns_stamp WHERE company_id=? AND period_year=? LIMIT 1", (company_id, year))
        ret = cur.fetchone()
        
        if not ret:
            conn.close()
            return {'status': 'skip', 'message': '无印花税申报', 'details': [], 'total_checks': 0, 'passed_checks': 0}
            
        ret_id = ret['id']
        cur.execute("SELECT * FROM tax_return_stamp_items WHERE return_id=?", (ret_id,))
        items = cur.fetchall()
        conn.close()
        
        checks = []
        for item in items:
            base = item['tax_base'] or 0
            rate = item['tax_rate'] or 0
            payable = item['tax_payable'] or 0
            
            calc = base * rate
            if abs(payable - calc) < 0.01:
                checks.append({'check': f"印花税-{item['tax_item']}", 'status': 'pass', 'message': '计算正确'})
            else:
                checks.append({'check': f"印花税-{item['tax_item']}", 'status': 'fail', 'message': f"税基×税率({calc:.2f}) ≠ 应纳({payable:.2f})", 'expected': calc, 'actual': payable})
        
        if not checks:
            checks.append({'check': '印花税基本结构', 'status': 'pass', 'message': '申报数据完整'})
                
        return self._create_result(checks)
