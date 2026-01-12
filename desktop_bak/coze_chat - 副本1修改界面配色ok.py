#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扣子智能体对话工具 - GUI完整优化版
修复内容：
1. 将 QTextEdit 替换为 QTextBrowser 以支持链接点击（复制功能）。
2. 实现流式 MD 源码显示，完成后瞬间覆盖为渲染后的 HTML。
3. 增加一键复制功能。
4. 修复对齐问题，确保全文左对齐。
"""

import sys
import time
import json
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QListWidget, QSplitter, QTextBrowser,
    QComboBox, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QTextCursor
import markdown2

# 历史记录文件路径
HISTORY_FILE = "data/chat_history.json"

# -------------------------- 配置信息 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592905400907989034"
USER_ID = "123"

if sys.platform == "win32":
    requests.packages.urllib3.disable_warnings()

def parse_sse_line(line: str):
    line = line.strip()
    if not line: return None, None
    if line.startswith('event:'): return line[6:].strip(), None
    if line.startswith('data:'):
        try: return None, json.loads(line[5:].strip())
        except: return None, None
    return None, None

class ChatThread(QThread):
    content_received = pyqtSignal(str)
    chat_completed = pyqtSignal(bool, str)

    def __init__(self, question: str, timeout=180):
        super().__init__()
        self.question = question
        self.timeout = timeout
        self.is_running = True

    def run(self):
        headers = {
            "Authorization": f"Bearer {PAT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "bot_id": BOT_ID,
            "user_id": USER_ID,
            "stream": True,
            "auto_save_history": True,
            "additional_messages": [{"role": "user", "content": self.question, "content_type": "text"}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        try:
            response = requests.post("https://api.coze.cn/v3/chat", headers=headers, json=payload, stream=True, timeout=self.timeout, verify=False)
            if response.status_code != 200:
                self.chat_completed.emit(False, f"HTTP错误：{response.status_code}")
                return

            has_content = False
            for chunk in response.iter_content(chunk_size=1024):
                if not self.is_running: break
                if not chunk: continue
                chunk_str = chunk.decode('utf-8', errors='ignore')
                lines = chunk_str.split('\n')
                current_event = None
                for line in lines:
                    event_type, data = parse_sse_line(line)
                    if event_type: current_event = event_type
                    if data and current_event == "conversation.message.delta":
                        if data.get("role") == "assistant" and data.get("type") == "answer":
                            content = data.get("content", "")
                            if content:
                                self.content_received.emit(content)
                                has_content = True
                                time.sleep(0.01)
            self.chat_completed.emit(has_content, "" if has_content else "未获取到回答")
        except Exception as e:
            self.chat_completed.emit(False, str(e))

    def stop(self):
        self.is_running = False
        self.wait()


# ======================== 新增:带路由功能的聊天线程 ========================
class RoutedChatThread(QThread):
    """
    带智能路由功能的聊天线程
    功能:
    1. 意图识别:判断是否为税收优惠/企业财务问题
    2. 智能路由:税收优惠 -> 本地数据库, 企业财务 -> financial.db, 其他 -> Coze API
    3. 支持前端选择公司
    """
    content_received = pyqtSignal(str)
    chat_completed = pyqtSignal(bool, str)

    def __init__(self, question: str, timeout=180, enable_routing: bool = True, selected_company: dict = None):
        super().__init__()
        self.question = question
        self.timeout = timeout
        self.is_running = True
        self.enable_routing = enable_routing  # 路由开关,可快速降级
        self.selected_company = selected_company  # 新增:前端选中的公司
        
        # 延迟导入模块(避免启动时加载失败)
        self.classifier = None
        self.db_query = None
        self.deepseek = None
        self.financial_query = None

    def run(self):
        """主运行逻辑"""
        try:
            # 如果禁用路由,直接使用Coze API
            if not self.enable_routing:
                self._query_coze_api()
                return
            
            # 延迟加载模块
            if not self._load_modules():
                # 模块加载失败,降级到Coze API
                print("⚠️  路由模块加载失败,使用Coze API")
                self._query_coze_api()
                return
            
            # === 新增逻辑:如果前端选择了公司,优先尝试财务查询 ===
            if self.selected_company:
                print(f"🏢 前端已选择公司: {self.selected_company['name']}")
                
                # 检查问题是否包含财务关键词
                if self._has_financial_keywords(self.question):
                    print("📊 检测到财务关键词,路由到财务数据库")
                    self._query_financial_database()
                    return
            
            # Step 1: 意图识别(原逻辑)
            intent = self.classifier.classify(self.question)
            print(f"🔍 意图识别结果: {intent}")
            
            if intent == "financial_data":
                # 路径A: 企业财务数据查询
                self._query_financial_database()
            elif intent == "tax_incentive":
                # 路径B: 税收优惠政策查询
                self._query_local_database()
            else:
                # 路径C: Coze API(原有逻辑)
                self._query_coze_api()
        
        except Exception as e:
            print(f"❌ 路由错误: {str(e)}, 降级到Coze API")
            self._query_coze_api()
    
    def _has_financial_keywords(self, question: str) -> bool:
        """检查问题是否包含财务关键词"""
        financial_keywords = [
            "销售额", "收入", "营业收入", "营收", "利润", "净利润",
            "毛利", "毛利率", "净利率", "利润率", "营业利润",
            "资产", "负债", "总资产", "总负债", "净资产",
            "存货", "应收账款", "应付账款", "周转率", "周转天数",
            "资产负债率", "流动比率", "速动比率",
            "ROA", "ROE", "增长率", "费用率", "税负率",
            "多少", "是多少", "数据", "金额", "查询"
        ]
        return any(kw in question for kw in financial_keywords)
    
    def _load_modules(self) -> bool:
        """延迟加载模块"""
        try:
            if self.classifier is None:
                from modules.intent_classifier import IntentClassifier
                from modules.db_query import TaxIncentiveQuery
                from modules.deepseek_client import DeepSeekClient
                from modules.financial_query import FinancialQuery
                
                self.classifier = IntentClassifier(use_llm=True)
                self.db_query = TaxIncentiveQuery()
                self.deepseek = DeepSeekClient()
                self.financial_query = FinancialQuery()  # 新增
            
            return True
        
        except Exception as e:
            print(f"❌ 模块加载失败: {str(e)}")
            return False
    
    def _query_local_database(self):
        """本地数据库查询路径"""
        try:
            # 1. 查询数据库(增加limit以返回更多结果)
            results, total_count, query_intent = self.db_query.search(self.question, limit=20)
            
            if not results:
                # 未找到结果
                self.content_received.emit("📊 **本地知识库查询结果**\n\n")
                self.content_received.emit("未找到相关税收优惠政策。\n\n")
                self.content_received.emit("💡 **建议**:\n")
                self.content_received.emit("1. 尝试使用更具体的关键词\n")
                self.content_received.emit("2. 咨询税务专业人士\n")
                self.chat_completed.emit(True, "")
                return
            
            # 2. 显示查询结果统计信息
            self.content_received.emit("📊 **本地知识库查询结果**\n\n")
            
            if total_count > len(results):
                # 总数超过显示数量
                self.content_received.emit(f"知识库共有 **{total_count}** 条相关政策,以下展示前 **{len(results)}** 条:\n\n")
                self.content_received.emit("💡 *如需查看更多,请使用更具体的关键词缩小范围*\n\n")
            else:
                # 显示全部结果
                self.content_received.emit(f"找到 **{total_count}** 条相关政策:\n\n")
            
            # 3. 构建结果文本(根据结果数量调整详细程度)
            results_text = ""
            is_detailed = len(results) <= 10  # 10条以内显示详细信息
            
            for idx, result in enumerate(results, 1):
                results_text += f"### 政策 {idx}\n"
                results_text += f"- **税种**: {result.get('tax_type', 'N/A')}\n"
                results_text += f"- **优惠项目**: {result.get('project_name', 'N/A')}\n"
                results_text += f"- **优惠方式**: {result.get('incentive_method', 'N/A')}\n"
                
                # 认定条件
                if result.get('qualification'):
                    qual = result['qualification']
                    if is_detailed or query_intent == "condition":
                        # 详细模式或条件查询:显示完整内容
                        if len(qual) > 500:
                            qual = qual[:500] + "..."
                    else:
                        if len(qual) > 100:
                            qual = qual[:100] + "..."
                    results_text += f"- **认定条件**: {qual}\n"
                
                # 具体优惠规定
                if result.get('detailed_rules'):
                    rules = result['detailed_rules']
                    if is_detailed:
                        # 详细模式:显示完整规定
                        if len(rules) > 800:
                            rules = rules[:800] + "..."
                    else:
                        if len(rules) > 150:
                            rules = rules[:150] + "..."
                    results_text += f"- **具体规定**: {rules}\n"
                
                # 法律依据
                if result.get('legal_basis'):
                    basis = result['legal_basis']
                    if is_detailed:
                        # 详细模式:显示完整法律依据
                        if len(basis) > 400:
                            basis = basis[:400] + "..."
                    else:
                        if len(basis) > 100:
                            basis = basis[:100] + "..."
                    results_text += f"- **法律依据**: {basis}\n"
                
                results_text += "\n"
            
            # 4. 构建DeepSeek prompt(根据查询意图优化)
            if query_intent == "condition":
                # 条件导向的查询
                prompt = f"""请根据以下税收优惠政策数据,回答用户问题,**重点说明优惠认定条件**。

