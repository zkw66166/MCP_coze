import { useNavigate } from 'react-router-dom';
import { logout } from '../services/api';
import './Header.css';

/**
 * 顶部导航栏组件（含logo）
 */
function Header({ companies, selectedCompanyId, onCompanyChange }) {
    const navigate = useNavigate();
    const currentTime = new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });

    // 获取当前用户信息
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    const userTypeMap = {
        'enterprise': '企业用户',
        'accounting': '事务所用户',
        'group': '集团用户'
    };

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login');
        } catch (error) {
            console.error('登出失败:', error);
            // 即使API调用失败，也清除本地存储并跳转
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            navigate('/login');
        }
    };

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
                    <span className="user-name">{user?.display_name || user?.username || '用户'}</span>
                    <span className="user-role">{userTypeMap[user?.user_type] || '未知'}</span>
                </div>
                <div className="user-avatar">👤</div>
                <button className="logout-btn" onClick={handleLogout} title="退出登录">
                    🚪
                </button>
            </div>
        </header>
    );
}

export default Header;
