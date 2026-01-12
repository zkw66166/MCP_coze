#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扣子智能体对话工具 - 流式输出修正版
基于 coze_chat_raw.py 微调，正确提取回答内容
"""

import requests
import json
import sys
import time

# -------------------------- 基础配置 --------------------------
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

# -------------------------- 配置信息 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"
USER_ID = "123"

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

def stream_chat(question: str, timeout=180):
    """
    流式对话函数
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
                "content": question,
                "content_type": "text"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    print(f"\n🔍 问题：{question}")
    print("=" * 80)
    print("💬 智能体回答：")
    print("-" * 80)

    try:
        response = requests.post(
            "https://api.coze.cn/v3/chat",
            headers=headers,
            json=payload,
            stream=True,
            timeout=timeout,
            verify=False
        )

        # 检查HTTP状态码
        if response.status_code != 200:
            print(f"\n❌ HTTP错误：{response.status_code}")
            print(response.text)
            return ""

        # 流式处理响应
        buffer = ""
        current_event = None
        full_answer = ""
        
        for chunk in response.iter_content(chunk_size=1024):
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
                            # 实时显示（打字机效果）
                            print(content, end='', flush=True)
                            full_answer += content
                            
                            # 短暂延迟，模拟打字机效果
                            time.sleep(0.01)

        print("\n" + "-" * 80)
        
        if full_answer:
            print("=" * 80)
            print("✅ 对话完成")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⚠️ 未获取到回答")
            print("=" * 80)
        
        return full_answer

    except requests.exceptions.Timeout:
        print("\n" + "=" * 80)
        print("⚠️ 请求超时")
        print("=" * 80)
        print(f"💡 建议增加超时时间（当前：{timeout}秒）")
        return ""
    
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 异常：{str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return ""

# -------------------------- 主程序 --------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("扣子智能体对话工具 - 流式输出修正版")
    print("=" * 80)

    while True:
        question = input("\n请输入你的问题（输入'退出'结束）：").strip()
        
        if question.lower() in ['退出', 'exit', 'quit']:
            print("\n👋 再见！")
            break
        
        if not question:
            continue
        
        stream_chat(question, timeout=180)
