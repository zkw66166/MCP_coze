
import React from 'react';
import './VatReturnRawView.css';

const VatReturnRawView = ({ data, companyInfo }) => {
    if (!data) return <div className="vat-raw-container">暂无数据</div>;

    // Helper to format currency
    const fmt = (val) => {
        if (val === null || val === undefined) return '';
        return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    // Helper for N/A cells
    const NA = <div className="vat-na">——</div>;

    const info = companyInfo || {};

    return (
        <div className="vat-raw-container">
            <div className="vat-title">增值税及附加税费申报表</div>
            <div className="vat-subtitle">（一般纳税人适用）</div>

            <div className="vat-header-info">
                <span>税款所属时间：{data.start_date || '2024年X月X日'} 至 {data.end_date || '2024年X月X日'}</span>
                <span>填表日期：{data.filing_date}</span>
                <span>金额单位：元</span>
            </div>

            <div style={{ display: 'flex', fontSize: '12px', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span>纳税人识别号：{info.tax_code || ''}</span>
                <span>所属行业：{info.industry || ''}</span>
            </div>
            <div style={{ display: 'flex', fontSize: '12px', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span>纳税人名称：{info.name || data.company_name || ''}</span>
                <span>法定代表人：{info.legal_person || ''}</span>
                <span>注册地址：{info.address || ''}</span>
                <span>生产经营地址：{info.address || ''}</span>
            </div>

            <table className="vat-table">
                <thead>
                    <tr>
                        <th rowSpan="2" colSpan="2" className="vat-cell-center">项目</th>
                        <th rowSpan="2" className="vat-col-index">栏次</th>
                        <th colSpan="2" className="vat-cell-center">一般项目</th>
                        <th colSpan="2" className="vat-cell-center">即征即退项目</th>
                    </tr>
                    <tr>
                        <th className="vat-cell-center">本月数</th>
                        <th className="vat-cell-center">本年累计</th>
                        <th className="vat-cell-center">本月数</th>
                        <th className="vat-cell-center">本年累计</th>
                    </tr>
                </thead>
                <tbody>
                    {/* 销售额 */}
                    <tr>
                        <td rowSpan="10" className="vat-cell-center">销售额</td>
                        <td>（一）按适用税率计税销售额</td>
                        <td className="vat-cell-center">1</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_taxable_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_taxable_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;其中：应税货物销售额</td>
                        <td className="vat-cell-center">2</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_goods_current || data.gen_sales_taxable_current)}</td> {/* Fallback logic if detail missing */}
                        <td className="vat-cell-right">{fmt(data.gen_sales_goods_ytd || data.gen_sales_taxable_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;应税劳务销售额</td>
                        <td className="vat-cell-center">3</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_service_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_service_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;纳税检查调整的销售额</td>
                        <td className="vat-cell-center">4</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>（二）按简易办法计税销售额</td>
                        <td className="vat-cell-center">5</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_simple_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_simple_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;其中：纳税检查调整的销售额</td>
                        <td className="vat-cell-center">6</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>（三）免、抵、退办法出口销售额</td>
                        <td className="vat-cell-center">7</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_export_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_export_ytd)}</td>
                        {NA}{NA}
                    </tr>
                    <tr>
                        <td>（四）免税销售额</td>
                        <td className="vat-cell-center">8</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_ytd)}</td>
                        {NA}{NA}
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;其中：免税货物销售额</td>
                        <td className="vat-cell-center">9</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_goods_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_goods_ytd)}</td>
                        {NA}{NA}
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;免税劳务销售额</td>
                        <td className="vat-cell-center">10</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_service_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_sales_exempt_service_ytd)}</td>
                        {NA}{NA}
                    </tr>

                    {/* 税款计算 */}
                    <tr>
                        <td rowSpan="14" className="vat-cell-center">税款计算</td>
                        <td>销项税额</td>
                        <td className="vat-cell-center">11</td>
                        <td className="vat-cell-right">{fmt(data.gen_output_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_output_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>进项税额</td>
                        <td className="vat-cell-center">12</td>
                        <td className="vat-cell-right">{fmt(data.gen_input_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_input_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>上期留抵税额</td>
                        <td className="vat-cell-center">13</td>
                        <td className="vat-cell-right">{fmt(data.gen_previous_credit_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>进项税额转出</td>
                        <td className="vat-cell-center">14</td>
                        <td className="vat-cell-right">{fmt(data.gen_input_tax_transfer_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_input_tax_transfer_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>免、抵、退应退税额</td>
                        <td className="vat-cell-center">15</td>
                        <td className="vat-cell-right">{fmt(data.gen_export_refund_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>按适用税率计算的纳税检查应补缴税额</td>
                        <td className="vat-cell-center">16</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_inspection_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>应抵扣税额合计</td>
                        <td className="vat-cell-center">17</td>
                        <td className="vat-cell-right">{fmt(data.gen_deductible_total_current)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>实际抵扣税额</td>
                        <td className="vat-cell-center">18</td>
                        <td className="vat-cell-right">{fmt(data.gen_actual_deduction_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_actual_deduction_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>应纳税额</td>
                        <td className="vat-cell-center">19</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_payable_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_payable_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>期末留抵税额</td>
                        <td className="vat-cell-center">20</td>
                        <td className="vat-cell-right">{fmt(data.gen_ending_credit_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>简易计税办法计算的应纳税额</td>
                        <td className="vat-cell-center">21</td>
                        <td className="vat-cell-right">{fmt(data.gen_simple_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_simple_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>按简易计税办法计算的纳税检查应补缴税额</td>
                        <td className="vat-cell-center">22</td>
                        <td className="vat-cell-right">{fmt(data.gen_simple_inspection_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>应纳税额减征额</td>
                        <td className="vat-cell-center">23</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_reduction_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_reduction_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>应纳税额合计</td>
                        <td className="vat-cell-center">24</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_total_current || data.gen_tax_payable_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_total_ytd || data.gen_tax_payable_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>

                    {/* 税款缴纳 */}
                    <tr>
                        <td rowSpan="15" className="vat-cell-center">税款缴纳</td>
                        <td>期初未缴税额（多缴为负数）</td>
                        <td className="vat-cell-center">25</td>
                        <td className="vat-cell-right">{fmt(data.gen_opening_unpaid_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_opening_unpaid_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>实收出口开具专用缴款书退税额</td>
                        <td className="vat-cell-center">26</td>
                        <td className="vat-cell-right">{fmt(data.gen_export_refund_received_current)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>本期已缴税额</td>
                        <td className="vat-cell-center">27</td>
                        <td className="vat-cell-right">{fmt(data.gen_paid_tax_total_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_paid_tax_total_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>①分次预缴税额</td>
                        <td className="vat-cell-center">28</td>
                        <td className="vat-cell-right">{fmt(data.gen_prepaid_tax_current)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>②出口开具专用缴款书预缴税额</td>
                        <td className="vat-cell-center">29</td>
                        <td className="vat-cell-right">{fmt(data.gen_export_prepaid_current)}</td>
                        {NA}
                        {NA}
                        {NA}
                    </tr>
                    <tr>
                        <td>③本期缴纳上期应纳税额</td>
                        <td className="vat-cell-center">30</td>
                        <td className="vat-cell-right">{fmt(data.gen_paid_previous_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_paid_previous_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>④本期缴纳欠缴税额</td>
                        <td className="vat-cell-center">31</td>
                        <td className="vat-cell-right">{fmt(data.gen_paid_overdue_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>期末未缴税额（多缴为负数）</td>
                        <td className="vat-cell-center">32</td>
                        <td className="vat-cell-right">{fmt(data.gen_ending_unpaid_tax_current)}</td>
                        <td className="vat-cell-right">{fmt(data.gen_ending_unpaid_tax_ytd)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>&nbsp;&nbsp;&nbsp;&nbsp;其中：欠缴税额（≥0）</td>
                        <td className="vat-cell-center">33</td>
                        <td className="vat-cell-right">{fmt(data.gen_overdue_tax_current)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>本期应补(退)税额</td>
                        <td className="vat-cell-center">34</td>
                        <td className="vat-cell-right">{fmt(data.gen_tax_payable_refund_current)}</td>
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}
                    </tr>
                    <tr>
                        <td>即征即退实际退税额</td>
                        <td className="vat-cell-center">35</td>
                        {NA}
                        {NA}
                        <td className="vat-cell-right">{fmt(0)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                    </tr>
                    <tr>
                        <td>期初未缴查补税额</td>
                        <td className="vat-cell-center">36</td>
                        <td className="vat-cell-right">{fmt(data.gen_opening_inspection_unpaid_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}{NA}
                    </tr>
                    <tr>
                        <td>本期入库查补税额</td>
                        <td className="vat-cell-center">37</td>
                        <td className="vat-cell-right">{fmt(data.gen_inspection_paid_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}{NA}
                    </tr>
                    <tr>
                        <td>期末未缴查补税额</td>
                        <td className="vat-cell-center">38</td>
                        <td className="vat-cell-right">{fmt(data.gen_ending_inspection_unpaid_current)}</td>
                        <td className="vat-cell-right">{fmt(0)}</td>
                        {NA}{NA}
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default VatReturnRawView;
