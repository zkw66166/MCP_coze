#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
财务数据图表组件
使用matplotlib生成图表,适配PyQt6显示
"""

import io
import base64
from typing import List, Dict, Optional
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端,避免与PyQt冲突
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FinancialChartGenerator:
    """财务数据图表生成器"""
    
    def __init__(self):
        # 柔和淡雅的颜色(浅色调)
        self.colors = ['#93C5FD', '#86EFAC', '#FCD34D', '#FCA5A5', '#C4B5FD', '#67E8F9']
        self.figure_size = (8, 3.5)  # 适中尺寸，平衡显示效果和数据传输
    
    def generate_bar_chart(self, results: List[Dict], title: str = "财务数据对比") -> str:
        """
        生成柱状图(用于多时间段对比)
        
        Args:
            results: 查询结果列表 [{'metric_name': '利润', 'year': 2023, 'quarter': 1, 'value': 100, 'unit': '元'}]
            title: 图表标题
        
        Returns:
            Base64编码的图片数据(用于嵌入HTML)
        """
        if not results:
            return ""
        
        # 准备数据
        labels = []
        values = []
        for r in results:
            year = r.get('year', '')
            quarter = r.get('quarter')
            label = f"{year}年" + (f"Q{quarter}" if quarter else "")
            labels.append(label)
            values.append(r.get('value', 0) or 0)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # 绘制柱状图
        bars = ax.bar(labels, values, color=self.colors[:len(labels)], edgecolor='white', linewidth=0.7)
        
        # 在柱状图上显示数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
        
        # 设置标题和标签
        metric_name = results[0].get('metric_name', '数据') if results else '数据'
        unit = results[0].get('unit', '元') if results else '元'
        ax.set_title(f"{title} - {metric_name}", fontsize=12, fontweight='bold')
        ax.set_ylabel(f"金额 ({unit})", fontsize=10)
        ax.set_xlabel("时间段", fontsize=10)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)
        
        # 倾斜横坐标标签，避免重叠
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 转换为Base64
        return self._fig_to_base64(fig)
    
    def generate_line_chart(self, results: List[Dict], title: str = "财务趋势分析") -> str:
        """
        生成折线图(用于趋势分析)
        
        Args:
            results: 查询结果列表
            title: 图表标题
        
        Returns:
            Base64编码的图片数据
        """
        if not results:
            return ""
        
        # 准备数据
        labels = []
        values = []
        for r in results:
            year = r.get('year', '')
            quarter = r.get('quarter')
            label = f"{year}年" + (f"Q{quarter}" if quarter else "")
            labels.append(label)
            values.append(r.get('value', 0) or 0)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # 绘制折线图
        line, = ax.plot(labels, values, marker='o', color=self.colors[0], 
                       linewidth=2, markersize=8, markerfacecolor='white', 
                       markeredgewidth=2)
        
        # 在数据点上显示数值
        for i, (label, val) in enumerate(zip(labels, values)):
            ax.annotate(f'{val:,.0f}',
                       xy=(i, val),
                       xytext=(0, 10),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
        
        # 填充区域
        ax.fill_between(range(len(labels)), values, alpha=0.1, color=self.colors[0])
        
        # 设置标题和标签
        metric_name = results[0].get('metric_name', '数据') if results else '数据'
        unit = results[0].get('unit', '元') if results else '元'
        ax.set_title(f"{title} - {metric_name}", fontsize=12, fontweight='bold')
        ax.set_ylabel(f"金额 ({unit})", fontsize=10)
        ax.set_xlabel("时间段", fontsize=10)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.3)
        
        # 倾斜横坐标标签，避免重叠
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def generate_comparison_chart(self, comparison_result: Dict, company_name: str = "") -> list:
        """
        生成对比分析图表(为每个指标生成独立图表)
        
        Args:
            comparison_result: calculate_comparison()返回的结果
            company_name: 公司名称
        
        Returns:
            图表列表 [(metric_name, chart_html), ...]
        """
        if not comparison_result.get('has_comparison'):
            return []
        
        comparisons = comparison_result.get('comparisons', [])
        if not comparisons:
            return []
        
        charts = []
        
        # 为每个指标生成图表
        for comp in comparisons:
            try:
                periods = comp.get('periods', [])
                
                if len(periods) < 2:
                    continue
                
                # 准备数据
                labels = []
                values = []
                for period in periods:
                    year, quarter, val, unit = period
                    label = f"{year}" + (f"Q{quarter}" if quarter else "")
                    labels.append(label)
                    values.append(val or 0)
                
                # 创建图表
                fig, ax = plt.subplots(figsize=self.figure_size)
                
                # 绘制柱状图
                x_pos = range(len(labels))
                bars = ax.bar(x_pos, values, color=self.colors[:len(labels)], edgecolor='white')
                
                # 在柱状图上显示数值
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax.annotate(f'{val:,.0f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
                
                # 添加增长率标注
                change_pct = comp.get('change_pct')
                trend = comp.get('trend', 'stable')
                trend_color = '#10B981' if trend == 'up' else ('#EF4444' if trend == 'down' else '#6B7280')
                
                if change_pct is not None:
                    trend_text = f"增长率: {change_pct:+.1f}%"
                    ax.text(0.98, 0.95, trend_text, transform=ax.transAxes, 
                           ha='right', va='top', fontsize=11, fontweight='bold',
                           color=trend_color,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                # 设置标题
                metric = comp.get('metric', '数据')
                title = f"{company_name} {metric}对比" if company_name else f"{metric}对比"
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_ylabel(f"金额 ({comp.get('unit', '元')})", fontsize=10)
                ax.set_xticks(x_pos)
                ax.set_xticklabels(labels)
                
                # 美化
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='y', alpha=0.3)
                
                # 倾斜横坐标标签，避免重叠
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                # 转换为Base64并添加到结果
                chart_base64 = self._fig_to_base64(fig)
                if chart_base64:
                    chart_html = self.get_chart_html(chart_base64, f"{company_name} {metric}对比图表")
                    charts.append((metric, chart_html))
            except Exception as e:
                print(f"⚠️ 生成 {comp.get('metric', '未知')} 图表失败: {e}")
                continue
        
        return charts
    
    def _fig_to_base64(self, fig: Figure) -> str:
        """将matplotlib图表转换为Base64编码"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=80, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        buf.close()  # 释放内存
        return f"data:image/png;base64,{img_base64}"
    
    def get_chart_html(self, base64_img: str, alt_text: str = "财务图表") -> str:
        """生成可嵌入HTML的图片标签"""
        if not base64_img:
            return ""
        return f'<div style="text-align: center; margin: 15px 0;"><img src="{base64_img}" alt="{alt_text}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></div>'


# 测试代码
if __name__ == "__main__":
    generator = FinancialChartGenerator()
    
    # 测试数据
    test_results = [
        {'metric_name': '利润', 'year': 2023, 'quarter': 1, 'value': 3431181, 'unit': '元'},
        {'metric_name': '利润', 'year': 2023, 'quarter': 2, 'value': 4126126, 'unit': '元'},
        {'metric_name': '利润', 'year': 2023, 'quarter': 3, 'value': 4545688, 'unit': '元'},
        {'metric_name': '利润', 'year': 2023, 'quarter': 4, 'value': 5314488, 'unit': '元'},
    ]
    
    # 生成柱状图
    bar_img = generator.generate_bar_chart(test_results, "ABC公司")
    print(f"柱状图生成成功: {len(bar_img)} bytes")
    
    # 生成折线图
    line_img = generator.generate_line_chart(test_results, "ABC公司")
    print(f"折线图生成成功: {len(line_img)} bytes")
