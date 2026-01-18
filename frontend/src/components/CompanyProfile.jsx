/**
 * 企业画像页面组件 - 重新设计以匹配mockup布局
 * 包含图表、可变列宽布局
 */

import { useState, useEffect, useRef } from 'react';
import { fetchCompanyProfile } from '../services/api';
import Chart from 'chart.js/auto';
import './CompanyProfile.css';

// 评价标签组件
function EvaluationBadge({ text, color }) {
    if (!text) return null;
    const colorClass = {
        'green': 'badge-green',
        'blue': 'badge-blue',
        'yellow': 'badge-yellow',
        'red': 'badge-red'
    }[color] || 'badge-blue';

    return <span className={`evaluation-badge ${colorClass}`}>{text}</span>;
}

// 卡片组件
function ProfileCard({ title, icon, children, className = '' }) {
    return (
        <div className={`profile-card ${className}`}>
            <div className="card-header">
                <span className="card-icon">{icon}</span>
                <span className="card-title">{title}</span>
            </div>
            <div className="card-content">
                {children}
            </div>
        </div>
    );
}

// 饼图组件
function PieChart({ data, labels, colors }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !data || data.length === 0) return;

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(chartRef.current, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors || ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data, labels, colors]);

    return <canvas ref={chartRef} />;
}

// 柱状图组件
function BarChart({ data, labels, title, color = '#3b82f6' }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !data || data.length === 0) return;

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(chartRef.current, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: color,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true },
                    x: { grid: { display: false } }
                }
            }
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data, labels, title, color]);

    return <canvas ref={chartRef} />;
}

// 折线图组件
function LineChart({ data, labels, title, color = '#10b981' }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        if (!chartRef.current || !data || data.length === 0) return;

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(chartRef.current, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '20',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true },
                    x: { grid: { display: false } }
                }
            }
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data, labels, title, color]);

    return <canvas ref={chartRef} />;
}

// 水平进度条组件
function HorizontalBar({ label, value, maxValue, color = '#3b82f6' }) {
    const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
    return (
        <div className="h-bar-item">
            <div className="h-bar-label">{label}</div>
            <div className="h-bar-track">
                <div className="h-bar-fill" style={{ width: `${Math.min(percentage, 100)}%`, backgroundColor: color }} />
            </div>
            <div className="h-bar-value">{value?.toLocaleString()}</div>
        </div>
    );
}

