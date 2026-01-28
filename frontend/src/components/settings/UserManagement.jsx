import { useState, useEffect } from 'react';
import { fetchUsers, createUser, updateUser, deleteUser } from '../../services/api';
import { Plus, Edit2, Trash2, X, AlertTriangle, Users, Building2, Briefcase, UserPlus, Search, Filter, Lock, Shield } from 'lucide-react';

function UserManagement() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [userToDelete, setUserToDelete] = useState(null);

    // Form state
    const [formData, setFormData] = useState({
        username: '',
        display_name: '',
        user_type: 'enterprise',
        password: '',
        is_active: 1
    });

    const userTypeMap = {
        'enterprise': '企业用户',
        'accounting': '事务所',
        'group': '集团用户'
    };

    // Stats calculation
    const totalUsers = users.length;
    const activeUsers = users.filter(u => u.is_active).length;
    const enterpriseUsers = users.filter(u => u.user_type === 'enterprise').length;
    const pendingReviews = 0; // Conceptual

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            setLoading(true);
            const data = await fetchUsers();
            setUsers(data);
            setError(null);
        } catch (err) {
            setError('加载用户列表失败');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenAddModal = () => {
        setCurrentUser(null);
        setFormData({
            username: '',
            display_name: '',
            user_type: 'enterprise',
            password: '',
            is_active: 1
        });
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (user) => {
        setCurrentUser(user);
        setFormData({
            username: user.username,
            display_name: user.display_name || '',
            user_type: user.user_type,
            password: '',
            is_active: user.is_active
        });
        setIsModalOpen(true);
    };

    const handleDeleteClick = (user) => {
        setUserToDelete(user);
        setIsDeleteModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (currentUser) {
                await updateUser(currentUser.id, formData);
            } else {
                await createUser(formData);
            }
            setIsModalOpen(false);
            loadUsers();
        } catch (err) {
            console.error('Failed to save user:', err);
            alert(err.message);
        }
    };

    const handleDeleteConfirm = async () => {
        if (!userToDelete) return;
        try {
            await deleteUser(userToDelete.id);
            setIsDeleteModalOpen(false);
            setUserToDelete(null);
            loadUsers();
        } catch (err) {
            console.error('Failed to delete user:', err);
            alert(err.message);
        }
    };

    const getUserInitial = (name) => {
        return name ? name.charAt(0).toUpperCase() : '?';
    };

    // Mock permissions for display
    const getMockPermissions = (type) => {
        if (type === 'enterprise') return ['财务管理', '报表查看'];
        if (type === 'accounting') return ['多企业管理', '税务申报', '审计'];
        return ['集团总览', '子公司监控'];
    };

    return (
        <div className="user-management-wrapper">
            {/* Statistics Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon-wrapper bg-blue-light text-blue">
                        <Users size={24} />
                    </div>
                    <div className="stat-value">{activeUsers}</div>
                    <div className="stat-label">活跃用户</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon-wrapper bg-green-light text-green">
                        <Building2 size={24} />
                    </div>
                    <div className="stat-value">{enterpriseUsers}</div>
                    <div className="stat-label">企业用户</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon-wrapper bg-purple-light text-purple">
                        <Briefcase size={24} />
                    </div>
                    <div className="stat-value">{totalUsers - enterpriseUsers}</div>
                    <div className="stat-label">专业用户</div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon-wrapper bg-orange-light text-orange">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="stat-value text-orange">2</div>
                    <div className="stat-label">待审核申请</div>
                </div>
            </div>

            {/* Bulk Operations */}
            <div className="bulk-ops-bar">
                <div className="bulk-info">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Shield size={16} />
                        <span>已选择 0 个用户进行批量操作</span>
                    </div>
                </div>
                <div className="bulk-actions">
                    <button className="bulk-btn">
                        <Edit2 size={14} /> 批量更改类型
                    </button>
                    <button className="bulk-btn">
                        <Filter size={14} /> 批量更改状态
                    </button>
                    <button className="bulk-btn bg-green-light text-green" style={{ borderColor: '#10b981' }}>
                        <Shield size={14} /> 批量权限设置
                    </button>
                    <button className="bulk-btn primary">
                        <Lock size={14} /> 批量重置密码
                    </button>
                </div>
            </div>

            {/* Main User List Card */}
            <div className="settings-card">
                <div className="card-title">
                    <Users size={20} />
                    <span>用户列表管理</span>
                </div>

                <div className="table-controls">
                    <div className="search-filter">
                        <div className="search-input-wrapper">
                            <Search size={16} className="search-icon-inside" />
                            <input type="text" placeholder="搜索用户名、姓名..." />
                        </div>
                        <select className="filter-select">
                            <option>全部类型</option>
                            <option>企业用户</option>
                            <option>事务所</option>
                            <option>集团用户</option>
                        </select>
                        <select className="filter-select">
                            <option>全部状态</option>
                            <option>活跃</option>
                            <option>禁用</option>
                        </select>
                    </div>
                    <button className="btn-primary" onClick={handleOpenAddModal}>
                        <UserPlus size={18} /> 添加用户
                    </button>
                    <button className="btn-secondary" style={{ marginLeft: '12px' }}>
                        <Filter size={18} /> 导出用户
                    </button>
                </div>

                {loading ? (
                    <div>加载中...</div>
                ) : (
                    <table className="data-table-modern">
                        <thead>
                            <tr>
                                <th style={{ width: '40px' }}><input type="checkbox" /></th>
                                <th>用户详情</th>
                                <th>用户类型</th>
                                <th>公司/组织</th>
                                <th>状态</th>
                                <th>权限</th>
                                <th>注册时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td><input type="checkbox" /></td>
                                    <td>
                                        <div className="user-cell">
                                            <div className="table-avatar bg-blue-light text-blue">
                                                {getUserInitial(user.display_name || user.username)}
                                            </div>
                                            <div className="user-details">
                                                <div className="user-realname">{user.display_name || user.username}</div>
                                                <div className="user-subtext">@{user.username}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`role-badge role-${user.user_type}`}>
                                            {userTypeMap[user.user_type] || user.user_type}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ fontSize: '13px', color: '#374151' }}>
                                            {user.user_type === 'enterprise' ? '演示企业有限公司' : '演示会计师事务所'}
                                        </div>
                                        <div style={{ fontSize: '12px', color: '#9ca3af' }}>
                                            {user.user_type === 'enterprise' ? '财务经理' : '项目总监'}
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
                                            {user.is_active ? '活跃' : '禁用'}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                                            {getMockPermissions(user.user_type).map((perm, idx) => (
                                                <span key={idx} style={{
                                                    fontSize: '11px',
                                                    padding: '2px 6px',
                                                    background: '#f3f4f6',
                                                    borderRadius: '4px',
                                                    color: '#4b5563'
                                                }}>
                                                    {perm}
                                                </span>
                                            ))}
                                            <span style={{ fontSize: '11px', color: '#9ca3af', paddingTop: '2px' }}>+1</span>
                                        </div>
                                    </td>
                                    <td style={{ fontSize: '13px', color: '#6b7280' }}>
                                        <div>{new Date(user.created_at).toLocaleDateString()}</div>
                                        <div style={{ fontSize: '11px', color: '#9ca3af' }}>14:30:00</div>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex' }}>
                                            <button className="action-btn btn-edit" onClick={() => handleOpenEditModal(user)}>
                                                <Edit2 size={16} />
                                            </button>
                                            <button className="action-btn btn-delete" onClick={() => handleDeleteClick(user)}>
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* User Application Management */}
            <div className="settings-card">
                <div className="card-title">
                    <Briefcase size={20} />
                    <span>用户类型变更申请管理</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{
                        padding: '16px',
                        border: '1px solid #f3f4f6',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <div>
                            <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontWeight: 600 }}>陈六</span>
                                <span className="role-badge role-enterprise">企业用户</span>
                                <span style={{ color: '#9ca3af' }}>→</span>
                                <span className="role-badge role-accounting">事务所用户</span>
                                <span style={{
                                    fontSize: '12px',
                                    padding: '2px 8px',
                                    background: '#fff7ed',
                                    color: '#ea580c',
                                    borderRadius: '12px'
                                }}>待审核</span>
                            </div>
                            <div style={{ fontSize: '13px', color: '#6b7280' }}>
                                申请理由：公司业务扩展，需要管理多个客户企业
                                <br />
                                <span style={{ fontSize: '12px', color: '#9ca3af' }}>申请时间: 2024-07-18 14:30:00</span>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <button className="btn-primary" style={{ backgroundColor: '#10b981', fontSize: '12px', padding: '6px 12px' }}>批准</button>
                            <button className="btn-primary" style={{ backgroundColor: '#dc2626', fontSize: '12px', padding: '6px 12px' }}>拒绝</button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modals remain mostly same but slightly styled */}
            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3 className="modal-title">{currentUser ? '编辑用户' : '新增用户'}</h3>
                            <button className="modal-close" onClick={() => setIsModalOpen(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                {!currentUser && (
                                    <div className="form-group">
                                        <label>用户名 <span style={{ color: 'red' }}>*</span></label>
                                        <input
                                            type="text"
                                            value={formData.username}
                                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                            required
                                        />
                                    </div>
                                )}
                                <div className="form-group">
                                    <label>显示名称</label>
                                    <input
                                        type="text"
                                        value={formData.display_name}
                                        onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>用户类型 <span style={{ color: 'red' }}>*</span></label>
                                    <select
                                        value={formData.user_type}
                                        onChange={(e) => setFormData({ ...formData, user_type: e.target.value })}
                                    >
                                        <option value="enterprise">企业用户</option>
                                        <option value="accounting">事务所</option>
                                        <option value="group">集团用户</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>{currentUser ? '重置密码 (留空则不修改)' : '密码'} {currentUser ? '' : <span style={{ color: 'red' }}>*</span>}</label>
                                    <input
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        required={!currentUser}
                                        placeholder={currentUser ? '******' : ''}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>状态</label>
                                    <select
                                        value={formData.is_active}
                                        onChange={(e) => setFormData({ ...formData, is_active: Number(e.target.value) })}
                                    >
                                        <option value={1}>启用</option>
                                        <option value={0}>禁用</option>
                                    </select>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(false)}>取消</button>
                                <button type="submit" className="btn-primary">保存</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            {/* Delete Confirmation Modal */}
            {isDeleteModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content" style={{ maxWidth: '400px' }}>
                        <div className="modal-header">
                            <h3 className="modal-title">确认删除</h3>
                            <button className="modal-close" onClick={() => setIsDeleteModalOpen(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body" style={{ textAlign: 'center', padding: '32px 24px' }}>
                            <AlertTriangle size={48} color="#dc2626" style={{ marginBottom: '16px' }} />
                            <p>确定要删除用户 <strong>{userToDelete?.username}</strong> 吗？</p>
                            <p style={{ fontSize: '13px', color: '#6b7280', marginTop: '8px' }}>此操作无法撤销。</p>
                        </div>
                        <div className="modal-footer" style={{ justifyContent: 'center' }}>
                            <button className="btn-secondary" onClick={() => setIsDeleteModalOpen(false)}>取消</button>
                            <button className="btn-primary" style={{ backgroundColor: '#dc2626' }} onClick={handleDeleteConfirm}>确认删除</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default UserManagement;
