import React from 'react';
import './CashFlowStatementRawView.css';

const CashFlowStatementRawView = ({ data, companyInfo }) => {
    if (!data) return null;

    const fmt = (val) => {
        if (val === null || val === undefined) return '';
        return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    // Placeholder for Year-to-Date (Previous Period is usually not in single record unless joined)
    // Assuming backend data might eventually have it, or we leave it blank for now.
    const fmtYTD = (val) => "";

    const companyName = companyInfo ? companyInfo.name : (data.company_id || 'ABC有限公司');

    return (
        <div className="cs-raw-container">
            <div className="cs-title">现金流量表</div>

            <div className="cs-header-info">
                <span>编制单位：{companyName}</span>
                <span>{data.period_year}年{data.period_month ? data.period_month + '月' : (data.period_quarter ? 'Q' + data.period_quarter : '')}</span>
                <span>金额单位：元</span>
            </div>

            <table className="cs-table">
                <thead>
                    <tr>
                        <th className="cs-col-item">项      目</th>
                        <th className="cs-col-line">行次</th>
                        <th className="cs-col-amount">本期金额</th>
                        <th className="cs-col-amount">本年累计金额</th>
                    </tr>
                </thead>
                <tbody>
                    {/* 一、经营活动产生的现金流量 */}
                    <tr>
                        <td className="cs-left">一、经营活动产生的现金流量：</td>
                        <td className="cs-center"></td>
                        <td className="cs-right"></td>
                        <td className="cs-right"></td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">销售产成品、成品、提供劳务收到的现金</td>
                        <td className="cs-center">1</td>
                        <td className="cs-right">{fmt(data.cash_received_goods_services)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">收到其他与经营活动有关的现金</td>
                        <td className="cs-center">2</td>
                        <td className="cs-right">{fmt(data.cash_received_other_operating)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">购买原材料、商品、接收劳务支付的现金</td>
                        <td className="cs-center">3</td>
                        <td className="cs-right">{fmt(data.cash_paid_goods_services)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">支付的职工薪酬</td>
                        <td className="cs-center">4</td>
                        <td className="cs-right">{fmt(data.cash_paid_employees)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">支付的税费</td>
                        <td className="cs-center">5</td>
                        <td className="cs-right">{fmt(data.cash_paid_taxes)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">支付其他与经营活动有关的现金</td>
                        <td className="cs-center">6</td>
                        <td className="cs-right">{fmt(data.cash_paid_other_operating)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">经营活动产生的现金流量净额</td>
                        <td className="cs-center">7</td>
                        <td className="cs-right">{fmt(data.net_cash_operating)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>

                    {/* 二、投资活动产生的现金流量 */}
                    <tr>
                        <td className="cs-left">二、投资活动产生的现金流量</td>
                        <td className="cs-center"></td>
                        <td className="cs-right"></td>
                        <td className="cs-right"></td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">收回短期投资、长期债券投资和长期股权投资收到的现金</td>
                        <td className="cs-center">8</td>
                        <td className="cs-right">{fmt(data.cash_received_investment_disposal)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">取得投资收益收到的现金</td>
                        <td className="cs-center">9</td>
                        <td className="cs-right">{fmt(data.cash_received_investment_return)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">处置固定资产、无形资产和其他非流动资产收回的现金净额</td>
                        <td className="cs-center">10</td>
                        <td className="cs-right">{fmt(data.cash_received_asset_disposal)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">短期投资、长期债券投资和长期股权投资支付的现金</td>
                        <td className="cs-center">11</td>
                        <td className="cs-right">{fmt(data.cash_paid_investments)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">购建固定资产、无形资产和其他非流动资产支付的现金</td>
                        <td className="cs-center">12</td>
                        <td className="cs-right">{fmt(data.cash_paid_asset_acquisition)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">投资活动产生的现金流量净额</td>
                        <td className="cs-center">13</td>
                        <td className="cs-right">{fmt(data.net_cash_investing)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>

                    {/* 三、筹资活动产生的现金流量 */}
                    <tr>
                        <td className="cs-left">三、筹资活动产生的现金流量：</td>
                        <td className="cs-center"></td>
                        <td className="cs-right"></td>
                        <td className="cs-right"></td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">取得借款收到的现金</td>
                        <td className="cs-center">14</td>
                        <td className="cs-right">{fmt(data.cash_received_borrowings)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">吸收投资者投资收到的现金</td>
                        <td className="cs-center">15</td>
                        <td className="cs-right">{fmt(data.cash_received_capital_contribution)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">偿还借款本金支付的现金</td>
                        <td className="cs-center">16</td>
                        <td className="cs-right">{fmt(data.cash_paid_debt_repayment)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">偿还借款利息支付的现金</td>
                        <td className="cs-center">17</td>
                        <td className="cs-right">{fmt(data.cash_paid_interest_dividends)}</td> {/* Note: This might mix interest and dividends */}
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">分配利润支付的现金</td>
                        <td className="cs-center">18</td>
                        <td className="cs-right">{/* Separate field if exists, else share above */}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left cs-indent">筹资活动产生的现金流量净额</td>
                        <td className="cs-center">19</td>
                        <td className="cs-right">{fmt(data.net_cash_financing)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>

                    {/* 四、现金净增加额 */}
                    <tr>
                        <td className="cs-left">四、现金净增加额</td>
                        <td className="cs-center">20</td>
                        <td className="cs-right">{fmt(data.net_increase_in_cash_and_equivalents)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left">加：期初现金余额</td>
                        <td className="cs-center">21</td>
                        <td className="cs-right">{fmt(data.cash_at_beginning_of_period)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                    <tr>
                        <td className="cs-left">五、期末现金余额</td>
                        <td className="cs-center">22</td>
                        <td className="cs-right">{fmt(data.cash_at_end_of_period)}</td>
                        <td className="cs-right">{fmtYTD()}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default CashFlowStatementRawView;
