import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, User, Lock, Calculator } from 'lucide-react';
import { login } from '../services/api';
import './Login.css';

function Login() {
    const credentialsMap = {
        'enterprise': { username: 'enterprise', password: '123456' },
        'accounting': { username: 'accounting', password: '123456' },
        'group': { username: 'group', password: '123456' }
    };

    // 初始化时如果默认是 enterprise，则填充 enterprise 的账号
    const [userType, setUserType] = useState('enterprise');
    const [username, setUsername] = useState(credentialsMap['enterprise'].username);
    const [password, setPassword] = useState(credentialsMap['enterprise'].password);
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleUserTypeChange = (type) => {
        setUserType(type);
        if (credentialsMap[type]) {
            setUsername(credentialsMap[type].username);
            setPassword(credentialsMap[type].password);
        } else {
            setUsername('');
            setPassword('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Use the centralized api service
            const data = await login(username, password);

            // 保存 token 和用户信息到 localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // 跳转到主应用
            navigate('/app');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                {/* Logo */}
                <div className="login-logo">
                    <div className="logo-icon">
                        <Calculator size={40} strokeWidth={2} />
                    </div>
                </div>

                {/* Title */}
                <h1 className="login-title">智能财税咨询系统</h1>
                <p className="login-subtitle">请登录您的账户</p>

                {/* User Type Selection */}
                <div className="user-type-section">
                    <label className="user-type-label">用户类型</label>
                    <div className="user-type-buttons">
                        <button
                            type="button"
                            className={`user-type-btn ${userType === 'enterprise' ? 'active' : ''}`}
                            onClick={() => handleUserTypeChange('enterprise')}
                        >
                            企业用户
                        </button>
                        <button
                            type="button"
                            className={`user-type-btn ${userType === 'accounting' ? 'active' : ''}`}
                            onClick={() => handleUserTypeChange('accounting')}
                        >
                            事务所
                        </button>
                        <button
                            type="button"
                            className={`user-type-btn ${userType === 'group' ? 'active' : ''}`}
                            onClick={() => handleUserTypeChange('group')}
                        >
                            集团用户
                        </button>
                    </div>
                </div>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="login-form">
                    {/* Username */}
                    <div className="form-group">
                        <label className="form-label">用户名</label>
                        <div className="input-wrapper">
                            <User className="input-icon" size={20} />
                            <input
                                type="text"
                                className="form-input"
                                placeholder="enterprise"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div className="form-group">
                        <label className="form-label">密码</label>
                        <div className="input-wrapper">
                            <Lock className="input-icon" size={20} />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                className="form-input"
                                placeholder="••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    {/* Error Message */}
                    {error && <div className="error-message">{error}</div>}

                    {/* Login Button */}
                    <button type="submit" className="login-button" disabled={loading}>
                        {loading ? '登录中...' : '登录'}
                    </button>
                </form>

                {/* Test Accounts Info */}
                <div className="test-accounts">
                    <p className="test-accounts-title">测试账号：</p>
                    <p className="test-account-item">企业用户: enterprise / 123456</p>
                    <p className="test-account-item">事务所用户: accounting / 123456</p>
                    <p className="test-account-item">集团用户: group / 123456</p>
                </div>
            </div>
        </div>
    );
}

export default Login;
