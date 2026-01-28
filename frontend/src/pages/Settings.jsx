import { useState } from 'react';
import UserManagement from '../components/settings/UserManagement';
import BasicSettings from '../components/settings/BasicSettings';
import ServiceSettings from '../components/settings/ServiceSettings';
import './Settings.css';

function Settings() {
    console.log('Settings component loaded');
    const [activeTab, setActiveTab] = useState('user-management');

    const renderContent = () => {
        switch (activeTab) {
            case 'user-management':
                return <UserManagement />;
            case 'basic':
                return <BasicSettings />;
            case 'service':
                return <ServiceSettings />;
            default:
                return <UserManagement />;
        }
    };

    return (
        <div className="settings-container">
            {/* Top Navigation Tabs */}
            <div className="settings-header">
                <div className="settings-tabs">
                    <div
                        className={`tab-item ${activeTab === 'user-management' ? 'active' : ''}`}
                        onClick={() => setActiveTab('user-management')}
                    >
                        用户管理
                    </div>
                    <div
                        className={`tab-item ${activeTab === 'basic' ? 'active' : ''}`}
                        onClick={() => setActiveTab('basic')}
                    >
                        基础设置
                    </div>
                    <div
                        className={`tab-item ${activeTab === 'service' ? 'active' : ''}`}
                        onClick={() => setActiveTab('service')}
                    >
                        服务设置
                    </div>
                </div>
            </div>

            {/* Content Area */}
            <div className="settings-content-area">
                {renderContent()}
            </div>
        </div>
    );
}

export default Settings;
