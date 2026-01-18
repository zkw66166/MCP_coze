import React, { useState, useEffect, useRef } from 'react';
import './CompanyProfile.css';
import {
    Building, GitBranch, Users, BarChart3, Truck, Award, Calculator,
    Globe, Shield, Briefcase, Database, CheckCircle, Target, Factory
} from 'lucide-react';
import Chart from 'chart.js/auto';

// ============================================================================
// 辅助组件
// ============================================================================

// 评价标签
const EvalLabel = ({ text, type = 'positive' }) => {
    const colorMap = {
        positive: 'eval-green',
        growth: 'eval-green',
        neutral: 'eval-blue',
        warning: 'eval-yellow',
        negative: 'eval-red',
        purple: 'eval-purple',
        orange: 'eval-orange'
    };
    return <span className={`eval-label ${colorMap[type] || 'eval-blue'}`}>{text}</span>;
};

// 二级模块标题
const SectionTitle = ({ name, color = 'green' }) => {
    return (
        <div className="section-title">
            <span className={`section-dot dot-${color}`}></span>
            <span className="section-name">{name}</span>
        </div>
    );
};

// 紧凑单行指标
const CompactMetric = ({ label, value, evalInfo, bgColor = '' }) => (
    <div className={`compact-metric ${bgColor}`}>
        <span className="metric-label">{label}</span>
        <span className="metric-value">
            {value}
            {evalInfo && <EvalLabel text={evalInfo.text} type={evalInfo.type} />}
        </span>
    </div>
);

// 进度条组件
const ProgressBar = ({ label, value, max = 100, color = 'blue' }) => (
    <div className="progress-item">
        <div className="progress-header">
            <span className="progress-label">{label}</span>
            <span className="progress-value">{value}%</span>
        </div>
        <div className="progress-bar">
            <div
                className={`progress-fill progress-${color}`}
                style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
            ></div>
        </div>
    </div>
);

// 饼图组件
const PieChart = ({ data, title }) => {
    const canvasRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!canvasRef.current || !data || data.length === 0) return;

        if (chartRef.current) {
            chartRef.current.destroy();
        }

        chartRef.current = new Chart(canvasRef.current, {
            type: 'pie',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => d.value),
                    backgroundColor: data.map(d => d.color || '#3b82f6'),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 11 }, padding: 8 }
                    },
                    title: title ? { display: true, text: title, font: { size: 13 } } : { display: false }
                }
            }
        });

        return () => {
            if (chartRef.current) chartRef.current.destroy();
        };
    }, [data, title]);

    return <canvas ref={canvasRef} />;
};

// 柱状图组件
const BarChart = ({ data, title }) => {
    const canvasRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!canvasRef.current || !data || data.length === 0) return;

        if (chartRef.current) {
            chartRef.current.destroy();
        }

        chartRef.current = new Chart(canvasRef.current, {
            type: 'bar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => d.value),
                    backgroundColor: data.map(d => d.color || '#3b82f6'),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: title ? { display: true, text: title, font: { size: 13 } } : { display: false }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });

        return () => {
            if (chartRef.current) chartRef.current.destroy();
        };
    }, [data, title]);

    return <canvas ref={canvasRef} />;
};