用户问题: {self.question}

政策数据:
{results_text}

要求:
1. 用清晰的Markdown格式回答
2. **重点突出优惠认定条件、申请要求、所需资料等**
3. 如有多个政策,分别说明各自的条件和要求
4. 语言简洁专业,易于理解
5. 如果需要更详细信息,建议咨询税务专业人士

请直接回答,不要重复问题。"""
            else:
                # 一般查询
                prompt = f"""请根据以下税收优惠政策数据,回答用户问题。

用户问题: {self.question}

政策数据:
{results_text}

要求:
1. 用清晰的Markdown格式回答
2. 突出关键信息(优惠比例、适用条件、法律依据等)
3. 如有多个政策,简要说明它们的区别和适用场景
4. 语言简洁专业,易于理解
5. 如果需要更详细信息,建议咨询税务专业人士

请直接回答,不要重复问题。"""
            
            messages = [{"role": "user", "content": prompt}]
            
            # 流式输出DeepSeek响应
            for chunk in self.deepseek.chat_completion(messages, stream=True):
                if self.is_running and chunk:
                    self.content_received.emit(chunk)
                    time.sleep(0.01)  # 控制输出速度
            
            # 添加数据来源标识
            self.content_received.emit("\n\n---\n")
            self.content_received.emit("*数据来源: 本地税收优惠政策数据库*\n")
            
            self.chat_completed.emit(True, "")
        
        except Exception as e:
            print(f"❌ 本地查询失败: {str(e)}, 降级到Coze API")
            self._query_coze_api()
    
    def _query_financial_database(self):
        """企业财务数据查询路径(新增)"""
        try:
            # === 新增:使用前端选中的公司 ===
            if self.selected_company:
                company = self.selected_company
                
                # 检查问题中是否提到了其他公司
                mentioned_company = self.financial_query.match_company(self.question)
                if mentioned_company and mentioned_company['id'] != company['id']:
                    # 问题中提到了不同的公司,给出提示
                    self.content_received.emit(f"💡 **提示**:您选择的是 **{company['name']}**,")
                    self.content_received.emit(f"问题中提到的 **{mentioned_company['name']}** 将被忽略。\n")
                    self.content_received.emit(f"如需查询其他公司,请从左侧下拉菜单切换。\n\n")
                
                # 提取时间和指标
                time_range = self.financial_query.extract_time_range(self.question)
                metrics = self.financial_query.extract_metrics(self.question)
                
                print(f"🏢 使用选中公司: {company['name']}")
                print(f"📅 时间范围: {time_range}")
                print(f"📊 识别指标: {metrics}")
                
                # 执行查询
                results = self.financial_query.execute_query(company['id'], time_range, metrics)
                
                if not results:
                    self.content_received.emit("📊 **企业财务数据查询**\n\n")
                    self.content_received.emit(f"📋 {company['name']} 暂无相关数据\n")
                    self.chat_completed.emit(True, "")
                    return
                
                status = "success"
            else:
                # 原逻辑:从问题中匹配公司
                results, company, status = self.financial_query.search(self.question)
            
            if status == "company_not_found":
                # 企业不存在
                self.content_received.emit("📊 **企业财务数据查询**\n\n")
                self.content_received.emit("❌ 未找到该企业,请检查企业名称是否正确。\n\n")
                self.content_received.emit("💡 **系统中的企业包括**:\n")
                # 列出所有企业
                for name in self.financial_query._load_companies().values():
                    self.content_received.emit(f"- {name}\n")
                self.chat_completed.emit(True, "")
                return
            
            if status == "no_data" or not results:
                self.content_received.emit("📊 **企业财务数据查询**\n\n")
                self.content_received.emit(f"📋 {company['name']} 暂无相关数据\n")
                self.chat_completed.emit(True, "")
                return
            
            # 2. 显示查询结果
            self.content_received.emit("📊 **企业财务数据查询**\n\n")
            formatted = self.financial_query.format_results(results, company)
            self.content_received.emit(formatted)
            
            # 2.5 如果是对比分析,显示计算结果
            comparison_result = None
            if time_range.get('is_comparison'):
                comparison_result = self.financial_query.calculate_comparison(results, time_range)
                if comparison_result.get('has_comparison'):
                    formatted_comparison = self.financial_query.format_comparison(comparison_result, company)
                    self.content_received.emit(formatted_comparison)
            
            # 2.6 生成图表(新增)
            if len(results) >= 2:
                try:
                    from modules.chart_widget import FinancialChartGenerator
                    chart_gen = FinancialChartGenerator()
                    
                    if comparison_result and comparison_result.get('has_comparison'):
                        # 对比分析使用对比图表
                        chart_base64 = chart_gen.generate_comparison_chart(comparison_result, company['name'])
                    else:
                        # 普通查询使用柱状图
                        chart_base64 = chart_gen.generate_bar_chart(results, company['name'])
                    
                    if chart_base64:
                        chart_html = chart_gen.get_chart_html(chart_base64, f"{company['name']}财务数据图表")
                        self.content_received.emit(chart_html)
                except Exception as e:
                    print(f"⚠️  图表生成失败: {e}")
            
            # 3. 使用DeepSeek归纳结果(对比分析时使用更专业的prompt)
            if len(results) > 2:
                self.content_received.emit("\n**分析总结**:\n")
                
                # 构建上下文
                results_text = formatted
                if comparison_result and comparison_result.get('has_comparison'):
                    # 对比分析类问题
                    def format_comparison_data(c):
                        pct_str = f"{c['change_pct']:.2f}%" if c['change_pct'] is not None else "N/A"
                        return f"- {c['metric']}: {c['first_period'][0]}年到{c['last_period'][0]}年, 增长率{pct_str}, 趋势{c['trend']}"
                    
                    comparison_data = "\n".join([
                        format_comparison_data(c) for c in comparison_result['comparisons']
                    ]) if comparison_result.get('comparisons') else ""
                    
                    prompt = f"""请根据以下企业财务数据和对比分析结果,回答用户问题。