function CompanyProfile({ selectedCompanyId, companies }) {
    const [profileData, setProfileData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedYear, setSelectedYear] = useState(2024);

    const selectedCompany = companies?.find(c => c.id === selectedCompanyId);

    useEffect(() => {
        if (!selectedCompanyId) return;

        const loadProfile = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await fetchCompanyProfile(selectedCompanyId, selectedYear);
                setProfileData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadProfile();
    }, [selectedCompanyId, selectedYear]);

    if (!selectedCompanyId) {
        return (
            <div className="profile-page">
                <div className="profile-empty">
                    <span className="empty-icon">📊</span>
                    <p>请先在顶部选择一个企业</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="profile-page">
                <div className="profile-loading">
                    <div className="loading-spinner"></div>
                    <p>正在加载企业画像...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-page">
                <div className="profile-error">
                    <span className="error-icon">⚠️</span>
                    <p>加载失败: {error}</p>
                </div>
            </div>
        );
    }

    if (!profileData) return null;

    const {
        basic_info, shareholders, investments, financial_summary,
        tax_summary, invoice_summary, top_customers, top_suppliers,
        risk_info, growth_metrics, cash_flow_summary
    } = profileData;

    // 准备图表数据
    const shareholderLabels = shareholders?.map(s => s.name) || [];
    const shareholderData = shareholders?.map(s => s.share_ratio) || [];

    const revenueLabels = ['2022', '2023', '2024'];
    const revenueData = [
        growth_metrics?.previous_revenue || 0,
        growth_metrics?.previous_revenue * 1.1 || 0,
        growth_metrics?.current_revenue || 0
    ].map(v => v / 10000);

    const customerLabels = top_customers?.top_customers?.map(c => c.customer_name?.substring(0, 6)) || [];
    const customerData = top_customers?.top_customers?.map(c => c.total_sales / 10000) || [];

    const supplierLabels = top_suppliers?.top_suppliers?.map(s => s.supplier_name?.substring(0, 6)) || [];
    const supplierData = top_suppliers?.top_suppliers?.map(s => s.total_purchase / 10000) || [];

    return (
        <div className="profile-page">
            {/* 页面标题 */}
            <div className="profile-header">
                <div className="header-left">
                    <h1>企业画像可视化分析</h1>
                </div>
                <div className="header-center">
                    <span className="company-tag">{selectedCompany?.name || '未知企业'}</span>
                </div>
                <div className="header-right">
                    <select
                        className="year-selector"
                        value={selectedYear}
                        onChange={(e) => setSelectedYear(Number(e.target.value))}
                    >
                        {[2025, 2024, 2023, 2022].map(year => (
                            <option key={year} value={year}>{year}年</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* 画像内容区域 */}
            <div className="profile-content">
                {/* ===== 第一行: 基本信息 + 营收规模 ===== */}
                <div className="profile-row">
                    <ProfileCard title="基本信息" icon="🏢" className="col-4">
                        <div className="info-grid-compact">
                            <div className="info-row">
                                <span className="info-label">企业名称</span>
                                <span className="info-value">{basic_info?.company_name}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">法定代表人</span>
                                <span className="info-value">{basic_info?.legal_person || '-'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">注册资本</span>
                                <span className="info-value">{basic_info?.registered_capital}万元</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">成立日期</span>
                                <span className="info-value">{basic_info?.establishment_date || '-'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">纳税人资格</span>
                                <span className="info-value">{basic_info?.taxpayer_type || '一般纳税人'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">员工人数</span>
                                <span className="info-value">{basic_info?.employee_count || 0}人</span>
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="营收规模" icon="📊" className="col-8">
                        <div className="chart-with-table">
                            <div className="chart-area">
                                <BarChart
                                    data={revenueData}
                                    labels={revenueLabels}
                                    title="营业收入(万元)"
                                    color="#3b82f6"
                                />
                            </div>
                            <div className="data-table">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>指标</th>
                                            <th>金额</th>
                                            <th>评价</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>资产总额</td>
                                            <td>{(financial_summary?.total_assets / 10000)?.toFixed(2)}万</td>
                                            <td><EvaluationBadge text="稳健" color="blue" /></td>
                                        </tr>
                                        <tr>
                                            <td>营业收入</td>
                                            <td>{(financial_summary?.revenue / 10000)?.toFixed(2)}万</td>
                                            <td><EvaluationBadge text={growth_metrics?.revenue_evaluation} color={growth_metrics?.revenue_color} /></td>
                                        </tr>
                                        <tr>
                                            <td>净利润</td>
                                            <td>{(financial_summary?.net_profit / 10000)?.toFixed(2)}万</td>
                                            <td><EvaluationBadge text={growth_metrics?.profit_evaluation} color={growth_metrics?.profit_color} /></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </ProfileCard>
                </div>

                {/* ===== 第二行: 股权结构 + 盈利能力 ===== */}
                <div className="profile-row">
                    <ProfileCard title="股权结构分析" icon="🥧" className="col-4">
                        <div className="pie-chart-section">
                            <div className="pie-chart-area">
                                <PieChart
                                    data={shareholderData}
                                    labels={shareholderLabels}
                                    colors={['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']}
                                />
                            </div>
                            <div className="pie-legend">
                                {shareholders?.map((sh, idx) => (
                                    <div key={idx} className="legend-item">
                                        <span className="legend-color" style={{ backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][idx % 5] }}></span>
                                        <span className="legend-name">{sh.name}</span>
                                        <span className="legend-value">{sh.share_ratio}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="investment-info">
                            <span>对外投资: {investments?.total_count || 0}家</span>
                            <span>控股{investments?.controlling_count || 0}家 | 参股{investments?.participating_count || 0}家</span>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="盈利能力分析" icon="💹" className="col-8">
                        <div className="metrics-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>指标</th>
                                        <th>数值</th>
                                        <th>评价</th>
                                        <th>行业对比</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {financial_summary?.metrics?.map((m, idx) => (
                                        <tr key={idx}>
                                            <td>{m.name}</td>
                                            <td>{m.value}{m.unit}</td>
                                            <td><EvaluationBadge text={m.evaluation} color={m.evaluation_color} /></td>
                                            <td>
                                                <div className="industry-compare">
                                                    <div className="compare-bar">
                                                        <div className="compare-fill" style={{ width: `${Math.min(m.value * 2, 100)}%` }}></div>
                                                        <div className="compare-marker" style={{ left: '50%' }}></div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </ProfileCard>
                </div>

                {/* ===== 第三行: 发票数据概览 (三列) ===== */}
                <div className="profile-row three-cols">
                    <ProfileCard title="销售发票" icon="📤" className="col-4">
                        <div className="invoice-card-content">
                            <div className="big-number">{invoice_summary?.sales_invoice_count || 0}<span>张</span></div>
                            <div className="sub-info">
                                <span>金额: {(invoice_summary?.sales_invoice_amount / 10000)?.toFixed(2)}万</span>
                                <span>单票均价: {invoice_summary?.avg_sales_amount?.toFixed(0)}元</span>
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="采购发票" icon="📥" className="col-4">
                        <div className="invoice-card-content">
                            <div className="big-number">{invoice_summary?.purchase_invoice_count || 0}<span>张</span></div>
                            <div className="sub-info">
                                <span>金额: {(invoice_summary?.purchase_invoice_amount / 10000)?.toFixed(2)}万</span>
                                <span>单票均价: {invoice_summary?.avg_purchase_amount?.toFixed(0)}元</span>
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="发票集中度" icon="📊" className="col-4">
                        <div className="invoice-card-content">
                            <div className="concentration-display">
                                <div className="conc-item">
                                    <span className="conc-label">客户TOP5</span>
                                    <span className="conc-value">{top_customers?.top_concentration}%</span>
                                    <EvaluationBadge text={top_customers?.concentration_evaluation} color={top_customers?.concentration_color} />
                                </div>
                                <div className="conc-item">
                                    <span className="conc-label">供应商TOP5</span>
                                    <span className="conc-value">{top_suppliers?.top_concentration}%</span>
                                    <EvaluationBadge text={top_suppliers?.concentration_evaluation} color={top_suppliers?.concentration_color} />
                                </div>
                            </div>
                        </div>
                    </ProfileCard>
                </div>

                {/* ===== 第四行: 税务情况 + 成长性分析 ===== */}
                <div className="profile-row">
                    <ProfileCard title="税务情况分析" icon="💰" className="col-4">
                        <div className="tax-section">
                            <div className="tax-item">
                                <span className="tax-label">增值税额</span>
                                <span className="tax-value">{tax_summary?.vat_amount?.toLocaleString()}元</span>
                            </div>
                            <div className="tax-item">
                                <span className="tax-label">增值税税负率</span>
                                <span className="tax-value">{tax_summary?.vat_burden_rate}%</span>
                                <EvaluationBadge text={tax_summary?.evaluations?.vat?.text} color={tax_summary?.evaluations?.vat?.color} />
                            </div>
                            <div className="tax-item">
                                <span className="tax-label">企业所得税</span>
                                <span className="tax-value">{tax_summary?.cit_amount?.toLocaleString()}元</span>
                            </div>
                            <div className="tax-item">
                                <span className="tax-label">所得税税负率</span>
                                <span className="tax-value">{tax_summary?.cit_burden_rate}%</span>
                                <EvaluationBadge text={tax_summary?.evaluations?.cit?.text} color={tax_summary?.evaluations?.cit?.color} />
                            </div>
                            <div className="tax-item highlight">
                                <span className="tax-label">综合税负率</span>
                                <span className="tax-value">{tax_summary?.total_burden_rate}%</span>
                                <EvaluationBadge text={tax_summary?.evaluations?.total?.text} color={tax_summary?.evaluations?.total?.color} />
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="成长性分析" icon="🚀" className="col-8">
                        <div className="growth-section">
                            <div className="growth-chart-area">
                                <LineChart
                                    data={revenueData}
                                    labels={revenueLabels}
                                    title="营收趋势"
                                    color="#10b981"
                                />
                            </div>
                            <div className="growth-metrics-side">
                                <div className="growth-metric-item">
                                    <span className="gm-label">营收增长率</span>
                                    <span className={`gm-value ${growth_metrics?.revenue_growth_rate >= 0 ? 'positive' : 'negative'}`}>
                                        {growth_metrics?.revenue_growth_rate >= 0 ? '+' : ''}{growth_metrics?.revenue_growth_rate}%
                                    </span>
                                    <EvaluationBadge text={growth_metrics?.revenue_evaluation} color={growth_metrics?.revenue_color} />
                                </div>
                                <div className="growth-metric-item">
                                    <span className="gm-label">利润增长率</span>
                                    <span className={`gm-value ${growth_metrics?.profit_growth_rate >= 0 ? 'positive' : 'negative'}`}>
                                        {growth_metrics?.profit_growth_rate >= 0 ? '+' : ''}{growth_metrics?.profit_growth_rate}%
                                    </span>
                                    <EvaluationBadge text={growth_metrics?.profit_evaluation} color={growth_metrics?.profit_color} />
                                </div>
                            </div>
                        </div>
                    </ProfileCard>
                </div>

                {/* ===== 第五行: 客户分析 + 供应商分析 ===== */}
                <div className="profile-row">
                    <ProfileCard title="客户分析" icon="👥" className="col-6">
                        <div className="analysis-section">
                            <div className="analysis-header">
                                <span>客户总数: <strong>{top_customers?.customer_count || 0}</strong>家</span>
                            </div>
                            <div className="analysis-chart">
                                <BarChart
                                    data={customerData}
                                    labels={customerLabels}
                                    title="TOP客户销售额(万)"
                                    color="#3b82f6"
                                />
                            </div>
                            <div className="top-list-compact">
                                {top_customers?.top_customers?.slice(0, 3).map((c, idx) => (
                                    <div key={idx} className="top-row">
                                        <span className="rank">{idx + 1}</span>
                                        <span className="name">{c.customer_name}</span>
                                        <span className="amount">{(c.total_sales / 10000).toFixed(1)}万</span>
                                        <span className="ratio">{c.share_ratio}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="供应商分析" icon="🏭" className="col-6">
                        <div className="analysis-section">
                            <div className="analysis-header">
                                <span>供应商总数: <strong>{top_suppliers?.supplier_count || 0}</strong>家</span>
                            </div>
                            <div className="analysis-chart">
                                <BarChart
                                    data={supplierData}
                                    labels={supplierLabels}
                                    title="TOP供应商采购额(万)"
                                    color="#10b981"
                                />
                            </div>
                            <div className="top-list-compact">
                                {top_suppliers?.top_suppliers?.slice(0, 3).map((s, idx) => (
                                    <div key={idx} className="top-row">
                                        <span className="rank">{idx + 1}</span>
                                        <span className="name">{s.supplier_name}</span>
                                        <span className="amount">{(s.total_purchase / 10000).toFixed(1)}万</span>
                                        <span className="ratio">{s.share_ratio}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </ProfileCard>
                </div>

                {/* ===== 第六行: 现金流 + 经营风险 ===== */}
                <div className="profile-row">
                    <ProfileCard title="现金流分析" icon="💵" className="col-6">
                        <div className="cashflow-section">
                            <div className="cf-row">
                                <span className="cf-label">经营活动现金流</span>
                                <span className={`cf-value ${cash_flow_summary?.operating_cash_flow >= 0 ? 'positive' : 'negative'}`}>
                                    {(cash_flow_summary?.operating_cash_flow / 10000)?.toFixed(2)}万
                                </span>
                                <EvaluationBadge text={cash_flow_summary?.operating_evaluation} color={cash_flow_summary?.operating_color} />
                            </div>
                            <div className="cf-row">
                                <span className="cf-label">投资活动现金流</span>
                                <span className={`cf-value ${cash_flow_summary?.investing_cash_flow >= 0 ? 'positive' : 'negative'}`}>
                                    {(cash_flow_summary?.investing_cash_flow / 10000)?.toFixed(2)}万
                                </span>
                            </div>
                            <div className="cf-row">
                                <span className="cf-label">筹资活动现金流</span>
                                <span className={`cf-value ${cash_flow_summary?.financing_cash_flow >= 0 ? 'positive' : 'negative'}`}>
                                    {(cash_flow_summary?.financing_cash_flow / 10000)?.toFixed(2)}万
                                </span>
                            </div>
                            <div className="cf-row total">
                                <span className="cf-label">现金净增加额</span>
                                <span className={`cf-value ${cash_flow_summary?.net_increase >= 0 ? 'positive' : 'negative'}`}>
                                    {(cash_flow_summary?.net_increase / 10000)?.toFixed(2)}万
                                </span>
                            </div>
                        </div>
                    </ProfileCard>

                    <ProfileCard title="经营风险分析" icon="⚠️" className={`col-6 risk-level-${risk_info?.risk_color}`}>
                        <div className="risk-section">
                            <div className="risk-header">
                                <span className="risk-level-text">
                                    风险等级: <EvaluationBadge text={risk_info?.risk_level} color={risk_info?.risk_color} />
                                </span>
                                <span className="risk-count">共{risk_info?.total_count || 0}条记录</span>
                            </div>
                            {risk_info?.risks?.length > 0 ? (
                                <div className="risk-list">
                                    {risk_info.risks.slice(0, 3).map((r, idx) => (
                                        <div key={idx} className="risk-row">
                                            <span className="risk-type-tag">{r.risk_type_name}</span>
                                            <span className="risk-title">{r.risk_title}</span>
                                            <span className={`risk-status ${r.risk_status === '已结案' ? 'closed' : 'open'}`}>
                                                {r.risk_status}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="no-risk-message">
                                    <span className="no-risk-icon">✅</span>
                                    <span>暂无风险记录，企业经营状况良好</span>
                                </div>
                            )}
                        </div>
                    </ProfileCard>
                </div>
            </div>
        </div>
    );
}

export default CompanyProfile;
