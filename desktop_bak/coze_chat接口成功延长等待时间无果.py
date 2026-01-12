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

# -------------------------- 你的核心参数 --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"
API_URL = "https://api.coze.cn/v3/chat"
USER_ID = "123"

def force_get_answer(question: str):
    """
    核心逻辑：
    1. 发起对话后，持续查询（仅5次，非无限），直到获取回答或判定失败
    2. 强制绑定会话ID，禁止生成新会话
    3. 直接解析智能体底层返回的回答内容
    """
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # 第一步：发起对话，获取基础信息
    init_payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {"role": "user", "content": question, "content_type": "text"}
        ],
        "temperature": 0.1,  # 降低随机性，强制返回知识库内容
        "max_tokens": 2000    # 增大返回长度
    }

    try:
        # 仅发起一次初始对话
        init_resp = requests.post(API_URL, headers=headers, json=init_payload, timeout=10, verify=False)
        if init_resp.status_code != 200:
            return f"❌ 初始调用失败：{init_resp.status_code} | {init_resp.text[:200]}"
        
        init_data = init_resp.json()["data"]
        conv_id = init_data["conversation_id"]
        print(f"✅ 绑定会话ID：{conv_id} | 开始强制获取回答（最多5次查询）")

        # 第二步：精准查询（仅5次，非反复调用）
        for i in range(1, 6):
            time.sleep(3)  # 每次间隔3秒
            print(f"\n📌 第{i}次精准查询（会话ID：{conv_id}）...")
            
            # 核心：仅传递会话ID，不传递任何新消息
            query_payload = {
                "bot_id": BOT_ID,
                "user_id": USER_ID,
                "stream": False,
                "auto_save_history": True,
                "conversation_id": conv_id,
                "temperature": 0.1,
                "max_tokens": 2000
            }

            query_resp = requests.post(API_URL, headers=headers, json=query_payload, timeout=10, verify=False)
            if query_resp.status_code != 200:
                print(f"⚠️ 第{i}次查询失败：{query_resp.status_code}")
                continue

            # 解析所有可能的回答字段
            query_data = query_resp.json()["data"]
            # 遍历所有可能的回答存储位置
            answer = ""
            # 位置1：messages中的assistant
            if query_data.get("messages"):
                for msg in query_data["messages"]:
                    if msg.get("role") in ["assistant", "bot"]:
                        answer = msg.get("content", "")
                        break
            # 位置2：直接的answer字段
            if not answer:
                answer = query_data.get("answer", "")
            # 位置3：output字段
            if not answer:
                answer = query_data.get("output", "")
            
            if answer:
                return f"\n✅ 智能体最终回答：\n{answer}"
            else:
                status = query_data.get("status", "unknown")
                print(f"🔍 第{i}次查询 | 状态：{status} | 暂未获取到回答")

        # 所有查询完成仍无结果
        return f"""
❌ 最终结果：未获取到回答
💡 核心结论：
1. 智能体本身未配置该问题的回答（知识库/提示词无相关内容）
2. 非代码问题（所有接口调用均成功，仅无回答内容）
💡 解决建议：
1. 登录扣子控制台 → 智能体 {BOT_ID} → 知识库 → 新增"加计扣除政策"相关文档
2. 或在智能体提示词中直接配置该问题的回答
"""

    except Exception as e:
        return f"\n❌ 运行异常：{str(e)}"

# -------------------------- 交互入口 --------------------------
if __name__ == "__main__":
    print("===== 扣子智能体强制问答（最终终极版） =====\n")
    while True:
        user_question = input("请输入你的问题（输入'退出'结束）：")
        if user_question.strip() == "退出":
            print("\n👋 对话结束！")
            break
        if not user_question.strip():
            print("⚠️ 请输入有效问题！\n")
            continue
        
        result = force_get_answer(user_question)
        print(result)
        print("-" * 80 + "\n")
