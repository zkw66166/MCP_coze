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

def chat_with_message_list(question: str):
    """
    正确的流程：
    1. 创建对话，获取 conversation_id
    2. 使用 message/list 接口查询消息
    """
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    # 第一步：创建对话
    print(f"\n🔍 问题：{question}")
    print("=" * 80)
    print("步骤1：创建对话...")
    print("-" * 80)
    
    chat_payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": False,
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

    response = requests.post(
        "https://api.coze.cn/v3/chat",
        headers=headers,
        json=chat_payload,
        timeout=30,
        verify=False
    )

    if response.status_code != 200:
        print(f"❌ 创建对话失败：{response.status_code}")
        print(response.text)
        return

    data = response.json()
    conversation_id = data.get("data", {}).get("conversation_id")
    
    if not conversation_id:
        print("❌ 未获取到 conversation_id")
        return

    print(f"✅ 对话创建成功")
    print(f"   conversation_id: {conversation_id}")
    print(f"   status: {data.get('data', {}).get('status')}")

    # 第二步：查询消息列表
    print("\n" + "=" * 80)
    print("步骤2：查询消息列表...")
    print("-" * 80)

    max_retries = 15  # 最多查询15次
    retry_interval = 2  # 每次间隔2秒

    for retry in range(1, max_retries + 1):
        time.sleep(retry_interval)
        
        print(f"\n🔄 第{retry}次查询...")
        
        # 使用正确的消息列表接口
        msg_url = f"https://api.coze.cn/v3/chat/message/list?conversation_id={conversation_id}"
        
        msg_response = requests.get(
            msg_url,
            headers=headers,
            timeout=10,
            verify=False
        )

        print(f"   状态码：{msg_response.status_code}")

        if msg_response.status_code != 200:
            print(f"   ⚠️ 查询失败：{msg_response.text[:200]}")
            continue

        msg_data = msg_response.json()
        messages = msg_data.get("data", [])

        print(f"   消息数量：{len(messages)}")

        if len(messages) > 0:
            print("\n   📋 消息详情：")
            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content_type = msg.get("content_type", "unknown")
                content = msg.get("content", "")
                
                print(f"\n   [{i+1}] 角色：{role}")
                print(f"       类型：{content_type}")
                
                if content:
                    content_preview = content[:200] if len(content) > 200 else content
                    print(f"       内容预览：{content_preview}")
                
                # 如果是assistant且有内容，这就是回答
                if role == "assistant" and content:
                    print("\n" + "=" * 80)
                    print("✅ 找到智能体回答：")
                    print("=" * 80)
                    print(content)
                    print("=" * 80)
                    return

    print("\n" + "=" * 80)
    print("❌ 轮询完成，未获取到回答")
    print("=" * 80)
    print("\n💡 可能的原因：")
    print("1. 智能体配置问题（知识库未连接、提示词未设置）")
    print("2. 智能体处理超时")
    print("3. API权限或配置问题")
    print("\n💡 建议操作：")
    print("1. 登录扣子控制台检查智能体配置")
    print("2. 确认知识库已连接并包含相关文档")
    print("3. 在智能体提示词中测试该问题")

def chat_with_retrieve(question: str):
    """
    另一种方式：使用 retrieve 接口
    """
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    print(f"\n🔍 问题：{question}")
    print("=" * 80)
    print("使用 retrieve 接口方式...")
    print("-" * 80)

    # 创建对话
    chat_payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": False,
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

    response = requests.post(
        "https://api.coze.cn/v3/chat",
        headers=headers,
        json=chat_payload,
        timeout=30,
        verify=False
    )

    if response.status_code != 200:
        print(f"❌ 创建对话失败：{response.status_code}")
        return

    data = response.json()
    conversation_id = data.get("data", {}).get("conversation_id")
    chat_id = data.get("data", {}).get("id")

    print(f"✅ 对话创建成功")
    print(f"   conversation_id: {conversation_id}")
    print(f"   chat_id: {chat_id}")

    # 使用 retrieve 接口
    print("\n" + "=" * 80)
    print("轮询检索对话状态...")
    print("-" * 80)

    max_retries = 15
    
    for retry in range(1, max_retries + 1):
        time.sleep(2)
        print(f"\n🔄 第{retry}次查询...")
        
        retrieve_url = f"https://api.coze.cn/v3/chat/retrieve?conversation_id={conversation_id}&chat_id={chat_id}"
        
        retrieve_response = requests.get(
            retrieve_url,
            headers=headers,
            timeout=10,
            verify=False
        )

        if retrieve_response.status_code != 200:
            print(f"   ⚠️ 查询失败：{retrieve_response.status_code}")
            continue

        retrieve_data = retrieve_response.json()
        status = retrieve_data.get("data", {}).get("status")
        print(f"   状态：{status}")

        if status == "completed":
            print("\n" + "=" * 80)
            print("✅ 对话已完成")
            print("=" * 80)
            print(f"\n完整响应：")
            print(json.dumps(retrieve_data, ensure_ascii=False, indent=2))
            return
        elif status == "failed":
            print(f"\n❌ 对话失败")
            print(json.dumps(retrieve_data, ensure_ascii=False, indent=2))
            return

    print("\n⚠️ 轮询完成，对话仍在进行中...")

# -------------------------- 主程序 --------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("扣子智能体对话工具")
    print("=" * 80)
    print("\n提供两种查询方式：")
    print("1. 使用 message/list 接口查询消息列表")
    print("2. 使用 retrieve 接口查询对话状态")
    
    print("\n" + "=" * 80)
    print("方式1：message/list")
    print("=" * 80)
    chat_with_message_list("加计扣除政策有哪些")

    print("\n\n" + "=" * 80)
    print("方式2：retrieve")
    print("=" * 80)
    chat_with_retrieve("加计扣除政策有哪些")
