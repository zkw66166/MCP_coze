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
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QListWidget, QSplitter, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QTextCursor
import markdown2

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

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_answer_text = ""
        self.start_pos = None 
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
        html = f'<div class="user-question"><span class="timestamp">[{timestamp}]</span> <b>您：</b>{question}</div>'
        self.chat_display.append(html)
        self.current_answer_text = ""
        self.start_pos = None 

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
    def __init__(self, on_send_callback):
        super().__init__()
        self.on_send_callback = on_send_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("📝 输入问题")
        title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("请输入内容...")
        self.input_field.setMaximumHeight(100)
        layout.addWidget(self.input_field)

        btn_layout = QHBoxLayout()
        self.send_button = QPushButton("📤 发送")
        self.send_button.clicked.connect(self.on_send)
        self.send_button.setStyleSheet("background: #2563eb; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        
        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.clicked.connect(self.input_field.clear)
        
        btn_layout.addWidget(self.send_button)
        btn_layout.addWidget(self.clear_button)
        layout.addLayout(btn_layout)

        layout.addWidget(QLabel("📜 历史记录"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(lambda it: self.input_field.setPlainText(it.text()))
        layout.addWidget(self.history_list)
        self.setLayout(layout)

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("扣子智能体对话工具 - GUI完整优化版")
        self.resize(1100, 750)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.input_w = InputWidget(self.handle_send)
        self.chat_w = ChatWidget()
        
        splitter.addWidget(self.input_w)
        splitter.addWidget(self.chat_w)
        splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(splitter)
        self.statusBar().showMessage("✅ 就绪")

    def handle_send(self, q):
        self.input_w.send_button.setEnabled(False)
        self.chat_w.append_user_question(q)
        self.thread = ChatThread(q)
        self.thread.content_received.connect(self.chat_w.append_assistant_content)
        self.thread.chat_completed.connect(self.handle_finish)
        self.thread.start()

    def handle_finish(self, success, err):
        self.input_w.send_button.setEnabled(True)
        if success:
            self.chat_w.append_assistant_content("", is_final=True)
            self.statusBar().showMessage("✅ 对话完成")
        else:
            self.chat_w.chat_display.append(f"<div style='color:red; text-align:left;'>❌ 错误: {err}</div>")
            self.statusBar().showMessage("❌ 发生错误")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
