import React, { useState, useEffect } from 'react';
import { Database, Calendar, Filter, FileText, List } from 'lucide-react';
import { fetchBrowseCompanies, fetchBrowseTables, fetchBrowsePeriods, fetchBrowseData } from '../services/api';
import VatReturnRawView from './VatReturnRawView';
import IncomeStatementRawView from './IncomeStatementRawView';
import BalanceSheetRawView from './BalanceSheetRawView';
import CashFlowStatementRawView from './CashFlowStatementRawView';
import CITReturnRawView from './CITReturnRawView';
import './DataBrowser.css';

const DataBrowser = () => {
    // Selection State
    const [companies, setCompanies] = useState([]);
    const [tables, setTables] = useState([]);
    const [periods, setPeriods] = useState([]);

    // View Mode State: 'general' | 'raw'
    const [viewMode, setViewMode] = useState('general');

    const [selectedCompany, setSelectedCompany] = useState('');
    const [selectedTable, setSelectedTable] = useState('');
    const [selectedPeriod, setSelectedPeriod] = useState('');

    // Data State
    const [tableData, setTableData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Initial Load
    useEffect(() => {
        const loadInitial = async () => {
            try {
                const [comps, tabs] = await Promise.all([
                    fetchBrowseCompanies(),
                    fetchBrowseTables()
                ]);
                setCompanies(comps);
                setTables(tabs);

                if (comps.length > 0) setSelectedCompany(comps[0].id);
                if (tabs.length > 0) {
                    const defaultTable = tabs.find(t => t.name === 'income_statements') || tabs[0];
                    setSelectedTable(defaultTable.name);
                }
            } catch (err) {
                console.error("Failed to load initial data", err);
                setError("加载基础数据失败");
            }
        };
        loadInitial();
    }, []);

    // Load Periods
    useEffect(() => {
        if (!selectedCompany || !selectedTable) return;

        const loadPeriods = async () => {
            try {
                const pList = await fetchBrowsePeriods(selectedCompany, selectedTable);
                setPeriods(pList);

                // If switching to raw mode, we must have a period selected. Default to latest.
                if (viewMode === 'raw' && pList.length > 0) {
                    setSelectedPeriod(pList[0]);
                } else if (viewMode === 'general') {
                    // General mode defaults to "All" (empty string)
                    setSelectedPeriod("");
                }
            } catch (err) {
                console.error("Failed to load periods", err);
                setPeriods([]);
            }
        };
        loadPeriods();
    }, [selectedCompany, selectedTable, viewMode]);

    // Fetch Data
    useEffect(() => {
        if (!selectedCompany || !selectedTable) return;

        // Validation for Raw Mode
        if (viewMode === 'raw' && !selectedPeriod && periods.length > 0) {
            if (periods.length > 0) setSelectedPeriod(periods[0]);
        }

        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await fetchBrowseData(selectedCompany, selectedTable, selectedPeriod);
                setTableData(data);
            } catch (err) {
                console.error("Failed to load table data", err);
                setError("加载数据失败: " + err.message);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [selectedCompany, selectedTable, selectedPeriod, viewMode]);

    // Helpers
    const getTableName = (name) => {
        const t = tables.find(t => t.name === name);
        return t ? t.label : name;
    };

    const supportsRawView = selectedTable === 'tax_returns_vat' ||
        selectedTable === 'income_statements' ||
        selectedTable === 'balance_sheets' ||
        selectedTable === 'cash_flow_statements' ||
        selectedTable === 'tax_returns_income';

    // Handle View Mode Toggle
    const handleViewModeChange = (mode) => {
        setViewMode(mode);
    };

    return (
        <div className="db-container">
            {/* Filters */}
            <div className="db-filters">
                <div className="db-filter-item">
                    <label className="db-filter-label">选择企业</label>
                    <div style={{ position: 'relative' }}>
                        <select
                            className="db-select"
                            style={{ width: '100%', paddingLeft: '32px' }}
                            value={selectedCompany}
                            onChange={(e) => setSelectedCompany(e.target.value)}
                        >
                            {companies.map(c => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                        <Filter style={{ width: '16px', height: '16px', position: 'absolute', left: '10px', top: '10px', color: '#6b7280' }} />
                    </div>
                </div>

                <div className="db-filter-item">
                    <label className="db-filter-label">选择数据表</label>
                    <div style={{ position: 'relative' }}>
                        <select
                            className="db-select"
                            style={{ width: '100%', paddingLeft: '32px' }}
                            value={selectedTable}
                            onChange={(e) => {
                                setSelectedTable(e.target.value);
                                setViewMode('general'); // Reset to general when switching tables
                            }}
                        >
                            {tables.map(t => (
                                <option key={t.name} value={t.name}>{t.label}</option>
                            ))}
                        </select>
                        <Database style={{ width: '16px', height: '16px', position: 'absolute', left: '10px', top: '10px', color: '#6b7280' }} />
                    </div>
                </div>

                <div className="db-filter-item">
                    <label className="db-filter-label">选择期间</label>
                    <div style={{ position: 'relative' }}>
                        <select
                            className="db-select"
                            style={{ width: '100%', paddingLeft: '32px' }}
                            value={selectedPeriod}
                            onChange={(e) => setSelectedPeriod(e.target.value)}
                        >
                            {viewMode === 'general' && <option value="">全部期间</option>}
                            {periods.map(p => (
                                <option key={p} value={p}>{p}</option>
                            ))}
                        </select>
                        <Calendar style={{ width: '16px', height: '16px', position: 'absolute', left: '10px', top: '10px', color: '#6b7280' }} />
                    </div>
                </div>

                {/* View Mode Toggle - Always Visible */}
                <div className="db-filter-item" style={{ marginLeft: 'auto', minWidth: 'auto' }}>
                    <label className="db-filter-label">&nbsp;</label>
                    <div className="db-view-toggle">
                        <button
                            className={`db-toggle-btn ${viewMode === 'general' ? 'active' : ''}`}
                            onClick={() => handleViewModeChange('general')}
                        >
                            <List size={16} /> 通表格式
                        </button>
                        <button
                            className={`db-toggle-btn ${viewMode === 'raw' ? 'active' : ''}`}
                            onClick={() => handleViewModeChange('raw')}
                        >
                            <FileText size={16} /> 原表格式
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="db-content">
                {viewMode === 'raw' ? (
                    supportsRawView ? (
                        // Supported Raw View
                        tableData ? (
                            <div className="db-table-wrapper">
                                {loading ? (
                                    <div className="db-loading"><div className="db-spinner"></div>加载中...</div>
                                ) : tableData.data && tableData.data.length > 0 ? (
                                    selectedTable === 'tax_returns_vat' ? (
                                        <VatReturnRawView
                                            data={tableData.data[0]}
                                            companyInfo={companies.find(c => String(c.id) === String(selectedCompany))}
                                        />
                                    ) : selectedTable === 'income_statements' ? (
                                        <IncomeStatementRawView
                                            data={tableData.data[0]}
                                            companyInfo={companies.find(c => String(c.id) === String(selectedCompany))}
                                        />
                                    ) : selectedTable === 'balance_sheets' ? (
                                        <BalanceSheetRawView
                                            data={tableData.data[0]}
                                            companyInfo={companies.find(c => String(c.id) === String(selectedCompany))}
                                        />
                                    ) : selectedTable === 'cash_flow_statements' ? (
                                        <CashFlowStatementRawView
                                            data={tableData.data[0]}
                                            companyInfo={companies.find(c => String(c.id) === String(selectedCompany))}
                                        />
                                    ) : selectedTable === 'tax_returns_income' ? (
                                        <CITReturnRawView
                                            data={tableData.data[0]}
                                            companyInfo={companies.find(c => String(c.id) === String(selectedCompany))}
                                        />
                                    ) : null
                                ) : (
                                    <div className="db-empty">暂无数据</div>
                                )}
                            </div>
                        ) : null
                    ) : (
                        // Not Supported Message
                        <div className="db-empty">
                            <FileText style={{ width: '48px', height: '48px', marginBottom: '16px', opacity: 0.5 }} />
                            <div>该报表暂不支持原表格式查看</div>
                            <button
                                className="dm-btn-secondary"
                                style={{ marginTop: '16px' }}
                                onClick={() => setViewMode('general')}
                            >
                                返回通表格式
                            </button>
                        </div>
                    )
                ) : (
                    <>
                        <div className="db-table-header">
                            <div className="db-title">
                                <Database style={{ color: '#2563eb', width: '20px' }} />
                                {getTableName(selectedTable)}
                                {tableData && <span className="db-count">{tableData.total} 条数据</span>}
                            </div>
                        </div>

                        <div className="db-table-wrapper">
                            {loading ? (
                                <div className="db-loading">
                                    <div className="db-spinner"></div>
                                    加载中...
                                </div>
                            ) : error ? (
                                <div className="db-empty" style={{ color: '#ef4444' }}>
                                    {error}
                                </div>
                            ) : !tableData || tableData.data.length === 0 ? (
                                <div className="db-empty">
                                    暂无数据
                                </div>
                            ) : (
                                <table className="db-table">
                                    <thead>
                                        <tr>
                                            {tableData.columns.map(col => (
                                                <th key={col.key}>{col.label}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {tableData.data.map((row, idx) => (
                                            <tr key={idx}>
                                                {tableData.columns.map(col => (
                                                    <td key={col.key}>{row[col.key]}</td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default DataBrowser;
