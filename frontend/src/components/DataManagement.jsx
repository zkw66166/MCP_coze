import React, { useState, useEffect } from 'react';
import { Database, Upload, Download, Settings, Shield, Archive, FileText, Eye, Edit, Trash2, Search, Filter, CheckCircle, AlertTriangle, AlertCircle, Clock, Server, Globe, Building, RefreshCw, MoreHorizontal, Activity, BarChart3, Users, ChevronDown, Plus, Calendar } from 'lucide-react';
import { fetchDataManagementStats, runDataQualityCheck } from '../services/api';
import './DataManagement.css';

const DataManagement = ({ selectedCompanyId }) => {
    const [activeTab, setActiveTab] = useState('single');
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [companySearchTerm, setCompanySearchTerm] = useState('');
    const [selectedCompanies, setSelectedCompanies] = useState([]);

    // Stats Data
    const [stats, setStats] = useState({
        summary: { subject_count: 0, report_count: 0, period_count: 0, completeness: 0 },
        companies: [],
        quality_checks: [],
        mapping_synonyms: [],
        update_frequency: []
    });
    const [loading, setLoading] = useState(false);

    // Quality Check State
    const [checkResults, setCheckResults] = useState(null);
    const [checking, setChecking] = useState(false);

    const handleRunCheck = async () => {
        setChecking(true);
        try {
            // Use selected company or default for test
            const results = await runDataQualityCheck(selectedCompanyId);
            setCheckResults(results);
        } catch (error) {
            console.error("Quality Check Failed", error);
            // In a real app, use a toast notification here
        } finally {
            setChecking(false);
        }
    };

    useEffect(() => {
        const loadStats = async () => {
            setLoading(true);
            try {
                // If Single Tab -> pass selectedCompanyId
                // If Multi Tab -> pass null
                const companyIdToFetch = activeTab === 'single' ? selectedCompanyId : null;
                const data = await fetchDataManagementStats(companyIdToFetch);
                setStats(data);
            } catch (error) {
                console.error("Failed to load Data Management stats:", error);
            } finally {
                setLoading(false);
            }
        };

        if (activeTab === 'multi' || (activeTab === 'single' && selectedCompanyId)) {
            loadStats();
        }
    }, [activeTab, selectedCompanyId]);


    const handleFileUpload = (event) => {
        // UI Only for Phase 1
        const files = Array.from(event.target.files);
        const newFiles = files.map(file => ({
            id: Date.now() + Math.random(),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadTime: new Date(),
            status: '处理中',
            progress: 0
        }));

        setUploadedFiles(prev => [...prev, ...newFiles]);

        // Mock upload progress
        newFiles.forEach(file => {
            const interval = setInterval(() => {
                setUploadedFiles(prev => prev.map(f => {
                    if (f.id === file.id && f.progress < 100) {
                        const newProgress = f.progress + 10;
                        return {
                            ...f,
                            progress: newProgress,
                            status: newProgress === 100 ? '已完成' : '处理中'
                        };
                    }
                    return f;
                }));
            }, 200);

            setTimeout(() => clearInterval(interval), 2000);
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Data Complete': return 'green';
            case '数据完整': return 'green';
            case 'Incomplete': return 'yellow';
            case '数据不完整': return 'yellow';
            case '待更新': return 'blue';
            case '数据异常': return 'red';
            default: return 'gray';
        }
    };

    const getMatchColor = (match) => {
        if (match >= 90) return 'green';
        if (match >= 70) return 'yellow';
        return 'red';
    };

    const filteredCompanies = (stats.companies || []).filter(company =>
        company.name.toLowerCase().includes(companySearchTerm.toLowerCase()) ||
        company.taxCode.includes(companySearchTerm)
    );

    const handleCompanySelect = (companyId) => {
        setSelectedCompanies(prev =>
            prev.includes(companyId)
                ? prev.filter(id => id !== companyId)
                : [...prev, companyId]
        );
    };

    // Helper to map icon string to component if needed, or just use hardcoded logic in render
    // Since backend returns simple strings, we map them here
    const getIconForCheck = (status) => {
        if (status === 'Pass') return CheckCircle;
        if (status === 'Warning') return AlertTriangle;
        if (status === 'Pending') return Clock;
        return Archive;
    };

    const SingleCompanyTab = () => (
        <div className="dm-tab-content">
            {/* 数据概览仪表盘 */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Database className="dm-card-icon" style={{ color: '#2563eb' }} />
                        数据管理中心
                    </h3>
                </div>
                <div className="dm-stats-grid">
                    <div className="dm-stat-card blue">
                        <Database className="dm-stat-icon" />
                        <p className="dm-stat-value">{stats.summary.subject_count}</p>
                        <p className="dm-stat-label">财务指标数量</p>
                        <p className="dm-stat-sub">已标准化映射</p>
                    </div>
                    <div className="dm-stat-card green">
                        <FileText className="dm-stat-icon" />
                        <p className="dm-stat-value">{stats.summary.report_count}</p>
                        <p className="dm-stat-label">报表/数据条目</p>
                        <p className="dm-stat-sub">自动同步更新</p>
                    </div>
                    <div className="dm-stat-card purple">
                        <Archive className="dm-stat-icon" />
                        <p className="dm-stat-value">{stats.summary.period_count}</p>
                        <p className="dm-stat-label">数据期间（月）</p>
                        <p className="dm-stat-sub">连续完整数据</p>
                    </div>
                    <div className="dm-stat-card yellow">
                        <CheckCircle className="dm-stat-icon" />
                        <p className="dm-stat-value">{stats.summary.completeness}%</p>
                        <p className="dm-stat-label">数据完整度</p>
                        <p className="dm-stat-sub">质量优良</p>
                    </div>
                </div>
            </div>

            {/* 智能数据映射 (Synonyms) */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Settings className="dm-card-icon" style={{ color: '#4f46e5' }} />
                        智能数据映射（指标同义词）
                    </h3>
                </div>
                <div className="dm-table-wrapper">
                    <table className="dm-table">
                        <thead>
                            <tr>
                                <th>标准指标名称</th>
                                <th>识别同义词</th>
                                <th>状态</th>
                                <th>匹配度</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats.mapping_synonyms && stats.mapping_synonyms.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.standard}</td>
                                    <td>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                            {item.synonyms.map((syn, i) => (
                                                <span key={i} className="dm-tag gray">{syn}</span>
                                            ))}
                                        </div>
                                    </td>
                                    <td>
                                        <span className="dm-tag green">
                                            {item.status}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center' }}>
                                            <span style={{ marginRight: '8px' }}>{item.match}%</span>
                                            <div className="dm-progress-bg">
                                                <div
                                                    className={`dm-progress-fill ${getMatchColor(item.match)}`}
                                                    style={{ width: `${item.match}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* 数据质量检查 */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Shield className="dm-card-icon" style={{ color: '#ea580c' }} />
                        数据质量检查
                    </h3>
                    <button
                        className="dm-btn-primary"
                        onClick={handleRunCheck}
                        disabled={checking}
                        style={{
                            padding: '6px 16px',
                            fontSize: '12px',
                            marginLeft: 'auto', // Right align
                            cursor: checking ? 'not-allowed' : 'pointer',
                            opacity: checking ? 0.7 : 1
                        }}
                    >
                        {checking ? <RefreshCw className="animate-spin" style={{ width: '14px', marginRight: '6px' }} /> : <Activity style={{ width: '14px', marginRight: '6px' }} />}
                        {checking ? '检测中...' : '开始检测'}
                    </button>
                </div>

                <div className="dm-checks-grid">
                    {(() => {
                        // Define fixed order and mapping for the 7 report types
                        const REPORT_TYPES = [
                            { key: 'subject_balance', label: '科目余额表' },
                            { key: 'balance_sheet', label: '资产负债表' },
                            { key: 'income_statement', label: '利润表' },
                            { key: 'cash_flow', label: '现金流量表' },
                            { key: 'vat_return', label: '增值税申报表' },
                            { key: 'cit_return', label: '企业所得税申报表' },
                            { key: 'stamp_duty', label: '印花税申报表' }
                        ];

                        // If checks passed, map backend results to these types
                        if (checkResults) {
                            // DEBUG: Uncomment to see raw data on screen if issues persist
                            // return <pre>{JSON.stringify(checkResults, null, 2)}</pre>;

                            return REPORT_TYPES.map((type, index) => {
                                const result = checkResults && checkResults[type.key];
                                // Fallback if result is entirely missing or null
                                if (!result) {
                                    return (
                                        <div key={index} className="dm-check-item gray">
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <Archive className="dm-card-icon" style={{ color: '#9ca3af' }} />
                                                <div>
                                                    <p style={{ fontWeight: 500, color: '#111827' }}>{type.label}</p>
                                                    <p style={{ fontSize: '12px', color: '#6b7280' }}>未获取到结果</p>
                                                </div>
                                            </div>
                                            <span className="dm-tag gray">未知</span>
                                        </div>
                                    );
                                }


                                const isPass = result.status === 'pass';
                                // Safety check: details might be missing if status is 'skip' or error
                                const details = result.details || [];
                                const failedItems = details.filter(d => d.status !== 'pass');

                                return (
                                    <div key={index} className={`dm-check-item ${isPass ? 'green' : 'red'}`} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', width: '100%', marginBottom: failedItems.length > 0 ? '8px' : '0' }}>
                                            {isPass ?
                                                <CheckCircle className="dm-card-icon" style={{ color: '#10b981' }} /> :
                                                <AlertCircle className="dm-card-icon" style={{ color: '#ef4444' }} />
                                            }
                                            <div style={{ flex: 1, marginLeft: '12px' }}>
                                                <div style={{ fontWeight: 500, color: '#111827' }}>{type.label}</div>
                                                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                                                    {isPass ? '检查通过' : `发现 ${failedItems.length} 个问题`}
                                                </div>
                                            </div>
                                            <span className={`dm-tag ${isPass ? 'green' : 'red'}`}>
                                                {isPass ? '通过' : '异常'}
                                            </span>
                                        </div>

                                        {/* Show failed items details if any */}
                                        {failedItems.length > 0 && (
                                            <div style={{
                                                width: '100%',
                                                marginTop: '8px',
                                                padding: '8px',
                                                backgroundColor: '#fef2f2',
                                                borderRadius: '6px',
                                                border: '1px solid #fee2e2'
                                            }}>
                                                {failedItems.slice(0, 3).map((item, i) => (
                                                    <div key={i} style={{ fontSize: '11px', color: '#b91c1c', marginBottom: '4px' }}>
                                                        • {item.check}: {item.message || 'Check failed'}
                                                    </div>
                                                ))}
                                                {failedItems.length > 3 && (
                                                    <div style={{ fontSize: '11px', color: '#b91c1c', fontStyle: 'italic' }}>
                                                        ...还有 {failedItems.length - 3} 个问题
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                );
                            });
                        }

                        // Initial State (Placeholder Stats)
                        // Backend now returns 7 items in stats.quality_checks matching the types
                        const displayList = stats.quality_checks || [];
                        if (displayList.length === 0) {
                            return (
                                <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '20px', color: '#9ca3af' }}>
                                    暂无检查数据，请点击上方按钮开始检测
                                </div>
                            );
                        }

                        return displayList.map((item, index) => {
                            // Map old/static status format
                            let color = 'gray';
                            let icon = Clock;
                            let text = '待检测';

                            if (item.status === 'Pass') { color = 'green'; icon = CheckCircle; text = '通过'; }
                            else if (item.status === 'Warning') { color = 'yellow'; icon = AlertTriangle; text = '警告'; }
                            else if (item.status === 'Pending') { color = 'blue'; icon = Clock; text = '待检测'; }

                            return (
                                <div key={index} className={`dm-check-item ${color}`}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        {React.createElement(icon, { className: "dm-card-icon", style: { color: 'inherit' } })}
                                        <div>
                                            <p style={{ fontWeight: 500, color: '#111827' }}>{item.check}</p> {/* Use CN name */}
                                            <p style={{ fontSize: '12px', color: '#4b5563' }}>{item.category}</p> {/* Use EN name as subtitle or vice/versa */}
                                        </div>
                                    </div>
                                    <span className={`dm-tag ${color}`}>
                                        {text}
                                    </span>
                                </div>
                            );
                        });
                    })()}
                </div>
            </div>

            {/* Data Update Frequency & Usage Stats Row */}
            <div className="dm-grid-2-cols">
                {/* Data Update Frequency */}
                <div className="dm-card">
                    <div className="dm-card-header">
                        <h3 className="dm-card-title">
                            <Clock className="dm-card-icon" style={{ color: '#0ea5e9' }} />
                            数据更新频率
                        </h3>
                    </div>
                    <div className="dm-table-wrapper">
                        <table className="dm-table">
                            <thead>
                                <tr>
                                    <th>数据源</th>
                                    <th>更新频率</th>
                                    <th>上次更新</th>
                                    <th>状态</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats.update_frequency && stats.update_frequency.map((item, index) => (
                                    <tr key={index}>
                                        <td>{item.source}</td>
                                        <td>{item.frequency}</td>
                                        <td>{item.last_update}</td>
                                        <td><span className="dm-tag green">正常</span></td>
                                    </tr>
                                ))}
                                {/* Fallback if no data */}
                                {!stats.update_frequency && (
                                    <>
                                        <tr><td>资产负债表</td><td>月度</td><td>2024-12-15</td><td><span className="dm-tag green">正常</span></td></tr>
                                        <tr><td>利润表</td><td>月度</td><td>2024-12-15</td><td><span className="dm-tag green">正常</span></td></tr>
                                        <tr><td>增值税申报表</td><td>月度</td><td>2024-12-15</td><td><span className="dm-tag green">正常</span></td></tr>
                                        <tr><td>企业所得税申报表</td><td>季度</td><td>2024-10-20</td><td><span className="dm-tag green">正常</span></td></tr>
                                    </>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Data Usage Stats (Mock) */}
                <div className="dm-card">
                    <div className="dm-card-header">
                        <h3 className="dm-card-title">
                            <Activity className="dm-card-icon" style={{ color: '#8b5cf6' }} />
                            数据使用统计
                        </h3>
                    </div>
                    <div className="dm-usage-stats">
                        <div className="dm-usage-item">
                            <span className="dm-usage-label">本月查询次数</span>
                            <span className="dm-usage-value">1,245</span>
                        </div>
                        <div className="dm-usage-item">
                            <span className="dm-usage-label">生成报告数</span>
                            <span className="dm-usage-value">56</span>
                        </div>
                        <div className="dm-usage-item">
                            <span className="dm-usage-label">API调用量</span>
                            <span className="dm-usage-value">8,932</span>
                        </div>
                        <div className="dm-usage-chart-placeholder">
                            {/* Simple CSS Bar Chart Placeholder */}
                            <div style={{ display: 'flex', alignItems: 'flex-end', height: '100px', gap: '8px', padding: '10px 0' }}>
                                <div style={{ flex: 1, background: '#e5e7eb', height: '40%', borderRadius: '4px' }}></div>
                                <div style={{ flex: 1, background: '#e5e7eb', height: '60%', borderRadius: '4px' }}></div>
                                <div style={{ flex: 1, background: '#e5e7eb', height: '30%', borderRadius: '4px' }}></div>
                                <div style={{ flex: 1, background: '#6366f1', height: '80%', borderRadius: '4px' }}></div>
                                <div style={{ flex: 1, background: '#e5e7eb', height: '50%', borderRadius: '4px' }}></div>
                                <div style={{ flex: 1, background: '#e5e7eb', height: '70%', borderRadius: '4px' }}></div>
                            </div>
                            <p style={{ textAlign: 'center', fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>近6个月数据使用趋势</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* UI-Only Upload Section */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Upload className="dm-card-icon" style={{ color: '#16a34a' }} />
                        智能数据导入 (演示功能)
                    </h3>
                </div>
                <div className="dm-upload-area">
                    <Upload className="dm-stat-icon" style={{ color: '#9ca3af' }} />
                    <h4 style={{ fontSize: '20px', fontWeight: 500, marginBottom: '8px' }}>拖拽文件到此处或点击上传</h4>
                    <p style={{ color: '#4b5563', marginBottom: '16px' }}>支持Excel、CSV、PDF等格式</p>
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                        <label className="dm-btn-primary">
                            <Upload style={{ width: '16px', height: '16px', marginRight: '8px' }} />
                            选择文件
                            <input type="file" multiple onChange={handleFileUpload} className="hidden" style={{ display: 'none' }} />
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );

    const MultiCompanyTab = () => (
        <div className="dm-tab-content">
            {/* 多户企业数据概览 */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Users className="dm-card-icon" style={{ color: '#9333ea' }} />
                        多户企业数据概览
                    </h3>
                </div>
                <div className="dm-stats-grid">
                    <div className="dm-stat-card purple">
                        <Users className="dm-stat-icon" />
                        <p className="dm-stat-value">{(stats.companies || []).length}</p>
                        <p className="dm-stat-label">管理企业总数</p>
                    </div>
                    {/* Add other aggregated stats as needed */}
                </div>
            </div>

            {/* 企业数据列表 */}
            <div className="dm-card">
                <div className="dm-card-header">
                    <h3 className="dm-card-title">
                        <Database className="dm-card-icon" style={{ color: '#4f46e5' }} />
                        企业数据状况列表
                    </h3>
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <div style={{ position: 'relative' }}>
                            <Search style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af' }} />
                            <input
                                type="text"
                                placeholder="搜索企业..."
                                value={companySearchTerm}
                                onChange={(e) => setCompanySearchTerm(e.target.value)}
                                style={{
                                    paddingLeft: '36px',
                                    paddingRight: '12px',
                                    paddingTop: '8px',
                                    paddingBottom: '8px',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    width: '200px'
                                }}
                            />
                        </div>
                        <button style={{
                            display: 'flex',
                            alignItems: 'center',
                            padding: '8px 12px',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            background: '#white',
                            fontSize: '14px',
                            color: '#374151',
                            cursor: 'pointer'
                        }}>
                            <Filter style={{ width: '16px', height: '16px', marginRight: '6px' }} />
                            筛选
                        </button>
                        <button style={{
                            display: 'flex',
                            alignItems: 'center',
                            padding: '8px 12px',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            background: '#white',
                            fontSize: '14px',
                            color: '#374151',
                            cursor: 'pointer'
                        }}>
                            <Download style={{ width: '16px', height: '16px', marginRight: '6px' }} />
                            导出
                        </button>
                    </div>
                </div>
                <div className="dm-table-wrapper">
                    <table className="dm-table">
                        <thead>
                            <tr>
                                <th>
                                    <input type="checkbox" />
                                </th>
                                <th>企业信息</th>
                                <th>数据状态</th>
                                <th>数据完整度</th>
                                <th>最后更新</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCompanies.map((company) => (
                                <tr key={company.id}>
                                    <td>
                                        <input type="checkbox" />
                                    </td>
                                    <td>
                                        <div>
                                            <div style={{ fontSize: '14px', fontWeight: 500, color: '#111827' }}>{company.name}</div>
                                            <div style={{ fontSize: '12px', color: '#6b7280' }}>{company.taxCode}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`dm-tag ${getStatusColor(company.status)}`}>
                                            {company.status}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center' }}>
                                            <span style={{ marginRight: '8px', fontSize: '14px' }}>{company.completeness}%</span>
                                            <div className="dm-progress-bg">
                                                <div
                                                    className={`dm-progress-fill ${getMatchColor(company.completeness)}`}
                                                    style={{ width: `${company.completeness}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td style={{ fontSize: '14px', color: '#6b7280' }}>
                                        {company.lastUpdate}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    return (
        <div className="dm-container">
            {/* 标签页导航 */}
            <div className="dm-tabs">
                <div className="dm-tabs-nav">
                    <button
                        onClick={() => setActiveTab('single')}
                        className={`dm-tab-btn ${activeTab === 'single' ? 'active' : ''}`}
                    >
                        <Database className="dm-tab-icon" />
                        单户企业数据
                    </button>
                    <button
                        onClick={() => setActiveTab('multi')}
                        className={`dm-tab-btn ${activeTab === 'multi' ? 'active' : ''}`}
                    >
                        <Users className="dm-tab-icon" />
                        多户企业数据
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="dm-spinner-container">
                    <div className="dm-spinner"></div>
                </div>
            ) : (
                activeTab === 'single' ? <SingleCompanyTab /> : <MultiCompanyTab />
            )}
        </div>
    );
};

export default DataManagement;
