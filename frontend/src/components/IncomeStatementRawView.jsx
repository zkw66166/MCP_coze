import React from 'react';
import './IncomeStatementRawView.css';

const IncomeStatementRawView = ({ data, companyInfo }) => {
    if (!data) return null;

    // Helper for formatting numbers
    const fmt = (val) => {
        if (val === null || val === undefined) return '';
        // If it's 0, should we show 0.00? Yes, usually.
        return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    // Helper for "Year-to-Date" or "Previous Period"
    // Currently backend only returns one set of data in `data`.
    // We assume `data` contains the values for "Current Period" (本期金额).
    // The "Year to Date" (本年累计金额) is not available efficiently without extra queries.
    // We will leave the second column blank for now or render same if it's annual?
    // Let's leave it blank to be accurate.
    const fmtYTD = (val) => {
        return ""; // Placeholder
    };

    const companyName = companyInfo ? companyInfo.name : (data.company_id || 'ABC有限公司');

    return (
        <div className="is-raw-container">
            <div className="is-title">利润表</div>

            <div className="is-header-info">
                <span>编制单位：{companyName}</span>
                {/* valid point: row data only has company_id. DataBrowser has selectedCompany name. */}
                {/* For now, just show blank or period. */}
                <span>所属时间：{data.period_year}年{data.period_month ? data.period_month + '月' : (data.period_quarter ? 'Q' + data.period_quarter : '')}</span>
                <span>单位：元</span>
            </div>

            <table className="is-table">
                <thead>
                    <tr>
                        <th className="is-col-item">项      目</th>
                        <th className="is-col-line">行  次</th>
                        <th className="is-col-amount">本期金额</th>
                        <th className="is-col-amount">本年累计金额</th>
                    </tr>
                </thead>
                <tbody>
                    {/* 一、营业收入 */}
                    <tr>
                        <td className="is-left">一、营业收入</td>
                        <td className="is-center">1</td>
                        <td className="is-right">{fmt(data.total_revenue)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">减：营业成本</td>
                        <td className="is-center">2</td>
                        <td className="is-right">{fmt(data.cost_of_sales)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">税金及附加</td>
                        <td className="is-center">3</td>
                        <td className="is-right">{fmt(data.taxes_and_surcharges)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">销售费用</td>
                        <td className="is-center">4</td>
                        <td className="is-right">{fmt(data.selling_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">管理费用</td>
                        <td className="is-center">5</td>
                        <td className="is-right">{fmt(data.administrative_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">研发费用</td>
                        <td className="is-center">6</td>
                        <td className="is-right">{fmt(data.rd_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">财务费用</td>
                        <td className="is-center">7</td>
                        <td className="is-right">{fmt(data.financial_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">其中：利息费用</td>
                        <td className="is-center">8</td>
                        <td className="is-right">{fmt(data.interest_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">      利息收入</td>
                        <td className="is-center">9</td>
                        <td className="is-right">{fmt(data.interest_income)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">加：其他收益</td>
                        <td className="is-center">10</td>
                        <td className="is-right">{fmt(data.other_income)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">    投资收益（损失以“-”号填列）</td>
                        <td className="is-center">11</td>
                        <td className="is-right">{fmt(data.investment_income)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">    公允价值变动收益（损失以“-”号填列）</td>
                        <td className="is-center">12</td>
                        <td className="is-right">{fmt(data.fair_value_gains)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">    信用减值损失（损失以“-”号填列）</td>
                        <td className="is-center">13</td>
                        <td className="is-right">{fmt(data.credit_impairment_losses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">    资产减值损失（损失以“-”号填列）</td>
                        <td className="is-center">14</td>
                        <td className="is-right">{fmt(data.asset_impairment_losses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">    资产处置收益（损失以“-”号填列）</td>
                        <td className="is-center">15</td>
                        <td className="is-right">{fmt(data.asset_disposal_income)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>

                    {/* 二、营业利润 */}
                    <tr>
                        <td className="is-left">二、营业利润（亏损以“-”号填列）</td>
                        <td className="is-center">18</td>
                        <td className="is-right">{fmt(data.operating_profit)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">加：营业外收入</td>
                        <td className="is-center">19</td>
                        <td className="is-right">{fmt(data.non_operating_income)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">减：营业外支出</td>
                        <td className="is-center">20</td>
                        <td className="is-right">{fmt(data.non_operating_expenses)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>

                    {/* 三、利润总额 */}
                    <tr>
                        <td className="is-left">三、利润总额（亏损总额以“-”号填列）</td>
                        <td className="is-center">21</td>
                        <td className="is-right">{fmt(data.total_profit)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="is-left is-indent">减：所得税费用</td>
                        <td className="is-center">22</td>
                        <td className="is-right">{fmt(data.income_tax_expense)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>

                    {/* 四、净利润 */}
                    <tr>
                        <td className="is-left">四、净利润（净亏损以“-”号填列）</td>
                        <td className="is-center">23</td>
                        <td className="is-right">{fmt(data.net_profit)}</td>
                        <td className="is-right">{fmtYTD()}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default IncomeStatementRawView;
