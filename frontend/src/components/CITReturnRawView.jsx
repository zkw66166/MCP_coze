import React from 'react';
import './CITReturnRawView.css';

const CITReturnRawView = ({ data, companyInfo }) => {
    if (!data) return null;

    const fmt = (val) => {
        if (val === null || val === undefined) return '-';
        return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    const companyName = companyInfo ? companyInfo.name : (data.company_id || '');

    // 税率显示 (如25%)
    const taxRateDisplay = data.tax_rate ? `${(data.tax_rate * 100).toFixed(0)}%` : '25%';

    return (
        <div className="cit-raw-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>A100000</span>
                <span style={{ flex: 1, textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
                    中华人民共和国企业所得税年度纳税申报表（A类）
                </span>
            </div>

            <div className="cit-header-info">
                <span>纳税人名称：{companyName}</span>
                <span>纳税人识别号：{companyInfo?.tax_code || ''}</span>
                <span>所属年度：{data.period_year}年</span>
            </div>

            <table className="cit-table">
                <thead>
                    <tr>
                        <th className="cit-col-line">行次</th>
                        <th className="cit-col-category">类别</th>
                        <th className="cit-col-item">项　　目</th>
                        <th className="cit-col-amount">金　额</th>
                    </tr>
                </thead>
                <tbody>
                    {/* 利润总额计算 */}
                    <tr>
                        <td className="cit-center">1</td>
                        <td rowSpan="9" className="cit-category">利润总额计算</td>
                        <td className="cit-left">一、营业收入（填写A101010\101020\103000）</td>
                        <td className="cit-right">{fmt(data.revenue)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">2</td>
                        <td className="cit-left cit-indent">减：营业成本（填写A102010\102020\103000）</td>
                        <td className="cit-right">{fmt(data.cost)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">3</td>
                        <td className="cit-left cit-indent">减：税金及附加</td>
                        <td className="cit-right">{fmt(data.taxes_and_surcharges)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">4</td>
                        <td className="cit-left cit-indent">减：销售费用（填写A104000）</td>
                        <td className="cit-right">{fmt(data.selling_expenses)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">5</td>
                        <td className="cit-left cit-indent">减：管理费用（填写A104000）</td>
                        <td className="cit-right">{fmt(data.administrative_expenses)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">6</td>
                        <td className="cit-left cit-indent">减：财务费用（填写A104000）</td>
                        <td className="cit-right">{fmt(data.financial_expenses)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">7</td>
                        <td className="cit-left cit-indent">减：资产减值损失</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">8</td>
                        <td className="cit-left cit-indent">加：公允价值变动收益</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">9</td>
                        <td className="cit-left cit-indent">加：投资收益</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">10</td>
                        <td rowSpan="4" className="cit-category"></td>
                        <td className="cit-left">二、营业利润（1-2-3-4-5-6-7+8+9）</td>
                        <td className="cit-right">{fmt(data.operating_profit)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">11</td>
                        <td className="cit-left cit-indent">加：营业外收入（填写A101010\101020\103000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">12</td>
                        <td className="cit-left cit-indent">减：营业外支出（填写A102010\102020\103000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">13</td>
                        <td className="cit-left">三、利润总额（10+11-12）</td>
                        <td className="cit-right">{fmt(data.total_profit)}</td>
                    </tr>

                    {/* 应纳税所得额计算 */}
                    <tr>
                        <td className="cit-center">14</td>
                        <td rowSpan="9" className="cit-category">应纳税所得额计算</td>
                        <td className="cit-left cit-indent">减：境外所得（填写A108010）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">15</td>
                        <td className="cit-left cit-indent">加：纳税调整增加额（填写A105000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">16</td>
                        <td className="cit-left cit-indent">减：纳税调整减少额（填写A105000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">17</td>
                        <td className="cit-left cit-indent">减：免税、减计收入及加计扣除（填写A107010）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">18</td>
                        <td className="cit-left cit-indent">加：境外应税所得抵减境内亏损（填写A108000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">19</td>
                        <td className="cit-left">四、纳税调整后所得（13-14+15-16-17+18）</td>
                        <td className="cit-right">{fmt(data.taxable_income)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">20</td>
                        <td className="cit-left cit-indent">减：所得减免（填写A107020）</td>
                        <td className="cit-right">{fmt(data.tax_reduction)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">21</td>
                        <td className="cit-left cit-indent">减：弥补以前年度亏损（填写A106000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">22</td>
                        <td className="cit-left cit-indent">减：抵扣应纳税所得额（填写A107030）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">23</td>
                        <td rowSpan="6" className="cit-category">应纳税额计算</td>
                        <td className="cit-left">五、应纳税所得额（19-20-21-22）</td>
                        <td className="cit-right">{fmt(data.taxable_income)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">24</td>
                        <td className="cit-left cit-indent">税率（25%）</td>
                        <td className="cit-right">{taxRateDisplay}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">25</td>
                        <td className="cit-left">六、应纳所得税额（23×24）</td>
                        <td className="cit-right">{fmt(data.nominal_tax)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">26</td>
                        <td className="cit-left cit-indent">减：减免所得税额（填写A107040）</td>
                        <td className="cit-right">{fmt(data.tax_reduction)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">27</td>
                        <td className="cit-left cit-indent">减：抵免所得税额（填写A107050）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">28</td>
                        <td className="cit-left">七、应纳税额（25-26-27）</td>
                        <td className="cit-right">{fmt(data.tax_payable)}</td>
                    </tr>

                    {/* 应纳税额计算（续） */}
                    <tr>
                        <td className="cit-center">29</td>
                        <td rowSpan="4" className="cit-category">应纳税额计算</td>
                        <td className="cit-left cit-indent">加：境外所得应纳所得税额（填写A108000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">30</td>
                        <td className="cit-left cit-indent">减：境外所得抵免所得税额（填写A108000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">31</td>
                        <td className="cit-left">八、实际应纳所得税额（28+29-30）</td>
                        <td className="cit-right">{fmt(data.final_tax_payable)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">32</td>
                        <td className="cit-left cit-indent">减：本年累计实际已缴纳的所得税额</td>
                        <td className="cit-right">-</td>
                    </tr>

                    {/* 实际应纳税额计算 */}
                    <tr>
                        <td className="cit-center">33</td>
                        <td rowSpan="6" className="cit-category">实际应纳税额计算</td>
                        <td className="cit-left">九、本年应补（退）所得税额（31-32）</td>
                        <td className="cit-right">{fmt(data.final_tax_payable)}</td>
                    </tr>
                    <tr>
                        <td className="cit-center">34</td>
                        <td className="cit-left cit-indent">其中：总机构分摊本年应补（退）所得税额（填写A109000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">35</td>
                        <td className="cit-left cit-indent">财政集中分配本年应补（退）所得税额（填写A109000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">36</td>
                        <td className="cit-left cit-indent">总机构主体生产经营部门分摊本年应补（退）所得税额（填写A109000）</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">37</td>
                        <td className="cit-left cit-indent">减：民族自治地区企业所得税地方分享部分：□ 免征 □ 减征：减征幅度____%</td>
                        <td className="cit-right">-</td>
                    </tr>
                    <tr>
                        <td className="cit-center">38</td>
                        <td className="cit-left">十、本年实际应补（退）所得税额（33-37）</td>
                        <td className="cit-right">{fmt(data.final_tax_payable)}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default CITReturnRawView;
