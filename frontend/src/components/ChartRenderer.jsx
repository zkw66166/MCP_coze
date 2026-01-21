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
        ...ds,
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

    // 默认 Scales 配置
    const defaultScales = {
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
    };

    // 合并传入的 options.scales
    const finalScales = { ...defaultScales };
    if (options.scales) {
        Object.keys(options.scales).forEach(key => {
            if (finalScales[key]) {
                // 如果已存在 (如 y 轴)，合并属性，但保留默认的 ticks callback (如果后端没传)
                const defaultTicks = finalScales[key].ticks;
                finalScales[key] = { ...finalScales[key], ...options.scales[key] };
                if (defaultTicks && !options.scales[key].ticks) {
                    finalScales[key].ticks = { ...finalScales[key].ticks, ...defaultTicks };
                }
            } else {
                // 如果不存在 (如 y1 轴)，直接添加
                finalScales[key] = options.scales[key];
            }
        });
    }

    // ---------------------------------------------------------
    // 双轴 0刻度对齐核心逻辑
    // ---------------------------------------------------------
    if (finalScales.y && finalScales.y1) {
        // 1. 提取两个数据集的值用于计算范围
        // 假设 dataset[0] 对应 y (左轴), dataset[1] 对应 y1 (右轴)
        // 实际场景应根据 dataset.yAxisID 匹配，这里假定标准双轴结构
        const yData = datasets.find(d => d.yAxisID === 'y' || !d.yAxisID)?.data || [];
        const y1Data = datasets.find(d => d.yAxisID === 'y1')?.data || [];

        const getRange = (arr) => {
            if (!arr.length) return { max: 1, min: 0 };
            let max = Math.max(...arr);
            let min = Math.min(...arr);
            // 确保包含0，避免单侧数据导致刻度异常
            max = Math.max(max, 0);
            min = Math.min(min, 0);
            // 避免最大最小相等导致的计算错误
            if (max === min) {
                max += 1;
                min -= 1;
            }
            return { max, min };
        };

        let yRange = getRange(yData);
        let y1Range = getRange(y1Data);

        // 2. 计算各轴"正半轴占比" (Position of Zero)
        // Ratio = Max / (Max - Min)
        // 含义：0线在整个高度的百分比位置（从下往上数是 (0-Min)/(Max-Min) = -Min/Range? 不，CSS top是反的。
        // Value 坐标系：Bottom是Min，Top是Max。0的位置 = (0 - Min) / (Max - Min).
        // 我们需要 alignmentRatio = -Min / (Max - Min) 保持一致。

        const getZeroRatio = (range) => {
            return -range.min / (range.max - range.min);
        };

        const r1 = getZeroRatio(yRange);
        const r2 = getZeroRatio(y1Range);

        // 3. 取最大的 Ratio 作为目标（意味着要把 0 线往上推，即增加负半轴区域）
        // 必须取最大值，因为不能截断数据（即只能延伸 Min，不能缩减 Max）
        const targetRatio = Math.max(r1, r2);

        // 4. 根据目标 Ratio 反推新的 Min 或 Max
        // Formula: targetRatio = -NewMin / (Max - NewMin)
        // => targetRatio * Max - targetRatio * NewMin = -NewMin
        // => targetRatio * Max = NewMin * (targetRatio - 1)
        // => NewMin = (targetRatio * Max) / (targetRatio - 1)

        // 修正各轴
        const alignAxis = (range, originalRatio) => {
            if (originalRatio < targetRatio) {
                // 当前0线太低（负轴不够），需要延伸 Min
                // 保持 Max 不变（除非不得不变，但这里逻辑是只扩充）
                // NewMin = - (targetRatio * range.max) / (1 - targetRatio)

                // 边界检查：如果 targetRatio close to 1 (全负?) or 0 (全正?)
                if (targetRatio >= 0.99) return range; // 几乎全负，不用动

                const newMin = - (targetRatio * range.max) / (1 - targetRatio);
                return { ...range, min: newMin };
            }
            return range;
        };

        const newYRange = alignAxis(yRange, r1);
        const newY1Range = alignAxis(y1Range, r2);

        // 5. 应用到 Scales
        // 注意：建议留一点 Padding (比如 1.1倍)，这里暂且严格对齐
        finalScales.y.min = newYRange.min;
        finalScales.y.max = newYRange.max;
        finalScales.y1.min = newY1Range.min;
        finalScales.y1.max = newY1Range.max;
    }

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
        scales: finalScales
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
            {
                growthRate && (
                    <div className={`growth-badge ${trend || 'stable'}`}>
                        增长率: {growthRate}
                    </div>
                )
            }
        </div >
    );
}

export default ChartRenderer;
