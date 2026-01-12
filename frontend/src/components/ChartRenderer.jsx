import { useEffect, useRef } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import './ChartRenderer.css';

// 注册 Chart.js 组件
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

// 柔和的颜色调色板
const COLORS = [
    'rgba(147, 197, 253, 0.8)',  // 蓝
    'rgba(134, 239, 172, 0.8)',  // 绿
    'rgba(252, 211, 77, 0.8)',   // 黄
    'rgba(252, 165, 165, 0.8)',  // 红
    'rgba(196, 181, 253, 0.8)',  // 紫
    'rgba(103, 232, 249, 0.8)'   // 青
];

const BORDER_COLORS = [
    'rgba(59, 130, 246, 1)',
    'rgba(34, 197, 94, 1)',
    'rgba(234, 179, 8, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(139, 92, 246, 1)',
    'rgba(6, 182, 212, 1)'
];

/**
 * 图表渲染组件
 */
/**
 * 图表渲染组件
 */
function ChartRenderer({ chartData, canvasId }) {
    if (!chartData || !chartData.labels || !chartData.datasets) {
        return null;
    }

    const { chartType = 'bar', title, labels, datasets, options = {} } = chartData;

    // 格式化数据
    const formattedDatasets = datasets.map((ds, idx) => ({
        label: ds.label || `数据 ${idx + 1}`,
        data: ds.data,
        backgroundColor: COLORS[idx % COLORS.length],
        borderColor: BORDER_COLORS[idx % BORDER_COLORS.length],
        borderWidth: 1,
        borderRadius: chartType === 'bar' ? 4 : 0,
        fill: chartType === 'line' ? 'origin' : undefined
    }));

    const data = {
        labels,
        datasets: formattedDatasets
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: datasets.length > 1,
                position: 'top'
            },
            title: {
                display: !!title,
                text: title,
                font: { size: 14, weight: 'bold' }
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let value = context.raw;
                        // 格式化大数字
                        if (Math.abs(value) >= 100000000) {
                            return `${context.dataset.label}: ${(value / 100000000).toFixed(2)}亿`;
                        } else if (Math.abs(value) >= 10000) {
                            return `${context.dataset.label}: ${(value / 10000).toFixed(2)}万`;
                        }
                        return `${context.dataset.label}: ${value.toFixed(2)}`;
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value) {
                        if (Math.abs(value) >= 100000000) {
                            return (value / 100000000).toFixed(1) + '亿';
                        } else if (Math.abs(value) >= 10000) {
                            return (value / 10000).toFixed(0) + '万';
                        }
                        return value;
                    }
                }
            }
        }
    };

    // 增长率标注
    const growthRate = options.growthRate;
    const trend = options.trend;

    return (
        <div className="chart-renderer">
            <div className="chart-wrapper">
                {chartType === 'line' ? (
                    <Line data={data} options={chartOptions} id={canvasId} />
                ) : (
                    <Bar data={data} options={chartOptions} id={canvasId} />
                )}
            </div>
            {growthRate && (
                <div className={`growth-badge ${trend || 'stable'}`}>
                    增长率: {growthRate}
                </div>
            )}
        </div>
    );
}

export default ChartRenderer;
