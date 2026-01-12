import requests
import json
import sys

# -------------------------- 强制Windows UTF-8编码（解决中文乱码/编码报错） --------------------------
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -------------------------- 配置你的核心参数（已填充你的真实值，无需修改） --------------------------
PAT_TOKEN = "pat_6IkhWiD17bW1qZmXHzeKPPU2YZzBQG8OlqyUyUSXlEFIGBPfOYlTsPK5VHjUSPz8"
BOT_ID = "7592559564151668742"  # 智能体ID（curl里的bot_id）
API_URL = "https://api.coze.cn/v3/chat"

def coze_chat(question: str):
    """
    调用扣子V3版Chat API
    :param question: 用户提问内容（如"早上好"）
    :return: 智能体回答/错误信息
    """
    # 1. 构造请求头（完全对齐curl示例）
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 2. 构造请求体（严格匹配curl的JSON结构）
    payload = {
        "bot_id": BOT_ID,
        "user_id": "123",  # 固定值，和curl一致
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": question,
                "content_type": "text"
            }
        ]
    }

    try:
        # 3. 发送请求（关闭SSL验证，兼容Windows环境）
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )

        print(f"📌 响应状态码：{response.status_code}")
        
        # 4. 强制UTF-8解析响应（彻底解决编码问题）
        response.encoding = "utf-8"
        
        # 5. 处理响应结果
        if response.status_code != 200:
            return f"❌ 请求失败：状态码 {response.status_code} | 详情：{response.text[:300]}"
        
        # 解析JSON响应
        result = response.json()
        
        # 6. 提取智能体回答
        if result.get("code") == 0:
            # 从data.messages中提取assistant的回答
            answer = ""
            for msg in result.get("data", {}).get("messages", []):
                if msg.get("role") == "assistant":
                    answer = msg.get("content", "")
                    break
            return f"✅ 智能体回答：\n{answer}"
        else:
            return f"❌ 调用失败：{result.get('msg', '未知错误')}（错误码：{result.get('code')}）"

    except json.JSONDecodeError as e:
        return f"❌ JSON解析失败：{str(e)} | 原始响应：{response.text[:300]}"
    except Exception as e:
        # 强制UTF-8输出错误信息
        err_msg = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        return f"❌ 运行错误：{err_msg}"

# -------------------------- 交互入口（可直接提问） --------------------------
if __name__ == "__main__":
    print("===== 扣子V3 API智能体问答 =====")
    print("输入'退出'可结束对话\n")
    
    while True:
        try:
            user_question = input("请输入你的问题：")
            if user_question.strip() == "退出":
                print("对话结束！")
                break
            if not user_question.strip():
                print("⚠️ 请输入有效问题！")
                continue
            
            # 调用问答函数
            result = coze_chat(user_question)
            print(result)
            print("-" * 50)
        
        except Exception as e:
            err = str(e).encode("utf-8", errors="ignore").decode("utf-8")
            print(f"❌ 输入错误：{err}")
