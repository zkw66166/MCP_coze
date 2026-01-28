import { Server, Database, Activity, Shuffle, CheckCircle, Cloud, Settings, Sliders, AlertCircle, HardDrive, Cpu, AlertTriangle } from 'lucide-react';
import '../../pages/Settings.css';

function ServiceSettings() {
    console.log("ServiceSettings loaded");
    return (
        <div className="service-settings-wrapper">
            {/* System Status Banner */}
            <div className="settings-card" style={{ background: 'linear-gradient(to right, #eff6ff, #ffffff)' }}>
                <div className="card-title">
                    <Activity size={20} />
                    <span>系统运行状态</span>
                </div>
                <div style={{ display: 'flex', gap: '40px', padding: '10px 0' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '24px', fontWeight: '700', color: '#10b981' }}>99.9%</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>系统可用性</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '24px', fontWeight: '700', color: '#3b82f6' }}>45ms</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>平均响应时间</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '24px', fontWeight: '700', color: '#8b5cf6' }}>1,247</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>今日访问量</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '24px', fontWeight: '700', color: '#f59e0b' }}>0</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>告警数量</div>
                    </div>
                </div>
            </div>

            <div className="prototype-grid">
                {/* Service Parameter Config */}
                <div className="settings-card">
                    <div className="card-title">
                        <Sliders size={20} />
                        <span>服务参数配置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item" style={{ display: 'block' }}>
                            <div className="setting-label" style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                                <div>
                                    <div style={{ fontWeight: 500 }}>并发处理限制</div>
                                    <div style={{ fontSize: '12px', color: '#6b7280' }}>系统最大并发任务数</div>
                                </div>
                                <span style={{ fontWeight: 600, color: '#2563EB' }}>500</span>
                            </div>
                            <div className="setting-control" style={{ width: '100%' }}>
                                <input type="range" className="filter-select" style={{ width: '100%' }} min="100" max="1000" defaultValue="500" />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>开票额度配置</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>默认企业的月度开票限额</div>
                            </div>
                            <div className="setting-control">
                                <select className="filter-select" defaultValue="100w">
                                    <option value="50w">50万</option>
                                    <option value="100w">100万</option>
                                    <option value="500w">500万</option>
                                </select>
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>存储策略</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>默认文件存储保留时间</div>
                            </div>
                            <div className="setting-control">
                                <select className="filter-select" defaultValue="3year">
                                    <option value="1year">1年</option>
                                    <option value="3year">3年</option>
                                    <option value="forever">永久</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Alert & Monitor */}
                <div className="settings-card">
                    <div className="card-title">
                        <AlertCircle size={20} />
                        <span>预警与监控设置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <Cpu size={14} /> CPU 负载预警
                                </div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>负载超过 80% 时发送告警</div>
                            </div>
                            <div className="setting-control">
                                <input type="checkbox" defaultChecked />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <HardDrive size={14} /> 磁盘空间预警
                                </div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>剩余空间不足 10% 时发送告警</div>
                            </div>
                            <div className="setting-control">
                                <input type="checkbox" defaultChecked />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <AlertTriangle size={14} /> 异常登录报警
                                </div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>检测到异常 IP 访问时报警</div>
                            </div>
                            <div className="setting-control">
                                <input type="checkbox" defaultChecked />
                            </div>
                        </div>
                    </div>
                </div>

                {/* External Interfaces */}
                <div className="settings-card">
                    <div className="card-title">
                        <Shuffle size={20} />
                        <span>外部接口配置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    税局接口服务
                                    <span className="status-badge status-active">已连接</span>
                                </div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>上次同步: 10分钟前</div>
                            </div>
                            <div className="setting-control">
                                <button className="bulk-btn">配置</button>
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    银行对账系统
                                    <span className="status-badge status-inactive">未连接</span>
                                </div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>需要更新授权凭证</div>
                            </div>
                            <div className="setting-control">
                                <button className="bulk-btn primary">连接</button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Data Management */}
                <div className="settings-card">
                    <div className="card-title">
                        <Database size={20} />
                        <span>数据管理设置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>自动备份</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>每日凌晨 2:00 执行全量备份</div>
                            </div>
                            <div className="setting-control">
                                <select className="filter-select" defaultValue="daily">
                                    <option value="daily">每日</option>
                                    <option value="weekly">每周</option>
                                </select>
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>数据保留策略</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>历史数据保留时长</div>
                            </div>
                            <div className="setting-control">
                                <select className="filter-select" defaultValue="365">
                                    <option value="365">1年</option>
                                    <option value="1095">3年</option>
                                    <option value="forever">永久</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ServiceSettings;
