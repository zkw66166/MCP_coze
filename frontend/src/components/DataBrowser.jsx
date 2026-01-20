
import React, { useState, useEffect } from 'react';
import { Database, Calendar, Filter, Download } from 'lucide-react';
import { fetchBrowseCompanies, fetchBrowseTables, fetchBrowsePeriods, fetchBrowseData } from '../services/api';
import './DataBrowser.css';

const DataBrowser = () => {
    // Selection State
    const [companies, setCompanies] = useState([]);
    const [tables, setTables] = useState([]);
    const [periods, setPeriods] = useState([]);

    const [selectedCompany, setSelectedCompany] = useState('');
    const [selectedTable, setSelectedTable] = useState('');
    const [selectedPeriod, setSelectedPeriod] = useState('');

    // Data State
    const [tableData, setTableData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Initial Load: Companies and Tables
    useEffect(() => {
        const loadInitial = async () => {
            try {
                const [comps, tabs] = await Promise.all([
                    fetchBrowseCompanies(),
                    fetchBrowseTables()
                ]);
                setCompanies(comps);
                setTables(tabs);

                // Select default if available
                if (comps.length > 0) setSelectedCompany(comps[0].id);
                if (tabs.length > 0) {
                    // Prefer Income Statement or Balance Sheet as default
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

    // Load Periods when Company or Table changes
    useEffect(() => {
        if (!selectedCompany || !selectedTable) return;

        const loadPeriods = async () => {
            try {
                const pList = await fetchBrowsePeriods(selectedCompany, selectedTable);
                setPeriods(pList);
                // Default select 'All' or empty for all periods? 
                // Specification implies viewing by period, but "All" is useful.
                // If periods exist, select the latest one by default for performance, or empty for all.
                // Let's default to empty (All) if user wants to see everything, 
                // OR select the first one (latest) if the list is long.
                // For "Browse", usually seeing the latest is good.
                // But the requirement says "Switch periods".
                // Let's default to "" (All) to show all data as user requested "vertical scroll for ALL data".
                setSelectedPeriod("");
            } catch (err) {
                console.error("Failed to load periods", err);
                // Don't block, just empty periods
                setPeriods([]);
            }
        };
        loadPeriods();
    }, [selectedCompany, selectedTable]);

    // Fetch Data
    useEffect(() => {
        if (!selectedCompany || !selectedTable) return;

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
    }, [selectedCompany, selectedTable, selectedPeriod]);

    // Helpers
    const getTableName = (name) => {
        const t = tables.find(t => t.name === name);
        return t ? t.label : name;
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
                            onChange={(e) => setSelectedTable(e.target.value)}
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
                            <option value="">全部期间</option>
                            {periods.map(p => (
                                <option key={p} value={p}>{p}</option>
                            ))}
                        </select>
                        <Calendar style={{ width: '16px', height: '16px', position: 'absolute', left: '10px', top: '10px', color: '#6b7280' }} />
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="db-content">
                <div className="db-table-header">
                    <div className="db-title">
                        <Database style={{ color: '#2563eb', width: '20px' }} />
                        {getTableName(selectedTable)}
                        {tableData && <span className="db-count">{tableData.total} 条数据</span>}
                    </div>
                    {/* Placeholder for export if needed later */}
                    {/* <button className="dm-btn-primary">
                        <Download style={{ width: '14px', marginRight: '6px' }} />
                        导出数据
                    </button> */}
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
            </div>
        </div>
    );
};

export default DataBrowser;
