import requests
import json
import sys

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

def chat_with_stream(question: str):
    """
    使用流式输出获取回答（修复版）
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
    print("使用流式输出获取回答...")
    print("=" * 80)

    try:
        response = requests.post(
            "https://api.coze.cn/v3/chat",
            headers=headers,
            json=payload,
            stream=True,
            timeout=180,
            verify=False
        )

        if response.status_code != 200:
            print(f"❌ 请求失败：{response.status_code}")
            print(response.text)
            return

        full_answer = ""
        conversation_id = ""
        delta_count = 0
        
        print("\n📡 开始接收流式数据...\n")

        for line in response.iter_lines():
            if not line:
                continue

            line_str = line.decode('utf-8')

            # 跳过注释行
            if line_str.startswith(':'):
                continue

            # 处理事件行
            if line_str.startswith('event:'):
                continue

            # 处理数据行
            if line_str.startswith('data: '):
                data_str = line_str[6:]

                # 处理 [DONE] 标记
                if data_str == '[DONE]':
                    print("\n\n📊 流结束")
                    break

                try:
                    data = json.loads(data_str)
                    event = data.get('event', '')
                    event_data = data.get('data', {})

                    # 提取 conversation_id
                    if not conversation_id and 'conversation_id' in event_data:
                        conversation_id = event_data['conversation_id']

                    # 处理对话创建事件
                    if event == 'conversation.chat.created':
                        status = event_data.get('status', 'unknown')
                        print(f"💬 对话创建 | 状态：{status}")
                        if conversation_id:
                            print(f"   会话ID：{conversation_id}\n")

                    # 处理对话进行中事件
                    elif event == 'conversation.chat.in_progress':
                        print("⏳ 对话进行中...\n")

                    # 处理知识库召回事件（verbose类型）
                    elif event == 'conversation.message.completed':
                        msg_type = event_data.get('type', '')
                        if msg_type == 'verbose':
                            # 这是知识库召回，不显示
                            pass
                        elif msg_type == 'answer':
                            # 这是最终答案
                            content = event_data.get('content', '')
                            if content and not full_answer:
                                full_answer = content
                                print(f"\n✅ 获取到最终答案（共{len(content)}字符）\n")

                    # 处理增量消息事件 - 这是最重要的！
                    elif event == 'conversation.message.delta':
                        delta_count += 1
                        msg_type = event_data.get('type', '')
                        content = event_data.get('content', '')
                        
                        # 只处理 answer 类型的增量
                        if msg_type == 'answer' and content:
                            full_answer += content
                            print(content, end='', flush=True)

                    # 处理对话完成事件
                    elif event == 'conversation.chat.completed':
                        print(f"\n\n🎉 对话完成 | 增量消息数：{delta_count}")

                except json.JSONDecodeError:
                    pass

        print("\n" + "=" * 80)
        if full_answer:
            print(f"✅ 成功获取回答（共{len(full_answer)}字符，{delta_count}次增量更新）")
        else:
            print("⚠️ 未获取到回答内容")
        print("=" * 80)

        return full_answer

    except Exception as e:
        print(f"❌ 异常：{str(e)}")
        import traceback
        traceback.print_exc()

# -------------------------- 主程序 --------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("扣子智能体对话工具 - 最终修复版")
    print("=" * 80)
    print("\n修复内容：")
    print("✅ 正确识别 SSE 事件类型")
    print("✅ 提取 conversation.message.delta 增量内容")
    print("✅ 提取 conversation.message.completed 最终答案")
    print("=" * 80)

    while True:
        user_question = input("\n请输入你的问题（输入'退出'结束）：")
        if user_question.strip() == "退出":
            print("\n👋 对话结束！")
            break
        if not user_question.strip():
            print("⚠️ 请输入有效问题！")
            continue
        
        result = chat_with_stream(user_question)
        print("=" * 80)