用户问题: {self.question}

原始数据:
{results_text}

对比分析:
{comparison_data}

要求:
1. 用2-3句话分析增长趋势
2. 解读增长率的含义(好/一般/差)
3. 如有明显变化,分析可能原因
4. 语言专业简洁

请直接回答。"""
                else:
                    # 普通查询
                    prompt = f"""请根据以下企业财务数据,简要分析总结。

用户问题: {self.question}

数据:
{results_text}

要求:
1. 用1-2句话简要总结数据特点
2. 如有明显趋势,简要说明
3. 不要重复数据,只做总结

请直接回答。"""
                
                messages = [{"role": "user", "content": prompt}]
                
                for chunk in self.deepseek.chat_completion(messages, stream=True):
                    if self.is_running and chunk:
                        self.content_received.emit(chunk)
                        time.sleep(0.01)
            
            # 添加数据来源标识
            self.content_received.emit("\n\n---\n")
            self.content_received.emit("*数据来源: 企业财务数据库*\n")
            
            self.chat_completed.emit(True, "")
            
        except Exception as e:
            print(f"❌ 财务查询失败: {str(e)}")
            self.content_received.emit(f"\n\n⚠️ 查询出错: {str(e)}\n")
            self.chat_completed.emit(False, str(e))
    
    def _query_coze_api(self):
        """原有Coze API查询(完全保持不变)"""
        headers = {
            "Authorization": f"Bearer {PAT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "bot_id": BOT_ID,
            "user_id": USER_ID,
            "stream": True,
            "auto_save_history": True,
            "additional_messages": [{"role": "user", "content": self.question, "content_type": "text"}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        try:
            response = requests.post("https://api.coze.cn/v3/chat", headers=headers, json=payload, stream=True, timeout=self.timeout, verify=False)
            if response.status_code != 200:
                self.chat_completed.emit(False, f"HTTP错误:{response.status_code}")
                return

            has_content = False
            for chunk in response.iter_content(chunk_size=1024):
                if not self.is_running: break
                if not chunk: continue
                chunk_str = chunk.decode('utf-8', errors='ignore')
                lines = chunk_str.split('\n')
                current_event = None
                for line in lines:
                    event_type, data = parse_sse_line(line)
                    if event_type: current_event = event_type
                    if data and current_event == "conversation.message.delta":
                        if data.get("role") == "assistant" and data.get("type") == "answer":
                            content = data.get("content", "")
                            if content:
                                self.content_received.emit(content)
                                has_content = True
                                time.sleep(0.01)
            self.chat_completed.emit(has_content, "" if has_content else "未获取到回答")
        except Exception as e:
            self.chat_completed.emit(False, str(e))

    def stop(self):
        self.is_running = False
        self.wait()
# ============================================================================


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_answer_text = ""
        self.start_pos = None
        self.question_positions = {}  # 新增:记录每个问题的滚动位置 {question: position}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # 使用 QTextBrowser 替代 QTextEdit
        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenLinks(False)  # 禁用自动打开网页
        self.chat_display.anchorClicked.connect(self.handle_anchor_click)
        
        self.chat_display.setHtml("""
            <style>
                body { font-family: 'Microsoft YaHei'; font-size: 14px; text-align: left; }
                .user-question { color: #2563eb; padding: 10px; background: #f0f7ff; border-radius: 5px; margin: 5px 0; text-align: left; }
                .assistant-answer { color: #1f2937; margin: 10px 0; padding: 12px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; text-align: left; }
                .copy-link { color: #2563eb; font-size: 12px; text-decoration: none; font-weight: bold; }
                pre { background: #1f2937; color: #e5e7eb; padding: 10px; border-radius: 5px; text-align: left; }
                code { font-family: 'Consolas'; color: #dc2626; background: #f3f4f6; }
                table { border-collapse: collapse; width: 100%; text-align: left; }
                th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }
                .timestamp { color: #9ca3af; font-size: 11px; margin-right: 5px; }
                p, div, li { text-align: left; }
            </style>
            <div style="text-align: center; color: #9ca3af; padding: 40px;">
                <div style="font-size: 48px;">💬</div>
                <div style="font-size: 16px;">开始对话</div>
            </div>
        """)
        layout.addWidget(self.chat_display)
        self.setLayout(layout)

    def handle_anchor_click(self, url: QUrl):
        """处理点击复制"""
        if url.scheme() == "copy":
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_answer_text)
            # 通过窗口查找状态栏显示反馈
            main_win = self.window()
            if isinstance(main_win, QMainWindow):
                main_win.statusBar().showMessage("✅ 已成功复制回答内容", 2000)

    def append_user_question(self, question: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 记录当前滚动位置(用于导航)
        scrollbar = self.chat_display.verticalScrollBar()
        current_pos = scrollbar.maximum()  # 记录添加前的最大位置
        
        html = f'<div class="user-question" id="q_{hash(question) % 1000000}"><span class="timestamp">[{timestamp}]</span> <b>您：</b>{question}</div>'
        self.chat_display.append(html)
        
        # 保存问题对应的滚动位置
        self.question_positions[question] = current_pos
        
        self.current_answer_text = ""
        self.start_pos = None
    
    def scroll_to_question(self, question: str):
        """滚动到指定问题的位置"""
        if question in self.question_positions:
            pos = self.question_positions[question]
            scrollbar = self.chat_display.verticalScrollBar()
            scrollbar.setValue(pos)
        else:
            # 如果找不到精确位置,尝试搜索文本
            cursor = self.chat_display.document().find(question)
            if not cursor.isNull():
                self.chat_display.setTextCursor(cursor)
                self.chat_display.ensureCursorVisible()

    def append_assistant_content(self, content: str, is_final=False):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if not is_final:
            if self.start_pos is None:
                # 插入起始标记
                self.chat_display.insertHtml("<br><b>智能体：</b><br>")
                cursor.movePosition(QTextCursor.MoveOperation.End)
                # 强制设置新段落左对齐
                bf = cursor.blockFormat()
                bf.setAlignment(Qt.AlignmentFlag.AlignLeft)
                cursor.setBlockFormat(bf)
                self.start_pos = cursor.position()
            
            self.current_answer_text += content
            # 流式插入纯文本
            cursor.insertText(content)
            self.chat_display.setTextCursor(cursor)
            self.chat_display.ensureCursorVisible()
        else:
            if self.start_pos is not None:
                # 选中刚才流式输出的所有 MD 源码
                cursor.setPosition(self.start_pos)
                cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
                
                # 转换 Markdown
                html_body = markdown2.markdown(
                    self.current_answer_text,
                    extras=["fenced-code-blocks", "tables", "break-on-newline"]
                )
                
                # 组装最终 HTML，包含左对齐样式和复制链接
                final_html = f"""
                <div class="assistant-answer" style="text-align: left;">
                    {html_body}
                    <div style="text-align: right; margin-top: 10px; border-top: 1px solid #f3f4f6; padding-top: 5px;">
                        <a href="copy://action" class="copy-link">📋 复制回答</a>
                    </div>
                </div>
                """
                # 覆盖替换
                cursor.insertHtml(final_html)
                self.chat_display.ensureCursorVisible()

class InputWidget(QWidget):
    # 新增:信号用于通知主窗口导航到历史记录
    navigate_to_history = pyqtSignal(str)
    
    def __init__(self, on_send_callback):
        super().__init__()
        self.on_send_callback = on_send_callback
        self.companies = self._load_companies()  # 加载公司列表
        self.init_ui()
        self._load_history()  # 加载历史记录
    
    def _load_companies(self):
        """从数据库加载公司列表"""
        try:
            import sqlite3
            conn = sqlite3.connect('database/financial.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM companies ORDER BY id')
            companies = [(row[0], row[1]) for row in cursor.fetchall()]
            conn.close()
            return companies
        except Exception as e:
            print(f"加载公司列表失败: {e}")
            return []
    
    def _load_history(self):
        """从文件加载历史记录"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for item in history:
                        self.history_list.addItem(item.get('question', ''))
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    
    def _save_history(self):
        """保存历史记录到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            
            history = []
            for i in range(self.history_list.count()):
                history.append({
                    'question': self.history_list.item(i).text(),
                    'timestamp': datetime.now().isoformat()
                })
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def init_ui(self):
        layout = QVBoxLayout()
        
        # === 公司选择区域 ===
        company_layout = QHBoxLayout()
        company_label = QLabel("🏢 查询企业:")
        company_label.setStyleSheet("font-size: 12px; color: #475569;")
        company_layout.addWidget(company_label)
        
        self.company_combo = QComboBox()
        self.company_combo.setMinimumWidth(200)
        for company_id, name in self.companies:
            self.company_combo.addItem(name, company_id)  # 显示名称,存储ID
        
        # 默认选中第一家
        if self.companies:
            self.company_combo.setCurrentIndex(0)
        
        company_layout.addWidget(self.company_combo)
        company_layout.addStretch()
        layout.addLayout(company_layout)
        
        # === 分隔线 ===
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e2e8f0; margin: 8px 0;")
        layout.addWidget(separator)
        
        # === 输入问题区域 ===
        title = QLabel("📝 输入问题 (财务数据/税收优惠/通用咨询)")
        title.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(title)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("如: 2023年利润率? / 小微企业优惠政策有哪些?")
        self.input_field.setMaximumHeight(80)
        layout.addWidget(self.input_field)

        btn_layout = QHBoxLayout()
        self.send_button = QPushButton("📤 发送")
        self.send_button.setObjectName("sendBtn")
        self.send_button.clicked.connect(self.on_send)
        
        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.setObjectName("clearBtn")
        self.clear_button.clicked.connect(self.input_field.clear)
        
        btn_layout.addWidget(self.send_button)
        btn_layout.addWidget(self.clear_button)
        layout.addLayout(btn_layout)

        # 历史记录标题和删除按钮
        history_header = QHBoxLayout()
        history_header.addWidget(QLabel("📜 历史记录"))
        
        self.delete_history_btn = QPushButton("删除记录")
        self.delete_history_btn.setObjectName("deleteBtn")
        self.delete_history_btn.clicked.connect(self._confirm_delete_history)
        history_header.addWidget(self.delete_history_btn)
        history_header.addStretch()
        layout.addLayout(history_header)
        
        self.history_list = QListWidget()
        # 双击:填充到输入框 | 单击:导航到对话位置
        self.history_list.itemClicked.connect(self._on_history_click)
        self.history_list.itemDoubleClicked.connect(lambda it: self.input_field.setPlainText(it.text()))
        layout.addWidget(self.history_list)
        self.setLayout(layout)
    
    def _on_history_click(self, item):
        """单击历史记录:发送导航信号"""
        question = item.text()
        self.navigate_to_history.emit(question)
    
    def _confirm_delete_history(self):
        """确认删除历史记录"""
        if self.history_list.count() == 0:
            QMessageBox.information(self, "提示", "没有历史记录需要删除")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除所有 {self.history_list.count()} 条历史记录吗?\n\n此操作不可撤销!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_list.clear()
            self._save_history()  # 保存空历史
            # 同时清空对话窗口的位置记录
            main_win = self.window()
            if hasattr(main_win, 'chat_w'):
                main_win.chat_w.question_positions.clear()
            QMessageBox.information(self, "完成", "历史记录已删除")
    
    def get_selected_company(self):
        """获取当前选中的公司"""
        idx = self.company_combo.currentIndex()
        if idx >= 0 and idx < len(self.companies):
            company_id, company_name = self.companies[idx]
            return {'id': company_id, 'name': company_name}
        return None

    def on_send(self):
        text = self.input_field.toPlainText().strip()
        if text:
            self.on_send_callback(text)
            self.input_field.clear()
            # 简单去重添加历史
            exists = False
            for i in range(self.history_list.count()):
                if self.history_list.item(i).text() == text:
                    exists = True
                    break
            if not exists:
                self.history_list.addItem(text)
                self._save_history()  # 新增:保存历史到文件

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("扣子智能体对话工具 - 智能路由版(本地数据库+Coze)")
        self.resize(1100, 750)
        
        # === 现代化样式表 ===
        self.setStyleSheet("""
            /* 整体窗口背景 */
            QMainWindow {
                background-color: #f0f4f8;
            }
            
            /* 通用Widget */
            QWidget {
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            
            /* 标签 */
            QLabel {
                color: #1e293b;
            }
            
            /* 输入框 */
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #3b82f6;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
            }
            
            /* 主按钮(发送按钮) - 更浅的蓝色 */
            QPushButton {
                background-color: #60a5fa;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
            
            /* 次要按钮(清空按钮) */
            QPushButton#clearBtn {
                background-color: #64748b;
            }
            QPushButton#clearBtn:hover {
                background-color: #475569;
            }
            
            /* 删除按钮 - 暗灰色无边框 */
            QPushButton#deleteBtn {
                background-color: transparent;
                color: #6b7280;
                border: none;
                font-size: 11px;
                padding: 4px 8px;
            }
            QPushButton#deleteBtn:hover {
                color: #374151;
                background-color: #f3f4f6;
            }
            
            /* 下拉框 */
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 180px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                selection-background-color: #eff6ff;
                selection-color: #1e40af;
            }
            
            /* 历史记录列表 */
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 3px;
                margin: 1px 0;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            
            /* 对话区域 */
            QTextBrowser {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
            }
            
            /* 分割条 */
            QSplitter::handle {
                background-color: #cbd5e1;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #3b82f6;
            }
            
            /* 状态栏 */
            QStatusBar {
                background-color: #e2e8f0;
                color: #475569;
                border-top: 1px solid #cbd5e1;
            }
        """)
        
        # 路由开关(True=启用智能路由, False=仅使用Coze)
        self.enable_routing = True
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.input_w = InputWidget(self.handle_send)
        self.chat_w = ChatWidget()
        
        # 连接历史记录导航信号
        self.input_w.navigate_to_history.connect(self._navigate_to_history)
        
        splitter.addWidget(self.input_w)
        splitter.addWidget(self.chat_w)
        splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(splitter)
        self.statusBar().showMessage("✅ 就绪 | 智能路由已启用")
    
    def _navigate_to_history(self, question: str):
        """导航到历史记录对应的对话位置"""
        self.chat_w.scroll_to_question(question)
        self.statusBar().showMessage(f"📍 已定位到: {question[:30]}...", 2000)

    def handle_send(self, q):
        self.input_w.send_button.setEnabled(False)
        self.chat_w.append_user_question(q)
        
        # 获取选中的公司(新增)
        selected_company = self.input_w.get_selected_company()
        
        # 使用带路由功能的线程,传递选中的公司
        self.thread = RoutedChatThread(
            q, 
            enable_routing=self.enable_routing,
            selected_company=selected_company  # 新增
        )
        
        self.thread.content_received.connect(self.chat_w.append_assistant_content)
        self.thread.chat_completed.connect(self.handle_finish)
        self.thread.start()

    def handle_finish(self, success, err):
        self.input_w.send_button.setEnabled(True)
        if success:
            self.chat_w.append_assistant_content("", is_final=True)
            self.statusBar().showMessage("✅ 对话完成")
        else:
            self.chat_w.chat_display.append(f"\u003cdiv style='color:red; text-align:left;'\u003e❌ 错误: {err}\u003c/div\u003e")
            self.statusBar().showMessage("❌ 发生错误")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
