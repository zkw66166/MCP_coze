#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扣子智能体对话工具 - GUI完整优化版
功能：
1. 图形用户界面（PyQt6）
2. Markdown格式渲染
3. 实时流式显示（打字机效果）
4. 分层渲染策略（实时纯文本 + 完成后Markdown）
5. 历史记录管理
6. 多轮对话支持
"""

import sys
import time
import json
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QListWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
import markdown2

# -------------------------- 基础配置 --------------------------
if sys.platform == "win32":
    # Windows下禁用SSL警告
    requests.packages.urllib3.disable_warnings()

# -------------------------- 配置信息 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"
USER_ID = "123"


# =========================== API调用逻辑（完全保留原有逻辑） ===========================

def parse_sse_line(line: str):
    """
    解析SSE格式的一行数据
    返回: (event_type, data_dict) 或 (None, None)
    """
    line = line.strip()
    if not line:
        return None, None

    if line.startswith('event:'):
        return line[6:].strip(), None

    if line.startswith('data:'):
        data_str = line[5:].strip()
        try:
            data = json.loads(data_str)
            return None, data
        except json.JSONDecodeError:
            return None, None

    return None, None


class ChatThread(QThread):
    """
    对话线程 - 在后台执行API调用，避免阻塞UI
    """
    # 信号：收到新内容(文本), 完成信号(成功/失败, 错误消息)
    content_received = pyqtSignal(str)
    chat_completed = pyqtSignal(bool, str)

    def __init__(self, question: str, timeout=180):
        super().__init__()
        self.question = question
        self.timeout = timeout
        self.is_running = True

    def run(self):
        """
        执行流式对话 - 完全保留原有逻辑
        """
        headers = {
            "Authorization": f"Bearer {PAT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        payload = {
            "bot_id": BOT_ID,
            "user_id": USER_ID,
            "stream": True,
            "auto_save_history": True,
            "additional_messages": [
                {
                    "role": "user",
                    "content": self.question,
                    "content_type": "text"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                "https://api.coze.cn/v3/chat",
                headers=headers,
                json=payload,
                stream=True,
                timeout=self.timeout,
                verify=False
            )

            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"HTTP错误：{response.status_code}\n{response.text}"
                self.chat_completed.emit(False, error_msg)
                return

            # 流式处理响应 - 完全保留原有逻辑
            buffer = ""
            current_event = None
            has_content = False

            for chunk in response.iter_content(chunk_size=1024):
                if not self.is_running:
                    break

                if not chunk:
                    continue

                # 解码并按行分割
                chunk_str = chunk.decode('utf-8', errors='ignore')
                buffer += chunk_str

                # 按行处理
                lines = buffer.split('\n')
                buffer = lines[-1]  # 保留最后一行（可能不完整）

                for line in lines[:-1]:  # 处理完整的行
                    event_type, data = parse_sse_line(line)

                    if event_type:
                        current_event = event_type
                        continue

                    if data and current_event == "conversation.message.delta":
                        # 检查是否是回答类型的消息
                        if data.get("role") == "assistant" and data.get("type") == "answer":
                            content = data.get("content", "")
                            if content:
                                self.content_received.emit(content)
                                has_content = True
                                time.sleep(0.01)  # 短暂延迟，模拟打字机效果

            if has_content:
                self.chat_completed.emit(True, "")
            else:
                self.chat_completed.emit(False, "未获取到回答")

        except requests.exceptions.Timeout:
            self.chat_completed.emit(False, f"请求超时（{self.timeout}秒）")
        except Exception as e:
            self.chat_completed.emit(False, f"异常：{str(e)}")

    def stop(self):
        """停止线程"""
        self.is_running = False
        self.wait()


# =========================== GUI界面 ===========================

class ChatWidget(QWidget):
    """对话区域控件"""

    def __init__(self):
        super().__init__()
        self.current_answer_text = ""  # 当前回答的纯文本缓冲区
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 对话历史区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        # 核心修改：确保全局 body 强制左对齐，并清理了可能干扰对齐的 html 结构
        self.chat_display.setHtml("""
            <style>
                body {
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                    font-size: 14px;
                    line-height: 1.8;
                    text-align: left;
                }
                .user-question {
                    color: #2563eb;
                    padding: 10px;
                    background: #ffffff;
                    border-radius: 5px;
                    text-align: left;                    
                }
                .assistant-answer {
                    color: #1f2937;
                    margin: 10px 0;
                    padding: 10px;
                    background: #ffffff;
                    border-radius: 5px;
                    text-align: left;
                }
                .timestamp {
                    color: #9ca3af;
                    font-size: 12px;
                    margin-right: 10px;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #111827;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    font-weight: bold;
                    text-align: left;
                }
                h1 { font-size: 24px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
                h2 { font-size: 20px; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }
                h3 { font-size: 18px; }
                code {
                    background: #f3f4f6;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 13px;
                    color: #dc2626;
                }
                pre {
                    background: #1f2937;
                    color: #e5e7eb;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    line-height: 1.6;
                    text-align: left;
                }
                pre code {
                    background: transparent;
                    color: inherit;
                    padding: 0;
                }
                ul, ol {
                    margin: 8px 0;
                    padding-left: 25px;
                    text-align: left;
                }
                li {
                    margin: 5px 0;
                    line-height: 1.8;
                    text-align: left;
                }
                p {
                    margin: 10px 0;
                    line-height: 1.8;
                    text-align: left;
                }
                strong {
                    color: #dc2626;
                    font-weight: bold;
                }
                em {
                    color: #059669;
                    font-style: italic;
                }
                a {
                    color: #2563eb;
                    text-decoration: underline;
                }
                blockquote {
                    border-left: 4px solid #e5e7eb;
                    margin: 15px 0;
                    padding: 10px 15px;
                    background: #f9fafb;
                    color: #6b7280;
                    text-align: left;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }
                th, td {
                    border: 1px solid #e5e7eb;
                    padding: 8px 12px;
                    text-align: left;
                }
                th {
                    background: #f3f4f6;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background: #f9fafb;
                }
            </style>
            <div style="text-align: center; color: #9ca3af; padding: 40px 20px;">
                <div style="font-size: 48px; margin-bottom: 20px;">💬</div>
                <div style="font-size: 18px; margin-bottom: 10px;">开始对话</div>
                <div style="font-size: 12px;">在左侧输入问题，点击"发送"按钮</div>
            </div>
        """)
        layout.addWidget(self.chat_display)

        self.setLayout(layout)

    def append_user_question(self, question: str):
        """添加用户问题"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # 显式在 div 样式中加入 text-align: left
        html = f"""
            <div class="user-question" style="text-align: left;">
                <span class="timestamp">[{timestamp}]</span>
                <strong>您：</strong>{question}
            </div>
        """
        self.chat_display.append(html)
        # 清空当前回答缓冲区
        self.current_answer_text = ""

    def append_assistant_content(self, content: str, is_final=False):
        """
        添加智能体回答
        采用分层渲染策略：
        - 实时阶段：显示纯文本
        - 完成阶段：渲染Markdown
        """
        if is_final:
            # 对话完成：将累积的纯文本转换为Markdown渲染
            if self.current_answer_text:
                html_content = markdown2.markdown(
                    self.current_answer_text,
                    extras=["fenced-code-blocks", "tables", "strike", "task_list", "code-friendly"]
                )
                # 显式加入 text-align: left
                self.chat_display.append(f'<div class="assistant-answer" style="text-align: left;">{html_content}</div>')
                self.current_answer_text = ""
        else:
            # 实时更新：累积纯文本，直接显示纯文本
            self.current_answer_text += content
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            # 确保打字机过程中的对齐也是靠左
            block_format = cursor.blockFormat()
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            cursor.setBlockFormat(block_format)
            
            self.chat_display.setTextCursor(cursor)
            self.chat_display.insertPlainText(content)

    def append_system_message(self, message: str, is_error=False):
        """添加系统消息"""
        color = "#dc2626" if is_error else "#059669"
        icon = "❌" if is_error else "✅"
        html = f"""
            <div style="color: {color}; padding: 10px; background: #f9fafb; border-radius: 5px; margin: 10px 0; border-left: 4px solid {color}; text-align: left;">
                <strong>{icon}</strong> {message}
            </div>
        """
        self.chat_display.append(html)


class InputWidget(QWidget):
    """输入区域控件"""

    def __init__(self, on_send_callback):
        super().__init__()
        self.on_send_callback = on_send_callback
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题
        title = QLabel("📝 输入问题")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # 输入框
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("请输入你的问题...")
        self.input_field.setMaximumHeight(120)
        self.input_field.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', sans-serif;
                background: #ffffff;
            }
            QTextEdit:focus {
                border-color: #2563eb;
            }
        """)
        layout.addWidget(self.input_field)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.send_button = QPushButton("📤 发送")
        self.send_button.clicked.connect(self.on_send)
        self.send_button.setMinimumHeight(40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        button_layout.addWidget(self.send_button)

        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.clicked.connect(self.on_clear)
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # 历史记录
        history_title = QLabel("📜 历史记录")
        history_title.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(history_title)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_clicked)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #f9fafb;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background: #e5e7eb;
            }
            QListWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
        """)
        layout.addWidget(self.history_list)

        self.setLayout(layout)

    def on_send(self):
        """发送按钮点击"""
        question = self.input_field.toPlainText().strip()
        if question:
            self.on_send_callback(question)
            self.input_field.clear()

    def on_clear(self):
        """清空按钮点击"""
        self.input_field.clear()
        self.input_field.setFocus()

    def on_history_clicked(self, item):
        """历史记录点击"""
        question = item.text()
        self.input_field.setPlainText(question)
        self.input_field.setFocus()

    def add_to_history(self, question: str):
        """添加到历史记录"""
        # 避免重复
        for i in range(self.history_list.count()):
            if self.history_list.item(i).text() == question:
                return
        self.history_list.addItem(question)
        # 滚动到底部
        self.history_list.scrollToBottom()

    def set_buttons_enabled(self, enabled: bool):
        """设置按钮状态"""
        self.send_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.chat_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("扣子智能体对话工具 - GUI完整优化版")
        self.setGeometry(100, 100, 1200, 800)

        # 中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局（水平分割）
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：输入区域（30%）
        self.input_widget = InputWidget(self.on_send)
        splitter.addWidget(self.input_widget)

        # 右侧：对话显示区域（70%）
        self.chat_widget = ChatWidget()
        splitter.addWidget(self.chat_widget)

        # 设置分割比例
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        main_layout.addWidget(splitter)

        # 状态栏
        self.statusBar().showMessage("✅ 就绪 - 请输入问题开始对话")

    def on_send(self, question: str):
        """发送问题"""
        # 禁用按钮
        self.input_widget.set_buttons_enabled(False)

        # 显示问题
        self.chat_widget.append_user_question(question)

        # 添加到历史记录
        self.input_widget.add_to_history(question)

        # 更新状态栏
        self.statusBar().showMessage(f"🔄 正在提问：{question[:30]}...")

        # 创建并启动对话线程
        self.chat_thread = ChatThread(question, timeout=180)
        self.chat_thread.content_received.connect(self.on_content_received)
        self.chat_thread.chat_completed.connect(self.on_chat_completed)
        self.chat_thread.start()

    def on_content_received(self, content: str):
        """收到新内容 - 实时显示"""
        self.chat_widget.append_assistant_content(content)

    def on_chat_completed(self, success: bool, error_message: str):
        """对话完成"""
        # 启用按钮
        self.input_widget.set_buttons_enabled(True)

        if success:
            # 触发最终的Markdown渲染
            self.chat_widget.append_assistant_content("", is_final=True)
            self.statusBar().showMessage("✅ 对话完成")
        else:
            self.chat_widget.append_system_message(error_message, is_error=True)
            self.statusBar().showMessage(f"❌ 错误：{error_message[:50]}")

        # 清理线程
        if self.chat_thread:
            self.chat_thread.deleteLater()
            self.chat_thread = None

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止正在运行的线程
        if self.chat_thread and self.chat_thread.isRunning():
            self.chat_thread.stop()
        event.accept()


# =========================== 主程序 ===========================

if __name__ == "__main__":
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())
