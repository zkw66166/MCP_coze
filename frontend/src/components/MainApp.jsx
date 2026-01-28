import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import AIChat from './AIChat';
import CompanyProfile from './CompanyProfile';
import DataManagement from './DataManagement';
import { fetchCompanies, fetchStatistics } from '../services/api';
import '../App.css';

function MainApp() {
    const [companies, setCompanies] = useState([]);
    const [selectedCompanyId, setSelectedCompanyId] = useState(null);
    const [activeMenu, setActiveMenu] = useState('ai-chat');
    const [stats, setStats] = useState(null);

    useEffect(() => {
        const loadCompanies = async () => {
            try {
                const data = await fetchCompanies();
                setCompanies(data);
                if (data.length > 0) setSelectedCompanyId(data[0].id);
            } catch (error) {
                console.error('加载企业列表失败:', error);
            }
        };
        loadCompanies();
    }, []);

    useEffect(() => {
        const loadStats = async () => {
            try {
                const data = await fetchStatistics();
                setStats(data);
            } catch (error) {
                console.error('加载统计信息失败:', error);
            }
        };
        loadStats();
    }, []);

    const renderContent = () => {
        switch (activeMenu) {
            case 'ai-chat':
                return <AIChat selectedCompanyId={selectedCompanyId} companies={companies} />;
            case 'workbench':
                return <div className="placeholder-page">📋 工作台 - 功能开发中...</div>;
            case 'company-profile':
                return <CompanyProfile selectedCompanyId={selectedCompanyId} companies={companies} />;
            case 'data-management':
                return <DataManagement selectedCompanyId={selectedCompanyId} />;
            case 'settings':
                return <div className="placeholder-page">⚙️ 系统设置 - 功能开发中...</div>;
            default:
                return <AIChat selectedCompanyId={selectedCompanyId} companies={companies} />;
        }
    };

    return (
        <div className="app-container">
            {/* 顶部导航栏 */}
            <Header
                companies={companies}
                selectedCompanyId={selectedCompanyId}
                onCompanyChange={setSelectedCompanyId}
            />

            {/* 主体区域 */}
            <div className="app-body">
                {/* 左侧导航 */}
                <Sidebar activeMenu={activeMenu} onMenuChange={setActiveMenu} />

                {/* 内容区域 */}
                <div className="content-area">
                    <main className="main-content">
                        {renderContent()}
                    </main>

                    {/* 底部版权 */}
                    <footer className="app-footer">
                        <span>© 2024 智能财税咨询系统. All rights reserved.</span>
                        <span className="footer-links">
                            版本 v1.0.0 | 帮助中心 | 技术支持
                        </span>
                    </footer>
                </div>
            </div>
        </div>
    );
}

export default MainApp;