// 折线图组件
const LineChart = ({ data, lines, title }) => {
    const canvasRef = useRef(null);
    const chartRef = useRef(null);

    useEffect(() => {
        if (!canvasRef.current || !data || data.length === 0 || !lines) return;

        if (chartRef.current) {
            chartRef.current.destroy();
        }

        chartRef.current = new Chart(canvasRef.current, {
            type: 'line',
            data: {
                labels: data.map(d => d.year || d.label),
                datasets: lines.map(line => ({
                    label: line.name,
                    data: data.map(d => d[line.key]),
                    borderColor: line.color,
                    backgroundColor: line.color + '20',
                    tension: 0.3,
                    fill: true
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { font: { size: 11 } } },
                    title: title ? { display: true, text: title, font: { size: 13 } } : { display: false }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });

        return () => {
            if (chartRef.current) chartRef.current.destroy();
        };
    }, [data, lines, title]);

    return <canvas ref={canvasRef} />;
};

// ============================================================================
// 主组件
// ============================================================================

function CompanyProfile({ selectedCompanyId, companies }) {
    const [year, setYear] = useState(2024);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [profile, setProfile] = useState(null);

    const companyId = selectedCompanyId;
    const companyName = companies?.find(c => c.id === companyId)?.name || '企业';

    // 加载数据
    useEffect(() => {
        if (!companyId) return;

        const loadProfile = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/company-profile/${companyId}/full?year=${year}`);
                if (!response.ok) throw new Error('加载失败');
                const data = await response.json();
                setProfile(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadProfile();
    }, [companyId, year]);

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="loading-spinner"></div>
                <p>加载企业画像...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-error">
                <span className="error-icon">⚠️</span>
                <p>加载失败: {error}</p>
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="profile-empty">
                <span className="empty-icon">📊</span>
                <p>请选择企业查看画像</p>
            </div>
        );
    }

    // 解构数据
    const {
        basic_info, certifications, shareholders, investments, employee_structure,
        financial_summary, growth_metrics, cash_flow_summary, top_customers, top_suppliers,
        invoice_summary, rd_innovation, tax_summary, cross_border, compliance, risk_info,
        bank_relations, digital_capability, esg, policy_eligibility, special_business
    } = profile;

    // 计算图表数据
    const shareholderPieData = shareholders?.map((s, i) => ({
        name: s.name?.substring(0, 6) || `股东${i + 1}`,
        value: s.share_ratio || 0,
        color: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'][i % 5]
    })) || [];

    const employeePieData = employee_structure?.has_data ? [
        { name: '研发人员', value: employee_structure.rd_employees || 0, color: '#3b82f6' },
        { name: '销售人员', value: employee_structure.sales_employees || 0, color: '#8b5cf6' },
        { name: '管理人员', value: employee_structure.admin_employees || 0, color: '#10b981' },
        { name: '其他人员', value: employee_structure.other_employees || 0, color: '#f59e0b' },
    ] : [];

    const taxPieData = tax_summary?.by_type ? Object.entries(tax_summary.by_type).map(([name, value], i) => ({
        name: name,
        value: value || 0,
        color: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][i % 4]
    })) : [];

    return (
        <div className="profile-page">
            {/* 页面标题 */}
            <div className="profile-header">
                <h1>企业画像可视化分析</h1>
                <div className="header-center">
                    <span className="company-tag">{companyName}</span>
                    {basic_info?.credit_code && (
                        <span className="credit-code">统一社会信用代码：{basic_info.credit_code}</span>
                    )}
                </div>
                <select className="year-selector" value={year} onChange={e => setYear(Number(e.target.value))}>
                    <option value={2024}>2024年</option>
                    <option value={2023}>2023年</option>
                    <option value={2022}>2022年</option>
                </select>
            </div>

            <div className="profile-content">
                {/* 一、企业身份画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Building size={18} /> 一、企业身份画像</h3>

                    <SectionTitle name="基本工商信息" color="green" />
                    <div className="metrics-grid cols-4">
                        <CompactMetric label="统一社会信用代码" value={basic_info?.credit_code || '-'} />
                        <CompactMetric label="企业名称" value={companyName} />
                        <CompactMetric label="企业类型" value={basic_info?.company_type || '-'} />
                        <CompactMetric label="法定代表人" value={basic_info?.legal_person || '-'} />
                        <CompactMetric label="成立日期" value={basic_info?.establishment_date || '-'} />
                        <CompactMetric label="经营状态" value={basic_info?.operating_status || '存续'} evalInfo={{ text: '正常', type: 'positive' }} />
                        <CompactMetric label="注册地址" value={basic_info?.address?.substring(0, 20) || '-'} />
                        <CompactMetric label="经营范围" value={basic_info?.business_scope?.substring(0, 20) || '-'} />
                    </div>

                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="规模特征" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="注册资本" value={`${(basic_info?.registered_capital / 10000 || 0).toFixed(0)}万元`} evalInfo={{ text: '充足', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="员工人数" value={`${employee_structure?.total_employees || basic_info?.employee_count || '-'}人`} bgColor="bg-purple" />
                                <CompactMetric label="纳税人资格" value={basic_info?.taxpayer_type || '一般纳税人'} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="行业定位" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="所属行业" value={basic_info?.industry || '-'} bgColor="bg-orange" />
                                <CompactMetric label="产业链位置" value={basic_info?.industry_chain_position || '-'} evalInfo={{ text: '核心环节', type: 'positive' }} bgColor="bg-orange" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="资质认证" color="blue" />
                            <div className="metrics-stack">
                                {certifications?.slice(0, 3).map((cert, i) => (
                                    <CompactMetric
                                        key={i}
                                        label={cert.cert_name}
                                        value={cert.status}
                                        evalInfo={{ text: `至${cert.expire_date?.substring(0, 7)}`, type: 'positive' }}
                                        bgColor="bg-blue"
                                    />
                                ))}
                                {(!certifications || certifications.length === 0) && (
                                    <CompactMetric label="暂无资质" value="-" bgColor="bg-blue" />
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 二、股权与治理画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><GitBranch size={18} /> 二、股权与治理画像</h3>
                    <div className="metrics-row-2">
                        <div className="chart-section">
                            <SectionTitle name="股权结构" color="purple" />
                            <div className="chart-container" style={{ height: '200px' }}>
                                {shareholderPieData.length > 0 ? (
                                    <PieChart data={shareholderPieData} />
                                ) : (
                                    <p className="no-data">暂无股东数据</p>
                                )}
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="股权信息" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="股东总数" value={`${shareholders?.length || 0}个`} />
                                {shareholders?.[0] && (
                                    <>
                                        <CompactMetric label="最大股东" value={shareholders[0].name?.substring(0, 10) || '-'} />
                                        <CompactMetric label="最大股东持股" value={`${shareholders[0].share_ratio || 0}%`} evalInfo={{ text: '控股', type: 'purple' }} />
                                    </>
                                )}
                                <CompactMetric label="对外投资数" value={`${investments?.length || 0}家`} />
                            </div>
                            <SectionTitle name="公司治理" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="财务审计意见" value={compliance?.financial_compliance?.audit_opinion || '标准无保留'} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-orange" />
                                <CompactMetric label="内控缺陷数" value={`${compliance?.financial_compliance?.control_defects || 0}个`} evalInfo={{ text: '规范', type: 'positive' }} bgColor="bg-orange" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 三、组织与人力画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Users size={18} /> 三、组织与人力画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="人员结构" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="员工总数" value={`${employee_structure?.total_employees || '-'}人`} evalInfo={{ text: '中型', type: 'neutral' }} />
                                <CompactMetric label="研发人员数" value={`${employee_structure?.rd_employees || '-'}人`} />
                                <CompactMetric label="研发人员占比" value={`${employee_structure?.rd_ratio || 0}%`} evalInfo={employee_structure?.rd_ratio_eval ? { text: employee_structure.rd_ratio_eval[0], type: employee_structure.rd_ratio_eval[1] } : null} />
                                <CompactMetric label="本科及以上占比" value={`${employee_structure?.bachelor_above_ratio || 0}%`} evalInfo={employee_structure?.bachelor_eval ? { text: employee_structure.bachelor_eval[0], type: employee_structure.bachelor_eval[1] === 'green' ? 'positive' : 'neutral' } : null} />
                            </div>
                            <SectionTitle name="薪酬成本" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="年度工资总额" value={`${(employee_structure?.total_salary || 0).toFixed(0)}万元`} bgColor="bg-purple" />
                                <CompactMetric label="人均年薪" value={`${employee_structure?.avg_salary || 0}万元`} evalInfo={{ text: '行业中上', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="社保覆盖率" value={`${employee_structure?.social_insurance_coverage || 100}%`} evalInfo={{ text: '合规', type: 'positive' }} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div className="chart-section bg-gradient-blue">
                            <SectionTitle name="人员构成分布" color="blue" />
                            <div className="chart-container" style={{ height: '200px' }}>
                                {employeePieData.length > 0 && employeePieData.some(d => d.value > 0) ? (
                                    <PieChart data={employeePieData} />
                                ) : (
                                    <p className="no-data">暂无人员结构数据</p>
                                )}
                            </div>
                        </div>
                        <div className="bg-gradient-orange">
                            <SectionTitle name="学历结构分析" color="orange" />
                            <div className="progress-section">
                                <ProgressBar label="硕士及以上" value={employee_structure?.has_data ? Math.round((employee_structure.master_above || 0) / (employee_structure.total_employees || 1) * 100) : 0} color="blue" />
                                <ProgressBar label="本科" value={employee_structure?.has_data ? Math.round((employee_structure.bachelor || 0) / (employee_structure.total_employees || 1) * 100) : 0} color="purple" />
                                <ProgressBar label="专科及以下" value={employee_structure?.has_data ? Math.round((employee_structure.below_bachelor || 0) / (employee_structure.total_employees || 1) * 100) : 0} color="green" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 四、财务画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><BarChart3 size={18} /> 四、财务画像</h3>

                    {/* 财务图表区 */}
                    <div className="metrics-row-3">
                        {/* 资产结构分析 - 饼图 */}
                        <div className="chart-section bg-gradient-blue">
                            <SectionTitle name="资产结构分析" color="blue" />
                            <div className="chart-container" style={{ height: '180px' }}>
                                <PieChart
                                    data={[
                                        { name: `流动资产: ${((financial_summary?.current_assets || 0) / 10000).toFixed(0)}`, value: financial_summary?.current_assets || 3850, color: '#3b82f6' },
                                        { name: `固定资产: ${((financial_summary?.fixed_assets || 0) / 10000).toFixed(0)}`, value: financial_summary?.fixed_assets || 980, color: '#8b5cf6' },
                                        { name: `无形资产: ${((financial_summary?.intangible_assets || 0) / 10000).toFixed(0)}`, value: financial_summary?.intangible_assets || 320, color: '#10b981' },
                                        { name: `其他: ${((financial_summary?.other_assets || 0) / 10000).toFixed(0)}`, value: financial_summary?.other_assets || 130, color: '#f59e0b' },
                                    ]}
                                />
                            </div>
                            <CompactMetric
                                label="资产总额"
                                value={`${((financial_summary?.total_assets || 0) / 10000).toFixed(0)}万`}
                                evalInfo={growth_metrics?.asset_growth ? { text: `${growth_metrics.asset_growth > 0 ? '+' : ''}${growth_metrics.asset_growth.toFixed(1)}%`, type: growth_metrics.asset_growth > 0 ? 'growth' : 'negative' } : null}
                                bgColor="bg-white"
                            />
                        </div>

                        {/* 负债与权益 - 柱状图 */}
                        <div className="chart-section bg-gradient-purple">
                            <SectionTitle name="负债与权益" color="purple" />
                            <div className="chart-container" style={{ height: '180px' }}>
                                <BarChart
                                    data={[
                                        { name: '负债', value: (financial_summary?.total_liabilities || 3618) / 10000, color: '#f59e0b' },
                                        { name: '所有者权益', value: (financial_summary?.equity || 1662) / 10000, color: '#10b981' },
                                    ]}
                                />
                            </div>
                            <CompactMetric
                                label="资产负债率"
                                value={`${(financial_summary?.debt_ratio || 0).toFixed(1)}%`}
                                evalInfo={{ text: financial_summary?.debt_ratio < 70 ? '稳健' : '偏高', type: financial_summary?.debt_ratio < 70 ? 'positive' : 'warning' }}
                                bgColor="bg-white"
                            />
                        </div>

                        {/* 财务综合能力 - 横向进度条 */}
                        <div className="chart-section bg-gradient-green">
                            <SectionTitle name="财务综合能力" color="green" />
                            <div className="progress-section">
                                <ProgressBar label="盈利能力" value={Math.min(Math.round((financial_summary?.net_margin || 0) * 10 + 50), 100)} color="blue" />
                                <ProgressBar label="偿债能力" value={Math.min(Math.round(100 - (financial_summary?.debt_ratio || 50)), 100)} color="purple" />
                                <ProgressBar label="运营效率" value={Math.min(Math.round((financial_summary?.asset_turnover || 0) * 50 + 30), 100)} color="green" />
                                <ProgressBar label="成长能力" value={Math.min(Math.round((growth_metrics?.revenue_growth || 0) * 3 + 50), 100)} color="orange" />
                                <ProgressBar label="现金流" value={cash_flow_summary?.operating > 0 ? 90 : 40} color="blue" />
                            </div>
                            <CompactMetric
                                label="综合评分"
                                value={`${(((financial_summary?.net_margin || 5) * 2 + (100 - (financial_summary?.debt_ratio || 50)) * 0.5 + (growth_metrics?.revenue_growth || 10) * 0.5 + 40) / 100 * 100).toFixed(1)}分`}
                                evalInfo={{ text: '优秀', type: 'positive' }}
                                bgColor="bg-white"
                            />
                        </div>
                    </div>

                    {/* 详细指标区 */}
                    <div className="metrics-row-4">
                        <div>
                            <SectionTitle name="盈利能力" color="cyan" />
                            <div className="metrics-stack">
                                <CompactMetric label="营业收入" value={`${((financial_summary?.revenue || 0) / 10000).toFixed(0)}万`} evalInfo={growth_metrics?.revenue_growth ? { text: `${growth_metrics.revenue_growth > 0 ? '+' : ''}${growth_metrics.revenue_growth.toFixed(1)}%`, type: growth_metrics.revenue_growth > 0 ? 'growth' : 'negative' } : null} bgColor="bg-cyan" />
                                <CompactMetric label="毛利率" value={`${(financial_summary?.gross_margin || 0).toFixed(1)}%`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-cyan" />
                                <CompactMetric label="净利润" value={`${((financial_summary?.net_profit || 0) / 10000).toFixed(0)}万`} bgColor="bg-cyan" />
                                <CompactMetric label="净利率" value={`${(financial_summary?.net_margin || 0).toFixed(1)}%`} bgColor="bg-cyan" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="偿债能力" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="资产负债率" value={`${(financial_summary?.debt_ratio || 0).toFixed(1)}%`} evalInfo={{ text: '稳健', type: 'neutral' }} bgColor="bg-green" />
                                <CompactMetric label="流动比率" value={`${(financial_summary?.current_ratio || 0).toFixed(2)}`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-green" />
                                <CompactMetric label="速动比率" value={`${(financial_summary?.quick_ratio || 0).toFixed(2)}`} bgColor="bg-green" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="运营效率" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="总资产周转率" value={`${(financial_summary?.asset_turnover || 0).toFixed(2)}次`} bgColor="bg-purple" />
                                <CompactMetric label="应收款周转率" value={`${(financial_summary?.receivable_turnover || 0).toFixed(1)}次`} bgColor="bg-purple" />
                                <CompactMetric label="应收款周转天数" value={`${(financial_summary?.receivable_days || 0).toFixed(0)}天`} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="成长能力" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="营收增长率" value={`${(growth_metrics?.revenue_growth || 0).toFixed(1)}%`} evalInfo={growth_metrics?.revenue_growth_eval ? { text: growth_metrics.revenue_growth_eval[0], type: growth_metrics.revenue_growth_eval[1] === 'green' ? 'positive' : 'neutral' } : null} bgColor="bg-orange" />
                                <CompactMetric label="净利润增长率" value={`${(growth_metrics?.profit_growth || 0).toFixed(1)}%`} bgColor="bg-orange" />
                                <CompactMetric label="资产增长率" value={`${(growth_metrics?.asset_growth || 0).toFixed(1)}%`} bgColor="bg-orange" />
                            </div>
                        </div>
                    </div>

                    <div className="metrics-row-2">
                        <div>
                            <SectionTitle name="成本费用结构" color="cyan" />
                            <div className="metrics-grid cols-2">
                                <CompactMetric label="销售费用" value={`${((financial_summary?.selling_expense || 0) / 10000).toFixed(0)}万`} bgColor="bg-cyan" />
                                <CompactMetric label="销售费用率" value={`${(financial_summary?.selling_expense_ratio || 0).toFixed(1)}%`} bgColor="bg-cyan" />
                                <CompactMetric label="管理费用" value={`${((financial_summary?.admin_expense || 0) / 10000).toFixed(0)}万`} bgColor="bg-cyan" />
                                <CompactMetric label="管理费用率" value={`${(financial_summary?.admin_expense_ratio || 0).toFixed(1)}%`} bgColor="bg-cyan" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="现金流量" color="blue" />
                            <div className="metrics-stack">
                                <CompactMetric label="经营活动现金流" value={`${((cash_flow_summary?.operating || 0) / 10000).toFixed(0)}万`} evalInfo={{ text: cash_flow_summary?.operating > 0 ? '充足' : '紧张', type: cash_flow_summary?.operating > 0 ? 'positive' : 'warning' }} bgColor="bg-blue" />
                                <CompactMetric label="投资活动现金流" value={`${((cash_flow_summary?.investing || 0) / 10000).toFixed(0)}万`} bgColor="bg-blue" />
                                <CompactMetric label="筹资活动现金流" value={`${((cash_flow_summary?.financing || 0) / 10000).toFixed(0)}万`} bgColor="bg-blue" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 五、业务运营画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Truck size={18} /> 五、业务运营画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="业务结构" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="主营业务收入" value={`${((financial_summary?.revenue || 0) / 10000).toFixed(0)}万`} />
                                <CompactMetric label="发票数量(销售)" value={`${invoice_summary?.sales_count || 0}张`} />
                                <CompactMetric label="发票数量(采购)" value={`${invoice_summary?.purchase_count || 0}张`} />
                            </div>
                        </div>
                        <div className="bg-gradient-purple">
                            <SectionTitle name="客户集中度" color="purple" />
                            {top_customers?.length > 0 ? (
                                <div className="top-list">
                                    {top_customers.slice(0, 5).map((c, i) => (
                                        <div key={i} className="top-item">
                                            <span className={`rank ${i === 0 ? 'rank-1' : ''}`}>{i + 1}</span>
                                            <span className="name">{c.customer_name?.substring(0, 10) || '-'}</span>
                                            <span className="amount">{((c.total_sales || 0) / 10000).toFixed(0)}万</span>
                                            <span className="ratio">{(c.share_ratio || 0).toFixed(1)}%</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="no-data">暂无客户数据</p>
                            )}
                        </div>
                        <div>
                            <SectionTitle name="供应商集中度" color="orange" />
                            {top_suppliers?.length > 0 ? (
                                <div className="top-list">
                                    {top_suppliers.slice(0, 5).map((s, i) => (
                                        <div key={i} className="top-item">
                                            <span className={`rank ${i === 0 ? 'rank-1' : ''}`}>{i + 1}</span>
                                            <span className="name">{s.supplier_name?.substring(0, 10) || '-'}</span>
                                            <span className="amount">{((s.total_purchase || 0) / 10000).toFixed(0)}万</span>
                                            <span className="ratio">{(s.share_ratio || 0).toFixed(1)}%</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="no-data">暂无供应商数据</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* 六、研发创新画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Award size={18} /> 六、研发创新画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="研发投入" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="研发投入总额" value={`${((rd_innovation?.rd_investment || 0) / 10000).toFixed(0)}万元`} evalInfo={{ text: '充足', type: 'positive' }} />
                                <CompactMetric label="研发投入强度" value={`${rd_innovation?.rd_investment_ratio || 0}%`} evalInfo={rd_innovation?.rd_ratio_eval ? { text: rd_innovation.rd_ratio_eval[0], type: rd_innovation.rd_ratio_eval[1] === 'green' ? 'positive' : 'neutral' } : null} />
                                <CompactMetric label="研发人员占比" value={`${employee_structure?.rd_ratio || 0}%`} />
                            </div>
                            <SectionTitle name="知识产权" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="专利总数" value={`${rd_innovation?.patent_total || 0}项`} evalInfo={rd_innovation?.patent_eval ? { text: rd_innovation.patent_eval[0], type: rd_innovation.patent_eval[1] === 'green' ? 'positive' : 'neutral' } : null} bgColor="bg-purple" />
                                <CompactMetric label="发明专利" value={`${rd_innovation?.patent_invention || 0}项`} bgColor="bg-purple" />
                                <CompactMetric label="软件著作权" value={`${rd_innovation?.software_copyright || 0}项`} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div className="bg-gradient-blue">
                            <SectionTitle name="专利趋势" color="blue" />
                            <div className="chart-container" style={{ height: '180px' }}>
                                <BarChart
                                    data={[
                                        { name: '2022', value: Math.round((rd_innovation?.patent_total || 0) * 0.6), color: '#3b82f6' },
                                        { name: '2023', value: Math.round((rd_innovation?.patent_total || 0) * 0.8), color: '#3b82f6' },
                                        { name: '2024', value: rd_innovation?.patent_total || 0, color: '#3b82f6' }
                                    ]}
                                />
                            </div>
                            <CompactMetric label="年度新增专利" value={`${rd_innovation?.new_patents_year || 0}项`} evalInfo={{ text: '活跃', type: 'positive' }} bgColor="bg-white" />
                        </div>
                        <div className="bg-gradient-green">
                            <SectionTitle name="研发成果" color="green" />
                            <ProgressBar label="高新产品收入占比" value={rd_innovation?.high_tech_product_ratio || 0} color="blue" />
                            <ProgressBar label="发明专利占比" value={rd_innovation?.patent_total > 0 ? Math.round((rd_innovation?.patent_invention || 0) / rd_innovation.patent_total * 100) : 0} color="purple" />
                        </div>
                    </div>
                </div>

                {/* 七、税务画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Calculator size={18} /> 七、税务画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="纳税人信息" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="纳税人识别号" value={basic_info?.credit_code || '-'} />
                                <CompactMetric label="纳税人类型" value={basic_info?.taxpayer_type || '一般纳税人'} evalInfo={{ text: '正常', type: 'positive' }} />
                                <CompactMetric label="征收方式" value={basic_info?.collection_method || '查账征收'} />
                                <CompactMetric label="纳税信用等级" value={basic_info?.tax_credit_rating || '-'} evalInfo={{ text: '优秀', type: 'positive' }} />
                            </div>
                        </div>
                        <div className="bg-gradient-blue">
                            <SectionTitle name="税种构成" color="cyan" />
                            <div className="chart-container" style={{ height: '180px' }}>
                                {taxPieData.length > 0 ? (
                                    <PieChart data={taxPieData} />
                                ) : (
                                    <BarChart data={[
                                        { name: '增值税', value: (tax_summary?.vat_amount || 0) / 10000, color: '#3b82f6' },
                                        { name: '所得税', value: (tax_summary?.income_tax || 0) / 10000, color: '#8b5cf6' }
                                    ]} />
                                )}
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="综合税负" color="blue" />
                            <div className="metrics-stack">
                                <CompactMetric label="年度纳税总额" value={`${((tax_summary?.total_tax || 0) / 10000).toFixed(2)}万元`} bgColor="bg-blue" />
                                <CompactMetric label="综合税负率" value={`${(tax_summary?.tax_burden || 0).toFixed(2)}%`} evalInfo={{ text: '合理', type: 'positive' }} bgColor="bg-blue" />
                                <CompactMetric label="增值税额" value={`${((tax_summary?.vat_amount || 0) / 10000).toFixed(2)}万元`} bgColor="bg-blue" />
                                <CompactMetric label="企业所得税" value={`${((tax_summary?.income_tax || 0) / 10000).toFixed(2)}万元`} bgColor="bg-blue" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 八、跨境业务画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Globe size={18} /> 八、跨境业务画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="跨境交易" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="境外收入总额" value={`${((cross_border?.overseas_revenue || 0) / 10000).toFixed(0)}万元`} />
                                <CompactMetric label="境外收入占比" value={`${(cross_border?.overseas_revenue_ratio || 0).toFixed(1)}%`} evalInfo={cross_border?.overseas_eval ? { text: cross_border.overseas_eval[0], type: 'neutral' } : null} />
                                <CompactMetric label="出口销售额" value={`${((cross_border?.export_sales || 0) / 10000).toFixed(0)}万元`} />
                                <CompactMetric label="进口采购额" value={`${((cross_border?.import_purchase || 0) / 10000).toFixed(0)}万元`} />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="关联交易" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="关联交易总额" value={`${((profile?.related_transactions?.reduce((sum, t) => sum + (t.transaction_amount || 0), 0) || 0) / 10000).toFixed(0)}万元`} bgColor="bg-purple" />
                                <CompactMetric label="关联交易定价" value="可比非受控价格法" evalInfo={{ text: '合规', type: 'positive' }} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="国际税收" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="适用税收协定" value={cross_border?.applicable_treaty || '无'} bgColor="bg-orange" />
                                <CompactMetric label="境外已缴税款" value={`${((cross_border?.overseas_tax_paid || 0) / 10000).toFixed(2)}万元`} bgColor="bg-orange" />
                                <CompactMetric label="境外税收抵免" value={`${((cross_border?.overseas_tax_credit || 0) / 10000).toFixed(2)}万元`} evalInfo={{ text: '已抵免', type: 'positive' }} bgColor="bg-orange" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 九、合规风险画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Shield size={18} /> 九、合规风险画像</h3>
                    <div className="metrics-row-5">
                        <div>
                            <SectionTitle name="税务合规" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="申报及时率" value={`${compliance?.tax_compliance?.filing_rate || 100}%`} evalInfo={{ text: '优秀', type: 'positive' }} />
                                <CompactMetric label="缴款及时率" value={`${compliance?.tax_compliance?.payment_rate || 100}%`} evalInfo={{ text: '优秀', type: 'positive' }} />
                                <CompactMetric label="稽查次数" value={`${compliance?.tax_compliance?.audit_count || 0}次`} evalInfo={{ text: '良好', type: 'positive' }} />
                                <CompactMetric label="税务风险等级" value={compliance?.tax_compliance?.risk_level || '低'} evalInfo={{ text: '安全', type: 'positive' }} />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="财务合规" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="审计意见" value={compliance?.financial_compliance?.audit_opinion || '标准无保留'} evalInfo={{ text: '优秀', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="内控缺陷" value={`${compliance?.financial_compliance?.control_defects || 0}个`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="会计规范性" value={compliance?.financial_compliance?.accounting_standard || '优'} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="经营合规" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="环保处罚" value={`${compliance?.operational_compliance?.env_penalty_count || 0}次`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-orange" />
                                <CompactMetric label="安全事故" value={`${compliance?.operational_compliance?.safety_incident_count || 0}次`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-orange" />
                                <CompactMetric label="质量处罚" value={`${compliance?.operational_compliance?.quality_penalty_count || 0}次`} bgColor="bg-orange" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="法律风险" color="cyan" />
                            <div className="metrics-stack">
                                <CompactMetric label="涉诉案件" value={`${risk_info?.length || 0}件`} evalInfo={{ text: risk_info?.length > 0 ? '较少' : '无', type: risk_info?.length > 0 ? 'warning' : 'positive' }} bgColor="bg-cyan" />
                                <CompactMetric label="失信被执行" value="否" evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-cyan" />
                                <CompactMetric label="经营异常" value="0条" evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-cyan" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="风险评估" color="blue" />
                            <div className="metrics-stack">
                                <CompactMetric label="流动性风险" value={compliance?.risk_assessment?.liquidity_risk || '低'} evalInfo={{ text: '安全', type: 'positive' }} bgColor="bg-blue" />
                                <CompactMetric label="客户集中风险" value={compliance?.risk_assessment?.customer_concentration_risk || '低'} bgColor="bg-blue" />
                                <CompactMetric label="供应商依赖" value={compliance?.risk_assessment?.supplier_dependency_risk || '中'} bgColor="bg-blue" />
                                <CompactMetric label="综合评级" value={compliance?.risk_assessment?.overall_rating || 'B'} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-blue" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 十、外部关系画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Briefcase size={18} /> 十、外部关系画像</h3>
                    <div className="metrics-row-2">
                        <div>
                            <SectionTitle name="银行关系" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="合作银行数量" value={`${bank_relations?.bank_count || 0}家`} />
                                <CompactMetric label="银行授信总额" value={`${((bank_relations?.total_credit_line || 0) / 10000).toFixed(0)}万元`} evalInfo={bank_relations?.credit_eval ? { text: bank_relations.credit_eval[0], type: 'positive' } : null} />
                                <CompactMetric label="贷款余额" value={`${((bank_relations?.loan_balance || 0) / 10000).toFixed(0)}万元`} evalInfo={{ text: `${bank_relations?.usage_ratio || 0}%使用`, type: 'neutral' }} />
                                <CompactMetric label="加权平均利率" value={`${bank_relations?.weighted_avg_rate || 0}%`} evalInfo={bank_relations?.rate_eval ? { text: bank_relations.rate_eval[0], type: bank_relations.rate_eval[1] === 'green' ? 'positive' : 'neutral' } : null} />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="信用状况" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="人行征信评级" value={bank_relations?.pboc_credit_rating || '-'} evalInfo={{ text: '优秀', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="海关信用等级" value={bank_relations?.customs_credit_rating || '-'} evalInfo={{ text: '正常', type: 'neutral' }} bgColor="bg-purple" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 十一、数字化画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Database size={18} /> 十一、数字化画像</h3>
                    <div className="metrics-row-2">
                        <div>
                            <SectionTitle name="系统覆盖" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="ERP系统覆盖率" value={`${digital_capability?.erp_coverage || 0}%`} evalInfo={{ text: '高', type: 'positive' }} />
                                <CompactMetric label="财务系统覆盖率" value={`${digital_capability?.finance_system_coverage || 0}%`} evalInfo={{ text: '全面', type: 'positive' }} />
                                <CompactMetric label="税务系统覆盖率" value={`${digital_capability?.tax_system_coverage || 0}%`} evalInfo={{ text: '全面', type: 'positive' }} />
                                <CompactMetric label="财务数据质量" value={digital_capability?.finance_data_quality || '-'} evalInfo={{ text: '高质量', type: 'positive' }} />
                                <CompactMetric label="税务数据质量" value={digital_capability?.tax_data_quality || '-'} evalInfo={{ text: '高质量', type: 'positive' }} />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="数字化能力" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="系统集成度" value={digital_capability?.system_integration || '-'} evalInfo={{ text: '互联互通', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="数据完整性" value={`${digital_capability?.data_completeness || 0}%`} evalInfo={{ text: '优秀', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="流程自动化率" value={`${digital_capability?.process_automation || 0}%`} evalInfo={{ text: '良好', type: 'positive' }} bgColor="bg-purple" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 十二、ESG画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><CheckCircle size={18} /> 十二、ESG画像</h3>
                    <div className="metrics-row-3">
                        <div>
                            <SectionTitle name="环境责任" color="green" />
                            <div className="metrics-stack">
                                <CompactMetric label="环保投入占比" value={`${esg?.environmental?.investment_ratio || 0}%`} evalInfo={{ text: '积极', type: 'positive' }} />
                                <CompactMetric label="节能减排投资" value={`${((esg?.environmental?.energy_saving_investment || 0) / 10000).toFixed(0)}万元`} />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="社会责任" color="purple" />
                            <div className="metrics-stack">
                                <CompactMetric label="公益捐赠金额" value={`${((esg?.social?.charity_donation || 0) / 10000).toFixed(0)}万元`} evalInfo={{ text: '积极', type: 'positive' }} bgColor="bg-purple" />
                                <CompactMetric label="残疾人雇用比例" value={`${esg?.social?.disability_employment_ratio || 0}%`} evalInfo={{ text: '达标', type: 'positive' }} bgColor="bg-purple" />
                            </div>
                        </div>
                        <div>
                            <SectionTitle name="公司治理" color="orange" />
                            <div className="metrics-stack">
                                <CompactMetric label="信息披露透明度" value={esg?.governance?.info_disclosure_level || '-'} evalInfo={{ text: '规范', type: 'positive' }} bgColor="bg-orange" />
                                <CompactMetric label="关联交易审批规范性" value={esg?.governance?.related_party_review || '-'} evalInfo={{ text: '合规', type: 'positive' }} bgColor="bg-orange" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* 十三、政策匹配画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Target size={18} /> 十三、政策匹配画像</h3>
                    <div className="metrics-row-2">
                        <div>
                            <SectionTitle name="当前享受政策" color="purple" />
                            {policy_eligibility?.filter(p => p.eligibility_status === '享受中' || p.eligibility_status === '符合').map((policy, i) => (
                                <CompactMetric
                                    key={i}
                                    label={policy.policy_name}
                                    value={policy.eligibility_status}
                                    evalInfo={policy.benefit_amount ? { text: `${(policy.benefit_amount / 10000).toFixed(0)}万/年`, type: 'positive' } : null}
                                    bgColor="bg-purple"
                                />
                            ))}
                            {(!policy_eligibility || policy_eligibility.filter(p => p.eligibility_status === '享受中' || p.eligibility_status === '符合').length === 0) && (
                                <CompactMetric label="暂无享受政策" value="-" bgColor="bg-purple" />
                            )}
                        </div>
                        <div>
                            <SectionTitle name="政策预警" color="orange" />
                            {policy_eligibility?.filter(p => p.alert_level).map((policy, i) => (
                                <CompactMetric
                                    key={i}
                                    label={policy.policy_name}
                                    value={policy.expire_date ? `${policy.expire_date}到期` : '-'}
                                    evalInfo={{ text: policy.alert_level === '中' ? '需关注' : '紧急', type: 'warning' }}
                                    bgColor="bg-orange"
                                />
                            ))}
                            {(!policy_eligibility || policy_eligibility.filter(p => p.alert_level).length === 0) && (
                                <CompactMetric label="无预警信息" value="-" bgColor="bg-orange" />
                            )}
                        </div>
                    </div>
                </div>

                {/* 十四、特殊业务画像 */}
                <div className="profile-card">
                    <h3 className="card-title"><Factory size={18} /> 十四、特殊业务画像</h3>
                    <div className="metrics-row-2">
                        {special_business?.map((biz, i) => (
                            <div key={i}>
                                <SectionTitle name={`${biz.business_type}业务`} color={i % 2 === 0 ? 'green' : 'purple'} />
                                <div className="metrics-stack">
                                    <CompactMetric label={`${biz.business_type}收入`} value={`${((biz.business_revenue || 0) / 10000).toFixed(0)}万元`} bgColor={i % 2 === 0 ? '' : 'bg-purple'} />
                                    <CompactMetric label="收入占比" value={`${biz.revenue_ratio || 0}%`} evalInfo={biz.revenue_ratio >= 50 ? { text: '主营', type: 'positive' } : null} bgColor={i % 2 === 0 ? '' : 'bg-purple'} />
                                    {biz.value_added_rate && (
                                        <CompactMetric label="增值率" value={`${biz.value_added_rate}%`} bgColor={i % 2 === 0 ? '' : 'bg-purple'} />
                                    )}
                                    {biz.tax_refund_amount > 0 && (
                                        <CompactMetric label="退税金额" value={`${((biz.tax_refund_amount || 0) / 10000).toFixed(0)}万元`} evalInfo={{ text: '已享受', type: 'positive' }} bgColor={i % 2 === 0 ? '' : 'bg-purple'} />
                                    )}
                                    {biz.cert_type && (
                                        <CompactMetric label="认定类型" value={biz.cert_type} bgColor={i % 2 === 0 ? '' : 'bg-purple'} />
                                    )}
                                </div>
                            </div>
                        ))}
                        {(!special_business || special_business.length === 0) && (
                            <div>
                                <SectionTitle name="暂无特殊业务" color="green" />
                                <p className="no-data">暂无特殊业务数据</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default CompanyProfile;
