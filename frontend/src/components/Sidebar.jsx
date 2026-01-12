import './Sidebar.css';

/**
 * 左侧导航栏组件（不含logo）
 */
function Sidebar({ activeMenu, onMenuChange }) {
    const menuItems = [
        { id: 'workbench', icon: '📋', label: '工作台' },
        { id: 'ai-chat', icon: '💬', label: 'AI智问' },
        { id: 'company-profile', icon: '📈', label: '企业画像' },
        { id: 'data-management', icon: '📊', label: '数据管理' },
        { id: 'settings', icon: '⚙️', label: '系统设置' },
    ];

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {menuItems.map(item => (
                    <div
                        key={item.id}
                        className={`nav-item ${activeMenu === item.id ? 'active' : ''}`}
                        onClick={() => onMenuChange(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </div>
                ))}
            </nav>
        </aside>
    );
}

export default Sidebar;
