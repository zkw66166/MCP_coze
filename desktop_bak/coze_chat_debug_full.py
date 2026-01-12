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

def debug_full_response(question: str):
    """
    完全调试版本：打印所有可能的响应信息
    """
    headers = {
        "Authorization": f"Bearer {PAT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    payload = {
        "bot_id": BOT_ID,
        "user_id": USER_ID,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {"role": "user", "content": question, "content_type": "text"}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    print("=" * 80)
    print("完整调试模式")
    print("=" * 80)
    
    print(f"\n📡 请求信息：")
    print(f"  URL: {API_URL}")
    print(f"  BOT_ID: {BOT_ID}")
    print(f"  问题: {question}")
    print(f"\n📋 请求头（隐藏Token）：")
    for k, v in headers.items():
        if k.lower() == 'authorization':
            print(f"  {k}: Bearer ************")
        else:
            print(f"  {k}: {v}")
    print(f"\n📝 请求体：")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("发送请求...")
    print("=" * 80)
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30, verify=False)
        
        print(f"\n📊 响应状态码：{response.status_code}")
        print(f"📊 响应头：")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        
        print(f"\n📄 原始响应内容（前2000字符）：")
        print(response.text[:2000])
        
        if response.status_code == 200:
            print(f"\n\n🔍 解析JSON...")
            try:
                data = response.json()
                print(f"\n完整JSON响应：")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                # 尝试提取所有可能的字段
                print("\n" + "=" * 80)
                print("尝试提取回答内容...")
                print("=" * 80)
                
                if "data" in data:
                    resp_data = data["data"]
                    print(f"✅ 找到 data 字段")
                    
                    # 打印 data 的所有键
                    print(f"\ndata 字段的所有键：{list(resp_data.keys())}")
                    
                    # 尝试各种可能的字段
                    for key in resp_data.keys():
                        value = resp_data[key]
                        print(f"\n📌 字段 '{key}' 类型: {type(value).__name__}")
                        if isinstance(value, str) and len(value) > 0:
                            print(f"  内容（前200字符）：{value[:200]}")
                        elif isinstance(value, list):
                            print(f"  列表长度：{len(value)}")
                            if len(value) > 0:
                                print(f"  第一个元素：{str(value[0])[:200]}")
                        elif isinstance(value, dict):
                            print(f"  字典键：{list(value.keys())}")
                
                # 尝试直接查找 answer 或 content 字段
                if "data" in data and "answer" in data["data"]:
                    print(f"\n✅ 找到 answer 字段：{data['data']['answer']}")
                
                # 检查是否有 messages
                if "data" in data and "messages" in data["data"]:
                    messages = data["data"]["messages"]
                    print(f"\n✅ 找到 messages 列表，共 {len(messages)} 条消息")
                    for i, msg in enumerate(messages):
                        print(f"\n  消息 {i+1}:")
                        for key, value in msg.items():
                            if isinstance(value, str) and len(value) > 0:
                                print(f"    {key}: {value[:200]}")
                            else:
                                print(f"    {key}: {value}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败：{e}")
        else:
            print(f"\n❌ 请求失败，状态码：{response.status_code}")
    
    except Exception as e:
        print(f"❌ 异常：{str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)

# 测试
if __name__ == "__main__":
    debug_full_response("加计扣除政策有哪些")
