import React from 'react';
import { Building, BarChart3, Award, Users, GitBranch, Shield, TrendingUp, FileText, Globe, Calculator, Receipt, Truck, Target, PieChart, Briefcase, Factory, Database, AlertTriangle, CheckCircle } from 'lucide-react';

const Profile = () => {
    // 评价标签组件
    const EvalLabel = ({ text, type = 'positive' }) => {
        const colorMap = {
            positive: 'bg-green-100 text-green-600',
            growth: 'bg-green-100 text-green-600',
            neutral: 'bg-blue-100 text-blue-600',
            warning: 'bg-yellow-100 text-yellow-600',
            negative: 'bg-red-100 text-red-600',
            purple: 'bg-purple-100 text-purple-600',
            orange: 'bg-orange-100 text-orange-600'
        };
        return <span className={`ml-1 px-1.5 py-0.5 rounded text-xs font-medium ${colorMap[type]}`}>{text}</span>;
    };

    // 二级模块标题组件
    const SectionTitle = ({ name, color }) => {
        const colorMap = { green: 'bg-green-500', purple: 'bg-purple-500', orange: 'bg-orange-500', blue: 'bg-blue-500', cyan: 'bg-cyan-500' };
        return (
            <div className="flex items-center mb-2 pb-1 border-b">
                <span className={`w-2 h-2 rounded-full ${colorMap[color]} mr-1.5`}></span>
                <span className="text-sm font-medium text-gray-700">{name}</span>
            </div>
        );
    };

    // 紧凑单行指标组件
    const CompactMetric = ({ label, value, eval: evalInfo, bgColor = 'bg-gray-50' }) => (
        <div className={`flex items-center justify-between px-2 py-1.5 ${bgColor} rounded text-sm`}>
            <span className="text-gray-600">{label}</span>
            <span className="font-medium text-gray-900">{value}{evalInfo && <EvalLabel text={evalInfo.text} type={evalInfo.type} />}</span>
        </div>
    );

    // 简单饼图组件
    const SimplePieChart = ({ data, size = 200 }) => {
        const total = data.reduce((sum, item) => sum + item.value, 0);
        let currentAngle = 0;

        const slices = data.map((item, index) => {
            const percentage = (item.value / total) * 100;
            const angle = (item.value / total) * 360;
            const startAngle = currentAngle;
            currentAngle += angle;

            const largeArcFlag = angle > 180 ? 1 : 0;
            const x1 = size/2 + (size/2 - 10) * Math.cos((startAngle - 90) * Math.PI / 180);
            const y1 = size/2 + (size/2 - 10) * Math.sin((startAngle - 90) * Math.PI / 180);
            const x2 = size/2 + (size/2 - 10) * Math.cos((startAngle + angle - 90) * Math.PI / 180);
            const y2 = size/2 + (size/2 - 10) * Math.sin((startAngle + angle - 90) * Math.PI / 180);

            const pathData = [
                `M ${size/2} ${size/2}`,
                `L ${x1} ${y1}`,
                `A ${size/2 - 10} ${size/2 - 10} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
            ].join(' ');

            return (
                <g key={index}>
                    <path d={pathData} fill={item.color} stroke="white" strokeWidth="2" />
                </g>
            );
        });

        return (
            <div className="flex flex-col items-center">
                <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                    {slices}
                </svg>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                    {data.map((item, index) => (
                        <div key={index} className="flex items-center">
                            <div className="w-3 h-3 rounded mr-1" style={{ backgroundColor: item.color }}></div>
                            <span className="text-gray-600">{item.name}: {item.value}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    // 简单柱状图组件
    const SimpleBarChart = ({ data, height = 200, colors = ['#3b82f6', '#10b981'] }) => {
        const maxValue = Math.max(...data.map(d => d.value));
        const barWidth = 80;
        const gap = 40;
        const width = data.length * (barWidth + gap) + gap;

        return (
            <div className="overflow-x-auto">
                <svg width={width} height={height} className="mx-auto">
                    {data.map((item, index) => {
                        const barHeight = (item.value / maxValue) * (height - 40);
                        const x = gap + index * (barWidth + gap);
                        const y = height - barHeight - 20;

                        return (
                            <g key={index}>
                                <rect
                                    x={x}
                                    y={y}
                                    width={barWidth}
                                    height={barHeight}
                                    fill={item.color || colors[index % colors.length]}
                                    rx="4"
                                />
                                <text
                                    x={x + barWidth / 2}
                                    y={height - 5}
                                    textAnchor="middle"
                                    className="text-xs fill-gray-600"
                                >
                                    {item.name}
                                </text>
                                <text
                                    x={x + barWidth / 2}
                                    y={y - 5}
                                    textAnchor="middle"
                                    className="text-xs font-medium fill-gray-900"
                                >
                                    {item.value}
                                </text>
                            </g>
                        );
                    })}
                </svg>
            </div>
        );
    };

    // 简单折线图组件
    const SimpleLineChart = ({ data, height = 200, width = 350, lines }) => {
        const maxValue = Math.max(...data.flatMap(d => lines.map(line => d[line.key])));
        const padding = { top: 20, right: 20, bottom: 30, left: 40 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        const pointGap = chartWidth / (data.length - 1);

        return (
            <svg width={width} height={height}>
                {/* 网格线 */}
                {[0, 1, 2, 3, 4].map(i => {
                    const y = padding.top + (chartHeight / 4) * i;
                    return (
                        <line
                            key={i}
                            x1={padding.left}
                            y1={y}
                            x2={width - padding.right}
                            y2={y}
                            stroke="#e5e7eb"
                            strokeDasharray="3,3"
                        />
                    );
                })}

                {/* 折线 */}
                {lines.map((line, lineIndex) => {
                    const points = data.map((d, i) => {
                        const x = padding.left + pointGap * i;
                        const y = padding.top + chartHeight - (d[line.key] / maxValue) * chartHeight;
                        return `${x},${y}`;
                    }).join(' ');

                    return (
                        <g key={lineIndex}>
                            <polyline
                                points={points}
                                fill="none"
                                stroke={line.color}
                                strokeWidth="2"
                            />
                            {data.map((d, i) => {
                                const x = padding.left + pointGap * i;
                                const y = padding.top + chartHeight - (d[line.key] / maxValue) * chartHeight;
                                return (
                                    <circle
                                        key={i}
                                        cx={x}
                                        cy={y}
                                        r="4"
                                        fill={line.color}
                                    />
                                );
                            })}
                        </g>
                    );
                })}

                {/* X轴标签 */}
                {data.map((d, i) => {
                    const x = padding.left + pointGap * i;
                    return (
                        <text
                            key={i}
                            x={x}
                            y={height - 10}
                            textAnchor="middle"
                            className="text-xs fill-gray-600"
                        >
                            {d.year}
                        </text>
                    );
                })}

                {/* 图例 */}
                <g transform={`translate(${width - 100}, 10)`}>
                    {lines.map((line, i) => (
                        <g key={i} transform={`translate(0, ${i * 20})`}>
                            <line x1="0" y1="0" x2="20" y2="0" stroke={line.color} strokeWidth="2" />
                            <text x="25" y="4" className="text-xs fill-gray-600">{line.name}</text>
                        </g>
                    ))}
                </g>
            </svg>
        );
    };

    // 进度条组件
    const ProgressBar = ({ label, value, max = 100, color = 'bg-blue-500' }) => (
        <div className="mb-3">
            <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">{label}</span>
                <span className="font-medium text-gray-900">{value}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                    className={`${color} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${(value / max) * 100}%` }}
                ></div>
            </div>
        </div>
    );

    // 数据准备
    const staffStructureData = [
        { name: '研发人员', value: 78, color: '#3b82f6' },
        { name: '销售人员', value: 28, color: '#8b5cf6' },
        { name: '管理人员', value: 25, color: '#10b981' },
        { name: '其他', value: 25, color: '#f59e0b' }
    ];

    const assetData = [
        { name: '流动资产', value: 3850, color: '#3b82f6' },
        { name: '固定资产', value: 980, color: '#8b5cf6' },
        { name: '无形资产', value: 320, color: '#10b981' },
        { name: '其他', value: 130, color: '#f59e0b' }
    ];

    const liabilityEquityData = [
        { name: '负债', value: 3618, color: '#ef4444' },
        { name: '所有者权益', value: 1662, color: '#10b981' }
    ];

    const patentTrendData = [
        { year: '2020', total: 12, invention: 3 },
        { year: '2021', total: 19, invention: 6 },
        { year: '2022', total: 27, invention: 9 },
        { year: '2023', total: 35, invention: 12 }
    ];

    const taxStructureData = [
        { name: '增值税', value: 138, color: '#3b82f6' },
        { name: '企业所得税', value: 54.75, color: '#8b5cf6' },
        { name: '个税代扣', value: 142, color: '#10b981' },
        { name: '其他税费', value: 15.7, color: '#f59e0b' }
    ];

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-4 bg-gray-50">
            {/* 页面标题 */}
            <div className="text-center mb-4 bg-white rounded-lg shadow-sm border p-6">
                <h1 className="text-3xl font-bold text-gray-900">企业画像可视化分析</h1>
                <p className="text-gray-600 mt-2 text-lg">大华科技有限公司</p>
                <p className="text-gray-500 text-sm mt-1">统一社会信用代码：91110000MA001234XY</p>
            </div>

            {/* 一、企业身份画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Building className="h-5 w-5 mr-2 text-blue-600" />一、企业身份画像
                </h3>

                {/* 基本工商信息 */}
                <div className="mb-3">
                    <SectionTitle name="基本工商信息" color="green" />
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-1">
                        <CompactMetric label="统一社会信用代码" value="91110000MA001234XY" />
                        <CompactMetric label="企业名称" value="大华科技有限公司" />
                        <CompactMetric label="企业类型" value="有限责任公司" />
                        <CompactMetric label="法定代表人" value="张明" />
                        <CompactMetric label="成立日期" value="2018-05-15" />
                        <CompactMetric label="经营状态" value="存续" eval={{ text: '正常', type: 'positive' }} />
                        <CompactMetric label="注册地址" value="北京市海淀区中关村软件园" />
                        <CompactMetric label="经营范围" value="软件开发、技术咨询、系统集成" />
                    </div>
                </div>

                {/* 规模特征 + 行业定位 + 资质认证 */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div>
                        <SectionTitle name="规模特征" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="注册资本" value="1000万元" eval={{ text: '充足', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="实缴资本" value="800万元" eval={{ text: '80%', type: 'neutral' }} bgColor="bg-purple-50" />
                            <CompactMetric label="资产总额" value="5280万元" bgColor="bg-purple-50" />
                            <CompactMetric label="年营业收入" value="3800万元" eval={{ text: '+15.2%', type: 'growth' }} bgColor="bg-purple-50" />
                            <CompactMetric label="员工人数" value="156人" bgColor="bg-purple-50" />
                            <CompactMetric label="企业规模等级" value="中型企业" eval={{ text: '稳健', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="行业定位" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="所属行业" value="软件和信息技术服务业" bgColor="bg-orange-50" />
                            <CompactMetric label="行业分类代码" value="I65" bgColor="bg-orange-50" />
                            <CompactMetric label="产业链位置" value="中游" eval={{ text: '核心环节', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="资质认证" color="blue" />
                        <div className="space-y-1">
                            <CompactMetric label="高新技术企业认定" value="有效" eval={{ text: '至2026-11', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="软件企业认定" value="有效" eval={{ text: '至2027-03', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="专精特新企业认定" value="市级" eval={{ text: '至2025-12', type: 'neutral' }} bgColor="bg-blue-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 二、股权与治理画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <GitBranch className="h-5 w-5 mr-2 text-blue-600" />二、股权与治理画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* 股权架构图 */}
                    <div className="lg:col-span-2">
                        <SectionTitle name="股权架构" color="purple" />
                        <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-6 rounded-lg">
                            <div className="text-center">
                                <div className="inline-block p-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl mb-3 shadow-lg">
                                    <p className="font-semibold text-lg">大华控股集团</p>
                                    <p className="text-sm text-blue-200 mt-1">控股 65%</p>
                                </div>
                                <div className="h-8 w-0.5 bg-gradient-to-b from-blue-400 to-green-400 mx-auto"></div>
                                <div className="inline-block p-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl my-3 shadow-lg">
                                    <p className="font-semibold text-lg">大华科技有限公司</p>
                                    <p className="text-sm text-green-200 mt-1">本企业（主体）</p>
                                </div>
                                <div className="flex justify-center gap-8 mt-4">
                                    <div className="text-center">
                                        <div className="h-6 w-0.5 bg-purple-300 mx-auto"></div>
                                        <div className="p-3 bg-purple-100 border-2 border-purple-300 rounded-lg text-sm shadow">
                                            <p className="font-medium text-purple-900">大华软件技术公司</p>
                                            <p className="text-purple-600 text-xs mt-1">全资 100%</p>
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <div className="h-6 w-0.5 bg-purple-300 mx-auto"></div>
                                        <div className="p-3 bg-purple-100 border-2 border-purple-300 rounded-lg text-sm shadow">
                                            <p className="font-medium text-purple-900">大华信息服务公司</p>
                                            <p className="text-purple-600 text-xs mt-1">控股 60%</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 股权数据 */}
                    <div>
                        <SectionTitle name="股权结构" color="green" />
                        <div className="space-y-1 mb-3">
                            <CompactMetric label="股东总数" value="3个" />
                            <CompactMetric label="最大股东名称" value="大华控股集团" />
                            <CompactMetric label="最大股东持股比例" value="65%" eval={{ text: '控股', type: 'purple' }} />
                            <CompactMetric label="实际控制人" value="大华控股集团" />
                        </div>
                        <div className="space-y-1 mb-3">
                            <CompactMetric label="全资子公司数量" value="1家" bgColor="bg-purple-50" />
                            <CompactMetric label="控股子公司数量" value="2家" bgColor="bg-purple-50" />
                            <CompactMetric label="参股公司数量" value="1家" bgColor="bg-purple-50" />
                            <CompactMetric label="关联企业数量" value="4家" bgColor="bg-purple-50" />
                        </div>
                        <SectionTitle name="公司治理" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="财务报告审计意见" value="标准无保留意见" eval={{ text: '良好', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="内部控制审计意见" value="无重大缺陷" eval={{ text: '规范', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 三、组织与人力画像 - 图表增强版 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Users className="h-5 w-5 mr-2 text-blue-600" />三、组织与人力画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* 人员结构数据 */}
                    <div>
                        <SectionTitle name="人员结构" color="green" />
                        <div className="space-y-1 mb-3">
                            <CompactMetric label="员工总数" value="156人" eval={{ text: '中型', type: 'neutral' }} />
                            <CompactMetric label="研发人员数量" value="78人" />
                            <CompactMetric label="研发人员占比" value="50%" eval={{ text: '高', type: 'positive' }} />
                            <CompactMetric label="本科及以上学历占比" value="72%" eval={{ text: '优秀', type: 'positive' }} />
                        </div>
                        <SectionTitle name="薪酬成本" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="年度工资总额" value="1890万元" bgColor="bg-purple-50" />
                            <CompactMetric label="人均年薪" value="12.1万元" eval={{ text: '行业中上', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="社保覆盖率" value="100%" eval={{ text: '合规', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>

                    {/* 人员结构饼图 */}
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg">
                        <SectionTitle name="人员构成分布" color="blue" />
                        <SimplePieChart data={staffStructureData} size={180} />
                    </div>

                    {/* 学历结构进度条 */}
                    <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-4 rounded-lg">
                        <SectionTitle name="学历结构分析" color="orange" />
                        <div className="pt-4">
                            <ProgressBar label="硕士及以上" value={22} color="bg-blue-500" />
                            <ProgressBar label="本科" value={49} color="bg-purple-500" />
                            <ProgressBar label="专科及以下" value={28} color="bg-green-500" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 四、财务画像 - 重点图表增强 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />四、财务画像
                </h3>

                {/* 第一行：资产结构图 + 负债权益对比 + 财务能力 */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                    {/* 资产结构饼图 */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-lg">
                        <SectionTitle name="资产结构分析" color="green" />
                        <SimplePieChart data={assetData} size={200} />
                        <div className="mt-3">
                            <CompactMetric label="资产总额" value="5280万" eval={{ text: '+18.5%', type: 'growth' }} bgColor="bg-white" />
                        </div>
                    </div>

                    {/* 负债权益对比柱状图 */}
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg">
                        <SectionTitle name="负债与权益" color="purple" />
                        <SimpleBarChart data={liabilityEquityData} height={220} />
                        <div className="mt-3">
                            <CompactMetric label="资产负债率" value="68.5%" eval={{ text: '稳健', type: 'neutral' }} bgColor="bg-white" />
                        </div>
                    </div>

                    {/* 财务能力进度条 */}
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg">
                        <SectionTitle name="财务综合能力" color="cyan" />
                        <div className="pt-2">
                            <ProgressBar label="盈利能力" value={85} color="bg-blue-500" />
                            <ProgressBar label="偿债能力" value={78} color="bg-purple-500" />
                            <ProgressBar label="运营效率" value={82} color="bg-green-500" />
                            <ProgressBar label="成长能力" value={88} color="bg-orange-500" />
                            <ProgressBar label="现金流" value={90} color="bg-cyan-500" />
                        </div>
                        <div className="mt-2">
                            <CompactMetric label="综合评分" value="84.6分" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-white" />
                        </div>
                    </div>
                </div>

                {/* 第二行：详细财务指标表格 */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
                    <div>
                        <SectionTitle name="盈利能力" color="cyan" />
                        <div className="space-y-1">
                            <CompactMetric label="营业收入" value="3800万" eval={{ text: '+15.2%', type: 'growth' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="毛利率" value="32.3%" eval={{ text: '强', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="净利润" value="292万" eval={{ text: '+22.8%', type: 'growth' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="净利率" value="7.7%" eval={{ text: '良好', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="ROE" value="15.4%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-cyan-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="偿债能力" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="资产负债率" value="68.5%" eval={{ text: '稳健', type: 'neutral' }} bgColor="bg-green-50" />
                            <CompactMetric label="流动比率" value="1.25" eval={{ text: '良好', type: 'positive' }} bgColor="bg-green-50" />
                            <CompactMetric label="速动比率" value="0.95" eval={{ text: '合格', type: 'neutral' }} bgColor="bg-green-50" />
                            <CompactMetric label="利息保障倍数" value="2.8倍" eval={{ text: '安全', type: 'positive' }} bgColor="bg-green-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="运营效率" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="总资产周转率" value="0.76次/年" eval={{ text: '良好', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="应收账款周转率" value="8.1次/年" eval={{ text: '高效', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="应收账款周转天数" value="45天" eval={{ text: '正常', type: 'neutral' }} bgColor="bg-purple-50" />
                            <CompactMetric label="现金周期" value="27天" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="成长能力" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="营业收入增长率" value="15.2%" eval={{ text: '强劲', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="净利润增长率" value="22.8%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="总资产增长率" value="18.5%" eval={{ text: '稳健', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                </div>

                {/* 第三行：成本费用 + 现金流 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <SectionTitle name="成本费用结构" color="cyan" />
                        <div className="grid grid-cols-2 gap-1">
                            <CompactMetric label="销售费用" value="312万" bgColor="bg-cyan-50" />
                            <CompactMetric label="销售费用率" value="8.2%" eval={{ text: '良好', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="管理费用" value="486万" bgColor="bg-cyan-50" />
                            <CompactMetric label="管理费用率" value="12.8%" eval={{ text: '适中', type: 'neutral' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="研发费用" value="247万" bgColor="bg-cyan-50" />
                            <CompactMetric label="研发费用率" value="6.5%" eval={{ text: '重视', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="财务费用" value="85万" bgColor="bg-cyan-50" />
                            <CompactMetric label="期间费用率" value="29.7%" eval={{ text: '合理', type: 'neutral' }} bgColor="bg-cyan-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="现金流量" color="blue" />
                        <div className="space-y-1">
                            <CompactMetric label="经营活动现金流净额" value="1250万" eval={{ text: '充足', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="投资活动现金流净额" value="-380万" eval={{ text: '扩张中', type: 'neutral' }} bgColor="bg-blue-50" />
                            <CompactMetric label="筹资活动现金流净额" value="-420万" eval={{ text: '还款中', type: 'neutral' }} bgColor="bg-blue-50" />
                            <CompactMetric label="销售收现比" value="95.8%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="净利润现金含量" value="428%" eval={{ text: '极佳', type: 'positive' }} bgColor="bg-blue-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 五、业务运营画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Truck className="h-5 w-5 mr-2 text-blue-600" />五、业务运营画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div>
                        <SectionTitle name="业务结构" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="主营业务收入" value="3610万" />
                            <CompactMetric label="主营业务收入占比" value="95%" eval={{ text: '聚焦', type: 'positive' }} />
                            <CompactMetric label="业务线数量" value="3条" />
                            <CompactMetric label="前三大业务集中度" value="88%" eval={{ text: '集中', type: 'neutral' }} />
                        </div>
                    </div>

                    {/* 客户集中度 */}
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg">
                        <SectionTitle name="客户集中度" color="purple" />
                        <div className="pt-2">
                            <ProgressBar label="第一大客户" value={12} color="bg-purple-600" />
                            <ProgressBar label="第2-5大客户" value={23} color="bg-purple-400" />
                            <ProgressBar label="其他客户" value={65} color="bg-purple-200" />
                        </div>
                        <div className="mt-2 space-y-1">
                            <CompactMetric label="客户总数" value="126家" bgColor="bg-white" />
                            <CompactMetric label="客户留存率" value="87%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-white" />
                        </div>
                    </div>

                    <div>
                        <SectionTitle name="供应商&合同" color="orange" />
                        <div className="space-y-1 mb-2">
                            <CompactMetric label="供应商总数" value="85家" bgColor="bg-orange-50" />
                            <CompactMetric label="第一大供应商占比" value="15%" eval={{ text: '合理', type: 'neutral' }} bgColor="bg-orange-50" />
                            <CompactMetric label="前五大供应商占比" value="38%" eval={{ text: '稳定', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                        <div className="space-y-1">
                            <CompactMetric label="年度签约合同总额" value="4280万" bgColor="bg-cyan-50" />
                            <CompactMetric label="合同履约率" value="98%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-cyan-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 六、研发创新画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Award className="h-5 w-5 mr-2 text-blue-600" />六、研发创新画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* 研发投入数据 */}
                    <div>
                        <SectionTitle name="研发投入" color="green" />
                        <div className="space-y-1 mb-3">
                            <CompactMetric label="研发投入总额" value="248万元" eval={{ text: '充足', type: 'positive' }} />
                            <CompactMetric label="研发投入强度" value="6.5%" eval={{ text: '高', type: 'positive' }} />
                            <CompactMetric label="研发人员占比" value="50%" eval={{ text: '优秀', type: 'positive' }} />
                        </div>
                        <SectionTitle name="知识产权" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="专利总数" value="35项" eval={{ text: '丰富', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="发明专利数量" value="12项" eval={{ text: '领先', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="软件著作权数量" value="25项" eval={{ text: '丰富', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>

                    {/* 专利增长趋势图 */}
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg">
                        <SectionTitle name="专利增长趋势" color="blue" />
                        <SimpleLineChart
                            data={patentTrendData}
                            height={200}
                            width={340}
                            lines={[
                                { key: 'total', name: '专利总数', color: '#3b82f6' },
                                { key: 'invention', name: '发明专利', color: '#10b981' }
                            ]}
                        />
                        <div className="mt-2">
                            <CompactMetric label="年度新增专利" value="8项" eval={{ text: '活跃', type: 'positive' }} bgColor="bg-white" />
                        </div>
                    </div>

                    {/* 研发投入趋势 */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-lg">
                        <SectionTitle name="研发投入增长" color="green" />
                        <div className="pt-2">
                            <ProgressBar label="2022年 研发投入165万 (5.8%)" value={5.8} max={10} color="bg-blue-400" />
                            <ProgressBar label="2023年 研发投入198万 (6.0%)" value={6.0} max={10} color="bg-blue-500" />
                            <ProgressBar label="2024年 研发投入248万 (6.5%)" value={6.5} max={10} color="bg-blue-600" />
                        </div>
                        <div className="mt-3">
                            <CompactMetric label="高新产品收入占比" value="78%" eval={{ text: '高', type: 'positive' }} bgColor="bg-white" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 七、税务画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Calculator className="h-5 w-5 mr-2 text-blue-600" />七、税务画像
                </h3>

                {/* 第一行：纳税人信息 + 税种结构图 + 综合税负 */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                    <div>
                        <SectionTitle name="纳税人信息" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="纳税人识别号" value="91110000MA001234XY" />
                            <CompactMetric label="纳税人类型" value="一般纳税人" eval={{ text: '正常', type: 'positive' }} />
                            <CompactMetric label="征收方式" value="查账征收" eval={{ text: '规范', type: 'positive' }} />
                            <CompactMetric label="纳税信用等级" value="A级" eval={{ text: '优秀', type: 'positive' }} />
                        </div>
                    </div>

                    {/* 税种结构饼图 */}
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg">
                        <SectionTitle name="税种构成分析" color="cyan" />
                        <SimplePieChart data={taxStructureData} size={180} />
                    </div>

                    <div>
                        <SectionTitle name="综合税负" color="blue" />
                        <div className="space-y-1">
                            <CompactMetric label="年度纳税总额" value="350.45万元" bgColor="bg-blue-50" />
                            <CompactMetric label="综合税负率" value="9.22%" eval={{ text: '合理', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="行业平均税负率" value="9.8%" bgColor="bg-blue-50" />
                            <CompactMetric label="税负偏离度" value="-5.9%" eval={{ text: '正常', type: 'positive' }} bgColor="bg-blue-50" />
                        </div>
                    </div>
                </div>

                {/* 第二行：增值税 + 企业所得税 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                    <div>
                        <SectionTitle name="增值税" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="年销售额" value="3800万元" bgColor="bg-purple-50" />
                            <CompactMetric label="销项税额" value="426万元" bgColor="bg-purple-50" />
                            <CompactMetric label="进项税额" value="198万元" bgColor="bg-purple-50" />
                            <CompactMetric label="应纳税额" value="228万元" bgColor="bg-purple-50" />
                            <CompactMetric label="实际缴纳额" value="138万元" bgColor="bg-purple-50" />
                            <CompactMetric label="税负率" value="6%" eval={{ text: '行业正常', type: 'neutral' }} bgColor="bg-purple-50" />
                            <CompactMetric label="软件产品退税" value="90万元" eval={{ text: '享受', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="企业所得税" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="年应纳税所得额" value="365万元" bgColor="bg-orange-50" />
                            <CompactMetric label="适用税率" value="15%" eval={{ text: '高新优惠', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="应纳所得税额" value="54.75万元" bgColor="bg-orange-50" />
                            <CompactMetric label="减免所得税额" value="36.5万元" eval={{ text: '高新15%', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="实际缴纳额" value="54.75万元" bgColor="bg-orange-50" />
                            <CompactMetric label="实际税率" value="15%" bgColor="bg-orange-50" />
                        </div>
                    </div>
                </div>

                {/* 第三行：发票管理 + 税收优惠 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <SectionTitle name="发票管理" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="专用发票开具金额" value="2964万元" bgColor="bg-green-50" />
                            <CompactMetric label="普通发票开具金额" value="836万元" bgColor="bg-green-50" />
                            <CompactMetric label="专票开具占比" value="78%" eval={{ text: '高', type: 'positive' }} bgColor="bg-green-50" />
                            <CompactMetric label="进项抵扣率" value="90%" eval={{ text: '良好', type: 'positive' }} bgColor="bg-green-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="税收优惠" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="享受优惠政策数量" value="3项" eval={{ text: '充分利用', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="高新技术企业优惠" value="36.5万元" eval={{ text: '15%税率', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="研发费用加计扣除额" value="496万元" eval={{ text: '200%', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="软件企业优惠" value="90万元" eval={{ text: '即征即退', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="年度税收优惠总额" value="126.5万元" eval={{ text: '显著', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 八、跨境业务画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Globe className="h-5 w-5 mr-2 text-blue-600" />八、跨境业务画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div>
                        <SectionTitle name="跨境交易" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="境外收入总额" value="285万元" />
                            <CompactMetric label="境外收入占比" value="7.5%" eval={{ text: '少量', type: 'neutral' }} />
                            <CompactMetric label="出口销售额" value="285万元" />
                            <CompactMetric label="进口采购额" value="0万元" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="关联交易" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="关联交易总额" value="684万元" bgColor="bg-purple-50" />
                            <CompactMetric label="关联交易占比" value="18%" eval={{ text: '正常', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="关联销售金额" value="456万元" bgColor="bg-purple-50" />
                            <CompactMetric label="关联采购金额" value="228万元" bgColor="bg-purple-50" />
                            <CompactMetric label="关联交易定价方法" value="可比非受控价格法" eval={{ text: '合规', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="同期资料准备状态" value="是" eval={{ text: '完备', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="国际税收" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="适用税收协定" value="中美税收协定" bgColor="bg-orange-50" />
                            <CompactMetric label="境外已缴税款" value="14.25万元" bgColor="bg-orange-50" />
                            <CompactMetric label="境外税收抵免额" value="14.25万元" eval={{ text: '已抵免', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 九、合规风险画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Shield className="h-5 w-5 mr-2 text-blue-600" />九、合规风险画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
                    <div>
                        <SectionTitle name="税务合规" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="纳税申报及时率" value="100%" eval={{ text: '优秀', type: 'positive' }} />
                            <CompactMetric label="税款缴纳及时率" value="100%" eval={{ text: '优秀', type: 'positive' }} />
                            <CompactMetric label="税务稽查次数" value="0次" eval={{ text: '良好', type: 'positive' }} />
                            <CompactMetric label="税务稽查补缴税款" value="0万元" />
                            <CompactMetric label="税务行政处罚次数" value="0次" eval={{ text: '良好', type: 'positive' }} />
                            <CompactMetric label="税务行政处罚金额" value="0万元" />
                            <CompactMetric label="税务风险等级" value="低" eval={{ text: '安全', type: 'positive' }} />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="财务合规" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="财务报告审计意见" value="标准无保留" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="内控缺陷数量" value="0个" eval={{ text: '良好', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="会计核算规范性" value="优" eval={{ text: '规范', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="经营合规" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="环保处罚次数" value="0次" eval={{ text: '良好', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="安全生产事故次数" value="0次" eval={{ text: '良好', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="质量监管处罚次数" value="0次" eval={{ text: '良好', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="法律风险" color="cyan" />
                        <div className="space-y-1">
                            <CompactMetric label="涉诉案件数量" value="2件" eval={{ text: '较少', type: 'neutral' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="涉诉金额合计" value="85万元" eval={{ text: '可控', type: 'neutral' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="行政处罚次数" value="0次" eval={{ text: '良好', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="失信被执行信息" value="否" eval={{ text: '良好', type: 'positive' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="经营异常记录" value="0条" eval={{ text: '良好', type: 'positive' }} bgColor="bg-cyan-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="风险评估汇总" color="blue" />
                        <div className="space-y-1">
                            <CompactMetric label="流动性风险等级" value="低" eval={{ text: '安全', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="客户集中风险等级" value="低" eval={{ text: '分散', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="供应商依赖风险等级" value="中" eval={{ text: '可控', type: 'neutral' }} bgColor="bg-blue-50" />
                            <CompactMetric label="税务合规风险等级" value="低" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-blue-50" />
                            <CompactMetric label="综合风险评级" value="B级" eval={{ text: '良好', type: 'positive' }} bgColor="bg-blue-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 十、外部关系画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Briefcase className="h-5 w-5 mr-2 text-blue-600" />十、外部关系画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <SectionTitle name="银行关系" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="合作银行数量" value="5家" />
                            <CompactMetric label="银行授信总额" value="2500万元" eval={{ text: '充足', type: 'positive' }} />
                            <CompactMetric label="银行贷款余额" value="1300万元" eval={{ text: '52%使用', type: 'neutral' }} />
                            <CompactMetric label="贷款加权平均利率" value="4.85%" eval={{ text: '优惠', type: 'positive' }} />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="信用状况" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="人民银行征信评级" value="AA级" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="海关信用等级" value="一般信用企业" eval={{ text: '正常', type: 'neutral' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 十一、数字化画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Database className="h-5 w-5 mr-2 text-blue-600" />十一、数字化画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <SectionTitle name="系统覆盖" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="ERP系统覆盖率" value="95%" eval={{ text: '高', type: 'positive' }} />
                            <CompactMetric label="财务系统覆盖率" value="100%" eval={{ text: '全面', type: 'positive' }} />
                            <CompactMetric label="税务系统覆盖率" value="100%" eval={{ text: '全面', type: 'positive' }} />
                            <CompactMetric label="财务系统数据质量" value="优" eval={{ text: '高质量', type: 'positive' }} />
                            <CompactMetric label="税务系统数据质量" value="优" eval={{ text: '高质量', type: 'positive' }} />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="数字化能力" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="系统集成度" value="高" eval={{ text: '互联互通', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="数据完整性" value="96%" eval={{ text: '优秀', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="流程自动化率" value="78%" eval={{ text: '良好', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 十二、ESG画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2 text-blue-600" />十二、ESG画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div>
                        <SectionTitle name="环境责任" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="环保投入占比" value="1.2%" eval={{ text: '积极', type: 'positive' }} />
                            <CompactMetric label="节能减排投资" value="45万元" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="社会责任" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="公益捐赠金额" value="15万元" eval={{ text: '积极', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="残疾人雇用比例" value="1.8%" eval={{ text: '达标', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="公司治理" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="信息披露透明度" value="高" eval={{ text: '规范', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="关联交易审批规范性" value="高" eval={{ text: '合规', type: 'positive' }} bgColor="bg-orange-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 十三、政策匹配画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Target className="h-5 w-5 mr-2 text-blue-600" />十三、政策匹配画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                    <div>
                        <SectionTitle name="资质条件" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="高新技术企业条件符合度" value="100%" eval={{ text: '符合', type: 'positive' }} />
                            <CompactMetric label="小微企业认定-应纳税所得额" value="不符合" eval={{ text: '超标', type: 'neutral' }} />
                            <CompactMetric label="小微企业认定-资产总额" value="不符合" eval={{ text: '超标', type: 'neutral' }} />
                            <CompactMetric label="小微企业认定-从业人数" value="符合" eval={{ text: '达标', type: 'positive' }} />
                            <CompactMetric label="软件企业认定条件符合度" value="100%" eval={{ text: '符合', type: 'positive' }} />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="当前享受政策" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="高新技术企业15%税率" value="有效" eval={{ text: '至2026-11', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="软件产品增值税即征即退" value="享受中" eval={{ text: '90万/年', type: 'positive' }} bgColor="bg-purple-50" />
                            <CompactMetric label="研发费用加计扣除200%" value="享受中" eval={{ text: '496万', type: 'positive' }} bgColor="bg-purple-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="潜在可申请政策" color="orange" />
                        <div className="space-y-1">
                            <CompactMetric label="专精特新国家级认定" value="建议申请" eval={{ text: '高', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="预计年度效益" value="政策支持+信用加分" bgColor="bg-orange-50" />
                            <CompactMetric label="申请可行性" value="高" eval={{ text: '条件充分', type: 'positive' }} bgColor="bg-orange-50" />
                            <CompactMetric label="缺失条件" value="需提升创新能力指标" bgColor="bg-orange-50" />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="政策预警" color="cyan" />
                        <div className="space-y-1">
                            <CompactMetric label="高新技术企业资格" value="2026-11到期" eval={{ text: '提前6个月准备', type: 'warning' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="预警级别" value="中" eval={{ text: '需关注', type: 'warning' }} bgColor="bg-cyan-50" />
                            <CompactMetric label="影响政策" value="15%所得税优惠" bgColor="bg-cyan-50" />
                            <CompactMetric label="预计影响金额" value="36.5万/年" eval={{ text: '重大', type: 'warning' }} bgColor="bg-cyan-50" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 十四、特殊业务画像 */}
            <div className="bg-white rounded-lg shadow-sm border p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Factory className="h-5 w-5 mr-2 text-blue-600" />十四、特殊业务画像
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                        <SectionTitle name="软件业务" color="green" />
                        <div className="space-y-1">
                            <CompactMetric label="软件产品销售收入" value="2280万元" />
                            <CompactMetric label="软件产品收入占比" value="60%" eval={{ text: '主营', type: 'positive' }} />
                            <CompactMetric label="软件产品增值率" value="35%" eval={{ text: '超标准', type: 'positive' }} />
                            <CompactMetric label="软件退税金额" value="90万元" eval={{ text: '已享受', type: 'positive' }} />
                        </div>
                    </div>
                    <div>
                        <SectionTitle name="集成电路业务" color="purple" />
                        <div className="space-y-1">
                            <CompactMetric label="集成电路业务收入" value="0万元" bgColor="bg-purple-50" />
                            <CompactMetric label="集成电路收入占比" value="0%" bgColor="bg-purple-50" />
                            <CompactMetric label="集成电路企业认定类型" value="未认定" bgColor="bg-purple-50" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
