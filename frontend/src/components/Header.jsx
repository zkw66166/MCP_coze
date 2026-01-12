import './Header.css';

/**
 * 顶部导航栏组件（含logo）
 */
function Header({ companies, selectedCompanyId, onCompanyChange }) {
    const currentTime = new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });

    return (
        <header className="header">
            {/* 左侧：Logo和系统名称 */}
            <div className="header-brand">
                <span className="brand-icon">💼</span>
                <div className="brand-text">
                    <span className="brand-title">智能财税咨询系统</span>
                    <span className="brand-subtitle">Enterprise Financial & Tax Intelligence Platform</span>
                </div>
            </div>

            {/* 中间：公司选择器 */}
            <div className="header-center">
                <div className="company-selector">
                    <span className="selector-icon">🏢</span>
                    <select
                        value={selectedCompanyId || ''}
                        onChange={(e) => onCompanyChange(Number(e.target.value) || null)}
                    >
                        {companies.map(company => (
                            <option key={company.id} value={company.id}>
                                {company.name}
                            </option>
                        ))}
                    </select>
                    <span className="dropdown-arrow">▼</span>
                </div>
            </div>

            {/* 右侧：时间和用户信息 */}
            <div className="header-right">
                <span className="current-time">🕐 {currentTime}</span>
                <span className="notification">🔔</span>
                <div className="user-info">
                    <span className="user-name">张三</span>
                    <span className="user-role">企业用户</span>
                </div>
                <div className="user-avatar">👤</div>
                <span className="more-icon">➕</span>
            </div>
        </header>
    );
}

export default Header;
