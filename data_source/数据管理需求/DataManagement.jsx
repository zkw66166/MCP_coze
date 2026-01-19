import React, { useState } from 'react';
import { Database, Upload, Download, Settings, Shield, Archive, FileText, Eye, Edit, Trash2, Search, Filter, CheckCircle, AlertTriangle, Clock, Server, Globe, Building, RefreshCw, MoreHorizontal, Activity, BarChart3, Users, ChevronDown, Plus, Calendar } from 'lucide-react';

const DataManagement = () => {
    const [activeTab, setActiveTab] = useState('single');
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [companySearchTerm, setCompanySearchTerm] = useState('');
    const [selectedCompanies, setSelectedCompanies] = useState([]);

    // 模拟多户企业数据
    const [companies] = useState([
        {
            id: 1,
            name: '北京科技有限公司',
            taxCode: '91110000123456789X',
            status: '数据完整',
            lastUpdate: '2024-07-15',
            dataTypes: ['财务报表', '纳税申报', '发票数据'],
            completeness: 95,
            issues: 0
        },
        {
            id: 2,
            name: '上海贸易股份公司',
            taxCode: '91310000987654321A',
            status: '数据不完整',
            lastUpdate: '2024-07-10',
            dataTypes: ['财务报表', '科目余额'],
            completeness: 68,
            issues: 2
        },
        {
            id: 3,
            name: '广州制造企业',
            taxCode: '91440000456789123B',
            status: '待更新',
            lastUpdate: '2024-06-28',
            dataTypes: ['财务报表', '纳税申报', '发票数据', '银行对账'],
            completeness: 85,
            issues: 1
        },
        {
            id: 4,
            name: '深圳创新科技',
            taxCode: '91440300789123456C',
            status: '数据完整',
            lastUpdate: '2024-07-16',
            dataTypes: ['财务报表', '纳税申报', '发票数据', '工商信息'],
            completeness: 100,
            issues: 0
        },
        {
            id: 5,
            name: '成都服务有限公司',
            taxCode: '91510100321654987D',
            status: '数据异常',
            lastUpdate: '2024-07-08',
            dataTypes: ['财务报表'],
            completeness: 45,
            issues: 3
        }
    ]);

    const handleFileUpload = (event) => {
        const files = Array.from(event.target.files);
        const newFiles = files.map(file => ({
            id: Date.now() + Math.random(),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadTime: new Date(),
            status: '处理中',
            progress: 0
        }));

        setUploadedFiles(prev => [...prev, ...newFiles]);

        // 模拟文件处理进度
        newFiles.forEach(file => {
            const interval = setInterval(() => {
                setUploadedFiles(prev => prev.map(f => {
                    if (f.id === file.id && f.progress < 100) {
                        const newProgress = f.progress + 10;
                        return {
                            ...f,
                            progress: newProgress,
                            status: newProgress === 100 ? '已完成' : '处理中'
                        };
                    }
                    return f;
                }));
            }, 200);

            setTimeout(() => clearInterval(interval), 2000);
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case '数据完整': return 'green';
            case '数据不完整': return 'yellow';
            case '待更新': return 'blue';
            case '数据异常': return 'red';
            default: return 'gray';
        }
    };

    const filteredCompanies = companies.filter(company =>
        company.name.toLowerCase().includes(companySearchTerm.toLowerCase()) ||
        company.taxCode.includes(companySearchTerm)
    );

    const handleCompanySelect = (companyId) => {
        setSelectedCompanies(prev =>
            prev.includes(companyId)
                ? prev.filter(id => id !== companyId)
                : [...prev, companyId]
        );
    };

    const SingleCompanyTab = () => (
        <div className="space-y-6">
            {/* 数据概览仪表盘 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Database className="h-6 w-6 mr-2 text-blue-600" />
                    数据管理中心
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <Database className="h-12 w-12 text-blue-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-blue-600">156</p>
                        <p className="text-sm text-gray-600">财务科目数量</p>
                        <p className="text-xs text-blue-600 mt-1">已标准化映射</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                        <FileText className="h-12 w-12 text-green-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-green-600">24</p>
                        <p className="text-sm text-gray-600">报表数量</p>
                        <p className="text-xs text-green-600 mt-1">自动同步更新</p>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <Archive className="h-12 w-12 text-purple-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-purple-600">12</p>
                        <p className="text-sm text-gray-600">数据期间（月）</p>
                        <p className="text-xs text-purple-600 mt-1">连续完整数据</p>
                    </div>
                    <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <CheckCircle className="h-12 w-12 text-yellow-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-yellow-600">98.5%</p>
                        <p className="text-sm text-gray-600">数据完整度</p>
                        <p className="text-xs text-yellow-600 mt-1">质量优良</p>
                    </div>
                </div>
            </div>

            {/* 智能数据导入 - 增加API导入功能 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Upload className="h-5 w-5 mr-2 text-green-600" />
                    智能数据导入
                </h3>

                {/* 手动上传区域 */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors mb-6">
                    <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-xl font-medium text-gray-900 mb-2">拖拽文件到此处或点击上传</h4>
                    <p className="text-gray-600 mb-4">
                        支持Excel、CSV、PDF等格式的财务数据、税务申报数据、发票数据
                    </p>
                    <div className="flex justify-center space-x-4 mb-4">
                        <label className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer flex items-center">
                            <Upload className="h-4 w-4 mr-2" />
                            选择文件
                            <input
                                type="file"
                                multiple
                                onChange={handleFileUpload}
                                className="hidden"
                                accept=".xlsx,.xls,.csv,.pdf"
                            />
                        </label>
                        <button className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center">
                            <Download className="h-4 w-4 mr-2" />
                            下载模板
                        </button>
                    </div>
                    <div className="text-sm text-gray-500">
                        <p>支持的数据类型：</p>
                        <div className="flex justify-center space-x-4 mt-2">
                            <span className="px-2 py-1 bg-gray-100 rounded">资产负债表</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">利润表</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">现金流量表</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">税务申报表</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">发票数据</span>
                        </div>
                    </div>
                </div>

                {/* 一键API自动导入功能 */}
                <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <RefreshCw className="h-5 w-5 mr-2 text-blue-600" />
                        一键API自动导入
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">财务系统对接</h5>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-white rounded border">
                                    <div className="flex items-center">
                                        <Server className="h-5 w-5 text-blue-500 mr-3" />
                                        <div>
                                            <p className="font-medium text-gray-900">慧经盈财务系统</p>
                                            <p className="text-sm text-gray-600">已配置API接口</p>
                                        </div>
                                    </div>
                                    <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center">
                                        <Download className="h-3 w-3 mr-1" />
                                        一键导入
                                    </button>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-white rounded border">
                                    <div className="flex items-center">
                                        <Server className="h-5 w-5 text-green-500 mr-3" />
                                        <div>
                                            <p className="font-medium text-gray-900">xx财务系统</p>
                                            <p className="text-sm text-gray-600">待配置接口</p>
                                        </div>
                                    </div>
                                    <button className="px-3 py-1 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50">
                                        配置接口
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">外部数据源</h5>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-white rounded border">
                                    <div className="flex items-center">
                                        <Globe className="h-5 w-5 text-purple-500 mr-3" />
                                        <div>
                                            <p className="font-medium text-gray-900">电子税务局</p>
                                            <p className="text-sm text-gray-600">纳税申报数据</p>
                                        </div>
                                    </div>
                                    <button className="px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 flex items-center">
                                        <Download className="h-3 w-3 mr-1" />
                                        同步数据
                                    </button>
                                </div>
                                <div className="flex items-center justify-between p-3 bg-white rounded border">
                                    <div className="flex items-center">
                                        <Building className="h-5 w-5 text-orange-500 mr-3" />
                                        <div>
                                            <p className="font-medium text-gray-900">银行API</p>
                                            <p className="text-sm text-gray-600">对账单数据</p>
                                        </div>
                                    </div>
                                    <button className="px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700 flex items-center">
                                        <Download className="h-3 w-3 mr-1" />
                                        获取数据
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 文件管理列表 */}
            {uploadedFiles.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Archive className="h-5 w-5 mr-2 text-purple-600" />
                        文件管理
                    </h3>
                    <div className="space-y-3">
                        {uploadedFiles.map((file, index) => (
                            <div key={file.id || index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                                <div className="flex items-center space-x-4">
                                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <FileText className="h-5 w-5 text-blue-500" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900">{file.name}</p>
                                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                                            <span>{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                                            <span>{file.uploadTime?.toLocaleString() || '刚刚'}</span>
                                            <span className="text-xs">
                                                {file.type?.includes('sheet') ? '电子表格' :
                                                    file.type?.includes('pdf') ? 'PDF文档' : '数据文件'}
                                            </span>
                                        </div>
                                        {file.progress !== undefined && file.progress < 100 && (
                                            <div className="mt-2">
                                                <div className="w-48 bg-gray-200 rounded-full h-1">
                                                    <div
                                                        className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                                                        style={{ width: `${file.progress}%` }}
                                                    ></div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <span className={`px-3 py-1 text-xs rounded-full ${file.status === '已完成' ? 'bg-green-100 text-green-800' :
                                        file.status === '处理中' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                        {file.status || '已上传'}
                                    </span>
                                    <div className="flex space-x-2">
                                        <button className="text-blue-600 hover:text-blue-800" title="预览">
                                            <Eye className="h-4 w-4" />
                                        </button>
                                        <button className="text-green-600 hover:text-green-800" title="下载">
                                            <Download className="h-4 w-4" />
                                        </button>
                                        <button className="text-red-600 hover:text-red-800" title="删除">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* 数据质量检查 - 分为7类 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Shield className="h-5 w-5 mr-2 text-orange-600" />
                        数据质量检查
                    </h3>
                    <button className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center">
                        <Settings className="h-4 w-4 mr-2" />
                        开始检查
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                        { category: '财务报表', check: '报表格式验证', status: '通过', details: '资产负债表、利润表、现金流量表格式正确', icon: CheckCircle, color: 'green' },
                        { category: '科目余额表', check: '科目平衡检查', status: '通过', details: '借贷平衡，科目设置规范', icon: CheckCircle, color: 'green' },
                        { category: '纳税申报表', check: '申报数据一致性', status: '警告', details: '增值税申报表与财务数据存在差异', icon: AlertTriangle, color: 'yellow' },
                        { category: '发票数据', check: '发票真伪验证', status: '通过', details: '发票查验通过，无异常发票', icon: CheckCircle, color: 'green' },
                        { category: '其他征管数据', check: '数据完整性', status: '通过', details: '印花税、房产税等申报数据完整', icon: CheckCircle, color: 'green' },
                        { category: '工商登记信息', check: '登记信息更新', status: '处理中', details: '正在同步最新工商变更信息', icon: Clock, color: 'blue' },
                        { category: '银行对账单', check: '资金流水匹配', status: '警告', details: '部分银行流水与财务记录不匹配', icon: AlertTriangle, color: 'yellow' }
                    ].map((item, index) => {
                        const IconComponent = item.icon;
                        return (
                            <div key={index} className={`flex items-center justify-between p-4 border-l-4 border-${item.color}-500 bg-${item.color}-50 rounded-lg`}>
                                <div className="flex items-center space-x-3">
                                    <IconComponent className={`h-5 w-5 text-${item.color}-500`} />
                                    <div>
                                        <p className="font-medium text-gray-900">{item.category}</p>
                                        <p className="text-sm font-medium text-gray-800">{item.check}</p>
                                        <p className="text-xs text-gray-600">{item.details}</p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${item.status === '通过' ? 'bg-green-100 text-green-800' :
                                    item.status === '警告' ? 'bg-yellow-100 text-yellow-800' :
                                        item.status === '处理中' ? 'bg-blue-100 text-blue-800' :
                                            'bg-red-100 text-red-800'
                                    }`}>
                                    {item.status}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* 智能数据映射 - 添加更多按钮 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Settings className="h-5 w-5 mr-2 text-indigo-600" />
                        智能数据映射（科目余额）
                    </h3>
                    <button className="text-blue-600 hover:text-blue-800 text-sm flex items-center">
                        <MoreHorizontal className="h-4 w-4 mr-1" />
                        更多
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">企业科目</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">标准科目</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">映射状态</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">匹配度</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {[
                                { company: '1001 现金', standard: '1001 库存现金', status: '已映射', match: 100 },
                                { company: '1003 银行存款', standard: '1002 银行存款', status: '已映射', match: 95 },
                                { company: '1121 应收账款', standard: '1122 应收账款', status: '已映射', match: 90 },
                                { company: '2002 短期借款', standard: '2001 短期借款', status: '未映射', match: 0 },
                                { company: '5001 管理费用', standard: '5101 管理费用', status: '部分映射', match: 85 }
                            ].map((item, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                    <td className="px-4 py-4 text-sm text-gray-900">{item.company}</td>
                                    <td className="px-4 py-4 text-sm text-gray-600">{item.standard}</td>
                                    <td className="px-4 py-4">
                                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${item.status === '已映射' ? 'bg-green-100 text-green-800' :
                                            item.status === '部分映射' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                            }`}>
                                            {item.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-4 text-sm text-gray-900">
                                        <div className="flex items-center">
                                            <span className="mr-2">{item.match}%</span>
                                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                                <div
                                                    className={`h-2 rounded-full ${item.match >= 90 ? 'bg-green-500' :
                                                        item.match >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                                                        }`}
                                                    style={{ width: `${item.match}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-4 text-sm">
                                        <button className="text-blue-600 hover:text-blue-800 flex items-center">
                                            <Edit className="h-4 w-4 mr-1" />
                                            {item.status === '已映射' ? '修改' : '设置'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* 数据更新频率 - 列出全部7类数据 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
                        数据更新频率
                    </h3>
                    <div className="space-y-4">
                        {[
                            { source: '财务报表', frequency: '实时同步', last: '5分钟前', status: '正常' },
                            { source: '科目余额表', frequency: '每日同步', last: '2小时前', status: '正常' },
                            { source: '纳税申报表', frequency: '每月同步', last: '1天前', status: '正常' },
                            { source: '发票数据', frequency: '每日同步', last: '1天前', status: '延迟' },
                            { source: '其他征管数据', frequency: '每周同步', last: '2天前', status: '正常' },
                            { source: '工商登记信息', frequency: '手动同步', last: '7天前', status: '待更新' },
                            { source: '银行对账单', frequency: '手动导入', last: '3天前', status: '待更新' }
                        ].map((item, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="font-medium text-gray-900">{item.source}</p>
                                    <p className="text-sm text-gray-600">{item.frequency} • 最后更新: {item.last}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs rounded-full ${item.status === '正常' ? 'bg-green-100 text-green-800' :
                                    item.status === '延迟' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800'
                                    }`}>
                                    {item.status}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Activity className="h-5 w-5 mr-2 text-purple-600" />
                        数据使用统计
                    </h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                            <span className="text-gray-700">今日查询次数</span>
                            <span className="font-bold text-blue-600">1,247</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                            <span className="text-gray-700">数据导出次数</span>
                            <span className="font-bold text-green-600">89</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                            <span className="text-gray-700">API调用次数</span>
                            <span className="font-bold text-purple-600">3,456</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                            <span className="text-gray-700">存储使用量</span>
                            <span className="font-bold text-yellow-600">2.3GB / 10GB</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const MultiCompanyTab = () => (
        <div className="space-y-6">
            {/* 多户企业数据概览 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Users className="h-6 w-6 mr-2 text-purple-600" />
                    多户企业数据概览
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <Users className="h-12 w-12 text-purple-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-purple-600">{companies.length}</p>
                        <p className="text-sm text-gray-600">管理企业总数</p>
                        <p className="text-xs text-purple-600 mt-1">数据已导入</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                        <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-green-600">{companies.filter(c => c.status === '数据完整').length}</p>
                        <p className="text-sm text-gray-600">数据完整企业</p>
                        <p className="text-xs text-green-600 mt-1">可正常分析</p>
                    </div>
                    <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-yellow-600">{companies.filter(c => c.status !== '数据完整').length}</p>
                        <p className="text-sm text-gray-600">待处理企业</p>
                        <p className="text-xs text-yellow-600 mt-1">需要关注</p>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <BarChart3 className="h-12 w-12 text-blue-500 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-blue-600">
                            {Math.round(companies.reduce((acc, c) => acc + c.completeness, 0) / companies.length)}%
                        </p>
                        <p className="text-sm text-gray-600">平均完整度</p>
                        <p className="text-xs text-blue-600 mt-1">整体数据质量</p>
                    </div>
                </div>
            </div>

            {/* 批量操作工具栏 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                    <div className="flex items-center space-x-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                            <input
                                type="text"
                                placeholder="搜索企业名称或税号..."
                                value={companySearchTerm}
                                onChange={(e) => setCompanySearchTerm(e.target.value)}
                                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
                            />
                        </div>
                        <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                            <Filter className="h-4 w-4 mr-2" />
                            筛选
                            <ChevronDown className="h-4 w-4 ml-1" />
                        </button>
                    </div>
                    <div className="flex items-center space-x-3">
                        <button className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                            <Plus className="h-4 w-4 mr-2" />
                            添加企业
                        </button>
                        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                            <Upload className="h-4 w-4 mr-2" />
                            批量导入
                        </button>
                        {selectedCompanies.length > 0 && (
                            <button className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                                <RefreshCw className="h-4 w-4 mr-2" />
                                批量更新 ({selectedCompanies.length})
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* 企业数据列表 */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Database className="h-5 w-5 mr-2 text-indigo-600" />
                        企业数据状况列表
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left">
                                    <input
                                        type="checkbox"
                                        onChange={(e) => {
                                            if (e.target.checked) {
                                                setSelectedCompanies(filteredCompanies.map(c => c.id));
                                            } else {
                                                setSelectedCompanies([]);
                                            }
                                        }}
                                        className="rounded border-gray-300"
                                    />
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">企业信息</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数据状态</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">数据类型</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">完整度</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后更新</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredCompanies.map((company) => (
                                <tr key={company.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4">
                                        <input
                                            type="checkbox"
                                            checked={selectedCompanies.includes(company.id)}
                                            onChange={() => handleCompanySelect(company.id)}
                                            className="rounded border-gray-300"
                                        />
                                    </td>
                                    <td className="px-6 py-4">
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">{company.name}</div>
                                            <div className="text-sm text-gray-500">{company.taxCode}</div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full 
                                            ${getStatusColor(company.status) === 'green' ? 'bg-green-100 text-green-800' :
                                                getStatusColor(company.status) === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                                                    getStatusColor(company.status) === 'blue' ? 'bg-blue-100 text-blue-800' :
                                                        getStatusColor(company.status) === 'red' ? 'bg-red-100 text-red-800' :
                                                            'bg-gray-100 text-gray-800'}`}>
                                            {company.status}
                                        </span>
                                        {company.issues > 0 && (
                                            <div className="mt-1 text-xs text-red-600">{company.issues} 个问题</div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1">
                                            {company.dataTypes.map((type, index) => (
                                                <span key={index} className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                                                    {type}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <span className="text-sm font-medium text-gray-900 mr-2">{company.completeness}%</span>
                                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                                <div
                                                    className={`h-2 rounded-full ${company.completeness >= 90 ? 'bg-green-500' :
                                                        company.completeness >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                                                        }`}
                                                    style={{ width: `${company.completeness}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <div className="flex items-center">
                                            <Calendar className="h-4 w-4 mr-1" />
                                            {company.lastUpdate}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm">
                                        <div className="flex space-x-2">
                                            <button className="text-blue-600 hover:text-blue-800" title="查看详情">
                                                <Eye className="h-4 w-4" />
                                            </button>
                                            <button className="text-green-600 hover:text-green-800" title="更新数据">
                                                <RefreshCw className="h-4 w-4" />
                                            </button>
                                            <button className="text-purple-600 hover:text-purple-800" title="数据管理">
                                                <Settings className="h-4 w-4" />
                                            </button>
                                            <button className="text-gray-600 hover:text-gray-800" title="更多操作">
                                                <MoreHorizontal className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* 批量操作面板 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Upload className="h-5 w-5 mr-2 text-green-600" />
                        批量数据导入
                    </h3>
                    <div className="space-y-4">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                            <p className="text-gray-600 mb-3">拖拽多家企业数据文件到此处</p>
                            <label className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 cursor-pointer">
                                选择文件
                                <input type="file" multiple className="hidden" accept=".xlsx,.xls,.csv,.pdf" />
                            </label>
                        </div>
                        <div className="text-sm text-gray-600">
                            <p className="mb-2">支持批量导入：</p>
                            <div className="grid grid-cols-2 gap-2">
                                <span className="px-2 py-1 bg-gray-100 rounded text-xs">多企业财务报表</span>
                                <span className="px-2 py-1 bg-gray-100 rounded text-xs">批量纳税申报</span>
                                <span className="px-2 py-1 bg-gray-100 rounded text-xs">发票数据包</span>
                                <span className="px-2 py-1 bg-gray-100 rounded text-xs">科目映射表</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Activity className="h-5 w-5 mr-2 text-purple-600" />
                        批量操作记录
                    </h3>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                            <div>
                                <p className="text-sm font-medium text-gray-900">批量导入财务报表</p>
                                <p className="text-xs text-gray-600">2024-07-18 14:30 • 5家企业</p>
                            </div>
                            <span className="text-xs text-green-600 font-medium">成功</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                            <div>
                                <p className="text-sm font-medium text-gray-900">批量更新纳税数据</p>
                                <p className="text-xs text-gray-600">2024-07-18 10:15 • 3家企业</p>
                            </div>
                            <span className="text-xs text-yellow-600 font-medium">部分成功</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                            <div>
                                <p className="text-sm font-medium text-gray-900">批量科目映射</p>
                                <p className="text-xs text-gray-600">2024-07-17 16:45 • 8家企业</p>
                            </div>
                            <span className="text-xs text-blue-600 font-medium">处理中</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="space-y-6">
            {/* 标签页导航 */}
            <div className="bg-white rounded-lg shadow-sm border">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        <button
                            onClick={() => setActiveTab('single')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === 'single'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <Database className="h-4 w-4 inline mr-2" />
                            单户企业数据
                        </button>
                        <button
                            onClick={() => setActiveTab('multi')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === 'multi'
                                    ? 'border-purple-500 text-purple-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            <Users className="h-4 w-4 inline mr-2" />
                            多户企业数据
                        </button>
                    </nav>
                </div>
            </div>

            {/* 标签页内容 */}
            {activeTab === 'single' ? <SingleCompanyTab /> : <MultiCompanyTab />}
        </div>
    );
};

export default DataManagement;