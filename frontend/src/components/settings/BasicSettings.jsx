import { Monitor, Shield, Bell, Moon, Globe, Lock, Clock, ToggleLeft, Wrench, Phone, MessageCircle, Mail } from 'lucide-react';
import '../../pages/Settings.css';

function BasicSettings() {
    console.log("BasicSettings loaded");
    return (
        <div className="basic-settings-wrapper">
            <div className="prototype-grid">
                {/* System Preferences */}
                <div className="settings-card">
                    <div className="card-title">
                        <Monitor size={20} />
                        <span>系统偏好</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>暗黑模式</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>开启系统的深色主题模式</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#d1d5db" />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>系统语言</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>选择系统显示语言</div>
                            </div>
                            <div className="setting-control">
                                <select className="filter-select" defaultValue="zh-CN">
                                    <option value="zh-CN">简体中文</option>
                                    <option value="en-US">English</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Security Settings */}
                <div className="settings-card">
                    <div className="card-title">
                        <Shield size={20} />
                        <span>安全设置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>强制密码过期</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>每 90 天强制更换密码</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#2563EB" style={{ transform: 'rotate(180deg)' }} />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>自动登出时间</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>无操作自动登出 (分钟)</div>
                            </div>
                            <div className="setting-control">
                                <input type="number" className="filter-select" defaultValue="30" style={{ width: '80px' }} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* System Maintenance (Timer Tasks) */}
                <div className="settings-card">
                    <div className="card-title">
                        <Wrench size={20} />
                        <span>系统维护 (定时任务)</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>自动数据清理</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>每日 3:00 清理临时文件</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#2563EB" style={{ transform: 'rotate(180deg)' }} />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>每日全量备份</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>每日 4:00 备份数据库</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#2563EB" style={{ transform: 'rotate(180deg)' }} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Notification Settings */}
                <div className="settings-card">
                    <div className="card-title">
                        <Bell size={20} />
                        <span>通知设置</span>
                    </div>
                    <div className="setting-list">
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>邮件通知</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>接收系统重要通知邮件</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#2563EB" style={{ transform: 'rotate(180deg)' }} />
                            </div>
                        </div>
                        <div className="setting-item">
                            <div className="setting-label">
                                <div style={{ fontWeight: 500 }}>登录提醒</div>
                                <div style={{ fontSize: '12px', color: '#6b7280' }}>异地登录时发送提醒</div>
                            </div>
                            <div className="setting-control">
                                <ToggleLeft size={36} color="#2563EB" style={{ transform: 'rotate(180deg)' }} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tech Support Section */}
            <div className="settings-card" style={{ marginTop: '24px' }}>
                <div className="card-title">
                    <MessageCircle size={20} />
                    <span>技术支持</span>
                </div>
                <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, padding: '16px', background: '#eff6ff', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563EB' }}>
                            <Phone size={20} />
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: '#1e40af' }}>电话支持</div>
                            <div style={{ fontSize: '12px', color: '#60a5fa' }}>400-123-4567</div>
                        </div>
                    </div>
                    <div style={{ flex: 1, padding: '16px', background: '#ecfdf5', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669' }}>
                            <Mail size={20} />
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: '#065f46' }}>邮件支持</div>
                            <div style={{ fontSize: '12px', color: '#34d399' }}>support@tax-platform.com</div>
                        </div>
                    </div>
                    <div style={{ flex: 1, padding: '16px', background: '#f5f3ff', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#7c3aed' }}>
                            <MessageCircle size={20} />
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: '#5b21b6' }}>在线客服</div>
                            <div style={{ fontSize: '12px', color: '#a78bfa' }}>早 9:00 - 晚 18:00</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default BasicSettings;
