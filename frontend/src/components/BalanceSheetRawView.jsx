import React from 'react';
import './BalanceSheetRawView.css';

const BalanceSheetRawView = ({ data }) => {
    if (!data) return null;

    const fmt = (val) => {
        if (val === null || val === undefined) return '';
        return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    // Placeholder for beginning of year data
    const fmtStart = (val) => "";

    return (
        <div className="bs-raw-container">
            <div className="bs-title">资产负债表</div>

            <div className="bs-header-info">
                <span>编制单位：{data.company_id || 'ABC有限公司'}</span>
                <span>{data.period_year}年{data.period_month ? data.period_month + '月' : '12月31日'}</span>
                <span>单位：元</span>
            </div>

            <table className="bs-table">
                <thead>
                    <tr>
                        <th className="bs-col-item">资 产</th>
                        <th className="bs-col-line">行次</th>
                        <th className="bs-col-amount">期末余额</th>
                        <th className="bs-col-amount">年初余额</th>
                        <th className="bs-col-item">负债和所有者权益</th>
                        <th className="bs-col-line">行次</th>
                        <th className="bs-col-amount">期末余额</th>
                        <th className="bs-col-amount">年初余额</th>
                    </tr>
                </thead>
                <tbody>
                    {/* Row 1 */}
                    <tr>
                        <td className="bs-left">流动资产：</td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                        <td className="bs-left">流动负债：</td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                    </tr>
                    {/* Row 2: Cash | Short-term Loan */}
                    <tr>
                        <td className="bs-left bs-indent">货币资金</td>
                        <td className="bs-center">1</td>
                        <td className="bs-right">{fmt(data.cash_and_equivalents)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">短期借款</td>
                        <td className="bs-center">31</td>
                        <td className="bs-right">{fmt(data.short_term_loans)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 3: Trading Assets | Notes Payable */}
                    <tr>
                        <td className="bs-left bs-indent">短期投资</td>
                        <td className="bs-center">2</td>
                        <td className="bs-right">{fmt(data.trading_financial_assets)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应付票据</td>
                        <td className="bs-center">32</td>
                        <td className="bs-right">{fmt(data.notes_payable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 4: Notes Receivable | Accounts Payable */}
                    <tr>
                        <td className="bs-left bs-indent">应收票据</td>
                        <td className="bs-center">3</td>
                        <td className="bs-right">{fmt(data.notes_receivable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应付账款</td>
                        <td className="bs-center">33</td>
                        <td className="bs-right">{fmt(data.accounts_payable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 5: Accounts Receivable | Prepayments (Liab? No, Contract Liab / Adv. Receipts) */}
                    <tr>
                        <td className="bs-left bs-indent">应收账款</td>
                        <td className="bs-center">4</td>
                        <td className="bs-right">{fmt(data.accounts_receivable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">预收账款</td>
                        <td className="bs-center">34</td>
                        <td className="bs-right">{fmt(data.contract_liabilities)}</td> {/* Mapping Contract Liab to Pre-receipts */}
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 6: Prepayments | Employee Benefits */}
                    <tr>
                        <td className="bs-left bs-indent">预付账款</td>
                        <td className="bs-center">5</td>
                        <td className="bs-right">{fmt(data.prepayments)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应付职工薪酬</td>
                        <td className="bs-center">35</td>
                        <td className="bs-right">{fmt(data.employee_benefits_payable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 7: Div Receivable | Taxes Payable */}
                    <tr>
                        <td className="bs-left bs-indent">应收股利</td>
                        <td className="bs-center">6</td>
                        <td className="bs-right">{/* No fields in config */}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应交税费</td>
                        <td className="bs-center">36</td>
                        <td className="bs-right">{fmt(data.taxes_payable)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 8: Interest Receivable | Interest Payable */}
                    <tr>
                        <td className="bs-left bs-indent">应收利息</td>
                        <td className="bs-center">7</td>
                        <td className="bs-right">{/* No fields */}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应付利息</td>
                        <td className="bs-center">37</td>
                        <td className="bs-right">{/* No fields */}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 9: Other Receivable | Div Payable */}
                    <tr>
                        <td className="bs-left bs-indent">其他应收款</td>
                        <td className="bs-center">8</td>
                        <td className="bs-right">{fmt(data.other_receivables)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">应付利润</td>
                        <td className="bs-center">38</td>
                        <td className="bs-right">{/* No fields */}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row 10: Inventory | Other Payable */}
                    <tr>
                        <td className="bs-left bs-indent">存货</td>
                        <td className="bs-center">9</td>
                        <td className="bs-right">{fmt(data.inventory)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">其他应付款</td>
                        <td className="bs-center">39</td>
                        <td className="bs-right">{fmt(data.other_payables)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    {/* Row ... Total Current Assets | Total Current Liab */}
                    <tr>
                        <td className="bs-left bs-bold">流动资产合计</td>
                        <td className="bs-center">15</td>
                        <td className="bs-right bs-bold">{fmt(data.current_assets_total)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                        <td className="bs-left bs-bold">流动负债合计</td>
                        <td className="bs-center">41</td>
                        <td className="bs-right bs-bold">{fmt(data.current_liabilities_total)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                    </tr>

                    {/* Non-Current Assets | Non-Current Liabilities */}
                    <tr>
                        <td className="bs-left">非流动资产：</td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                        <td className="bs-left">非流动负债：</td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                    </tr>
                    {/* Fixed Assets | Long-term Loans */}
                    <tr>
                        <td className="bs-left bs-indent">长期股权投资</td>
                        <td className="bs-center">16</td>
                        <td className="bs-right">{fmt(data.long_term_equity_investment)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">长期借款</td>
                        <td className="bs-center">42</td>
                        <td className="bs-right">{fmt(data.long_term_loans)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td className="bs-left bs-indent">固定资产原价</td>
                        <td className="bs-center">18</td>
                        <td className="bs-right">{fmt(data.fixed_assets)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">长期应付款</td>
                        <td className="bs-center">43</td>
                        <td className="bs-right">{fmt(data.long_term_payables)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td className="bs-left bs-indent">减：累计折旧</td>
                        <td className="bs-center">19</td>
                        <td className="bs-right">{fmt(data.accumulated_depreciation)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent">递延收益</td>
                        <td className="bs-center">44</td>
                        <td className="bs-right">{fmt(data.deferred_revenue)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td className="bs-left bs-indent">在建工程</td>
                        <td className="bs-center">21</td>
                        <td className="bs-right">{fmt(data.construction_in_progress)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-indent"></td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                    </tr>
                    {/* Intangible | Total Non-Current Liab */}
                    <tr>
                        <td className="bs-left bs-indent">无形资产</td>
                        <td className="bs-center">25</td>
                        <td className="bs-right">{fmt(data.intangible_assets)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                        <td className="bs-left bs-bold">非流动负债合计</td>
                        <td className="bs-center">46</td>
                        <td className="bs-right bs-bold">{fmt(data.non_current_liabilities_total)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                    </tr>
                    {/* Total Assets | Total Liab */}
                    <tr>
                        <td className="bs-left bs-bold">非流动资产合计</td>
                        <td className="bs-center">29</td>
                        <td className="bs-right bs-bold">{fmt(data.non_current_assets_total)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                        <td className="bs-left bs-bold">负债合计</td>
                        <td className="bs-center">47</td>
                        <td className="bs-right bs-bold">{fmt(data.total_liabilities)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                    </tr>

                    {/* Empty Row for Separation */}
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        <td className="bs-left">所有者权益：</td>
                        <td className="bs-center"></td>
                        <td className="bs-right"></td>
                        <td className="bs-right"></td>
                    </tr>

                    {/* Final Totals: Assets | Equity Items */}
                    {/* Final Totals: Assets | Equity Items */}
                    {/* Paid-in Capital */}
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        {/* Equity Section nested in right col visually, but table row corresponds */}
                        <td className="bs-left bs-indent">实收资本</td>
                        <td className="bs-center">48</td>
                        <td className="bs-right">{fmt(data.paid_in_capital)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        <td className="bs-left bs-indent">资本公积</td>
                        <td className="bs-center">49</td>
                        <td className="bs-right">{fmt(data.capital_reserve)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        <td className="bs-left bs-indent">盈余公积</td>
                        <td className="bs-center">50</td>
                        <td className="bs-right">{fmt(data.surplus_reserve)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        <td className="bs-left bs-indent">未分配利润</td>
                        <td className="bs-center">51</td>
                        <td className="bs-right">{fmt(data.undistributed_profit)}</td>
                        <td className="bs-right">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td colSpan="4" style={{ border: 'none' }}></td>
                        <td className="bs-left bs-bold">所有者权益合计</td>
                        <td className="bs-center">52</td>
                        <td className="bs-right bs-bold">{fmt(data.total_equity)}</td>
                        <td className="bs-right bs-bold">{fmtStart()}</td>
                    </tr>
                    <tr>
                        <td className="bs-left bs-bold" style={{ borderBottom: 'double 3px black' }}>资产总计</td>
                        <td className="bs-center" style={{ borderBottom: 'double 3px black' }}>30</td>
                        <td className="bs-right bs-bold" style={{ borderBottom: 'double 3px black' }}>{fmt(data.total_assets)}</td>
                        <td className="bs-right bs-bold" style={{ borderBottom: 'double 3px black' }}>{fmtStart()}</td>
                        <td className="bs-left bs-bold" style={{ borderBottom: 'double 3px black' }}>负债和所有者权益总计</td>
                        <td className="bs-center" style={{ borderBottom: 'double 3px black' }}>53</td>
                        <td className="bs-right bs-bold" style={{ borderBottom: 'double 3px black' }}>
                            {fmt(data.total_liabilities_and_equity || (Number(data.total_liabilities || 0) + Number(data.total_equity || 0)))}
                        </td>
                        <td className="bs-right bs-bold" style={{ borderBottom: 'double 3px black' }}>{fmtStart()}</td>
                    </tr>

                </tbody>
            </table>
        </div>
    );
};

export default BalanceSheetRawView;
